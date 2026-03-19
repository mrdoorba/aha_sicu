---
phase: 01-critical-security
plan: 01
subsystem: infra, security
tags: [oidc, terraform, health-check, cors, gcs, cloud-run, ci-cd]

requires:
  - phase: none
    provides: first plan in milestone

provides:
  - OIDC audience validation activated in production
  - OIDC allowlist fail-closed when unconfigured
  - Real health check with DB connectivity verification
  - Deploy verification against /health endpoint
  - GCS public_access_prevention enforced
  - Environment-driven CORS origins

affects: [02-infrastructure-isolation, 03-defensive-hardening]

tech-stack:
  added: []
  patterns:
    - "Fail-closed security: empty allowlist = deny, not permit"
    - "Environment-driven config: CORS_ORIGINS parsed from env var with localhost defaults"
    - "Health check pattern: SELECT 1 via pool, 503 on failure with exception logging"

key-files:
  created:
    - backend/tests/unit/test_dependencies.py
    - backend/tests/unit/test_health.py
    - backend/tests/unit/test_config.py
  modified:
    - backend/app/core/dependencies.py
    - backend/app/main.py
    - backend/app/config.py
    - infrastructure/terraform/modules/environment/main.tf
    - .github/workflows/_deploy-backend.yml

key-decisions:
  - "Fail-closed OIDC: empty allowlist rejects rather than permits"
  - "Health check logs exception with exc_info for post-incident debugging"
  - "CORS defaults to localhost for local dev, Terraform injects per-environment origins"

patterns-established:
  - "Security config from Terraform env vars, not hardcoded in Python"
  - "Health check verifies downstream dependencies, returns structured JSON"

duration: ~20min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 1 Plan 01: Critical Security & Config Summary

**Activated OIDC security (fail-closed), real health check with DB verification, GCS hardening, and environment-driven CORS — addressing 4 CRITICAL and 3 HIGH AEGIS findings.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~20min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 3 completed |
| Files modified | 11 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: OIDC Audience Validation Activated | Pass | Terraform injects CLOUD_RUN_URL + ALLOWED_SCHEDULER_EMAILS |
| AC-2: OIDC Fail-Closed When Unconfigured | Pass | Empty allowlist raises AuthException, logged at WARNING |
| AC-3: Health Check Verifies DB Connectivity | Pass | 200+ok / 503+unreachable with exc_info logging |
| AC-4: Deploy Verification Uses Health Endpoint | Pass | CI hits /health, parses JSON status field |
| AC-5: GCS Buckets Block Public Access | Pass | public_access_prevention = "enforced" added |
| AC-6: CORS Origins Are Environment-Driven | Pass | settings.cors_origin_list from CORS_ORIGINS env var |

## Accomplishments

- OIDC security chain fully activated: Terraform sets CLOUD_RUN_URL (audience) and ALLOWED_SCHEDULER_EMAILS, Python denies when unconfigured — closes the audit's central finding (identified by 5 of 11 agents)
- Health check now verifies DB connectivity and returns 503 when unreachable, with exception logging for debugging; deploy verification checks /health instead of /docs
- CORS origins driven by environment variable with localhost defaults, GCS bucket hardened with public_access_prevention

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/core/dependencies.py` | Modified | OIDC allowlist fail-closed (deny when empty) |
| `backend/app/main.py` | Modified | Real health check + JSONResponse import + logger + env-driven CORS |
| `backend/app/config.py` | Modified | Added cors_origins setting + cors_origin_list property |
| `infrastructure/terraform/modules/environment/main.tf` | Modified | CLOUD_RUN_URL, ALLOWED_SCHEDULER_EMAILS, CORS_ORIGINS env vars + GCS public_access_prevention |
| `.github/workflows/_deploy-backend.yml` | Modified | Deploy verification hits /health with JSON status parsing |
| `backend/tests/unit/test_dependencies.py` | Created | 3 OIDC fail-closed tests |
| `backend/tests/unit/test_health.py` | Created | 3 health check tests (healthy, unhealthy, no pool) |
| `backend/tests/unit/test_config.py` | Created | 3 CORS config parsing tests |
| `backend/tests/integration/api/test_sync_trigger.py` | Modified | Updated 2 OIDC tests to mock allowlist (fail-closed requires it) |
| `backend/tests/integration/api/test_auth.py` | Modified | Updated health check assertion for new response shape |
| `backend/tests/test_main.py` | Modified | Updated health check assertion for new response shape |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Fail-closed OIDC (deny when empty) | AEGIS playbook PB-04-001: empty config must deny, not permit | Existing OIDC tests needed settings mock — 2 tests updated |
| Import JSONResponse at module level | Audit finding: lazy imports obscure dependencies | Cleaner static analysis |
| Log health check exceptions with exc_info | Audit finding: silent exception swallowing hinders incident response | Ops can distinguish misconfigured connection from network failure |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 3 | Essential — existing tests broke due to planned behavioral changes |
| Scope additions | 0 | None |
| Deferred | 0 | None |

**Total impact:** Essential fixes, no scope creep

### Auto-fixed Issues

**1. Health check response shape changed — 2 existing tests**
- **Found during:** Task 2 (health check)
- **Issue:** `test_auth.py::test_health_endpoint` and `test_main.py::test_health_check_returns_healthy` asserted exact `{"status": "healthy"}` without `checks` key
- **Fix:** Updated assertions to check `data["status"] == "healthy"` and `"checks" in data`
- **Files:** `tests/integration/api/test_auth.py`, `tests/test_main.py`
- **Verification:** 1118 tests pass

**2. OIDC fail-closed broke tests without settings mock**
- **Found during:** Task 1 verification (full suite)
- **Issue:** `test_sync_trigger.py::test_post_sync_with_oidc_token_returns_200` and `test_post_sync_oidc_skips_db_user_lookup` didn't mock `settings.allowed_scheduler_emails` — fail-closed correctly rejected
- **Fix:** Added `patch("app.core.dependencies.settings")` with `allowed_scheduler_emails` matching scheduler email
- **Files:** `tests/integration/api/test_sync_trigger.py`
- **Verification:** 1118 tests pass

## Issues Encountered

None — all tasks executed cleanly. Test fixes were expected consequences of the behavioral changes.

## Skill Audit

No required skills configured — all optional. Skipped.

## Next Phase Readiness

**Ready:**
- OIDC security chain activated — production is protected
- Health check provides meaningful readiness signal for Cloud Run
- CORS is environment-driven — per-environment isolation achieved
- Foundation for Phase 2 (infrastructure isolation) is set

**Concerns:**
- Terraform state is still local (Phase 2 will address)
- Dev/prod still share DB credentials (Phase 2 will address)
- terraform apply needed to deploy OIDC and CORS env var changes

**Blockers:**
- None

---
*Phase: 01-critical-security, Plan: 01*
*Completed: 2026-03-19*
