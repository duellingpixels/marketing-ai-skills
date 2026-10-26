# Shopify: prepare the checker inputs

## Export products

In Shopify admin, open **Products** and use **Export**. Download the product CSV, keeping the original English headers. Export variants with unique SKUs.

Supported header pairs include:

| Current | Legacy |
|---|---|
| URL handle | Handle |
| SKU | Variant SKU |
| Price | Variant Price |
| Published on online store | Published |

Keep Title and Status too. Product-level title, publication and status are carried to variant rows sharing the handle. Image-only rows are skipped. Draft/archived products are flagged. Missing visibility data or an unlisted product remains unverified. An active product with the online-store publication flag true is considered published by the export; actual customer access still needs checking.

## Provide available stock

Use the separate **Inventory** export to obtain availability for the locations serving your campaign. Prepare the shared stock.csv with exactly one sku and available_quantity per promoted variant. Use available-to-sell units, not on-hand totals that include committed/unavailable stock. Only combine locations that can fulfil the campaign. Do not include third-party inventory you cannot sell.

The product CSV's inventory field does not establish multi-location availability. The checker deliberately ignores it and requests the explicit stock file. It does not directly import the native inventory CSV in this version.

Missing SKUs must be assigned or mapped before checking. Duplicate variant SKUs cannot be safely matched and stop the run.

## Prices and discounts

Price/Variant Price is the current base price. Compare-at price is not the current price. Automatic discounts, discount codes and market-specific prices need separate observation. Run one currency/market at a time. Set up offers.csv using the effective price a shopper should pay and document any code required.

Costs and prices must share a comparable tax and currency basis before enabling contribution calculations. Confirm actual product access and offer behaviour on the storefront.

## Run and status

Use the Shopify command in the root README, including `--stock`. Tested using synthetic current and legacy header fixtures, continuation variants and image rows. A live development-store export and checkout have not been tested for this release.

Official references, checked 26 October 2026:

- [Product CSV format](https://help.shopify.com/en/manual/products/import-export/using-csv)
- [Product exports](https://help.shopify.com/en/manual/products/import-export/export-products)
- [Inventory CSVs](https://help.shopify.com/en/manual/inventory-and-locations/setup/inventory-csv)
