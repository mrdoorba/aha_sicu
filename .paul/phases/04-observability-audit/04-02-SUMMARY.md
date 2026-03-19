---
phase: 04-observability-audit
plan: 02
subsystem: compliance, api
tags: [audit-log, asyncpg, migration, accounts, admin-actions, forensics]

requires:
  - phase: 04-observability-audit (plan 01)
    provides: Structured JSON logging, correlation IDs — audit failure errors logged as structured JSON

provides:
  - Append-only audit_log table with BIGSERIAL id, JSONB details, TIMESTAMPTZ
  - record_audit_event() async function for programmatic audit trail
  - All admin account mutations audited (create, role_change, password_reset, delete)
  - Audit failure resilience — errors logged but never break mutation responses

affects: [05-testing-infrastructure, 06-data-api-integrity]

tech-stack:
  added: []
  patterns:
    - "Router-layer audit: audit calls at router where current_user is available, service layer untouched"
    - "Audit failure resilience: _audit() wraps record_audit_event in try/except, logs ERROR on failure"
    - "Pre-mutation state capture: fetch old_role/user before mutation for audit details"
    - "No FK on audit_log: audit records survive target entity deletion"

key-files:
  created:
    - backend/app/db/migrations/versions/029_create_audit_log_table.py
    - backend/app/core/audit.py
    - backend/tests/unit/test_audit.py
  modified:
    - backend/app/modules/accounts/router.py
    - backend/tests/integration/api/test_accounts.py

key-decisions:
  - "Router-layer audit placement — service layer untouched, current_user context naturally available at router"
  - "Separate connection for audit — not transactional with mutation, failure doesn't roll back successful operation"
  - "json.dumps for details — asyncpg JSONB codec handles deserialization, but explicit serialization for INSERT"
  - "_audit helper centralizes try/except pattern — single point for error handling across all endpoints"

patterns-established:
  - "Audit pattern: _audit(action, actor, target_type, target_id, details) at router layer after service call"
  - "Audit failure: try/except with logger.error, never propagate to HTTP response"
  - "Pre-mutation capture: fetch entity state before mutation for before/after audit details"

duration: ~10min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 4 Plan 02: Admin Audit Trail Summary

**Append-only audit_log table with record_audit_event() function, wired into all admin account mutations with failure-resilient logging — enabling forensic investigation and compliance auditing.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~10min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 2 completed (all auto) |
| Files modified | 5 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Audit Log Table Exists | Pass | Migration 029 creates table with 8 columns + 4 indexes |
| AC-2: record_audit_event Inserts Row | Pass | Parameterized INSERT, json.dumps for details, NULL for None |
| AC-3: Account Creation Audited | Pass | action="account.create", details={email, role} |
| AC-4: Role Change Audited | Pass | action="account.role_change", details={old_role, new_role} |
| AC-5: Password Reset Audited | Pass | action="account.password_reset", no details (never log passwords) |
| AC-6: Account Deletion Audited | Pass | action="account.delete", details={email, role} of deleted user |
| AC-7: Audit Failure Resilience | Pass | _audit catches exceptions, logs ERROR, mutation response unaffected |

## Accomplishments

- Every admin account mutation now produces a permanent, queryable audit record with who/what/whom/when
- Audit mechanism is self-documenting: either the row exists, or an ERROR log entry records the gap
- _audit() helper centralizes the try/except pattern, making it trivial to add audit to future endpoints
- No service layer changes — audit is cleanly layered at the router where current_user context exists

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/db/migrations/versions/029_create_audit_log_table.py` | Created | audit_log table with BIGSERIAL id, JSONB details, 4 indexes |
| `backend/app/core/audit.py` | Created | record_audit_event() async function |
| `backend/app/modules/accounts/router.py` | Modified | Added _audit helper + audit calls to all 4 mutation endpoints |
| `backend/tests/unit/test_audit.py` | Created | 4 tests for record_audit_event |
| `backend/tests/integration/api/test_accounts.py` | Modified | Updated 7 existing tests + 1 new AC-7 resilience test |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Router-layer audit (not service) | Service doesn't have current_user; adding actor params to every service function is scope creep | Clean separation, no service refactor needed |
| Separate DB connection for audit | Audit failure should never roll back a successful mutation | Independent failure domains |
| _audit() helper with try/except | Centralizes resilience pattern, prevents copy-paste of error handling | Single maintenance point for audit error handling |
| json.dumps for details param | Explicit serialization before passing to asyncpg — consistent behavior regardless of codec config | Portable, no implicit behavior |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 0 | None |
| Scope additions | 0 | None |
| Deferred | 0 | None |

**Total impact:** Plan executed exactly as specified.

## Skill Audit

No required skills configured — all optional. Skipped.

## Issues Encountered

None.

## Next Phase Readiness

**Ready:**
- Phase 4 complete: structured logging + correlation IDs + access logging + PG audit flags + admin audit trail
- 1141 tests pass, ruff clean
- Foundation for Phase 5 (Testing Infrastructure) and Phase 6 (Data & API Integrity)

**Concerns:**
- audit_log table has no REVOKE UPDATE/DELETE at database level (requires DBA access, not application code)
- Email send audit not yet covered (future enhancement, separate from admin actions)

**Blockers:**
- None

---
*Phase: 04-observability-audit, Plan: 02*
*Completed: 2026-03-19*
