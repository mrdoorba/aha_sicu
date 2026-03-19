# Enterprise Plan Audit Report

**Plan:** .paul/phases/06-data-api-integrity/06-02-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally acceptable (accepted after fixes applied)

---

## 1. Executive Verdict

**Conditionally acceptable.** The plan correctly diagnoses the multi-instance state problem and proposes a sound database-backed solution. However, the original plan introduced a **critical race condition** — two Cloud Run instances could both read the same pending upload row simultaneously, both proceed to process, creating duplicate entries. This is the exact class of bug the plan intends to fix. After applying the atomic claim pattern and supporting fixes, the plan is enterprise-ready.

Would I approve this for production? **Yes, with the applied fixes.** Not without them.

## 2. What Is Solid

- **Root cause diagnosis is correct:** `_pending_uploads: dict` in ephemeral Cloud Run instances is the real problem. The plan targets the right code (service.py:118).
- **UUID as natural primary key:** No surrogate key bloat, aligns with existing upload_id semantics from `uuid.uuid4()`.
- **TTL-based cleanup with expires_at index:** Prevents unbounded table growth. Inline cleanup on signed URL request is appropriate for this traffic volume.
- **Following existing patterns:** Migration style mirrors 029, query layer follows `fetch_one`/`fetch_all` from utils.
- **PendingUpload dataclass preserved as internal DTO:** Clean layering — no unnecessary Pydantic schema for internal state.
- **Clear, conservative boundaries:** Router, parser, GCS client, and response schemas explicitly excluded from scope.
- **Parameterized SQL throughout:** No injection risk in the query layer design.

## 3. Enterprise Gaps Identified

### G-1: Race condition on concurrent process_upload (CRITICAL)

The original plan used separate `get_pending_upload()` + `delete_pending_upload()` calls. Two Cloud Run instances handling the same `upload_id` simultaneously would both SELECT the row, both succeed, and both proceed to download/parse/store — creating duplicate `brand_uploads` entries. The in-memory `dict.pop()` was process-atomic; a plain SELECT+DELETE across instances is not.

### G-2: No transaction boundary for pending upload lifecycle

The original plan's Task 2 described passing `conn` to `_validate_pending_upload()` but did not specify that the validate-process-delete sequence must be atomic. A crash between validation and deletion leaves a re-processable row.

### G-3: FK ON DELETE behavior unspecified

`REFERENCES brands(id)` defaults to RESTRICT. A brand deletion during the 15-minute pending window would fail with a foreign key violation. Pending uploads are ephemeral — there's no reason to block brand deletion.

### G-4: No SQL-level expiry guard

The original plan relied entirely on Python-side `datetime.now() > expires_at` checks. The SELECT query would return expired rows to the application. Defense-in-depth requires `WHERE expires_at > NOW()` in the SQL.

### G-5: No test for the multi-instance scenario

The plan exists to fix a multi-instance bug, but the test plan did not include a test verifying that a second concurrent `process_upload` call fails after the first claims the row.

### G-6: Missing claim_pending_upload function

The query layer had no atomic claim operation. Without `DELETE ... RETURNING *`, the plan required a separate get and delete, which is inherently racy.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Race condition: concurrent process_upload can duplicate processing (G-1, G-2) | AC-2, Task 1 query module, Task 2 steps 5-6 | Added `claim_pending_upload(conn, upload_id)` using `DELETE...RETURNING * WHERE expires_at > NOW()`. Replaced get+delete pattern with atomic claim in `_validate_pending_upload()`. AC-2 now requires second concurrent call to fail. |
| 2 | No transaction boundary for pending upload lifecycle (G-2) | Task 2 step 6 | Atomic claim eliminates the need for a separate transaction — DELETE...RETURNING is a single atomic statement. Removed post-processing delete step. |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | FK ON DELETE unspecified defaults to RESTRICT (G-3) | Task 1 migration SQL | Changed `REFERENCES brands(id)` to `REFERENCES brands(id) ON DELETE CASCADE` |
| 2 | No SQL-level expiry guard (G-4) | Task 1 query functions | Added `WHERE expires_at > NOW()` to both `get_pending_upload` and `claim_pending_upload` queries |
| 3 | No test for multi-instance race scenario (G-5) | Task 3 integration tests | Added `test_process_fails_when_already_claimed` test case |
| 4 | Missing atomic claim function (G-6) | Task 1 query module, Task 1 verify | Added `claim_pending_upload` function specification and import verification |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Multiple DB connections per process_upload request (4 separate connections) | Existing behavior pre-dating this plan. Connection pooling mitigates. Consolidation is a performance optimization, not a correctness issue. |
| 2 | Inline cleanup_expired_uploads on every signed URL request | Acceptable for current traffic volume (business development tool with limited concurrent users). Move to periodic task if traffic increases. |
| 3 | No `requested_by` column on pending_uploads | Upload initiator is tracked in `brand_uploads.uploaded_by` at completion. Pending state is ephemeral (15 min TTL). Audit trail exists at the final state. |

## 5. Audit & Compliance Readiness

**Audit evidence:** The atomic claim pattern (DELETE...RETURNING) produces a clear state transition — each upload_id can only be claimed once. This is auditable: if a row exists, it hasn't been processed; if it's gone, it was either claimed or expired and cleaned up.

**Silent failure prevention:** SQL-level `WHERE expires_at > NOW()` prevents the application from processing expired uploads even if the Python check has a clock skew. Defense-in-depth.

**Post-incident reconstruction:** The `created_at` column provides creation timestamp. The `brand_uploads` table (via `uploaded_by` and `uploaded_at`) provides the completion record. The gap between creation and completion is the pending window.

**Ownership:** Upload mutations flow through `process_upload` which receives `user_id` from the authenticated router. The `brand_uploads.uploaded_by` field provides accountability.

**Compliance gap:** No explicit logging when a pending upload is claimed or expires. For SOC 2 purposes, the existing audit_log table could be used, but this is outside the plan's scope and is correctly deferred.

## 6. Final Release Bar

**What must be true before this ships:**
- The `claim_pending_upload` function uses `DELETE FROM pending_uploads WHERE upload_id = $1 AND expires_at > NOW() RETURNING *`
- `_validate_pending_upload` uses `claim_pending_upload`, not `get_pending_upload`
- No separate delete call exists after processing
- The FK specifies `ON DELETE CASCADE`
- Integration tests include the already-claimed scenario

**Risks if shipped as-is (with fixes applied):** Low. The atomic claim pattern is well-understood. The main residual risk is the deferred items (connection count, inline cleanup), neither of which affects correctness.

**Would I sign my name to this system?** Yes, with the applied fixes. The atomic claim pattern is the correct solution for cross-instance state coordination in a shared database.

---

**Summary:** Applied 2 must-have + 4 strongly-recommended upgrades. Deferred 3 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
