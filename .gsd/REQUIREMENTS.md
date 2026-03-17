# Requirements

## Active

### DATA-01 — Evaluation stores marketplace selection (ID or TH) chosen by user at evaluation time

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: S01
- Notes: Schema and query layer ready (marketplace column, upsert, insert all accept marketplace). Frontend integration pending (S04).

Evaluation stores marketplace selection (ID or TH) chosen by user at evaluation time

### SCORE-03 — All revenue-related thresholds in scoring use marketplace-specific values

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: none yet

All revenue-related thresholds in scoring use marketplace-specific values

### CSV-01 — Price parsing handles THB number format (`.` as decimal, `,` as thousands) without corruption

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: S03
- Notes: T01 creates shared _parse_price with marketplace-aware parsing. T02 wires marketplace from evaluation_inputs through calculator_service.

Price parsing handles THB number format (`.` as decimal, `,` as thousands) without corruption

### CSV-02 — Existing IDR parsing continues to work unchanged

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: S03
- Notes: Backward compat via default marketplace="ID" on all new params. All existing tests must pass unchanged.

Existing IDR parsing continues to work unchanged

### RULES-01 — Rules page has marketplace tabs (IDR / THB) for admins/leaders

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: none yet

Rules page has marketplace tabs (IDR / THB) for admins/leaders

### RULES-02 — Admin can edit THB thresholds independently from IDR thresholds

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: none yet
- Notes: Backend API ready (PUT /api/v1/rules/default?marketplace=TH). Frontend UI pending (S04).

Admin can edit THB thresholds independently from IDR thresholds

### EVAL-01 — User can select marketplace (Indonesia / Thailand) on the evaluation page before evaluating

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: none yet

User can select marketplace (Indonesia / Thailand) on the evaluation page before evaluating

### EVAL-02 — Currency formatting shows code prefix (THB / IDR) based on selected marketplace

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: none yet

Currency formatting shows code prefix (THB / IDR) based on selected marketplace

### EVAL-03 — Evaluation results display currency values in the correct format for the selected marketplace

- Status: active
- Class: core-capability
- Source: inferred
- Primary Slice: none yet

Evaluation results display currency values in the correct format for the selected marketplace

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

## Deferred

## Out of Scope
