# M003: Hardcoded IDR Cleanup

**Vision:** Clean up remaining IDR-specific formatting and thresholds in the scoring and ads calculators so both ID and TH marketplaces produce correct, consistently formatted output.

## Success Criteria

- Follower count messages display threshold as `>50,000` (international comma) instead of `>50.000` (Indonesian dot)
- Follower val_str values use comma thousands separator, not dot
- Ads calculator BOTTOM ads cost floor is 100,000 for ID and 190 for TH
- Juta display convention preserved for Indonesian marketplace sales range
- All existing tests pass without regression

## Key Risks / Unknowns

- DB migration must update stored follower message templates without breaking existing evaluations — low risk, well-established pattern from migrations 012-027
- TestMigrationTemplatesDrift replay chain must include the new migration — mechanical, but forgetting it breaks the test

## Proof Strategy

- DB migration risk → retire in S01 by proving migration applies and TestMigrationTemplatesDrift passes with updated replay chain
- Formatting correctness → retire in S01 by proving scoring output uses comma separator via unit tests

## Verification Classes

- Contract verification: pytest unit tests for formatting output and threshold behavior
- Integration verification: none — pure calculator logic
- Operational verification: DB migration applies cleanly
- UAT / human verification: visual check of scoring output formatting

## Milestone Definition of Done

This milestone is complete only when all are true:

- All four requirements (R023-R026) are satisfied
- DB migration updates stored `>50.000` templates to `>50,000`
- DEFAULT_RULES, inline fallbacks, and DB templates are in sync
- TestMigrationTemplatesDrift passes with new migration in replay chain
- Ads calculator uses marketplace-aware min_cost
- Full backend test suite passes

## Requirement Coverage

- Covers: R023, R024, R025, R026
- Partially covers: none
- Leaves for later: none
- Orphan risks: none

## Slices

- [x] **S01: International formatting & marketplace-aware ads thresholds** `risk:low` `depends:[]`
  > After this: Scoring output shows `>50,000` with comma separator; follower values formatted with commas; ads calculator uses THB-appropriate cost floor (190) for Thai marketplace. Proven by unit tests and migration drift test.

## Boundary Map

### S01 (single slice — no downstream consumers)

Produces:
- Updated `DEFAULT_RULES` in `rules.py` — followers message_fail uses `>50,000`
- Updated `messages.py` — val_str uses comma separator, inline fallback uses `>50,000`
- Updated `ads_keyword.py` — `min_cost` branched by marketplace (100,000 ID / 190 TH)
- DB migration — stored message templates updated from `>50.000` to `>50,000`

Consumes:
- nothing (single slice milestone)
