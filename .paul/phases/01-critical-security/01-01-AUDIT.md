# Enterprise Plan Audit Report

**Plan:** .paul/phases/01-critical-security/01-01-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally Acceptable (accepted after applying findings below)

---

## 1. Executive Verdict

**Conditionally acceptable.** The plan correctly targets the highest-impact AEGIS findings with minimal code changes. Scope discipline is strong — 3 tasks, clear boundaries, concrete verification. The plan leverages existing code (OIDC validation already written, just needs activation) rather than rewriting, which is the correct approach.

However, three implementation details required strengthening before this is production-safe: a lazy import inside a function body, missing exception logging in the health check (needed for post-incident debugging), and no unit test coverage for the CORS configuration parsing. All have been applied.

Would I approve this plan for production after applying findings? **Yes.**

---

## 2. What Is Solid

**OIDC fail-closed approach (Task 1):** The plan correctly identifies that the fix is in `dependencies.py` (the allowlist check), not `oidc.py` (the token verification). The audience validation is already handled correctly — Terraform just needs to provide the value. The deny-by-default pattern (`if not allowed_raw: raise`) is the right security posture. The plan also correctly notes that local dev is unaffected because Firebase auth succeeds first, so the OIDC fallback path is never reached.

**Scope protection:** The boundaries section explicitly protects `oidc.py`, `security.py`, `sync/router.py` (already fixed), `cloud_sql.tf` (Phase 2), and frontend files. This prevents scope creep and protects completed work.

**Terraform variable reuse:** The plan reuses the existing `cors_origins` module variable for the application CORS env var rather than creating a new variable. This is correct — the values are semantically identical.

**`db.pool` attribute verification:** The plan uses `db.pool` to check database availability. Verified against `connection.py:24` — `self.pool: asyncpg.Pool | None = None` is a public attribute, correctly `None` before `init()` and set after. The `if db.pool:` guard prevents the `RuntimeError("Database pool not initialized")` that `connection()` throws when pool is None.

**Acceptance criteria format:** All 6 ACs are testable Given/When/Then with specific expected responses. AC-2 (fail-closed) is particularly important — it tests the security-critical path.

---

## 3. Enterprise Gaps Identified

### Gap 1: Lazy import inside function body (Task 2)
**Risk:** The plan's health check code has `from fastapi.responses import JSONResponse` inside the function body. Lazy imports obscure dependencies, break static analysis tools, and are inconsistent with the rest of `main.py` which imports everything at module level.
**Impact:** Code review friction, potential import-time errors masked until first unhealthy check.

### Gap 2: Silent exception swallowing in health check (Task 2)
**Risk:** The `except Exception` block in the health check sets `checks["database"] = "unreachable"` but does not log the actual exception. If the database is unreachable due to a misconfigured connection string, expired credentials, or network issue, the health check reports "unreachable" but the ops team has no way to distinguish between these root causes without additional investigation.
**Impact:** Slows incident response. Health check correctly reports unhealthy but provides no diagnostic signal.

### Gap 3: No test for CORS origin parsing (Task 3)
**Risk:** AC-6 specifies CORS behavior but the task verification only says "all existing tests pass." The `cors_origin_list` property parses a comma-separated string — edge cases (extra whitespace, trailing comma, empty string) are not tested. A misconfigured `CORS_ORIGINS` env var could silently include empty strings in the origins list.
**Impact:** CORS misconfiguration in production could block all frontend requests (blast radius: 4/5 per AEGIS playbook PB-10-004).

### Gap 4: New test files not marked as NEW
**Risk:** The plan references `test_dependencies.py` and `test_health.py` without noting these are new files. During execution, the implementer might try to `Edit` a non-existent file instead of `Write`.
**Impact:** Execution friction, not a production risk.

### Gap 5: Terraform CLOUD_RUN_URL self-reference timing
**Risk:** The plan notes "Terraform resolves `google_cloud_run_v2_service.api.uri` after creation, so the self-reference works." This is correct for existing environments (update-in-place). For the record: on a completely fresh `terraform apply` to a new environment, Terraform resolves the URI within the same apply because Cloud Run v2 service URI is deterministic from name+region+project. No second apply needed.
**Impact:** None for existing environments. Documented for future environment bootstrapping.

---

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | `JSONResponse` imported inside function body | Task 2 action | Added instruction to import at module level with other FastAPI imports |
| 2 | Health check swallows exceptions silently | Task 2 action + AC-3 | Added `logger.warning("Health check DB probe failed", exc_info=True)` to except block; strengthened AC-3 to require exception logging |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | No CORS config test despite AC-6 | Task 3 files + action + verify | Added `test_config.py` with 3 test cases for `cors_origin_list` parsing; added to files_modified frontmatter |
| 2 | Test files not marked as new | Task 1 + Task 2 action | Added "(NEW FILE — does not exist yet)" annotation to test file references |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Health check response caching to avoid DB round-trip on every probe | Cloud Run probes are infrequent (every 10s default). A `SELECT 1` is ~1ms. Cost is negligible. |
| 2 | Rate limiting on /health endpoint | /health is behind Cloud Run's own infrastructure. External abuse is mitigated by Cloud Run's request handling. Phase 3 covers rate limiting broadly. |
| 3 | CORS max origins validation | Internal tool with controlled infrastructure. Origins are set by Terraform, not user input. |

---

## 5. Audit & Compliance Readiness

**Audit evidence produced by this plan:**
- OIDC rejection logs (`logger.warning`) create forensic trail of unauthorized access attempts
- Health check exception logging provides diagnostic evidence for incidents
- Terraform plan output serves as change documentation (CLOUD_RUN_URL, ALLOWED_SCHEDULER_EMAILS, CORS_ORIGINS additions visible in plan diff)
- Unit tests serve as regression evidence

**Silent failure prevention:**
- Fail-closed OIDC: empty allowlist = deny (not silent pass-through)
- Health check: DB failure = 503 (not false 200)
- Exception logging: DB issues are logged with full traceback

**Post-incident reconstruction:**
- OIDC rejections logged with service account email
- Health check failures logged with exception details
- Deploy verification step logs full health response on failure

**Ownership and accountability:**
- Plan boundaries clearly define what is and isn't in scope
- Each task maps to specific acceptance criteria (AC-N)
- Verification section provides concrete pass/fail commands

**Gap:** No audit log table for admin actions (Phase 4 scope — acknowledged, not a gap in this plan's scope).

---

## 6. Final Release Bar

**What must be true before this plan ships:**
1. All 3 OIDC tests pass (fail-closed on empty, reject wrong email, accept correct email)
2. All 3 health check tests pass (healthy, unhealthy with logged exception, not_configured)
3. CORS config tests pass (parsing, whitespace, defaults)
4. `terraform plan` shows exactly: CLOUD_RUN_URL, ALLOWED_SCHEDULER_EMAILS, CORS_ORIGINS env vars + public_access_prevention
5. No regressions in existing test suite
6. `ruff check` clean

**Risks remaining if shipped as-is (after audit fixes):**
- Terraform state is still local (Phase 2 — acknowledged risk, not this plan's scope)
- Dev/prod share DB credentials (Phase 2)
- No deploy rollback if health check fails after deploy (Phase 6)
- These are explicitly deferred to their respective phases and are not forgotten

**Sign-off:** After applying the 4 findings above, I would sign my name to this plan. The changes are small, well-scoped, high-impact, and correctly prioritized. The plan addresses the AEGIS report's central finding (configuration-code boundary failure) with surgical precision.

---

**Summary:** Applied 2 must-have + 2 strongly-recommended upgrades. Deferred 3 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
