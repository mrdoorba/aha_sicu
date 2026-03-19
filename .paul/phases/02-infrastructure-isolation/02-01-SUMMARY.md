---
phase: 02-infrastructure-isolation
plan: 01
subsystem: infra, security
tags: [terraform, gcs, cloud-sql, db-credentials, state-backend, secret-manager]

requires:
  - phase: 01-critical-security
    provides: environment-driven config pattern (Terraform env vars for CORS, OIDC)

provides:
  - Per-environment DB users (aha_sicu_dev, aha_sicu_prod) with independent passwords
  - GCS-backed Terraform state with locking and versioning
  - CLOUD_RUN_URL wired as explicit variable (fixes Phase 1 self-reference bug)
  - create_before_destroy on secret versions (prevents race condition)

affects: [03-defensive-hardening]

tech-stack:
  added: []
  patterns:
    - "Per-env credentials: random_password + google_sql_user inside environment module"
    - "Terraform removed block: unmanage without destroying (safe migration)"
    - "GCS state backend with versioning for recovery and locking for collaboration"
    - "create_before_destroy on secret versions to prevent Cloud Run mount race"

key-files:
  created:
    - infrastructure/terraform/state.tf
  modified:
    - infrastructure/terraform/cloud_sql.tf
    - infrastructure/terraform/main.tf
    - infrastructure/terraform/variables.tf
    - infrastructure/terraform/modules/environment/main.tf
    - infrastructure/terraform/modules/environment/variables.tf
    - infrastructure/terraform/environments/dev.tfvars
    - infrastructure/terraform/environments/prod.tfvars

key-decisions:
  - "Use Terraform removed block instead of state mv — username changes make state mv impossible"
  - "Per-env root variables for Cloud Run URL (dev_cloud_run_url, prod_cloud_run_url) following existing dev_/prod_ pattern"
  - "create_before_destroy on secret versions to prevent Cloud Run deployment failures"
  - "Old shared user kept alive (unmanaged) as safety net until manual cleanup"

patterns-established:
  - "Per-environment credentials generated inside the environment module, not passed from root"
  - "Terraform removed block for safe resource migration without destruction"
  - "Secret version lifecycle: create_before_destroy to avoid mount race conditions"

duration: ~30min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 2 Plan 01: Infrastructure Isolation Summary

**Per-environment DB credentials (aha_sicu_dev/prod) with independent passwords, Terraform state migrated to GCS with locking — eliminating shared credential risk and local state single-point-of-failure.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~30min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 3 completed (2 auto + 1 checkpoint) |
| Files modified | 9 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Per-Environment DB Users | Pass | `aha_sicu_dev` and `aha_sicu_prod` created on Cloud SQL |
| AC-2: Per-Environment DB Passwords in Secret Manager | Pass | Each module generates own `random_password.db`, stored as secret version v3 |
| AC-3: DB_USER Environment Variable Is Per-Environment | Pass | Cloud Run uses `google_sql_user.app.name` — resolves to per-env username |
| AC-4: Terraform State Backed by GCS | Pass | Backend is `gcs`, bucket `aha-coms-sicu-terraform-state` with versioning |
| AC-5: Terraform Plan Clean | Pass | `terraform plan` shows "No changes" after full apply |
| AC-6: Old Shared User Removed Safely | Pass | Old user unmanaged via `removed` block — still alive as safety net |
| AC-7: State Migration Reversible | Pass | Pre-migration backup taken, rollback documented (not needed) |

## Accomplishments

- Dev and prod now have completely independent DB credentials — a credential leak in dev no longer compromises prod, and DB audit logs can distinguish environment origin
- Terraform state is in GCS with native locking — multiple operators can safely collaborate, and state is recoverable via bucket versioning
- Fixed pre-existing Phase 1 self-referential bug (`CLOUD_RUN_URL = google_cloud_run_v2_service.api.uri`) that would have blocked any future `terraform plan`
- Established `create_before_destroy` pattern on secret versions to prevent Cloud Run deployment race conditions

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `infrastructure/terraform/state.tf` | Created | GCS state bucket resource with versioning + lifecycle |
| `infrastructure/terraform/cloud_sql.tf` | Modified | Replaced shared `random_password.db` + `google_sql_user.app` with `removed` blocks |
| `infrastructure/terraform/main.tf` | Modified | Switched backend to GCS, removed `db_user`/`db_password` from module calls, added `cloud_run_url` pass-through |
| `infrastructure/terraform/variables.tf` | Modified | Removed `db_user`, added `dev_cloud_run_url`/`prod_cloud_run_url` |
| `infrastructure/terraform/modules/environment/main.tf` | Modified | Added per-env `random_password.db` + `google_sql_user.app`, updated secret version source, fixed CLOUD_RUN_URL, added `create_before_destroy` |
| `infrastructure/terraform/modules/environment/variables.tf` | Modified | Removed `db_user` and `db_password` variables |
| `infrastructure/terraform/environments/dev.tfvars` | Modified | Set `dev_cloud_run_url`/`prod_cloud_run_url`, removed stale `db_user`/`db_name` |
| `infrastructure/terraform/environments/prod.tfvars` | Modified | Set `dev_cloud_run_url`/`prod_cloud_run_url`, removed stale `db_user`/`db_name` |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Use `removed` block instead of `terraform state mv` | Username changes from `aha_sicu` to `aha_sicu_dev`/`aha_sicu_prod` — can't move state for a resource with different attributes | Old user stays alive as safety net; manual cleanup needed later |
| Fix Phase 1 CLOUD_RUN_URL self-reference | `google_cloud_run_v2_service.api.uri` referencing itself blocks all `terraform plan` | Added `dev_cloud_run_url`/`prod_cloud_run_url` root variables following existing `dev_`/`prod_` pattern |
| Add `create_before_destroy` on secret versions | First apply hit race condition: old secret version destroyed before Cloud Run finished reading it | Prevents future deployments from failing when password rotates |
| Import GCS state bucket after gcloud creation | Chicken-and-egg: bucket must exist before `terraform init`, but resource declared in Terraform | `terraform import` after manual creation |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 3 | Essential — blocked terraform plan/apply without fixes |
| Scope additions | 0 | None |
| Deferred | 1 | Old shared user cleanup |

**Total impact:** Essential fixes for pre-existing issues discovered during execution. No scope creep.

### Auto-fixed Issues

**1. Phase 1 self-referential CLOUD_RUN_URL**
- **Found during:** Task 2 verification (terraform plan)
- **Issue:** `CLOUD_RUN_URL = google_cloud_run_v2_service.api.uri` — a resource cannot reference itself
- **Fix:** Changed to `var.cloud_run_url`, added `dev_cloud_run_url`/`prod_cloud_run_url` root variables, set actual URLs in tfvars
- **Files:** `modules/environment/main.tf`, `variables.tf`, `main.tf`, `dev.tfvars`, `prod.tfvars`
- **Verification:** `terraform plan` succeeds

**2. Secret version race condition**
- **Found during:** Checkpoint (first terraform apply)
- **Issue:** Terraform destroyed old secret version before Cloud Run finished updating, causing "Secret Version in DESTROYED state" error
- **Fix:** Added `lifecycle { create_before_destroy = true }` to `google_secret_manager_secret_version.db_password`
- **Files:** `modules/environment/main.tf`
- **Verification:** Re-apply succeeded, `terraform plan` shows no changes

**3. State bucket 409 conflict on first apply**
- **Found during:** Checkpoint (first terraform apply)
- **Issue:** Bucket created via `gcloud` for migration, then Terraform tried to create it again
- **Fix:** `terraform import google_storage_bucket.terraform_state aha-coms-sicu-terraform-state`
- **Files:** State only (no code change)
- **Verification:** Re-apply succeeded

### Deferred Items

- Old shared DB user `aha_sicu` remains alive on Cloud SQL instance (unmanaged by Terraform). Clean up via `gcloud sql users delete aha_sicu --instance=aha-sicu-db` after verifying both environments work, then remove `removed` blocks from `cloud_sql.tf`.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Self-referential CLOUD_RUN_URL from Phase 1 | Switched to explicit variable pattern |
| Secret version race condition on first apply | Added create_before_destroy lifecycle, re-applied |
| State bucket already existed for import | Used terraform import |
| Stale tfvars variables (db_user, db_name, cloud_run_url) | Cleaned up stale vars, added correct per-env vars |

## Skill Audit

No required skills configured — all optional. Skipped.

## Next Phase Readiness

**Ready:**
- Per-env DB credentials fully operational — dev and prod isolated
- Terraform state in GCS — shared access with locking enabled
- CLOUD_RUN_URL properly wired via variables (fixes OIDC audience validation)
- Foundation for Phase 3 (Defensive Hardening) is set

**Concerns:**
- Old shared DB user `aha_sicu` still alive — should be cleaned up manually
- `removed` blocks in `cloud_sql.tf` should be removed after old user cleanup
- Undeclared variable warnings in tfvars (`environment`, `db_name`) — cosmetic, not blocking

**Blockers:**
- None

---
*Phase: 02-infrastructure-isolation, Plan: 01*
*Completed: 2026-03-19*
