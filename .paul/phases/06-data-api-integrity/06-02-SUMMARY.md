---
phase: 06-data-api-integrity
plan: 02
subsystem: database
tags: [asyncpg, cloud-run, pending-uploads, race-condition, delete-returning]

requires:
  - phase: 06-data-api-integrity/06-01
    provides: Transaction pattern (conn.transaction()) established for batch operations
provides:
  - Database-backed pending upload state (pending_uploads table)
  - Atomic claim pattern for cross-instance coordination (DELETE...RETURNING)
  - Query layer for pending upload lifecycle (create/get/claim/delete/cleanup)
affects: []

tech-stack:
  added: []
  patterns:
    - "Atomic claim pattern: DELETE...RETURNING WHERE expires_at > NOW() for cross-instance state"
    - "SQL-level expiry guard: WHERE expires_at > NOW() as defense-in-depth"

key-files:
  created:
    - backend/app/db/migrations/versions/030_create_pending_uploads_table.py
    - backend/app/db/queries/pending_uploads.py
    - backend/tests/unit/upload/test_pending_uploads.py
  modified:
    - backend/app/modules/upload/service.py
    - backend/tests/integration/api/test_upload.py

key-decisions:
  - "Atomic claim (DELETE...RETURNING) instead of SELECT+DELETE to prevent race conditions"
  - "ON DELETE CASCADE on brand_id FK — pending uploads are ephemeral, should not block brand deletion"
  - "SQL-level expires_at filter in addition to Python check — defense-in-depth"

patterns-established:
  - "Cross-instance state coordination via DELETE...RETURNING atomic claim"

duration: ~15min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 6 Plan 02: Pending Uploads DB Migration Summary

**Replaced in-memory `_pending_uploads` dict with database-backed `pending_uploads` table using atomic claim pattern (DELETE...RETURNING) for multi-instance Cloud Run reliability.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~15min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 3 completed |
| Files modified | 5 |
| Tests | 1165 passed |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Pending uploads persisted in database | Pass | INSERT on signed-url request, no module-level dict |
| AC-2: Process atomically claims pending upload | Pass | DELETE...RETURNING prevents race conditions across instances |
| AC-3: Expired pending uploads cleaned up | Pass | cleanup_expired_uploads() deletes WHERE expires_at < NOW() |
| AC-4: Completed uploads removed from pending | Pass | Row deleted at claim time (atomic), no post-processing delete |
| AC-5: Expired uploads never returned by queries | Pass | SQL WHERE expires_at > NOW() on get and claim functions |

## Accomplishments

- Eliminated cross-instance state loss: pending uploads survive Cloud Run instance scaling/rotation
- Atomic claim pattern prevents duplicate file processing when two instances handle the same upload_id
- SQL-level expiry guard provides defense-in-depth alongside application-level checks
- All 1165 existing tests continue to pass — zero regressions

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/db/migrations/versions/030_create_pending_uploads_table.py` | Created | Alembic migration: pending_uploads table with TTL index |
| `backend/app/db/queries/pending_uploads.py` | Created | Query functions: create, get, claim, delete, cleanup |
| `backend/app/modules/upload/service.py` | Modified | Replaced in-memory dict with DB calls, atomic claim pattern |
| `backend/tests/unit/upload/test_pending_uploads.py` | Created | 7 unit tests for query layer |
| `backend/tests/integration/api/test_upload.py` | Modified | Replaced dict injection with pending_queries mocks, added already-claimed test |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Atomic claim (DELETE...RETURNING) over SELECT+DELETE | Prevents race condition where two instances claim the same upload | Core pattern for cross-instance coordination |
| ON DELETE CASCADE on brand_id FK | Pending uploads are ephemeral (15min TTL), should not block brand deletion | No operational friction from FK constraints |
| SQL-level expires_at filter | Defense-in-depth: expired rows never returned even if Python check has clock skew | Stronger correctness guarantee |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 0 | N/A |
| Scope additions | 0 | N/A |
| Deferred | 0 | N/A |

**Total impact:** Plan executed exactly as written (audit findings were applied before APPLY).

## Issues Encountered

None.

## Skill Audit

All skills in SPECIAL-FLOWS.md are priority "optional". No gaps.

## Next Phase Readiness

**Ready:**
- Phase 6 complete: both plans (06-01 batch upsert transactions, 06-02 pending uploads DB migration) executed
- All AEGIS data integrity findings addressed
- 1165 tests passing, ruff clean

**Concerns:**
- Migration 030 needs to be run against staging/production databases during deployment
- Multiple DB connections per process_upload request (4 connections) — deferred optimization

**Blockers:**
- None

---
*Phase: 06-data-api-integrity, Plan: 02*
*Completed: 2026-03-19*
