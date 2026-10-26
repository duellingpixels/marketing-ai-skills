# Black Friday readiness: methods and references

These professional sources were consulted on 26 October 2026 during review after the initial offline preview was built. The notes below explain how their methods apply to the checker and its next validation work. They do not claim that the books prescribe our exact code or thresholds.

| Source | Relevant section | Application |
|---|---|---|
| Judah Phillips, *Ecommerce Analytics: Analyze and Improve the Impact of Your Digital Strategy* | Chapter 2: Developing an Analytical Plan | Start with a sale-preparation decision and require evidence plus an action for every finding. |
| Judah Phillips, *Ecommerce Analytics* | Chapter 2: Collecting and Governing Data and Metadata; Preparing and Wrangling Data | Check source dates, record matching and data suitability. Do not turn missing information into a pass. |
| Judah Phillips, *Ecommerce Analytics* | Chapter 3: revenue and gross-margin KPI examples | Define financial measures consistently. Our contribution calculation uses only supplied comparable costs; it is not gross margin or net profit. |
| Alistair Croll and Benjamin Yoskovitz, *Lean Analytics* | Part One: Vanity versus actionable metrics; correlation versus causation | Show decisions supported by the figures. A review threshold is not a forecast or proof of improved sales. |
| Antonio Gulli, *Agentic Design Patterns* | Chapter 13: Human-in-the-Loop | Keep commercial decisions and store changes under human review. |
| Antonio Gulli, *Agentic Design Patterns* | Chapter 19: Evaluation and Monitoring | Evaluate real outputs against the task, including real export trials and checks of individual findings. |

The local source library and full texts are not distributed with this repository. These are original summaries and bibliographic references. They do not establish rights to redistribute any book content.

Implementation details still require current official platform documentation; see the WooCommerce and Shopify guides. Professional concepts, platform facts and our own configurable review rules should be identified separately in the accompanying article.

## Before claiming a validated release

Automated tests and sample commands must pass. Test a real WooCommerce export and a real Shopify export, manually check representative findings against source records, and validate the AI application workflow that the guide describes. Record remaining limits rather than calling an untested path supported.

The current release is an offline preview. Real-store and AI application validation are pending. An export-based trial runs locally and does not require installing this checker on a live store.
