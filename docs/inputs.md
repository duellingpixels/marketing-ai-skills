# Inputs and report interpretation

Files are local UTF-8 comma-separated CSV, or JSON for observations. No network request is made. Decimal numbers use a full stop without currency symbols or thousands separators. This release supports monetary values to two decimal places (harmless trailing zeros are accepted); more precise amounts are rejected instead of silently rounded. Header spelling and case matter. Extra irrelevant product columns are ignored. Duplicate headers, duplicate SKUs and malformed rows fail clearly.

## Offers CSV

| Field | Required | Meaning |
|---|---|---|
| sku | Yes | Exact unique purchasable variant SKU. Preserve case and leading zeros. |
| planned_price | Yes | Effective planned unit selling price, non-negative, in the report currency. |
| currency | Yes | Must equal the report's three-letter uppercase currency, e.g. AUD. |
| expected_units | No | Your planned campaign demand, a non-negative integer. Not an AI forecast. |
| unit_cost | No | Unit product cost, comparable to the selling-price tax basis. |
| other_unit_cost | No | Supplied unit selling costs on that same basis. Enter 0 only if known to be zero. |
| cost_basis_confirmed | No | true only when currency and tax treatment match across price and costs. |

Empty optional cells mean unknown. Unit Margin requires both costs and cost_basis_confirmed=true. Unit Margin = planned selling price − unit cost − other unit costs. Unit Margin/Sale Price (%) is that margin divided by planned selling price, expressed as a percentage. The report shows the cost inputs alongside the results. Missing costs show Not supplied; uncalculated margins show Not calculated. Known zero costs show 0.00. These measures exclude costs you have not included and are not total business profit. A positive margin is not a recommendation to spend more.

## Stock CSV

sku,available_quantity. One row per SKU. Whole numbers only; zero and negative availability are meaningful. Missing rows fall back to usable WooCommerce export stock, or remain unknown on Shopify. Do not mix campaign markets or double-count shared stock pools.

## Recorded evidence JSON

See examples/black-friday/evidence.json for a complete fictional example. This is a shared observation format, not a raw Merchant Center or Analytics export. Do not claim a service was connected merely because this file was supplied.

- as_of: required ISO observation date (YYYY-MM-DD), not after the report date. Only include observations actually checked on this date. Older data must not be relabelled as fresh.
- merchant: optional list of objects with sku, status (approved/disapproved/pending), and optional issue text. One row per SKU. Record the destination and country in issue text where relevant. Service item IDs must be mapped to variant SKUs before preparing this file.
- analytics: optional object with period_start, period_end, purchase_events (non-negative integer) and purchase_revenue (non-negative amount). Period dates must be ordered and end on or before the observation date. Use the same report currency. Purchase activity is evidence of recorded events, not validation of their correctness.
- pages: optional list with sku, url, http_status (integer), observed_price and currency. Use final URLs/statuses after redirects, and actual shopper-visible prices. One row per SKU. HTTP 200 alone cannot establish that the correct page, price, stock or checkout works. Without price and currency, price remains unverified.

Evidence older than --max-evidence-age-days (default 7) is not used for current checks. An old Analytics period remains unverified even if the observation file is recent. Future dates and duplicate entries are errors.

## Dates and outputs

--as-of is the explicit report date; --exported-on is the oldest product or stock export snapshot. Missing/old snapshot dates produce a finding. Stale exports are still analysed to surface possible problems, but the report requests new exports. Campaign start and end are inclusive planning dates; the checker does not activate or schedule offers.

report.json stores findings with code, priority, sku, title, evidence and action. Money is represented as decimal strings to preserve calculations. report.md is the human-readable version. Every run needs a fresh output directory; existing reports are never silently overwritten.

blocker means known evidence warrants resolving the issue before promotion. review means investigate a risk or difference. unknown means evidence is absent or inadequate; some checks may be inapplicable to a particular campaign. Counts measure findings, not distinct products. There is no blanket ready score.

For compatibility, JSON fields contribution_per_unit and contribution_percent retain their original names. They supply the readable report's Unit Margin and Unit Margin/Sale Price (%) columns. Product results now also include unit_cost, other_unit_cost and cost_basis_confirmed so the inputs can be checked.
