# Contributing

Report a reproducible problem using synthetic or anonymised product data. Include the platform, export headers, Python version, command and expected versus actual behaviour. Never include credentials, customer records or private store reports.

Keep calculations testable and separate from AI interpretation. Missing information must remain unknown. Add a failing behaviour test before changing a rule. Run the full unittest suite and both documented examples before proposing a change.

Changes introducing network access, credentials or store edits need an explicit design and documentation; they are not part of the offline runner.
