# Marketing AI Skills

**Practical marketing tools from [Duelling Pixels](https://duellingpixels.com). Free code, worked examples and reusable AI skills.**

Use your own marketing and store data to find the next action worth taking. Each tool shows its evidence, explains missing information and includes examples you can run before connecting a real account.

Code and guides are MIT-licensed. Third-party accounts, data services and AI subscriptions can have their own charges. The first tool runs locally without API keys, AI calls, paid services or extra Python packages.

## First tool: Black Friday readiness checker

Find problems before promoting a sale on **WooCommerce or Shopify**:

- Promoted SKUs missing from the product export or not published to the online store.
- Unavailable products, low stock and stock below your supplied campaign demand.
- Current prices that differ from planned offers, including differences that may be intentional before launch.
- Offers that retain too little after supplied comparable costs.
- Recorded Merchant Center issues, page observations and gaps in purchase-tracking evidence.

**Current status: initial offline release, tested against synthetic fixtures in documented export formats. Live-store exports and AI application installation have not yet been independently validated.** Direct API connections and an automated page crawler are not included. Page, Merchant Center and Analytics checks use observations you supply; missing evidence stays unverified.

## Try it in five minutes

Install Python 3.10 or newer. Download this repository using **Code → Download ZIP** and extract it, or clone it. Open a terminal in the repository folder.

**WooCommerce example**

```sh
python3 skills/black-friday-readiness/scripts/check.py \
  --platform woocommerce \
  --products examples/black-friday/woocommerce-products.csv \
  --offers examples/black-friday/offers.csv \
  --evidence examples/black-friday/evidence.json \
  --currency AUD --as-of 2026-11-02 --exported-on 2026-11-02 \
  --campaign-start 2026-11-27 --campaign-end 2026-11-30 \
  --output-dir reports/woo-demo
```

**Shopify example**

```sh
python3 skills/black-friday-readiness/scripts/check.py \
  --platform shopify \
  --products examples/black-friday/shopify-products.csv \
  --stock examples/black-friday/stock.csv \
  --offers examples/black-friday/offers.csv \
  --evidence examples/black-friday/evidence.json \
  --currency AUD --as-of 2026-11-02 --exported-on 2026-11-02 \
  --campaign-start 2026-11-27 --campaign-end 2026-11-30 \
  --output-dir reports/shopify-demo
```

On Windows, use `py` if `python3` is not available. Each example writes `report.md` for reading and `report.json` for further processing. Use a new output directory each time: existing reports are preserved. See the checked-in [example report](examples/black-friday/expected-report.md).

The examples deliberately include a stockout, an unpublished variant, an unprofitable offer after supplied costs and a missing product. They are fictional and are never imported into your store.

Exit code 0 means report generation succeeded, **not that your store is ready**. Invalid input returns exit code 2.

## Use your own store data

1. Follow the [WooCommerce guide](docs/platforms/woocommerce.md) or [Shopify guide](docs/platforms/shopify.md).
2. Copy the [offer template](templates/offers.csv), then list the exact variant SKUs you plan to promote. Keep SKU text intact, including leading zeros.
3. Supply fresh available-to-sell stock where the export cannot establish it. Shopify requires the [stock template](templates/stock.csv) for quantity checks.
4. Optionally record Merchant Center, Analytics and page observations using the [input reference](docs/inputs.md). The example evidence JSON is a filled fictional example, not a native service export.
5. Run the command with your file paths, currency, actual report date and campaign dates. Do not use the sample dates for a current audit. Set `--exported-on` to the oldest product or stock snapshot used.
6. Review blockers first, then review items and missing checks. Confirm changing stock and prices again at launch.

Without API connections the checker does not discover issues in the live services. It analyses what you provide and makes coverage limits visible. Even a report with no known blockers is not a checkout test or store certification.

## Use it as an AI skill

Read [the skill instructions](skills/black-friday-readiness/SKILL.md) in your AI coding assistant. Keep the cloned repository available: the script depends on the repository's `src` folder, so copying the skill folder alone is insufficient.

For example, ask your assistant:

> Read skills/black-friday-readiness/SKILL.md from this repository. Help me prepare my store exports and planned offers, run the Black Friday readiness checker, and explain the three most important actions. Treat missing checks as unverified and ask before changing anything in my store.

This is a reusable instruction file and local tool, not a hosted AI agent. The Python runner is tested; installation/discovery in individual AI applications is still pending validation.

## Interpretation and limits

- Monetary values support up to two decimal places. All amounts in one run must use the stated currency and comparable tax treatment. Shopify Markets prices, automatic discounts and WooCommerce tax display settings require manual confirmation.
- Unit Margin = planned selling price − unit cost − other unit costs. Value = Unit Margin ÷ planned selling price × 100, shown with a % sign. The table shows both cost inputs and defines the calculation. Unit Margin is not total business profit; it is only calculated when both supplied costs have a confirmed matching currency and tax basis.
- Recorded Analytics purchase events do not prove events are correct or unique. Compare with store orders and separately test checkout.
- Merchant Center statuses are SKU-matched observations for the destination and market you checked. Map service item IDs to your variant SKUs first; do not guess that they match.
- The default evidence age limit is seven days; adjust with `--max-evidence-age-days`. Default low-stock threshold is ten units; adjust with `--low-stock`. These are prompts to investigate, not demand predictions.
- Do not share reports or store exports publicly unless you intend to. Use a local `data/` folder, which is ignored by Git, and keep customer/order exports outside this tool.

## Methods and references

See [the methodology and source notes](docs/research/black-friday-methodology.md) for professional ecommerce analytics and agent-evaluation principles applied during review. Book references support methods; current official documentation defines platform formats. Real WooCommerce and Shopify export trials and AI application workflow checks remain required before claiming a validated release.

## Development

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Tests cover product variants, legacy/current Shopify headers, missing values, stock, money, evidence age and malformed data, report generation and overwrite protection. GitHub Actions runs them on Python 3.10 and 3.13. [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md) · [Licence](LICENSE).
