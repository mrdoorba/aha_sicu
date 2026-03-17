---
id: M001
provides:
  - Full-stack THB (Thai Baht) marketplace support alongside existing IDR (Indonesian Rupiah)
  - marketplace VARCHAR(2) column with CHECK constraints on scoring_rules, evaluation_inputs, evaluations tables
  - Alembic migrations 026 (schema + seed) and 027 (template currency placeholders)
  - Marketplace-aware scoring engine with {currency} template placeholders and THB-specific conclusion scaling
  - Centralized price parser handling IDR (dot-thousands) and THB (comma-thousands, dot-decimal) formats
  - Frontend marketplace tabs on Rules page, marketplace selector on Evaluation page, currency-aware display components
  - formatCurrency/parseCurrency/getCurrencyCode centralized utilities replacing all local formatting copies
key_decisions:
  - D001: VARCHAR(2) + CHECK constraint for marketplace column (matches migration 023 pattern)
  - D002: Fixed IDR_TO_THB_RATE = 0.0019 for migration seeding only (not live exchange)
  - D003: UNIQUE(template, marketplace) replacing UNIQUE(template) on scoring_rules
  - D004: All functions default marketplace='ID' for zero-breaking-change backward compatibility
  - D005: Migration 027 patches all message templates to {currency} placeholder
  - D006: THB conclusion text uses raw numbers; IDR keeps /1M juta scaling
  - D007: _fmt_currency delegates to _fmt_idr — identical formatting, code from templates
  - D008: marketplace as keyword-only param with MARKETPLACE_CURRENCY.get fallback
  - D011: Centralized price parsing in price_parser.py
  - D016: Currency formatting centralized in formUtils.ts with deprecated re-exports
  - D017: React Query queryKey includes marketplace dimension for cache isolation
  - D018: Marketplace is explicit user selection, not derived from brand data
patterns_established:
  - Marketplace constants centralized in app.core.marketplace — single source of truth
  - CHECK constraint naming convention: chk_{table}_marketplace
  - Query/service/router functions use keyword-only marketplace param with default 'ID'
  - {currency} template placeholder + currency=code kwarg for message formatting
  - Price parsing centralized in price_parser.py — future marketplaces add a branch there
  - Calculator service reads marketplace from evaluation_inputs, passes to pure calculators
  - Frontend formatCurrency/parseCurrency with marketplace param replaces all local copies
  - React Query queryKey includes marketplace for cache isolation: ['rules', marketplace]
  - Marketplace state flows top-down from useEvaluationOrchestrator to hooks and UI
observability_surfaces:
  - Import check: python -c "from app.core.marketplace import VALID_MARKETPLACES; print(VALID_MARKETPLACES)"
  - DB inspection: SELECT template, marketplace FROM scoring_rules — shows ID/TH rows after migration
  - Constraint errors: CheckViolationError with constraint name chk_{table}_marketplace
  - Migration state: alembic current shows revision 027 after successful migration
  - API: GET /api/v1/rules?marketplace=TH returns THB rules
  - Scoring: generate_score reads marketplace from eval_inputs, formats messages with correct currency
  - Frontend: React Query devtools — ['rules', 'ID'] and ['rules', 'TH'] cache keys
  - Frontend: Network tab — marketplace field in PUT/POST request bodies
  - Grep audit: grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated
requirement_outcomes:
  - id: SCORE-01
    from_status: active
    to_status: validated
    proof: 4 wiring tests in test_generate_score_marketplace.py verify generate_score reads marketplace from eval_inputs and passes to calculate_score
  - id: SCORE-02
    from_status: active
    to_status: validated
    proof: 24 unit tests prove THB messages show "THB", IDR unchanged; TestMigrationTemplatesDrift confirms DB↔code sync
  - id: SCORE-03
    from_status: active
    to_status: active
    proof: Backend scoring engine fully supports marketplace-specific rules. Frontend passes marketplace to rules API. Full end-to-end validation requires live runtime test with TH brand evaluation.
  - id: DATA-01
    from_status: active
    to_status: validated
    proof: Backend schemas accept marketplace (S01). Frontend sends marketplace in PUT/POST bodies (S04). 536 frontend tests + 1072 backend tests pass.
  - id: DATA-02
    from_status: active
    to_status: validated
    proof: Migration 026 adds marketplace column with CHECK constraint; UNIQUE(template, marketplace); query layer filters by marketplace; 40+ unit tests + 20 integration tests pass
  - id: DATA-03
    from_status: active
    to_status: validated
    proof: Migration 026 seeds TH row with six_month_avg_threshold=190,000; PUT /api/v1/rules/default?marketplace=TH enables admin editing; verified by migration structure tests and API integration tests
  - id: CSV-01
    from_status: active
    to_status: validated
    proof: 21 unit tests in test_price_parser.py prove THB format parses correctly. 4 wiring tests prove marketplace flows from eval_inputs through calculator_service.
  - id: CSV-02
    from_status: active
    to_status: validated
    proof: 125 pre-existing discount/top_sku tests pass unchanged with default marketplace="ID"; 457 calculator tests pass with zero regressions
  - id: RULES-01
    from_status: active
    to_status: validated
    proof: RulesPage renders ID/TH tabs; 4 new tests verify tab rendering, default state, switching, and edit cancellation on tab change
  - id: RULES-02
    from_status: active
    to_status: validated
    proof: Backend PUT /api/v1/rules/default?marketplace=TH ready. Frontend useUpdateRule sends marketplace query param. Edit state resets on tab switch.
  - id: EVAL-01
    from_status: active
    to_status: validated
    proof: Radio selector on evaluation page. Orchestrator exposes marketplace/setMarketplace. Marketplace sent in all save requests.
  - id: EVAL-02
    from_status: active
    to_status: validated
    proof: getCurrencyCode maps marketplace→currency code. CurrencyField renders dynamic label. 9 tests including THB variant and unknown fallback.
  - id: EVAL-03
    from_status: active
    to_status: validated
    proof: All local formatIDR/formatCurrencyDisplay removed. Single shared formatCurrency used everywhere. 19 formUtils tests verify both marketplaces.
duration: ~3 hours across 4 slices (S01–S04)
verification_result: passed
completed_at: 2026-03-17
---

# M001: THB Marketplace Expansion

**Full-stack multi-marketplace currency support — from database schema through scoring engine, CSV parsing, and frontend UI — enabling Thai Baht brand evaluations alongside existing Indonesian Rupiah, with zero breaking changes to the existing system.**

## What Happened

This milestone added THB (Thai Baht) as a second marketplace to the AHA SICU evaluation system, which was previously hardcoded for IDR (Indonesian Rupiah) only. The work spanned four slices across the full stack.

**S01 (Data Model Foundation)** established the marketplace dimension. A constants module (`app/core/marketplace.py`) centralizes all marketplace definitions. Migration 026 added `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` with CHECK constraints to three tables (scoring_rules, evaluation_inputs, evaluations), replaced the old UNIQUE(template) constraint with UNIQUE(template, marketplace), and seeded a THB scoring_rules row with `six_month_avg_threshold` converted to 190,000 THB. The entire query layer, service layer, and API endpoints were updated to accept a `marketplace` parameter defaulting to 'ID' — ensuring zero breaking changes for existing callers. 43 unit tests and 20 integration tests verify the wiring.

**S02 (Scoring Engine Marketplace Awareness)** threaded `marketplace` through all five scoring sub-functions. All eight message templates were updated from hardcoded "IDR" to a `{currency}` placeholder, resolved at format time via `MARKETPLACE_CURRENCY.get(marketplace, "IDR")`. A `_fmt_currency` helper handles number formatting (identical for both currencies), while the currency code is injected by templates. THB conclusion text uses raw comma-formatted numbers instead of the IDR-specific `/1M juta` scaling (THB values are ~500× smaller). Migration 027 patches stored DB templates to use `{currency}`. 28 new tests verify THB output correctness, backward compatibility, and unknown marketplace fallback.

**S03 (CSV THB Parsing)** extracted duplicated `_clean_price` functions from discount and top_sku calculators into a shared `price_parser.py` module with `_parse_price(value, marketplace="ID")`. For IDR, it strips `.` as thousands separator. For THB, it strips `,` as thousands separator and preserves `.` as decimal. Both calculators gained a keyword-only `marketplace` parameter. The calculator_service reads marketplace from evaluation_inputs and passes it through. 25 new tests verify parsing and wiring, with 125 existing calculator tests unchanged.

**S04 (Frontend Currency and Marketplace UI)** delivered the user-facing experience. `formatCurrency`, `parseCurrency`, and `getCurrencyCode` utilities replaced all local formatting copies across the codebase. The Rules page gained marketplace tabs (🇮🇩 Indonesia / 🇹🇭 Thailand) with marketplace-scoped React Query caching. The evaluation page gained a marketplace radio selector, with marketplace state managed by `useEvaluationOrchestrator` and threaded to all save hooks. Every display component now uses the shared `formatCurrency`. 536 frontend tests pass with zero regressions.

## Cross-Slice Verification

The roadmap defined no explicit success criteria bullets, but the milestone vision ("Multi-marketplace currency support for the AHA SICU evaluation system") and slice definitions establish clear deliverables. Each was verified:

1. **Data model supports marketplace dimension** — Migration 026 adds marketplace columns with CHECK constraints to 3 tables; UNIQUE(template, marketplace) on scoring_rules; THB seed row present. Verified by 32 migration structure tests + DB inspection queries.

2. **Scoring engine produces marketplace-correct output** — `calculate_score(marketplace='TH')` produces THB-labeled messages, benchmarks, and conclusion text. Verified by 24 scoring marketplace tests + 4 wiring tests + TestMigrationTemplatesDrift.

3. **CSV parsing handles THB number format** — `_parse_price("1,250.50", "TH")` → `1250.5`. Verified by 21 price parser tests + 4 calculator service wiring tests.

4. **Frontend surfaces marketplace context** — Rules page tabs, evaluation page selector, currency-aware display. Verified by 536 frontend tests (63 test files) with zero regressions.

5. **Backward compatibility preserved** — All functions default `marketplace='ID'`. 1072 backend tests pass (3 pre-existing failures in test_ads_keyword.py unrelated to marketplace). 536 frontend tests pass.

6. **Cross-slice integration** — `generate_score` reads marketplace from eval_inputs (S01), fetches marketplace-specific rules (S01), formats messages with correct currency (S02), and the frontend sends marketplace in all save requests (S04). Calculator service reads marketplace from eval_inputs and passes to parsers (S03). Verified by end-to-end wiring tests at each integration boundary.

## Requirement Changes

- **SCORE-01**: active → validated — generate_score reads marketplace from eval_inputs, passes to calculate_score. 4 wiring tests verify.
- **SCORE-02**: active → validated — 24 unit tests prove THB/IDR message correctness. TestMigrationTemplatesDrift confirms DB↔code sync.
- **SCORE-03**: remains active — Backend fully supports marketplace-specific thresholds. Frontend wiring complete. Full end-to-end proof requires live runtime test with TH brand evaluation (not possible in test environment).
- **DATA-01**: active → validated — Backend schemas + frontend bodies include marketplace. 1072+536 tests pass.
- **DATA-02**: active → validated — Migration 026 with CHECK constraint, UNIQUE(template, marketplace), query layer filtering. 60+ tests.
- **DATA-03**: active → validated — THB seed at 190,000 THB. Admin-editable via PUT with ?marketplace=TH.
- **CSV-01**: active → validated — 21 parser tests + 4 wiring tests prove THB format handling.
- **CSV-02**: active → validated — 125 existing calculator tests pass unchanged.
- **RULES-01**: active → validated — Marketplace tabs on Rules page with 4 dedicated tests.
- **RULES-02**: active → validated — Independent THB editing via marketplace query param + edit cancellation on tab switch.
- **EVAL-01**: active → validated — Marketplace radio selector + orchestrator state management.
- **EVAL-02**: active → validated — getCurrencyCode + dynamic CurrencyField label. 9 tests.
- **EVAL-03**: active → validated — All local formatting removed. Single shared formatCurrency. 19 tests.

## Forward Intelligence

### What the next milestone should know
- THB marketplace is fully wired end-to-end but has not been tested against a live database or with real Thai marketplace CSV data. Migration 026+027 should be run on staging first.
- All functions default `marketplace='ID'` — adding a third marketplace requires updating: `VALID_MARKETPLACES` in `app/core/marketplace.py`, `getCurrencyCode` in `formUtils.ts`, the orchestrator's inline ternary for currency derivation, and DB CHECK constraints via a new migration.
- `fields.ts` still has `unit: 'IDR'` hardcoded on ~25 field definitions. The render layer overrides this with the `currency` prop, but anyone reading `unit` directly from field config gets 'IDR'.
- The `price_parser.py` module is the single extension point for price format handling. New marketplace = one new branch there.
- `SCORE-03` remains active — the only requirement not fully validated. It needs a live runtime test: start a TH evaluation, score it, verify THB thresholds applied.

### What's fragile
- **Template placeholder coverage** — new message templates must include `{currency}` instead of `IDR`, and formatting calls must pass `currency=code`. Only `TestMigrationTemplatesDrift` and marketplace tests catch this; no compile-time enforcement.
- **Marketplace default 'ID'** is hardcoded in ~15 places across backend and frontend. Adding a third marketplace touches all of them. Consider a config constant.
- **`get_rules_by_template` backward-compat wrapper** in `rules.py` — any new code should use `get_rules_by_template_and_marketplace` directly.
- **Price parser silent fallback** — `_parse_price` returns 0.0 for unparseable values and doesn't validate marketplace codes. Wrong marketplace = silently incorrect values.
- **`upsert_evaluation_inputs` ON CONFLICT is on `(brand_id)`** — each brand has one eval_inputs row, so marketplace is overwritten on re-upsert. A brand's marketplace is whatever was last saved.

### Authoritative diagnostics
- `pytest backend/tests/unit/marketplace/ backend/tests/unit/test_rules_queries.py backend/tests/unit/test_generate_score_marketplace.py backend/tests/unit/calculators/test_scoring_marketplace.py backend/tests/unit/calculators/test_price_parser.py backend/tests/unit/calculators/test_calculator_service_marketplace.py` — 94 marketplace-specific tests, the single suite that proves all marketplace wiring works
- `cd frontend && npx vitest run` — 536 tests is the baseline; any regression indicates a problem
- `grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated` — should return only formUtils.ts and formConfig.ts barrel lines

### What assumptions changed
- **Task executor reliability** — Multiple task executors (S01/T02, S02/T01) wrote code only in the worktree but committed only documentation. Closers had to implement or copy actual code changes. Future milestones should verify task summaries against actual file diffs, not trust claimed outcomes.
- **Integration test coverage** — Calculator integration tests (`test_calculators.py`) did not account for the new `get_evaluation_inputs` call added by S03. This required fixing mock side_effect lists during milestone closure. Service layer changes that add DB calls will break integration tests that use ordered mock side_effects.
- **`eval_inputs["marketplace"]` vs `.get()`** — `calculator_service.py` originally used dict key access instead of `.get()` with default, causing KeyError on pre-migration rows without the marketplace key. Fixed to use `.get("marketplace", "ID")`.

## Files Created/Modified

### Backend — New Files
- `backend/app/core/marketplace.py` — Marketplace constants, currency mappings, IDR→THB conversion helper
- `backend/app/calculators/price_parser.py` — Shared `_parse_price(value, marketplace)` replacing duplicate `_clean_price`
- `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py` — Schema migration: marketplace columns, CHECK constraints, THB seed
- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py` — Template migration: IDR → {currency} in stored templates
- `backend/tests/unit/marketplace/test_marketplace.py` — 32 tests for constants, conversion, migration structure
- `backend/tests/unit/test_rules_queries.py` — 10 tests for marketplace-aware rules queries
- `backend/tests/unit/test_generate_score_marketplace.py` — 4 tests for generate_score marketplace wiring
- `backend/tests/unit/calculators/test_scoring_marketplace.py` — 24 tests for THB scoring output
- `backend/tests/unit/calculators/test_price_parser.py` — 21 tests for IDR/THB price parsing
- `backend/tests/unit/calculators/test_calculator_service_marketplace.py` — 4 tests for calculator service wiring

### Backend — Modified Files
- `backend/app/db/queries/rules.py` — Marketplace filtering in all query functions
- `backend/app/db/queries/evaluations.py` — Marketplace in eval_inputs/evaluations queries
- `backend/app/modules/rules/schemas.py` — marketplace field in ScoringRuleResponse
- `backend/app/modules/rules/service.py` — marketplace threading through service
- `backend/app/modules/rules/router.py` — marketplace query parameter on GET/PUT
- `backend/app/modules/evaluations/service.py` — generate_score reads marketplace, passes to calculate_score
- `backend/app/modules/evaluations/schemas.py` — marketplace in request/response schemas
- `backend/app/modules/evaluations/router.py` — marketplace threading to service layer
- `backend/app/modules/evaluations/calculator_service.py` — marketplace reading from eval_inputs for discount/top_sku
- `backend/app/calculators/scoring/helpers.py` — `_fmt_currency` helper
- `backend/app/calculators/scoring/rules.py` — {currency} in DEFAULT_RULES templates
- `backend/app/calculators/scoring/messages.py` — marketplace param + {currency} in message generators
- `backend/app/calculators/scoring/categories.py` — marketplace param + dynamic currency in benchmark
- `backend/app/calculators/scoring/computations.py` — marketplace param + THB raw number scaling
- `backend/app/calculators/scoring/_calculator.py` — marketplace param on calculate_score
- `backend/app/calculators/discount.py` — replaced `_clean_price` with `_parse_price`, added marketplace kwarg
- `backend/app/calculators/top_sku.py` — replaced `_clean_price` with `_parse_price`, added marketplace kwarg
- `backend/tests/integration/api/test_calculators.py` — Added SAMPLE_EVAL_INPUTS to mock side_effect lists for marketplace-aware service calls
- `backend/tests/integration/api/test_scoring.py` — Updated mocks to use get_rules_by_template_and_marketplace
- `backend/tests/integration/api/test_rules_update.py` — Updated expected_fields to include marketplace

### Frontend — New Files
- `frontend/src/components/evaluation/forms/formUtils.test.ts` — 19 tests for currency utilities

### Frontend — Modified Files
- `frontend/src/components/evaluation/forms/formUtils.ts` — getCurrencyCode, formatCurrency, parseCurrency; deprecated old functions
- `frontend/src/components/evaluation/forms/formConfig.ts` — barrel exports for currency utilities
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — currency prop, dynamic label
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx` — THB variant + unknown fallback tests
- `frontend/src/services/apiClient.ts` — marketplace in rules/evaluation API types
- `frontend/src/hooks/useRules.ts` — marketplace-scoped queryKey + query param
- `frontend/src/hooks/useUpdateRule.ts` — marketplace in update params
- `frontend/src/hooks/useEvaluation.ts` — marketplace in EvaluationInputsUpdate
- `frontend/src/hooks/useAutoSaveForm.ts` — marketplace in save body
- `frontend/src/hooks/useSaveEvaluation.ts` — marketplace in save request
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — marketplace state + currency derivation
- `frontend/src/hooks/useEvaluationDetail.ts` — marketplace in EvaluationDetail interface
- `frontend/src/pages/RulesPage.tsx` — marketplace tabs UI
- `frontend/src/components/rules/RulesPage.test.tsx` — 4 marketplace tab tests
- `frontend/src/components/evaluation/EvaluationSections.tsx` — marketplace radio selector
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — marketplace badge
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — currency prop, removed local formatCurrencyDisplay
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — currency prop threading
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx` — currency prop threading
- `frontend/src/pages/EvaluationPage.tsx` — marketplace/currency from orchestrator
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — marketplace prop, shared formatCurrency
- `frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx` — marketplace prop threading
- `frontend/src/components/dashboard/DataIntelligence.tsx` — removed local formatIDR, marketplace-aware
- `frontend/src/components/dashboard/PresentationDashboard.tsx` — passes marketplace to DataIntelligence
- `frontend/src/pages/EvaluationDetailPage.tsx` — removed local formatIDR, marketplace-aware formatting
