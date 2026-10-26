# WooCommerce: prepare the checker inputs

## Export products

In WordPress, go to **Products → All Products → Export**. Use the built-in WooCommerce exporter and English column headers. Export the full catalogue where possible so variation parents can be resolved. Keep IDs, Type, SKU, Name, Published, Parent, Regular price, Sale price, sale dates, Stock and In stock?. Do not import or edit the source store for this check.

The premium Product CSV Import Suite has a different schema and is not supported by this adapter. Translated/localised headers are not yet supported.

Use each purchasable variation's unique SKU in offers.csv. Variable, grouped and external parent products are excluded. A variation whose parent is missing has unverified publication status. Blank SKUs cannot be matched; duplicate SKUs stop the run and need correction or an unambiguous export.

## Stock and prices

The core export may supply Stock and In stock?. Blank quantities and Stock=parent stay unknown. Comma-separated Type flags are recognised; In stock?=backorder produces a fulfilment review. Where stock is managed at parent level or by a third-party system, prepare stock.csv with the actual available-to-sell quantity for each promoted variation. Shared parent stock must not be counted in full for every child: this first version does not model shared inventory pools.

A product marked out of stock remains a blocker even if a separate quantity file is positive; investigate the conflicting evidence. Backorders need a manual policy review.

The adapter uses a non-scheduled sale price when present, otherwise regular price. Scheduled sale dates cause current price to remain unverified: the checker does not guess the store timezone or schedule state. Automatic/coupon discounts are not in this snapshot. Supply observed effective page prices separately and confirm the offer at launch.

Prices and costs must use a comparable currency and tax basis. Enter unit_cost, other_unit_cost and cost_basis_confirmed=true only after checking that basis. Do not interpret contribution as total profit.

## Run

Use the WooCommerce command in the root README with your own files and dates. Include `--stock path/to/stock.csv` if using a quantity file. Keep original inputs in a local ignored data/ folder.

## Verification status

Tested using synthetic core-export fixtures, including variable parents and variations. A real development-store export and checkout have not been tested for this release.

Official format reference, checked 26 October 2026: [WooCommerce core CSV importer/exporter](https://woocommerce.com/document/product-csv-importer-exporter/).
