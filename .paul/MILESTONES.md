# Milestones

Completed milestone log for this project.

| Milestone | Completed | Duration | Stats |
|-----------|-----------|----------|-------|
| v0.2 AEGIS Security Remediation | 2026-03-19 | 1 day | 7 phases, 10 plans |

---

## ✅ v0.2 AEGIS Security Remediation

**Completed:** 2026-03-19
**Duration:** 1 day (all phases same day)

### Stats

| Metric | Value |
|--------|-------|
| Phases | 7 |
| Plans | 10 |
| Files changed | 91 |
| Findings addressed | 136 (4 critical, 20 high, 45 medium, 30 low) |
| Backend tests | 1180 passed, 90.19% coverage |
| Frontend tests | 612 passed |

### Key Accomplishments

- **Fail-closed security pattern** established across OIDC, email domain validation, and Cloud SQL authorized_networks — empty/missing config denies by default
- **Per-environment DB credentials** with independent passwords, eliminating shared credential risk between dev and prod
- **Terraform state migrated to GCS** with native locking and versioning for safe team collaboration
- **Structured JSON logging** with Cloud Logging severity parsing and request correlation IDs (X-Request-ID)
- **Append-only audit trail** for all admin mutations with resilient failure handling
- **Atomic batch upserts** replacing row-by-row INSERTs (O(1) round-trips), transactional sync pipeline
- **Database-backed upload state** with atomic claim pattern (DELETE...RETURNING) for multi-instance Cloud Run
- **Auto-generated frontend API types** from backend OpenAPI schema, eliminating ~920 lines of hand-maintained TypeScript
- **Non-root Docker container** (appuser UID 1001) with deploy rollback on health check failure
- **Coverage enforcement** with pytest-cov floor gate and CI PostgreSQL service container

### Key Decisions

- Fail-closed as default security posture — empty allowlist = deny, not permit
- Database-backed state over in-memory dicts — Cloud Run instances are ephemeral
- Per-environment credentials in Terraform modules — independent random_password per env
- Router-layer audit placement — current_user context naturally available, avoids service refactor
- API boundary type casting — generated types stricter than hand-written, cast at hook consumption points
- Middleware catch-and-return 500 — preserves X-Request-ID on error responses for observability

---
