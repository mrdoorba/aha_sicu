---
phase: 03-defensive-hardening
plan: 01
subsystem: security, infra, api
tags: [dockerfile, non-root, exception-handler, email-validation, fail-closed, pydantic, terraform]

requires:
  - phase: 01-critical-security
    provides: OIDC fail-closed pattern, environment-driven config
  - phase: 02-infrastructure-isolation
    provides: Per-env DB credentials, GCS state backend, stable terraform configs

provides:
  - Non-root Docker container (appuser UID 1001)
  - Global catch-all exception handler (no stack traces to clients)
  - Fail-closed email domain validation with EMAIL_ALLOWED_DOMAINS terraform variable
  - Required verdict field on ScoringRequest (no invalid empty default)
  - Verified SQL sort allowlist defense-in-depth

affects: [04-observability-audit, 05-testing-infrastructure]

tech-stack:
  added: []
  patterns:
    - "Global exception handler: log full traceback server-side, return generic 500 to client"
    - "Fail-closed validation: empty config = deny (email follows OIDC precedent)"
    - "Non-root Dockerfile: groupadd + useradd after install, chown /app, USER before CMD"

key-files:
  created:
    - backend/locales/.gitkeep
  modified:
    - backend/Dockerfile
    - backend/app/main.py
    - backend/app/modules/email/schemas.py
    - backend/app/modules/evaluations/schemas.py
    - backend/tests/test_main.py
    - backend/tests/unit/email/test_config.py
    - backend/tests/unit/email/test_schemas.py
    - infrastructure/terraform/modules/environment/main.tf
    - infrastructure/terraform/modules/environment/variables.tf
    - infrastructure/terraform/variables.tf
    - infrastructure/terraform/main.tf
    - infrastructure/terraform/environments/dev.tfvars
    - infrastructure/terraform/environments/prod.tfvars

key-decisions:
  - "chown after uv sync, not COPY --chown — uv sync needs root for /usr/local writes"
  - "raise_app_exceptions=False in exception handler test — Starlette's ServerErrorMiddleware re-raises after sending response"
  - "Set EMAIL_ALLOWED_DOMAINS to ahacommerce.co.id in both environments (matches existing test fixtures)"
  - "Created backend/locales/.gitkeep to fix pre-existing Dockerfile COPY failure"

patterns-established:
  - "Fail-closed config validation: empty/missing config value = deny, not permit"
  - "Exception handler test pattern: ASGITransport(raise_app_exceptions=False) + dynamic route injection"
  - "Email tests must mock settings.email_allowed_domains with valid domain"

duration: ~25min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 3 Plan 01: Defensive Hardening Summary

**Non-root Docker container, global catch-all exception handler, fail-closed email domain validation, and required ScoringRequest verdict — 8 AEGIS findings addressed (6 remediated, 2 confirmed already resolved).**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~25min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 3 completed (all auto) |
| Files modified | 13 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Container runs as non-root user | Pass | `docker run --rm aha-sicu-test whoami` → `appuser` |
| AC-2: Unhandled exceptions return generic error | Pass | Test confirms 500 + `{"error": "Internal server error"}` with no traceback |
| AC-3: Email domain validation denies when unconfigured | Pass | Empty EMAIL_ALLOWED_DOMAINS raises ValueError |
| AC-4: ScoringRequest requires explicit verdict | Pass | Field now required, no invalid empty-string default |
| AC-5: SQL sort allowlist remains in place | Pass | Verified at evaluations.py:215-218, hardcoded ORDER BY in grouped query |
| AC-6: Exception handler has regression test | Pass | test_generic_500_when_unhandled_exception in test_main.py |
| AC-7: Email fail-closed has regression test | Pass | test_send_email_rejects_when_allowlist_empty in test_schemas.py |

## Accomplishments

- Container now runs as non-root (appuser UID 1001) — defense-in-depth against container escape even with gVisor
- Unhandled exceptions no longer leak stack traces, file paths, or library versions to clients — full traceback logged server-side
- Email domain validation is fail-closed: no configured domains = all email blocked (prevents misconfigured deployments from becoming phishing vectors)
- EMAIL_ALLOWED_DOMAINS wired through terraform for both dev and prod environments
- ScoringRequest verdict field now required with Literal validation — eliminates invalid empty-string bypass

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/Dockerfile` | Modified | Added appuser (UID 1001) + USER directive |
| `backend/app/main.py` | Modified | Added global_exception_handler for unhandled exceptions |
| `backend/app/modules/email/schemas.py` | Modified | Changed domain validation from fail-open to fail-closed |
| `backend/app/modules/evaluations/schemas.py` | Modified | Removed invalid empty-string default from verdict field |
| `backend/tests/test_main.py` | Modified | Added exception handler regression test |
| `backend/tests/unit/email/test_config.py` | Modified | Patched settings.email_allowed_domains in all SendEmailRequest tests |
| `backend/tests/unit/email/test_schemas.py` | Modified | Updated fail-open test to verify fail-closed behavior |
| `infrastructure/terraform/modules/environment/main.tf` | Modified | Added EMAIL_ALLOWED_DOMAINS Cloud Run env var |
| `infrastructure/terraform/modules/environment/variables.tf` | Modified | Added email_allowed_domains variable |
| `infrastructure/terraform/variables.tf` | Modified | Added dev/prod email_allowed_domains root variables |
| `infrastructure/terraform/main.tf` | Modified | Pass email_allowed_domains to both environment modules |
| `infrastructure/terraform/environments/dev.tfvars` | Modified | Set dev/prod email_allowed_domains to ahacommerce.co.id |
| `infrastructure/terraform/environments/prod.tfvars` | Modified | Set dev/prod email_allowed_domains to ahacommerce.co.id |
| `backend/locales/.gitkeep` | Created | Fix pre-existing Dockerfile COPY failure |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| chown after uv sync, not COPY --chown | uv sync installs to /usr/local which needs root; chown /app after all installs complete | Correct layer ordering in Dockerfile |
| raise_app_exceptions=False in test | Starlette's ServerErrorMiddleware re-raises exceptions after sending the response; httpx default catches the re-raise | Test pattern for all future exception handler tests |
| EMAIL_ALLOWED_DOMAINS = ahacommerce.co.id | Matches existing test fixtures and SMTP sender domain pattern | User should verify this is the correct production domain |
| Created locales/.gitkeep | Dockerfile COPY locales ./locales fails without directory | Pre-existing issue, not scope creep |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential — Dockerfile build would fail without it |
| Scope additions | 0 | None |
| Deferred | 0 | None |

**Total impact:** One pre-existing issue fixed, no scope creep.

### Auto-fixed Issues

**1. Missing backend/locales directory**
- **Found during:** Task 1 verification (docker build)
- **Issue:** Dockerfile `COPY locales ./locales` fails — directory doesn't exist
- **Fix:** Created `backend/locales/.gitkeep` placeholder
- **Files:** `backend/locales/.gitkeep`
- **Verification:** Docker build succeeds

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Missing locales dir blocking Docker build | Created .gitkeep placeholder |
| httpx ASGITransport re-raises app exceptions in test | Used raise_app_exceptions=False |
| 9 existing email tests broke (fail-closed change) | Patched settings.email_allowed_domains in test fixtures |

## Skill Audit

No required skills configured — all optional. Skipped.

## Next Phase Readiness

**Ready:**
- Exception handler logs full traceback server-side — Phase 4 (Observability) can add structured JSON logging and correlation IDs on top
- Fail-closed email validation established — rate limiting (Phase 6) can build on this
- All 1119 tests pass, ruff clean

**Concerns:**
- EMAIL_ALLOWED_DOMAINS set to `ahacommerce.co.id` — user should verify this is the correct domain for production
- `backend/locales/` directory is empty — unclear if locales were removed or never existed

**Blockers:**
- None

---
*Phase: 03-defensive-hardening, Plan: 01*
*Completed: 2026-03-19*
