## Context

`docs/calculator-logic-reference.md` is the single source of truth for calculator logic documentation. It was authored 2026-02-12 and covers all five calculator modules. Since then, calculator code has been updated (e.g., language variants, scoring fixes, fashion retention logic). The doc needs to be audited against current code and enhanced with pseudocode.

## Goals / Non-Goals

**Goals:**
- Sync every section of `calculator-logic-reference.md` with current code in `backend/app/calculators/`
- Add a **Pseudocode** subsection to each calculator chapter using hybrid format (ASCII flow diagram + structured pseudocode)
- Maintain the existing document structure and table of contents

**Non-Goals:**
- Rewriting the document from scratch — only update what's changed and add pseudocode
- Changing any calculator code — this is documentation only
- Updating `my-documents/` files — those are personal reference material
- Adding pseudocode for `calculator_service.py` (I/O layer) — only pure calculator logic

## Decisions

### 1. Hybrid pseudocode format (Option C)

Each calculator gets:
1. **ASCII flow diagram** — high-level data pipeline overview
2. **Structured pseudocode** — step-by-step logic with variable names matching the code

**Rationale:** Flow diagrams give instant comprehension of the pipeline shape. Structured pseudocode gives the detail needed for reimplementation. Together they serve both quick-scan and deep-dive readers.

**Alternative considered:** Pure structured pseudocode only (Option A) — rejected because it lacks the at-a-glance overview. Flowchart-only (Option B) — rejected because it can't capture branching logic detail.

### 2. Pseudocode placement within existing sections

Insert pseudocode as a new `### Pseudocode` subsection at the end of each calculator's chapter, before the next calculator chapter begins.

**Rationale:** Keeps existing structure intact. Readers who want the formula tables and column references still find them first; pseudocode is an additional reference layer.

### 3. Audit approach — diff code against docs

For each calculator: read the current Python source, compare against the documented logic, and update any discrepancies (changed thresholds, new branches, renamed columns, added logic).

**Rationale:** Systematic comparison ensures nothing is missed.

## Risks / Trade-offs

- **[Risk] Doc may be already accurate** → If no drift is found, the only change is adding pseudocode sections. Minimal wasted effort.
- **[Risk] Scoring system is 1,850 lines** → Pseudocode for scoring will be longer. Mitigation: focus on the structural flow and key branching logic (fashion vs non-fashion, row groups), not every individual row formula.
