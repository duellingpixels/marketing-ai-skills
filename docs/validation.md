# Initial validation — 26 October 2026

## Verified locally

- 56 automated unittest cases pass on Python 3.13.7.
- The documented WooCommerce and Shopify commands generate JSON and Markdown reports.
- Integration tests also run the legacy Shopify-header example.
- Both platform examples return the expected five blocker findings, five review findings and six checks needing evidence. They use fictional products and observations.
- The sample includes contribution of AUD 3.00 per unit for TEA-250 and AUD -1.00 for CUP-BLU from the supplied comparable costs.
- Python source parses with Python 3.10 syntax. Runtime validation on Python 3.10 is delegated to GitHub Actions; see the workflow run for its actual result.
- The reusable skill passes the skill frontmatter/naming validator.

## Independent review

A separate reviewer checked source, tests, instructions and examples against the design. Review findings led to regression tests and fixes for WooCommerce parent-managed stock, backorder status, variation type flags and unsupported monetary precision. Final local suite passed after the fixes.

## Not yet verified

- A fresh real WooCommerce or Shopify development-store export.
- Direct API access, native inventory-file imports or live-page crawling; these are not implemented.
- Skill installation/discovery in individual AI applications.
- A real purchase, checkout, payment, shipping calculation or capacity test.
- Measured marketing or revenue improvement.

The release produces an evidence-led preparation report. It is not proof that a store or campaign is ready to launch.
