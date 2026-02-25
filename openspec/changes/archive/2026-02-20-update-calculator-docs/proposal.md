## Why

The `docs/calculator-logic-reference.md` (1,692 lines) was written on 2026-02-12 and may have drifted from the current codebase after subsequent calculator changes. Additionally, the document lacks pseudocode and flow diagrams — making it harder for developers to quickly grasp each calculator's logic without reading the Python source directly. Adding hybrid pseudocode (flow diagram overview + structured pseudocode detail) will make the reference significantly more accessible.

## What Changes

- **Audit & sync** `docs/calculator-logic-reference.md` against current calculator source files to fix any outdated formulas, thresholds, column names, or logic descriptions
- **Add pseudocode sections** to each calculator chapter using a hybrid format:
  - ASCII flow diagram as a high-level overview
  - Structured pseudocode with detailed step-by-step logic
- Calculators covered:
  - Calculator 1: Ads Keyword (`ads_keyword.py`)
  - Calculator 2: Top SKU (`top_sku.py`)
  - Calculator 3: Discount (`discount.py`)
  - Scoring System (`scoring.py`)
  - Orchestration Engine (`engine.py`)

## Capabilities

### New Capabilities

_(none — this is a documentation-only change)_

### Modified Capabilities

_(no spec-level requirement changes — implementation behavior is unchanged)_

## Impact

- **Files modified:** `docs/calculator-logic-reference.md` only
- **No code changes** — documentation only
- **No API, dependency, or infrastructure impact**
