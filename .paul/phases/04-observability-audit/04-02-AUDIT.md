# Enterprise Plan Audit Report

**Plan:** .paul/phases/04-observability-audit/04-02-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally Acceptable (accepted after applying findings)

---

## 1. Executive Verdict

**Conditionally Acceptable.** The plan is well-scoped and addresses the right gap (F-05-001). The router-layer audit approach is pragmatic — it avoids refactoring the service layer and places audit calls where `current_user` context is naturally available. The no-foreign-key design is correct for an append-only audit log.

The critical gap in the original plan: audit INSERT failures would silently disappear. The mutation succeeds, the response is sent, but the audit record is lost — and nobody knows. In a compliance context, a *silent* audit gap is worse than a *known* gap. After applying the must-have fix (try/except with error logging), the audit system becomes self-documenting: either the audit row exists, or an ERROR log entry records that it failed.

After applying 1 must-have and 2 strongly-recommended upgrades, I would sign off on this plan.

## 2. What Is Solid (Do Not Change)

**Router-layer audit placement.** The plan correctly keeps audit at the router layer rather than refactoring the service layer. This is the right call: the router has `current_user`, the service doesn't. Adding `actor_id`/`actor_email` parameters to every service function would be a scope-creeping refactor with no architectural benefit.

**No foreign keys on audit_log.** Correct. An audit log that cascades-deletes when users are removed defeats its entire purpose. The audit log must survive the deletion of the entities it records.

**Separate connection for audit.** Using `db.connection()` independently from the service's connection is correct. The audit record doesn't need to be transactional with the mutation — if the mutation succeeds and audit fails, we want the mutation result (plus an error log about the audit gap), not a rollback of a successful operation.

**JSONB for details.** Correct choice — queryable in PostgreSQL, flexible schema for different action types, and asyncpg handles serialization natively via the codec configured in connection.py.

**VARCHAR(255) for target_id (not INTEGER).** Smart. Target IDs may not always be numeric database IDs — this accommodates future audit of non-integer targets.

## 3. Enterprise Gaps Identified

### GAP-1: Silent audit failure (CRITICAL)
The original plan specifies audit calls after mutations but has no error handling. If `record_audit_event()` fails (DB connection pool exhausted, table constraints, network issue), the exception would propagate up and either: (a) crash the response after the mutation already succeeded (confusing 500 after successful operation), or (b) be caught by the global exception handler (returning 500, hiding the successful mutation). Either outcome is wrong. The correct behavior: the mutation result is returned, and the audit failure is logged as an ERROR.

### GAP-2: Integration test strategy mismatch
The original plan assumed real-DB integration tests ("query audit_log table in test assertions"). The actual test suite uses extensive mocking — there's no real database in the integration tests. The test strategy must match: mock `record_audit_event` and assert it was called with correct arguments.

### GAP-3: No test for audit failure resilience
Without a test that simulates audit INSERT failure, there's no regression protection for GAP-1. A future refactor could accidentally remove the try/except and reintroduce silent audit failures.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | GAP-1: Audit failure must not break mutation response | AC (added AC-7), Task 2 action (try/except pattern), Verification section | Added explicit try/except pattern for all audit calls, AC-7 for resilience, verification check |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | GAP-2: Test strategy must match mock-based suite | Task 2 action (integration tests section) | Replaced "query audit_log table" with "mock record_audit_event, assert called with correct args" |
| 2 | GAP-3: Need test for audit failure resilience | Task 2 action (integration tests section) | Added: "test when audit INSERT raises, mutation response still succeeds" |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Race condition: old_role fetch and update_role are not atomic | Low risk — single-admin teams, role changes are rare. Making this atomic would require refactoring service.py (out of scope). The worst case is a slightly incorrect old_role in the audit details, not a functional bug. |
| 2 | Email send audit (F-05-001 broader scope) | Plan explicitly scopes to accounts module. Email audit is a different action type with different actor context (any user, not just admin). Better as a separate task. |

## 5. Audit & Compliance Readiness

**Audit evidence:** After this plan, every admin mutation produces a permanent database record with: who did it (actor_id, actor_email), what they did (action), who was affected (target_type, target_id), what changed (details JSONB), and when (created_at). This satisfies SOC 2 CC6.1 and ISO 27001 A.12.4.3 requirements for administrative action logging.

**Silent failure prevention:** The must-have GAP-1 fix ensures that audit failures are visible. The structured JSON logging from Plan 01 means the ERROR log for a failed audit INSERT will be queryable in Cloud Logging — an operator can set up an alert on `"Audit failed"` log entries.

**Post-incident reconstruction:** An investigator can query: `SELECT * FROM audit_log WHERE target_type='user' AND target_id='42' ORDER BY created_at` to see the complete history of actions taken on a specific user. Combined with Plan 01's correlation IDs, they can also trace each audit event back to the specific HTTP request.

**Immutability:** The audit_log table has no UPDATE or DELETE operations exposed through the application layer. Only INSERTs via `record_audit_event()`. Database-level REVOKE is noted in the AEGIS playbook but not in this plan's scope (requires DBA access, not application code).

## 6. Final Release Bar

**What must be true before this plan ships:**
- audit_log table exists with correct schema and indexes
- Every admin mutation (create, role_change, password_reset, delete) calls record_audit_event
- Audit failures are caught and logged, never crash the mutation response
- Tests verify both the happy path (audit called correctly) and failure path (audit fails gracefully)

**Remaining risks after audit fixes:**
- Race condition between old-state fetch and mutation (low impact, deferred)
- No REVOKE UPDATE/DELETE on audit_log at database level (requires DBA, not application code)
- No retention policy on audit_log (table grows indefinitely — acceptable for now, monitor)

**Sign-off:** After applying the 3 upgrades above, I would approve this plan for production deployment. The plan establishes the admin audit trail that F-05-001 identified as missing, with appropriate resilience for the audit mechanism itself.

---

**Summary:** Applied 1 must-have + 2 strongly-recommended upgrades. Deferred 2 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
