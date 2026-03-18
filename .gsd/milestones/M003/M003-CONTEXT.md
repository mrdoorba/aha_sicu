# M003: Hardcoded IDR Cleanup — Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

## Project Description

M001 added THB marketplace support, but several IDR-specific assumptions remain hardcoded in the scoring and ads calculators. This milestone cleans them up so both marketplaces produce correct output.

## Why This Milestone

After M001's marketplace expansion, the scoring engine and ads calculator still contain hardcoded IDR formatting and thresholds that produce incorrect or misleading output for THB evaluations. These are leftover artifacts from when the system was Indonesia-only.

## User-Visible Outcome

### When this milestone is complete, the user can:

- See follower count messages with international comma formatting (>50,000) instead of Indonesian dot formatting (>50.000)
- See THB ads evaluations with an appropriate cost floor (~190 THB) instead of the IDR-scale 100,000

### Entry point / environment

- Entry point: Backend scoring and ads calculators (invoked during evaluation)
- Environment: local dev / production
- Live dependencies involved: PostgreSQL (for DB-stored message templates)

## Completion Class

- Contract complete means: tests prove formatting output and threshold behavior per marketplace
- Integration complete means: none — pure calculator logic, no cross-system wiring
- Operational complete means: DB migration applies cleanly

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- Scoring output for follower messages uses comma separator in both the threshold display and the value display
- Ads calculator uses marketplace-appropriate min_cost (100,000 for ID, 190 for TH)
- Juta convention is preserved for Indonesian marketplace sales range
- Existing tests continue to pass (no regressions)

## Risks and Unknowns

- DB migration must update stored message templates without breaking existing evaluations — low risk, pattern established in migrations 012/019/020/027

## Existing Codebase / Prior Art

- `backend/app/calculators/scoring/rules.py` — DEFAULT_RULES with hardcoded `>50.000` in followers message_fail
- `backend/app/calculators/scoring/messages.py:164` — `.replace(",", ".")` converting val_str to dot notation
- `backend/app/calculators/scoring/messages.py:175` — inline fallback with `>50.000`
- `backend/app/calculators/ads_keyword.py:497` — `min_cost = 100000` hardcoded
- `backend/app/calculators/scoring/computations.py:168-171` — `/ 1_000_000` + "juta" (correct, keep as-is)
- `backend/app/core/marketplace.py` — `IDR_TO_THB_RATE = 0.0019`
- `backend/app/db/migrations/versions/012_add_message_templates.py` — original DB template with `>50.000`
- `backend/app/db/migrations/versions/020_add_brackets_to_all_scoring_messages.py` — bracket update with `>50.000`

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions — it is an append-only register; read it during planning, append to it during execution.

## Relevant Requirements

- R023 — Follower threshold uses international comma separator
- R024 — Follower val_str uses comma not dot
- R025 — Ads min_cost is marketplace-aware
- R026 — Juta convention preserved for Indonesian

## Scope

### In Scope

- Fix `>50.000` → `>50,000` in DEFAULT_RULES, inline fallbacks, and DB-stored templates
- Remove `.replace(",", ".")` from follower val_str formatting
- Make ads calculator `min_cost` marketplace-aware using IDR_TO_THB_RATE
- DB migration for stored message templates
- Verify juta convention is preserved

### Out of Scope / Non-Goals

- Changing the juta/million display convention for Indonesian marketplace
- Changing the six_month_avg_threshold (already marketplace-scoped via DB rules)
- Any frontend changes
- Any i18n key changes

## Technical Constraints

- DB migration must follow established pattern (see migrations 012-027)
- DEFAULT_RULES, inline fallbacks, and DB templates must stay in sync (see NOTE in rules.py about three sources of truth)
- TestMigrationTemplatesDrift test must continue to pass — any migration modifying templates must be added to the replay chain

## Integration Points

- PostgreSQL scoring_rules table — stored message templates need migration
- TestMigrationTemplatesDrift in test_scoring.py — migration replay chain

## Open Questions

- None — scope is clear and well-defined
