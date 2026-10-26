"""Deterministic readiness findings. Missing evidence never becomes a pass."""
from collections import Counter
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from .evidence import validate_evidence, iso_date
from .imports import InputError, money


def amount(value):
    return format(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f')


def audit(products, offers, platform, currency, as_of, stock=None, evidence=None,
          low_stock=10, max_age_days=7):
    if type(low_stock) is not int or low_stock < 0 or type(max_age_days) is not int or max_age_days < 0:
        raise InputError('Stock threshold and evidence age must be non-negative whole numbers.')
    if type(as_of) is not date:
        raise InputError('Report date must be a date.')
    if not offers:
        raise InputError('At least one promoted offer is required.')
    findings = []

    def add(priority, code, sku, title, evidence_text, action):
        findings.append(dict(priority=priority, code=code, sku=sku, title=title,
                             evidence=evidence_text, action=action))

    observations = {}
    if evidence is not None:
        observed = validate_evidence(evidence, as_of)
        if (as_of - observed).days > max_age_days:
            add('unknown','evidence_stale',None,'Refresh the supplied observations',
                f'Evidence date {observed.isoformat()}; maximum age {max_age_days} days.',
                'Repeat Merchant Center, Analytics and page checks, then rerun the report.')
        else:
            observations = evidence
    merchant = {row['sku']:row for row in observations.get('merchant',[])}
    pages = {row['sku']:row for row in observations.get('pages',[])}
    results = []
    for offer in offers:
        sku = offer.sku
        if offer.currency != currency:
            raise InputError(f'{sku}: currency differs from the report.')
        product = products.get(sku)
        result = dict(sku=sku, name=product.name if product else None,
                      planned_price=amount(offer.planned_price), stock=None,
                      contribution_per_unit=None, contribution_percent=None)
        results.append(result)
        if product is None:
            add('blocker','product_missing',sku,'Promoted SKU is missing from the usable product export',
                f'No purchasable variant with exact SKU {sku!r} was imported.',
                'Check the SKU, export the relevant variant and confirm it is purchasable.')
        else:
            if product.published is False:
                add('blocker','not_published',sku,'Product is not published to the online store',
                    'The export marks this product or its parent as unpublished/inactive.',
                    'Review product and parent publication before promoting it.')
            elif product.published is None:
                add('unknown','publication_unknown',sku,'Verify product visibility',
                    'The export does not establish online-store publication.',
                    'Open the product as a shopper and check its parent and sales-channel settings.')
            if product.price is None:
                add('unknown','price_unknown',sku,'Verify the current product price',
                    'The price is missing or a WooCommerce scheduled sale cannot be resolved from this snapshot.',
                    'Check the actual storefront price and the sale schedule in the store timezone.')
            elif product.price != offer.planned_price:
                add('review','price_difference',sku,'Current and planned prices differ',
                    f'Export price {amount(product.price)}; planned price {amount(offer.planned_price)} {currency}.',
                    'Confirm whether this is the intended pre-sale price or an offer that still needs configuring. Check at launch.')
            if product.backorder:
                add('review','backorder_review',sku,'Review fulfilment before promoting a backordered product',
                    'The WooCommerce export marks this product as on backorder.',
                    'Confirm replenishment dates, shopper messaging and delivery promises. Backorders do not establish campaign readiness.')
            quantity = stock.get(sku) if stock is not None and sku in stock else product.stock
            result['stock'] = quantity
            if quantity is not None and quantity <= 0 or product.in_stock is False:
                add('blocker','no_stock',sku,'Promoted product is unavailable or has no available stock',
                    f'Available quantity {quantity}; export in-stock flag {product.in_stock}.',
                    'Check availability, replenishment and backorder policy before promoting this product.')
            elif quantity is None:
                add('unknown','stock_unknown',sku,'Verify available-to-sell stock',
                    'No usable available quantity was supplied; unknown is not zero.',
                    'Supply stock.csv with available-to-sell units for the locations serving this campaign.')
            else:
                if quantity < low_stock:
                    add('review','low_stock',sku,'Stock is below the selected threshold',
                        f'{quantity} units available; low-stock threshold {low_stock}.',
                        'Review promotion volume and replenishment before increasing spend.')
                if offer.expected_units is not None and quantity < offer.expected_units:
                    add('review','stock_shortfall',sku,'Stock is below your supplied campaign demand',
                        f'{quantity} units available; your expected demand {offer.expected_units}.',
                        'Adjust the campaign quantity or replenish. This check does not forecast demand.')
        if offer.expected_units is None:
            add('unknown','demand_unknown',sku,'Supply expected campaign units',
                'No expected_units value was supplied.',
                'Add your planned unit demand to compare campaign needs with stock.')
        if offer.cost_basis_confirmed is True and offer.unit_cost is not None and offer.other_unit_cost is not None:
            contribution = offer.planned_price - offer.unit_cost - offer.other_unit_cost
            result['contribution_per_unit'] = amount(contribution)
            result['contribution_percent'] = amount(contribution / offer.planned_price * 100) if offer.planned_price else None
            if contribution < 0:
                add('review','negative_contribution',sku,'Offer retains less than its supplied unit costs',
                    f'{amount(offer.planned_price)} - {amount(offer.unit_cost)} - {amount(offer.other_unit_cost)} = {amount(contribution)} {currency} per unit.',
                    'Review the discount and costs before launching. This calculation excludes unprovided overhead.')
            elif contribution == 0:
                add('review','zero_contribution',sku,'Offer leaves no contribution after supplied unit costs',
                    f'Contribution {amount(contribution)} {currency} per unit.',
                    'Review whether the promotion can cover business overhead or has another stated purpose.')
        else:
            add('unknown','costs_unknown',sku,'Verify offer contribution',
                'Comparable unit_cost, other_unit_cost and explicit cost_basis_confirmed=true are required.',
                'Supply both costs on the same currency and tax basis as the price; use 0 only for a known zero cost.')
        issue = merchant.get(sku)
        if issue is None:
            add('unknown','merchant_unknown',sku,'Check Merchant Center eligibility if using Google Shopping',
                'No current, SKU-matched Merchant Center observation was supplied.',
                'Review the intended destination and country; record status and issue against this exact SKU.')
        elif issue['status'] != 'approved':
            disapproved = issue['status'] == 'disapproved'
            add('blocker' if disapproved else 'review', 'merchant_disapproved' if disapproved else 'merchant_pending',
                sku,'Review Merchant Center product status',
                f'Status {issue["status"]}; issue: {issue.get("issue", "not supplied")}.',
                'Resolve the listed issue and confirm eligibility for the intended campaign destination.')
        page = pages.get(sku)
        if page is None:
            add('unknown','page_unknown',sku,'Verify the advertised page',
                'No current, SKU-matched page observation was supplied.',
                'Open the sale URL on mobile, record its final HTTP status, visible price and currency, and test the offer.')
        else:
            if not 200 <= page['http_status'] < 300:
                add('blocker' if page['http_status'] in (404,410) else 'review','page_error',sku,
                    'Review the sale page response',f'{page["url"]}: observed HTTP {page["http_status"]}.',
                    'Check the final destination and update the campaign link where needed.')
            if page.get('observed_price') is None or not page.get('currency'):
                add('unknown','page_price_unknown',sku,'Record the visible page price and currency',
                    'Page evidence does not include both an observed_price and currency.',
                    'Record the actual offer price visible to the shopper, including any code requirements.')
            else:
                if page['currency'] != currency:
                    add('review','page_currency',sku,'Observed page currency differs',
                        f'Page currency {page["currency"]}; planned currency {currency}.',
                        'Verify the intended market and use a separate report for each currency.')
                elif money(page['observed_price'],'observed price') != offer.planned_price:
                    add('review','page_price_difference',sku,'Observed page price differs from the planned offer',
                        f'Observed {page["observed_price"]}; planned {amount(offer.planned_price)} {currency}.',
                        'Confirm the schedule or discount code and repeat this check when the offer is live.')
    analytics = observations.get('analytics')
    if analytics is None or (as_of - iso_date(analytics['period_end'],'period_end')).days > max_age_days:
        add('unknown','tracking_unknown',None,'Verify recent purchase tracking',
            'No sufficiently recent Analytics purchase observation was supplied.',
            'Record the reporting period, purchase event count and purchase revenue, then validate against store orders.')
    else:
        if analytics['purchase_events'] == 0:
            add('review','no_purchase_events',None,'No purchase events were recorded in the supplied period',
                f'{analytics["period_start"]} to {analytics["period_end"]}: 0 purchase events.',
                'Check whether sales occurred. Zero events can reflect no purchases or a tracking problem.')
        add('unknown','tracking_validation',None,'Recorded events do not prove tracking is correct',
            f'{analytics["period_start"]} to {analytics["period_end"]}: {analytics["purchase_events"]} purchase events; revenue {analytics["purchase_revenue"]} (report currency assumed).',
            'Compare store order IDs, revenue and duplicate events. Perform a separately authorised checkout test where needed.')
    add('unknown','manual_checks',None,'Complete the remaining shopper checks',
        'Exports and recorded observations do not test checkout, payment, mobile usability, shipping or site capacity.',
        'Verify offer dates/timezone, mobile checkout, payments, shipping, returns, discount codes and capacity before launch.')
    rank = {'blocker':0,'review':1,'unknown':2}
    findings.sort(key=lambda item: rank[item['priority']])
    counts = Counter(f['priority'] for f in findings)
    return dict(schema_version='1.0', platform=platform, currency=currency, as_of=as_of.isoformat(),
                summary='Action list generated; this is not a store readiness certification.',
                counts={p:counts[p] for p in rank}, products=results, findings=findings,
                coverage=dict(product_export=True, stock_file_supplied=stock is not None,
                              current_evidence=bool(observations), merchant_skus=len(merchant), page_skus=len(pages),
                              analytics_observation=analytics is not None),
                sources={}, assumptions=[
                    'Product export prices are interpreted in the report currency and the store export price basis.',
                    'Stock and product snapshots can change after export; confirm them again before launch.',
                    'Contribution uses only supplied comparable unit costs; it is not total business profit.',
                    'No network, API, AI or store changes were performed. This is not a checkout test.'])
