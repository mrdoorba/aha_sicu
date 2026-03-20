# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-03-20)

**Core value:** Business development can quickly assess whether a store/lead is worth pursuing using calculators from input data, and present findings via dashboards.
**Current focus:** v0.3 i18n Completeness

## Current Position

Milestone: v0.3 i18n Completeness
Phase: 9 of 9 (Language Addition Streamlining) — Not started
Plan: Not started
Status: Ready to plan
Last activity: 2026-03-20 — Phase 8 complete, transitioned to Phase 9

Progress:
- v0.3 i18n Completeness: [█████░░░░░] 50% (1/2 phases complete)

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ○        ○        ○     [Idle — ready for Phase 9 planning]
```

## Accumulated Context

### Decisions
- 2026-03-20: Phase 8 complete — all calculator output sections (AdsKeyword, Discount, Email) render i18n with backward-compatible fallback
- 2026-03-20: buildI18nEmailBody extracted as shared utility for email body translation assembly
- 2026-03-20: Scoring G68/G72 refactored to read from discount details dict (no regex dependency)
(Carried forward from v0.2 — still relevant)
- Fail-closed security pattern: empty/missing config = deny, not permit
- Database-backed state over in-memory dicts for Cloud Run ephemeral instances
- Router-layer audit placement for current_user availability
- API boundary type casting for generated types at hook consumption points

### v0.3 Constraints
- Existing database must not break — old evaluations are immutable JSONB snapshots
- "Store ICU" brand name stays English (intentional branding)
- Extend existing `TranslatableText` pattern for calculator outputs
- `Header.tsx` is dead code — out of scope

### Deferred Issues
- Old shared DB user `aha_sicu` cleanup (manual — after verifying per-env users work in prod) — verified 2026-03-19, safe to remove
- `removed` blocks in cloud_sql.tf cleanup (after old user deletion)
- Firebase signup restriction audit (manual check — F-DA-013)
- audit_log REVOKE UPDATE/DELETE at database level (requires DBA access)
- Email send audit trail (future enhancement, separate from admin actions)
- Email endpoints lack require_role access control (product/security decision, not test scope)
- Coverage threshold ratchet: increase fail_under from 28%
- Competition section in email missing product links (backend email assembly doesn't include links in raw message rendering — partially fixed frontend-side)

### Blockers/Concerns
None.

### Git State
Last commit: pending (phase 8 commit)
Branch: develop
Feature branches merged: none

## Session Continuity

Last session: 2026-03-20
Stopped at: Phase 8 complete, transitioned to Phase 9
Next action: /paul:plan for Phase 9
Resume file: .paul/ROADMAP.md
Resume context:
- Phase 8: Complete (calculator output i18n — 2 plans, all ACs passed)
- Phase 9: Not started (Language Addition Streamlining)
- v0.3 milestone: 50% (1/2 phases complete)

---
*STATE.md — Updated after every significant action*
