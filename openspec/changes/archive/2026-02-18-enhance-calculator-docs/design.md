## Context

The calculator-logic-reference.md (1160 lines) is the single source of truth for the evaluation/calculator system. It was written to document the initial implementation but lacks details needed for exact reimplementation: message templates, formatting conventions, the complete rules structure, and test vectors. The target audience is both human developers making changes and AI agents implementing modifications.

The source code files:
- `backend/app/calculators/ads_keyword.py` (590 lines)
- `backend/app/calculators/top_sku.py` (360 lines)
- `backend/app/calculators/discount.py` (381 lines)
- `backend/app/calculators/scoring.py` (1823 lines)
- `backend/app/calculators/engine.py` (263 lines)

Existing test suite: ~200 test functions across 5 unit test files with sample data for MND, KYPSO, and SUKA brands.

## Goals / Non-Goals

**Goals:**
- Make the doc sufficient for exact reimplementation in any language
- Fix known inaccuracies (single DEFAULT_RULES, not two separate sets)
- Document all ~40 G-column message templates with exact placeholder syntax
- Document all formatting functions with input→output examples
- Provide test vectors extracted from the existing test suite
- Clarify fashion vs non-fashion behavior differences

**Non-Goals:**
- Documenting the orchestration engine (engine.py), service layer, or API endpoints — these are infrastructure, not business logic
- Changing any calculator or scoring logic
- Creating a separate document — enhancing the existing one in-place
- Documenting the frontend components or hooks

## Decisions

### 1. Single document, not modular files

**Decision:** Enhance `docs/calculator-logic-reference.md` as one self-contained document.

**Rationale:** AI agents work best with a single reference file — no cross-file lookups. At ~2000 lines it's still manageable. The logic is deeply interconnected (Calculator 3 output feeds into Scoring G68/G72/G73), making separation awkward.

**Alternative considered:** Modular docs (separate message-templates.md, rules-reference.md). Rejected because cross-referencing adds friction for both humans and AI.

### 2. Inline message templates per scoring category, not a separate appendix

**Decision:** Add message templates directly within each scoring category section, alongside the existing threshold/formula documentation.

**Rationale:** When modifying a category's logic, you need to see the template right next to the formula — not jump to an appendix. This follows the "everything about Row 7 is in one place" principle.

### 3. Test vectors as an appendix

**Decision:** Put test vectors at the end of the document as an appendix.

**Rationale:** Test vectors are reference data, not part of the logic explanation. Putting them inline would break reading flow. An appendix lets readers verify their implementation against known-good outputs without cluttering the main spec.

### 4. Extract test data from existing tests, not from production

**Decision:** Use the MND/KYPSO/SUKA sample data already in the test suite.

**Rationale:** These are verified (tests pass), cover different scenarios (no fake discount, fake discount, various ad configurations), and are already structured as input→output pairs.

### 5. Document DEFAULT_RULES as a rendered table, not raw Python

**Decision:** Present DEFAULT_RULES as structured tables organized by category, showing key, threshold, points, and message templates.

**Rationale:** Raw Python dict syntax is language-specific and hard to scan. Tables are readable by both humans and AI in any target language.

## Risks / Trade-offs

- **[Doc drift]** The doc could fall out of sync with code changes → Mitigation: Add a note at the top referencing source files and rule_version. The existing test `test_default_rules_produce_identical_messages` catches template drift.
- **[Doc length]** ~2000 lines is long → Mitigation: Strong TOC with anchor links. Each section is self-contained. The alternative (splitting) creates worse problems.
- **[Test vector staleness]** Test data may not cover all edge cases → Mitigation: Include the most representative cases (MND end-to-end for discount, threshold calculations for ads keyword). Note that test vectors supplement, not replace, the formula specifications.
