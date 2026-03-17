# THB Marketplace Expansion

## What This Is

Multi-marketplace currency support for the AHA SICU evaluation system. THB (Thai Baht) support has been added alongside existing IDR (Indonesian Rupiah), enabling Thai marketplace brands to be evaluated using appropriately converted thresholds, with admin-editable values per marketplace.

## Core Value

Thai marketplace brands can be evaluated using THB-appropriate thresholds, with the same accuracy and completeness as existing IDR evaluations.

## Milestone Status

- ✅ **M001: THB Marketplace Expansion** — completed 2026-03-17

## Requirements

### Validated

- ✓ IDR evaluation thresholds and scoring — existing
- ✓ Calculator engine with registry pattern — existing
- ✓ Scoring rules management (admin/leader) — existing
- ✓ Brand evaluation workflow — existing
- ✓ CSV parsing for Shopee data — existing
- ✓ CSV parser handles THB-formatted values from Shopee Thailand (CSV-01, CSV-02)
- ✓ Currency formatting throughout UI — THB/IDR code prefix, proper formatting (EVAL-02, EVAL-03)
- ✓ Marketplace selection per evaluation — user chooses ID or TH (EVAL-01)
- ✓ THB thresholds derived from IDR values, independently editable (DATA-02, DATA-03)
- ✓ Rules page with marketplace tabs for admin/leader management (RULES-01, RULES-02)
- ✓ Evaluation page marketplace selector (EVAL-01)
- ✓ Evaluation stores marketplace selection (DATA-01)
- ✓ generate_score selects rules based on marketplace (SCORE-01)
- ✓ Scoring message templates display correct currency (SCORE-02)

### Active

- [ ] All revenue-related thresholds in scoring use marketplace-specific values (SCORE-03) — backend ready, needs live runtime validation

### Out of Scope

- Live exchange rate integration — thresholds are set once and manually adjusted
- Automatic currency conversion of raw data — THB data stays in THB
- Multi-currency within a single evaluation — one evaluation = one marketplace
- Other marketplaces beyond ID and TH — future expansion

## Architecture Summary (Post-M001)

### Backend
- **Marketplace constants**: `app/core/marketplace.py` — VALID_MARKETPLACES, MARKETPLACE_CURRENCY, convert_idr_to_thb
- **Database**: Migrations 026 (schema + seed) and 027 (template placeholders) add marketplace to scoring_rules, evaluation_inputs, evaluations
- **Query layer**: All query functions accept `marketplace` keyword param defaulting to 'ID'
- **Scoring engine**: `calculate_score(marketplace='TH')` produces THB-labeled output; `{currency}` template placeholders
- **Price parsing**: `price_parser.py` — centralized `_parse_price(value, marketplace)` for IDR/THB formats
- **Calculator service**: Reads marketplace from evaluation_inputs, passes to calculators

### Frontend
- **Currency utilities**: `formUtils.ts` — `formatCurrency`, `parseCurrency`, `getCurrencyCode`
- **Rules page**: Marketplace tabs with scoped React Query caching `['rules', marketplace]`
- **Evaluation page**: Marketplace radio selector, state in `useEvaluationOrchestrator`
- **Display components**: All use shared `formatCurrency` with marketplace prop

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Evaluation-level marketplace (not per-brand) | User knows which marketplace a brand belongs to; selects at evaluation time | Implemented (D018) |
| Rules page marketplace tabs | Keeps all threshold management in one place; admins can compare IDR vs THB | Implemented (D017) |
| Initial THB thresholds from IDR conversion | Provides reasonable starting values; admins can adjust manually after | Implemented (D002) |
| Marketplace default 'ID' everywhere | Zero breaking changes for existing callers | Implemented (D004) |
| Currency formatting centralized in formUtils.ts | Eliminates duplication; single breakpoint; deprecated re-exports for migration | Implemented (D016) |
| React Query queryKey includes marketplace | Prevents stale cross-marketplace cache hits | Implemented (D017) |
| VARCHAR(2) + CHECK constraint for marketplace | Matches existing pattern; compact; enforces at DB level | Implemented (D001) |
| {currency} template placeholder in scoring messages | Both ID and TH rows use same templates; currency code injected at format time | Implemented (D005) |
| THB raw numbers, IDR /1M juta scaling in conclusions | THB values are 3 OOM smaller; juta scaling is unreadable for THB | Implemented (D009) |
| Centralized price parsing in price_parser.py | DRY — replaces duplicate _clean_price; single extension point | Implemented (D011) |
| Read marketplace from evaluation_inputs in calculator_service | eval_inputs has marketplace column; brand_vp_data does not | Implemented (D012) |

## Known Limitations

- Migration 026+027 have not been run against a live database — verified through tests and migration structure inspection only
- `SCORE-03` not fully validated — needs live runtime test with TH brand evaluation
- `fields.ts` has `unit: 'IDR'` hardcoded on ~25 field definitions — render layer overrides correctly, but raw config reads return 'IDR'
- 3 pre-existing test failures in `test_ads_keyword.py` remain unrelated to marketplace work
- Marketplace selector defaults to 'ID' on page load — no persistence of marketplace choice per brand

---
*Last updated: 2026-03-17 — M001 completed*
