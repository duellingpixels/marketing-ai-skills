> Fictional WooCommerce example. Generated from the checked-in synthetic fixtures with report date 2 November 2026.

# Black Friday readiness: actions to review

Platform: **woocommerce** · Report date: **2026-11-02** · Currency: **AUD**

Action list generated; this is not a store readiness certification.

**5 blockers · 5 review items · 6 checks needing evidence**

Finding counts are individual checks, not numbers of affected products. Unknown checks may be inapplicable; record why when reviewing them.

## Sources

- products: woocommerce-products.csv
- offers: offers.csv
- evidence: evidence.json

## Promoted products

| SKU | Planned price | Available units | Contribution per unit | Contribution % |
|---|---:|---:|---:|---:|
| TEA-250 | 15.00 | 8 | 3.00 | 20.00 |
| CUP-BLU | 20.00 | 0 | -1.00 | -5.00 |
| CUP-RED | 25.00 | 40 | 10.00 | 40.00 |
| BUNDLE-MISSING | 35.00 | Unverified | Unverified | Unverified |

## Resolve before promotion

### Product is not published to the online store [CUP-BLU]

**Evidence:** The export marks this product or its parent as unpublished/inactive.

**Action:** Review product and parent publication before promoting it.

### Promoted product is unavailable or has no available stock [CUP-BLU]

**Evidence:** Available quantity 0; export in-stock flag False.

**Action:** Check availability, replenishment and backorder policy before promoting this product.

### Review Merchant Center product status [CUP-BLU]

**Evidence:** Status disapproved; issue: Fictional price mismatch for AU Shopping.

**Action:** Resolve the listed issue and confirm eligibility for the intended campaign destination.

### Review the sale page response [CUP-BLU]

**Evidence:** https://example.com/products/ceramic-cup-blue: observed HTTP 404.

**Action:** Check the final destination and update the campaign link where needed.

### Promoted SKU is missing from the usable product export [BUNDLE-MISSING]

**Evidence:** No purchasable variant with exact SKU 'BUNDLE-MISSING' was imported.

**Action:** Check the SKU, export the relevant variant and confirm it is purchasable.


## Review before launch

### Current and planned prices differ [TEA-250]

**Evidence:** Export price 20.00; planned price 15.00 AUD.

**Action:** Confirm whether this is the intended pre-sale price or an offer that still needs configuring. Check at launch.

### Stock is below the selected threshold [TEA-250]

**Evidence:** 8 units available; low-stock threshold 10.

**Action:** Review promotion volume and replenishment before increasing spend.

### Stock is below your supplied campaign demand [TEA-250]

**Evidence:** 8 units available; your expected demand 30.

**Action:** Adjust the campaign quantity or replenish. This check does not forecast demand.

### Observed page price differs from the planned offer [TEA-250]

**Evidence:** Observed 20.00; planned 15.00 AUD.

**Action:** Confirm the schedule or discount code and repeat this check when the offer is live.

### Offer retains less than its supplied unit costs [CUP-BLU]

**Evidence:** 20.00 - 15.00 - 6.00 = -1.00 AUD per unit.

**Action:** Review the discount and costs before launching. This calculation excludes unprovided overhead.


## Checks still needing evidence

### Verify the advertised page [CUP-RED]

**Evidence:** No current, SKU-matched page observation was supplied.

**Action:** Open the sale URL on mobile, record its final HTTP status, visible price and currency, and test the offer.

### Verify offer contribution [BUNDLE-MISSING]

**Evidence:** Comparable unit\_cost, other\_unit\_cost and explicit cost\_basis\_confirmed=true are required.

**Action:** Supply both costs on the same currency and tax basis as the price; use 0 only for a known zero cost.

### Check Merchant Center eligibility if using Google Shopping [BUNDLE-MISSING]

**Evidence:** No current, SKU-matched Merchant Center observation was supplied.

**Action:** Review the intended destination and country; record status and issue against this exact SKU.

### Verify the advertised page [BUNDLE-MISSING]

**Evidence:** No current, SKU-matched page observation was supplied.

**Action:** Open the sale URL on mobile, record its final HTTP status, visible price and currency, and test the offer.

### Recorded events do not prove tracking is correct

**Evidence:** 2026-10-26 to 2026-11-01: 12 purchase events; revenue 420.00 (report currency assumed).

**Action:** Compare store order IDs, revenue and duplicate events. Perform a separately authorised checkout test where needed.

### Complete the remaining shopper checks

**Evidence:** Exports and recorded observations do not test checkout, payment, mobile usability, shipping or site capacity.

**Action:** Verify offer dates/timezone, mobile checkout, payments, shipping, returns, discount codes and capacity before launch.


## Limits and assumptions

- Product export prices are interpreted in the report currency and the store export price basis.
- Stock and product snapshots can change after export; confirm them again before launch.
- Contribution uses only supplied comparable unit costs; it is not total business profit.
- No network, API, AI or store changes were performed. This is not a checkout test.
- Campaign dates 2026-11-27 to 2026-11-30; check scheduling in the store timezone.
