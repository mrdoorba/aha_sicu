# Requirements

## Active

### SCORE-03 — All revenue-related thresholds in scoring use marketplace-specific values

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: S02
- Notes: Backend scoring engine selects rules by marketplace (S02). Frontend useRules hook passes marketplace to rules API (S04). Full end-to-end validation requires live runtime test with TH brand evaluation.

All revenue-related thresholds in scoring use marketplace-specific values

## Validated

### SCORE-01 — `generate_score()` selects rules based on evaluation's marketplace

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S02
- Validation: generate_score reads marketplace from eval_inputs, passes to calculate_score as keyword arg. 4 wiring tests in test_generate_score_marketplace.py verify positional and keyword passthrough.

`generate_score()` selects rules based on evaluation's marketplace

### SCORE-02 — Scoring message templates display correct currency (THB/IDR) based on marketplace

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S02
- Validation: 24 unit tests prove THB messages show "THB" not "IDR", IDR messages unchanged, competition benchmarks use correct currency code, {currency} placeholder resolves in all 8 template locations. TestMigrationTemplatesDrift confirms DB↔code sync.

Scoring message templates display correct currency (THB/IDR) based on marketplace

### DATA-02 — Scoring rules table supports marketplace dimension (IDR rules and THB rules coexist)

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S01
- Validation: Migration 026 adds marketplace column with CHECK constraint; UNIQUE(template, marketplace) enables coexistence; query layer filters by marketplace; 40+ unit tests + 20 integration tests pass

Scoring rules table supports marketplace dimension (IDR rules and THB rules coexist)

### DATA-03 — THB scoring rule thresholds seeded from IDR conversion (admin-editable after)

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S01
- Validation: Migration 026 seeds TH row with six_month_avg_threshold=190,000 (100M IDR × 0.0019); PUT /api/v1/rules/default?marketplace=TH enables admin editing; verified by migration structure tests and API integration tests

THB scoring rule thresholds seeded from IDR conversion (admin-editable after)

### CSV-01 — Price parsing handles THB number format (`.` as decimal, `,` as thousands) without corruption

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S03
- Validation: 21 unit tests in test_price_parser.py prove THB format (comma thousands, dot decimal) parses correctly. 4 wiring tests prove marketplace flows from evaluation_inputs through calculator_service to calculate_discount and calculate_top_sku. REPL-verified: _parse_price("1,250.50", "TH") → 1250.5

Price parsing handles THB number format (`.` as decimal, `,` as thousands) without corruption

### CSV-02 — Existing IDR parsing continues to work unchanged

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S03
- Validation: 69 test_discount.py tests + 56 test_top_sku.py tests pass unchanged with default marketplace="ID". No existing caller modified. Backward compat confirmed by all 457 calculator tests passing.

Existing IDR parsing continues to work unchanged

### DATA-01 — Evaluation stores marketplace selection (ID or TH) chosen by user at evaluation time

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S01
- Supporting Slices: S04
- Validation: Backend schema ready (S01). Frontend useEvaluationOrchestrator manages marketplace state, auto-save includes marketplace in PUT body, save evaluation includes marketplace in POST body. 536 frontend tests pass. Network requests verified to include marketplace field.

Evaluation stores marketplace selection (ID or TH) chosen by user at evaluation time

### RULES-01 — Rules page has marketplace tabs (IDR / THB) for admins/leaders

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S04
- Validation: RulesPage renders ID/TH marketplace tabs using shadcn Tabs; switching tabs triggers re-fetch with ?marketplace=TH query param; React Query queryKey ['rules', marketplace] ensures cache isolation. 4 new tests in RulesPage.test.tsx verify tab rendering, default state, switching, and edit cancellation on tab change. 38/38 rules tests pass.

Rules page has marketplace tabs (IDR / THB) for admins/leaders

### RULES-02 — Admin can edit THB thresholds independently from IDR thresholds

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S04
- Supporting Slices: S01
- Validation: Backend PUT /api/v1/rules/default?marketplace=TH ready (S01). Frontend useUpdateRule sends marketplace as query param on PUT. Edit state resets on marketplace tab switch to prevent cross-marketplace overwrites. Tested in RulesPage.test.tsx.

Admin can edit THB thresholds independently from IDR thresholds

### EVAL-01 — User can select marketplace (Indonesia / Thailand) on the evaluation page before evaluating

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S04
- Validation: EvaluationSections renders marketplace radio selector (ID/TH) above category selector. useEvaluationOrchestrator exposes marketplace/setMarketplace. Marketplace threaded to useAutoSaveForm and useSaveEvaluation. 536 frontend tests pass with zero regressions.

User can select marketplace (Indonesia / Thailand) on the evaluation page before evaluating

### EVAL-02 — Currency formatting shows code prefix (THB / IDR) based on selected marketplace

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S04
- Validation: getCurrencyCode maps marketplace→currency code. CurrencyField renders dynamic ({currency}) label. 9 CurrencyField tests pass including THB variant and unknown currency fallback. All display components (TopSkuResults, DataIntelligence, EvaluationDetailPage, BusinessForm) use marketplace-aware getCurrencyCode prefix.

Currency formatting shows code prefix (THB / IDR) based on selected marketplace

### EVAL-03 — Evaluation results display currency values in the correct format for the selected marketplace

- Status: validated
- Class: core-capability
- Source: inferred
- Primary Slice: S04
- Validation: All local formatIDR/formatCurrencyDisplay functions removed. Single shared formatCurrency in formUtils.ts handles all formatting. marketplace prop threaded through TopSkuResults, DataIntelligence, EvaluationDetailPage, BusinessForm. 19 formUtils tests verify both marketplace formats. grep audit confirms zero local formatting copies remain.

Evaluation results display currency values in the correct format for the selected marketplace

## Deferred

## Out of Scope
