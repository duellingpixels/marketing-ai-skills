# Black Friday Readiness Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Execution and initial GitHub publication are already requested in the conversation.

**Goal:** Publish a usable offline checker and AI skill for WooCommerce and Shopify sale preparation.

**Architecture:** Import platform product CSVs into common product records. Validate a shared offer sheet and optional evidence, then produce prioritised JSON and Markdown reports. Keep calculations independent from AI interpretation.

**Tech Stack:** Python 3.10+, standard library, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-26-black-friday-readiness-design.md`

## Global Constraints

- No installation dependencies, credentials, paid APIs, AI calls or network calls are needed.
- Limit matching to exact unique variant SKUs.
- Missing price, inventory or visibility evidence is unknown, never a pass.
- Outputs remain local unless the user chooses to share them.
- Initial validation uses synthetic fixtures matching official export documentation, not live-store tests.

## Review Focus

- Shopify image rows and continuation variants must not create phantom products or lose parent visibility.
- WooCommerce variable parents must not become purchasable variants.
- Duplicate identifiers and malformed quantities must fail clearly instead of silently matching.
- Missing, stale and future evidence must not create a readiness pass.
- Monetary values must reject non-finite values and use decimal arithmetic.

### Task 1: Import and validate data

Files: `src/marketing_ai_skills/black_friday/imports.py`, `tests/test_imports.py`.
Interfaces: `load_products(path, platform) -> dict[str, Product]`; `load_offers(path, currency) -> list[Offer]`; `load_stock(path) -> dict[str, int]`; `InputError` for actionable validation failures.

- [x] Write import tests for WooCommerce simple/variable/variation exports and current/legacy Shopify headers, image rows, metadata inheritance, duplicate SKUs, malformed CSV, optional fields and Decimal values.
- [x] Run `python3 -m unittest discover -s tests -v`; confirm the new behavior fails before implementation.
- [x] Implement validated dataclasses and import functions; rerun the suite.

### Task 2: Findings and reports

Files: `checks.py`, `report.py`, `tests/test_checks.py`.
Interfaces: `audit(products, offers, platform, currency, as_of, stock=None, evidence=None, low_stock=10, max_age_days=7) -> dict`; `render_markdown(report) -> str`.

- [x] Write tests for missing/unpublished products, unavailable/low/unknown stock, demand, planned price differences, comparable and unconfirmed costs, disapprovals, missing/stale/future evidence and purchase-activity limitations.
- [x] Run and confirm the failures; implement rules and report rendering; rerun all tests.
- [x] Verify every finding contains evidence and an action; no output makes a blanket readiness claim.

### Task 3: CLI, examples, documentation and publication

Files: `cli.py`, skill wrapper and `SKILL.md`, root README, platform guides, input reference, synthetic examples, templates, MIT licence and GitHub Actions.
Interfaces: `main(argv=None) -> int`, invoked by the portable skill script. Exit 0 means a report was generated, not store readiness; exit 2 means invalid input. Outputs require an explicit directory and refuse overwriting existing reports.

- [x] Write CLI tests for both platform fixtures, report outputs, invalid evidence, invalid numeric options and overwrite protection; observe failures before implementation.
- [x] Implement CLI and publishable packaging; run examples and the full suite.
- [x] Review fresh against the design; fix substantiated defects and rerun affected checks.
- [ ] Commit original public files only, create the public GitHub repository, push and verify its remote contents and CI result.

## Execution notes

- The user requested implementation and public repository creation after approving the series and first-build scope. Normal builder choices were recorded in the design; no additional approval round was needed.
- An independent design check found no material unanswered questions.
- Export-first implementation uses no API credentials or network calls. Direct connectors and live-store validation remain follow-up work.
- Regression tests cover review findings: parent-managed stock, backorders, variation type flags and overly precise monetary values.
- Local verification: 56 tests pass; both documented platform commands generate reports.
