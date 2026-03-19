# Project: aha_sicu

## Description
Fullstack web app for business development teams to evaluate whether stores/leads are worth pursuing using calculators from input data, with dashboards for presentations.

## Core Value
Business development can quickly assess whether a store/lead is worth pursuing using calculators from input data, and present findings via dashboards.

## Requirements

### Must Have
- [To be defined during planning]

### Should Have
- [To be defined during planning]

### Nice to Have
- [To be defined during planning]

## Validated Requirements (shipped)
- ✓ OIDC authentication with fail-closed pattern — Phase 1
- ✓ Real health check with DB connectivity probe — Phase 1
- ✓ Per-environment DB credentials with independent passwords — Phase 2
- ✓ GCS-backed Terraform state with locking — Phase 2
- ✓ Non-root Docker container (appuser UID 1001) — Phase 3
- ✓ Global exception handler (no stack traces to clients) — Phase 3
- ✓ Fail-closed email domain validation — Phase 3
- ✓ SQL sort allowlist defense-in-depth — Phase 3
- ✓ Structured JSON logging with Cloud Logging severity parsing — Phase 4
- ✓ Request correlation IDs (X-Request-ID) and access logging middleware — Phase 4
- ✓ Configurable log level via environment variable — Phase 4
- ✓ PostgreSQL audit logging flags (connections, mutations, slow queries) — Phase 4
- ✓ Admin action audit trail (append-only audit_log table) — Phase 4
- ✓ pytest-cov coverage enforcement with fail_under regression gate — Phase 5
- ✓ CI PostgreSQL 16 service container with Alembic migrations — Phase 5
- ✓ Shared auth test fixtures (create_test_token, auth_headers) — Phase 5
- ✓ Email endpoint integration tests (send + preview, 8 tests) — Phase 5
- ✓ Async marker cleanup (asyncio_mode=auto as single source of truth) — Phase 5
- ✓ Transactionally atomic sync pipeline with batch upserts — Phase 6
- ✓ Database-backed pending uploads with atomic claim pattern — Phase 6
- ✓ Auto-generated frontend API types from backend OpenAPI schema — Phase 6
- ✓ Automated deploy rollback on health check failure — Phase 6
- ✓ WIF branch restriction per environment (dev=develop, prod=main) — Phase 7
- ✓ Cloud SQL authorized_networks lockdown (empty default = no public IP) — Phase 7
- ✓ Evaluation schema Literal type enforcement (13 response fields) — Phase 7

## Constraints
- [To be identified during planning]

## Success Criteria
- Business development can make informed pursue/pass decisions on stores/leads in minutes
- [To be refined during planning]

## Specialized Flows

See: .paul/SPECIAL-FLOWS.md

Quick Reference:
- /ui-ux-pro-max → UI/UX design
- /superpowers → Software development workflow
- /base → Workspace management
- /carl → Code standards & rules
- /aegis → Security auditing

---
*Created: 2026-03-19*
*Last updated: 2026-03-19 after Phase 7 — v0.2 AEGIS Security Remediation milestone complete*
