## Why

The existing `docs/calculator-logic-reference.md` covers core formulas and architecture but has gaps that prevent exact reimplementation: missing G-column message templates, an inaccurate description of DEFAULT_RULES (claims two separate fashion/non-fashion rule sets when there's only one), undocumented formatting functions, and no test vectors. Both human developers and AI agents need a single document they can follow to perfectly replicate or modify the calculator and scoring logic.

## What Changes

- Fix inaccuracies in the existing doc (single `DEFAULT_RULES` dict, not separate fashion/non-fashion sets; ROI threshold override flow; conversion rate post-scoring override)
- Add a **Formatting Functions Reference** section documenting all value formatters with exact signatures and examples
- Add a **Message Templates Reference** section with all ~40 G-column message templates including `{placeholder}` syntax
- Add a **Complete DEFAULT_RULES Reference** section showing the full rules dict structure
- Add a **Fashion vs Non-Fashion Behavior** section clarifying exactly what differs and where
- Add an **Edge Cases & Zero-State Behavior** section documenting what each calculator returns for empty/zero/missing data
- Add a **Test Vectors** appendix with sample input → expected output for all 3 calculators and scoring

## Capabilities

### New Capabilities

- `calculator-docs-enhancement`: Comprehensive additions to calculator-logic-reference.md covering message templates, formatting functions, DEFAULT_RULES reference, fashion/non-fashion behavior, edge cases, and test vectors

### Modified Capabilities

_(none — this is a documentation-only change with no spec-level behavior changes)_

## Impact

- **File modified**: `docs/calculator-logic-reference.md` (~1160 lines → ~2000-2200 lines)
- **No code changes**: This is purely documentation
- **No API changes**: No endpoints affected
- **No dependency changes**: No new packages
