# M001 Context

**Scope:** Multi-marketplace currency support for the AHA SICU evaluation system — adding THB (Thai Baht) as a second marketplace alongside existing IDR (Indonesian Rupiah).

**Goals:**
- Add `marketplace` dimension to scoring rules, evaluation inputs, and evaluations tables
- Wire the scoring engine to select rules by marketplace
- Handle THB number format in CSV parsing
- Surface marketplace context throughout the frontend (rules tabs, evaluation page, currency formatting)

**Constraints:**
- No new runtime dependencies required — all tooling already installed
- All existing brands are IDR — migration must preserve as `marketplace='ID'`
- Follow existing module patterns (router/service/schemas) and calculator registry
- THB thresholds derived from IDR via fixed 0.0019 conversion rate, then admin-editable
- No live exchange rate integration

**Key Decisions:**
- Marketplace as `VARCHAR(2) + CHECK` constraint (not ENUM) — matches migration 023 pattern
- Evaluation-level marketplace selection (user chooses at evaluation time)
- `marketplace` column on `scoring_rules` with `UNIQUE(template, marketplace)` — two rows per template
- Single migration covering all three tables for atomicity

**Upstream Dependencies:** None — first milestone in this project.
