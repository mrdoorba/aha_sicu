---
phase: 04-observability-audit
plan: 01
subsystem: observability, infra
tags: [json-logging, correlation-id, middleware, contextvars, terraform, postgresql, cloud-logging]

requires:
  - phase: 03-defensive-hardening
    provides: Global exception handler (logger.exception pattern), fail-closed config patterns

provides:
  - Structured JSON logging (Cloud Logging native severity parsing)
  - Request correlation IDs via contextvars (X-Request-ID header)
  - Request access logging middleware with /health exclusion
  - Configurable LOG_LEVEL via environment variable
  - PostgreSQL audit logging flags (5 flags in Terraform)

affects: [04-02-audit-trail, 05-testing-infrastructure]

tech-stack:
  added: []
  patterns:
    - "Structured JSON logging: JSONFormatter on root logger, Cloud Logging parses severity natively"
    - "Request correlation: ContextVar(request_id) set by middleware, read by formatter"
    - "Access logging: BaseHTTPMiddleware emits method/path/status/duration at appropriate severity"
    - "Middleware exception resilience: catch + return 500 JSONResponse instead of re-raise to preserve X-Request-ID"

key-files:
  created:
    - backend/app/core/logging.py
    - backend/tests/unit/test_logging.py
    - backend/tests/unit/test_request_middleware.py
  modified:
    - backend/app/core/middleware.py
    - backend/app/main.py
    - backend/app/config.py
    - infrastructure/terraform/cloud_sql.tf

key-decisions:
  - "Catch-and-return instead of re-raise in middleware exception path — preserves X-Request-ID on error responses"
  - "stdlib-only JSON logging (no python-json-logger or google-cloud-logging dependency)"
  - "time.monotonic() for duration measurement (NTP-immune)"
  - "log_statement=mod (not all) — avoids SELECT noise while capturing mutations"

patterns-established:
  - "Middleware exception handling: catch exceptions from call_next, return 500 JSONResponse with correlation header, log at ERROR"
  - "Access log exclusion: frozenset _SILENT_PATHS for readiness probe paths"
  - "Configurable log level: settings.log_level env var, validated in setup_logging()"

duration: ~15min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 4 Plan 01: Structured Logging & Observability Infrastructure Summary

**Structured JSON logging with request correlation IDs, access logging middleware, and PostgreSQL audit flags — establishing the observability foundation for incident investigation and compliance.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~15min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 3 completed (all auto) |
| Files modified | 7 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Structured JSON Logging | Pass | JSONFormatter outputs severity, message, logger, timestamp, request_id as single-line JSON |
| AC-2: Request Correlation IDs | Pass | X-Request-ID generated or echoed, appears in all log entries via contextvars |
| AC-3: Request Access Logging | Pass | method, path, status_code, duration_ms logged; INFO/WARNING/ERROR by status code |
| AC-3a: Middleware Resilience During Exceptions | Pass | 500 responses include X-Request-ID, access log emitted, context cleaned up |
| AC-4: Health Endpoint Excluded | Pass | /health in _SILENT_PATHS frozenset, no access log emitted |
| AC-5: PostgreSQL Logging Flags | Pass | 5 database_flags added to cloud_sql.tf, terraform fmt clean |

## Accomplishments

- All application logs are now structured JSON with Cloud Logging native severity parsing — queryable by severity, request_id, logger name
- Every HTTP request (except /health) produces a correlated access log with method, path, status code, and duration — enables incident investigation and access auditing
- Correlation IDs survive error responses — middleware catches BaseHTTPMiddleware re-raises and returns 500 with X-Request-ID preserved
- PostgreSQL audit logging enabled via Terraform — connection tracking, mutation logging (mod), and slow query detection (>1s)
- Log level configurable via LOG_LEVEL env var — operations can enable DEBUG during incidents without redeploying

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/app/core/logging.py` | Created | JSONFormatter, request_id_var ContextVar, setup_logging() |
| `backend/app/core/middleware.py` | Modified | Added RequestLoggingMiddleware with correlation IDs and access logging |
| `backend/app/main.py` | Modified | Replaced basicConfig with setup_logging, wired RequestLoggingMiddleware |
| `backend/app/config.py` | Modified | Added log_level setting (LOG_LEVEL env var) |
| `backend/tests/unit/test_logging.py` | Created | 11 tests for JSONFormatter and setup_logging |
| `backend/tests/unit/test_request_middleware.py` | Created | 6 tests for middleware correlation IDs, access logging, exception resilience |
| `infrastructure/terraform/cloud_sql.tf` | Modified | 5 PostgreSQL database_flags for audit logging |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Catch-and-return in middleware exception path | BaseHTTPMiddleware re-raises app exceptions after handler response; re-raising loses X-Request-ID header | Ensures observability on the requests that need it most (errors) |
| stdlib-only logging | python-json-logger/google-cloud-logging add dependency risk for no functional gain | Zero new dependencies |
| time.monotonic() for duration | time.time() drifts with NTP adjustments, can produce negative durations | Correct elapsed-time measurement |
| log_statement=mod | Logging all SELECTs generates enormous volume; mod captures INSERT/UPDATE/DELETE/DDL | Captures mutations and schema changes without noise |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 2 | Essential — lint cleanup and Terraform formatting |
| Scope additions | 0 | None |
| Deferred | 0 | None |

**Total impact:** Minimal fixes, no scope creep.

### Auto-fixed Issues

**1. Unused imports in test file**
- **Found during:** Task 2 verification (ruff check)
- **Issue:** `json` and `setup_logging` imported but unused in test_request_middleware.py
- **Fix:** Removed unused imports
- **Verification:** ruff check passes clean

**2. Terraform main.tf formatting**
- **Found during:** Final verification (terraform fmt -check)
- **Issue:** main.tf had pre-existing formatting drift
- **Fix:** terraform fmt main.tf
- **Verification:** terraform fmt -check clean

## Skill Audit

No required skills configured — all optional. Skipped.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| BaseHTTPMiddleware re-raises exceptions after handler response | Changed from re-raise to catch-and-return 500 JSONResponse to preserve X-Request-ID |
| test_access_log_emitted_on_500_error failed on first run | Fixed middleware to return response instead of re-raising; test now passes |

## Next Phase Readiness

**Ready:**
- Structured JSON logging is the foundation Plan 02 (audit trail) needs — audit events will be logged as structured JSON
- Correlation IDs enable tracing audit events back to specific HTTP requests
- 1136 tests pass, ruff and terraform fmt clean

**Concerns:**
- PostgreSQL flags require `terraform apply` which triggers instance restart — coordinate with team
- Cloud Logging retention defaults to 30 days — may need longer retention for compliance

**Blockers:**
- None

---
*Phase: 04-observability-audit, Plan: 01*
*Completed: 2026-03-19*
