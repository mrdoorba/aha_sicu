# CI/CD Dev → Prod Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Establish separate dev and prod environments with branch-based promotion, rename GCP resources to `aha-coms-sicu` prefix, and add database safety measures.

**Architecture:** Refactor Terraform from single-environment to dual-environment using modules. Shared resources (Cloud SQL instance, WIF) stay at root; per-environment resources (Cloud Run, Firebase, Secrets, GCS, SAs) go into a reusable module called twice. GitHub Actions already routes by branch — just needs prod environment variables.

**Tech Stack:** Terraform (~7.0), GitHub Actions, GCP (Cloud Run v2, Cloud SQL PostgreSQL 18, Firebase Hosting, Secret Manager, Artifact Registry, WIF)

**Design doc:** `docs/plans/2026-03-10-cicd-dev-prod-pipeline-design.md`

---

## Phase 1: Terraform Refactor + Rename

### Task 1: Create Terraform environment module structure

**Why:** Current Terraform creates one environment per apply. We need both dev and prod in a single state so one `terraform apply` provisions everything.

**Files:**
- Create: `infrastructure/terraform/modules/environment/main.tf`
- Create: `infrastructure/terraform/modules/environment/variables.tf`
- Create: `infrastructure/terraform/modules/environment/outputs.tf`

**Step 1: Create module directory**

```bash
mkdir -p infrastructure/terraform/modules/environment
```

**Step 2: Create `modules/environment/variables.tf`**

Module input variables — everything the per-environment resources need:

```hcl
variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "cloud_sql_instance_name" { type = string }
variable "cloud_sql_instance_connection_name" { type = string }
variable "db_user" { type = string }
variable "github_repo" { type = string }
variable "firebase_project_id" { type = string }
variable "cloud_run_image" { type = string }
variable "cloud_run_min_instances" { type = number }
variable "cloud_run_max_instances" { type = number }
variable "cloud_run_memory" { type = string }
variable "cloud_run_cpu" { type = string }
variable "cloud_run_service_name" { type = string, default = "" }
variable "smtp_user" { type = string }
variable "smtp_from_name" { type = string }
variable "gsheets_vp_spreadsheet_id" { type = string }
variable "gsheets_meeting_spreadsheet_id" { type = string }
variable "cloud_run_url" { type = string, default = "" }
variable "cors_origins" { type = list(string) }

# Dependencies passed from root (API enablement resources)
variable "depends_on_apis" {
  type    = list(any)
  default = []
}
```

**Step 3: Create `modules/environment/main.tf`**

Move per-environment resources here from root. Each resource uses `aha-coms-sicu-${var.environment}` naming pattern. This file contains:

- **Service Accounts** (from `iam.tf`): `cloud_run`, `deploy`, `scheduler`, `gsheets_sync`
  - Account IDs: `aha-coms-sicu-{env}-api-sa`, `aha-coms-sicu-{env}-deploy-sa`, `aha-coms-sicu-{env}-sched-sa`, `aha-coms-sicu-{env}-sheets-sa`
  - Note: Scheduler SA shortened to `sched` to stay within 30-char limit
- **IAM bindings** (from `iam.tf`): All project-level and SA-level role bindings
- **Secrets** (from `secrets.tf`): 4 secrets with `aha_coms_sicu_{env}_*` IDs + IAM accessor bindings
- **Cloud Run v2** (from `cloud_run.tf`): Service name `aha-coms-sicu-{env}-api`, env vars, Cloud SQL connector, public access
- **Firebase Hosting** (from `firebase.tf`): Site ID `aha-coms-sicu-{env}`
- **Artifact Registry** (from `artifact_registry.tf`): Repo ID `aha-coms-sicu-{env}-registry`
- **GCS Bucket** (from `storage.tf`): Bucket name `{project_id}-aha-coms-sicu-{env}-uploads`, CORS origins passed via variable
- **WIF** (from `workload_identity.tf`): Pool ID `aha-coms-sicu-{env}-github-pool`
- **Cloud Scheduler** (from `scheduler.tf`): Daily sync job `aha-coms-sicu-{env}-daily-sync`
- **Database** (from `cloud_sql.tf`): `google_sql_database` with name `aha_coms_sicu_{env}`

**Key naming changes from old → new:**

| Resource | Old Pattern | New Pattern |
|----------|-------------|-------------|
| Cloud Run | `aha-sicu-{env}-api` | `aha-coms-sicu-{env}-api` |
| SA (API) | `aha-sicu-{env}-api-sa` | `aha-coms-sicu-{env}-api-sa` |
| SA (Deploy) | `aha-sicu-{env}-deploy-sa` | `aha-coms-sicu-{env}-deploy-sa` |
| SA (Scheduler) | `aha-sicu-{env}-scheduler-sa` | `aha-coms-sicu-{env}-sched-sa` |
| SA (Sheets) | `aha-sicu-{env}-sheets-sa` | `aha-coms-sicu-{env}-sheets-sa` |
| Secrets | `aha_sicu_{env}_*` | `aha_coms_sicu_{env}_*` |
| Firebase | `aha-sicu-{env}` | `aha-coms-sicu-{env}` |
| Artifact Registry | `aha-sicu-{env}-registry` | `aha-coms-sicu-{env}-registry` |
| GCS | `{proj}-aha-sicu-{env}-uploads` | `{proj}-aha-coms-sicu-{env}-uploads` |
| WIF Pool | `aha-sicu-{env}-github-pool` | `aha-coms-sicu-{env}-github-pool` |
| Scheduler | `aha-sicu-{env}-daily-sync` | `aha-coms-sicu-{env}-daily-sync` |
| Database | `aha_sicu_{env}` | `aha_coms_sicu_{env}` |

**Step 4: Create `modules/environment/outputs.tf`**

Export key values the root module and GitHub Actions need:

```hcl
output "cloud_run_url" { value = google_cloud_run_v2_service.api.uri }
output "artifact_registry_url" { value = "..." }
output "deploy_service_account_email" { value = google_service_account.deploy.email }
output "workload_identity_provider" { value = google_iam_workload_identity_pool_provider.github.name }
output "gcs_upload_bucket" { value = google_storage_bucket.uploads.name }
output "gsheets_service_account_email" { value = google_service_account.gsheets_sync.email }
output "firebase_hosting_site" { value = google_firebase_hosting_site.frontend.site_id }
```

**Step 5: Commit**

```
feat: create Terraform environment module structure
```

---

### Task 2: Refactor root Terraform to use modules

**Files:**
- Modify: `infrastructure/terraform/main.tf` — Keep only shared resources + module calls
- Modify: `infrastructure/terraform/variables.tf` — Add prod-specific vars, remove `environment`
- Modify: `infrastructure/terraform/outputs.tf` — Reference module outputs
- Delete content from: `infrastructure/terraform/iam.tf` (moved to module)
- Delete content from: `infrastructure/terraform/secrets.tf` (moved to module)
- Delete content from: `infrastructure/terraform/cloud_run.tf` (moved to module)
- Delete content from: `infrastructure/terraform/firebase.tf` (moved to module)
- Delete content from: `infrastructure/terraform/artifact_registry.tf` (moved to module)
- Delete content from: `infrastructure/terraform/storage.tf` (moved to module)
- Delete content from: `infrastructure/terraform/workload_identity.tf` (moved to module)
- Delete content from: `infrastructure/terraform/scheduler.tf` (moved to module)
- Modify: `infrastructure/terraform/cloud_sql.tf` — Keep instance + user (shared), remove per-env databases (moved to module)

**Step 1: Update `main.tf`**

Keep: provider blocks, API enablement resources.
Remove: `google_service_account.gsheets_sync` (moved to module).
Add: Module calls:

```hcl
module "dev" {
  source      = "./modules/environment"
  environment = "dev"
  project_id  = var.project_id
  region      = var.region
  # ... pass all required variables
  cloud_sql_instance_name            = google_sql_database_instance.main.name
  cloud_sql_instance_connection_name = google_sql_database_instance.main.connection_name
  cors_origins = [
    "https://aha-coms-sicu-dev.web.app",
    "http://localhost:5173"
  ]
}

module "prod" {
  source      = "./modules/environment"
  environment = "prod"
  project_id  = var.project_id
  region      = var.region
  # ... pass all required variables
  cloud_sql_instance_name            = google_sql_database_instance.main.name
  cloud_sql_instance_connection_name = google_sql_database_instance.main.connection_name
  cors_origins = [
    "https://aha-coms-sicu-prod.web.app"
  ]
}
```

**Step 2: Update `cloud_sql.tf`**

Keep: `google_sql_database_instance.main` (shared instance), `google_sql_user.app`, Cloud SQL scheduler SA + start/stop jobs.
Remove: `google_sql_database.dev` and `google_sql_database.prod` (moved into module).
Rename Cloud SQL scheduler SA: `aha-sicu-sql-scheduler-sa` → `aha-coms-sicu-sql-sched-sa`.
Rename scheduler jobs: `aha-sicu-cloud-sql-start/stop` → `aha-coms-sicu-sql-start/stop`.

**Important:** Enable automatic backups (currently `enabled = false`):

```hcl
backup_configuration {
  enabled                        = true
  point_in_time_recovery_enabled = true
  backup_retention_settings {
    retained_backups = 7
  }
}
```

**Step 3: Update `variables.tf`**

Remove: `environment` variable (no longer needed at root — each module sets its own).
Keep: All shared variables (`project_id`, `region`, `github_repo`, etc.).
The `db_name` variable is no longer needed at root (module constructs `aha_coms_sicu_{env}` internally).

**Step 4: Update `outputs.tf`**

Reference module outputs:

```hcl
output "dev_cloud_run_url" { value = module.dev.cloud_run_url }
output "prod_cloud_run_url" { value = module.prod.cloud_run_url }
output "dev_artifact_registry_url" { value = module.dev.artifact_registry_url }
output "prod_artifact_registry_url" { value = module.prod.artifact_registry_url }
# ... etc for all outputs, prefixed with dev_ or prod_
```

**Step 5: Empty out old root-level files**

Files that had their content moved to the module should be emptied or deleted:
- `iam.tf`, `secrets.tf`, `cloud_run.tf`, `firebase.tf`, `artifact_registry.tf`, `storage.tf`, `workload_identity.tf`, `scheduler.tf`

Option A: Delete these files entirely.
Option B: Leave them with a comment `# Moved to modules/environment/main.tf`.

Prefer Option A for cleanliness.

**Step 6: Commit**

```
refactor: restructure Terraform into shared + per-environment modules
```

---

### Task 3: Terraform state migration

**Why:** Terraform will see the module refactor as "destroy all old resources + create all new". We need to move existing state entries to their new module paths to avoid unnecessary destruction and recreation.

**Prerequisites:** Task 2 complete. Dev environment currently running.

**Step 1: Backup current state**

```bash
cd infrastructure/terraform
cp terraform.tfstate terraform.tfstate.backup-pre-migration
```

**Step 2: Move state entries for dev resources**

Map old resource addresses to new module addresses. Run `terraform state mv` for each:

```bash
# Service Accounts
terraform state mv 'google_service_account.cloud_run' 'module.dev.google_service_account.cloud_run'
terraform state mv 'google_service_account.deploy' 'module.dev.google_service_account.deploy'
terraform state mv 'google_service_account.scheduler' 'module.dev.google_service_account.scheduler'
terraform state mv 'google_service_account.gsheets_sync' 'module.dev.google_service_account.gsheets_sync'

# IAM bindings (all project-level and SA-level)
terraform state mv 'google_project_iam_member.deploy_run_admin' 'module.dev.google_project_iam_member.deploy_run_admin'
# ... (repeat for each IAM resource)

# Secrets
terraform state mv 'google_secret_manager_secret.db_password' 'module.dev.google_secret_manager_secret.db_password'
# ... (repeat for each secret + IAM binding)

# Cloud Run
terraform state mv 'google_cloud_run_v2_service.api' 'module.dev.google_cloud_run_v2_service.api'
terraform state mv 'google_cloud_run_v2_service_iam_member.public_access' 'module.dev.google_cloud_run_v2_service_iam_member.public_access'
terraform state mv 'google_cloud_run_v2_service_iam_member.scheduler_invoker_v2' 'module.dev.google_cloud_run_v2_service_iam_member.scheduler_invoker_v2'

# Firebase Hosting
terraform state mv 'google_firebase_hosting_site.frontend' 'module.dev.google_firebase_hosting_site.frontend'

# Artifact Registry
terraform state mv 'google_artifact_registry_repository.registry' 'module.dev.google_artifact_registry_repository.registry'

# GCS
terraform state mv 'google_storage_bucket.uploads' 'module.dev.google_storage_bucket.uploads'
terraform state mv 'google_storage_bucket_iam_member.api_sa_uploads' 'module.dev.google_storage_bucket_iam_member.api_sa_uploads'

# WIF
terraform state mv 'google_iam_workload_identity_pool.github' 'module.dev.google_iam_workload_identity_pool.github'
terraform state mv 'google_iam_workload_identity_pool_provider.github' 'module.dev.google_iam_workload_identity_pool_provider.github'
terraform state mv 'google_service_account_iam_member.deploy_wi_user' 'module.dev.google_service_account_iam_member.deploy_wi_user'

# Scheduler
terraform state mv 'google_cloud_scheduler_job.daily_sync' 'module.dev.google_cloud_scheduler_job.daily_sync'

# Databases
terraform state mv 'google_sql_database.dev' 'module.dev.google_sql_database.main'
terraform state mv 'google_sql_database.prod' 'module.prod.google_sql_database.main'
```

**Step 3: Run `terraform plan`**

Verify the plan shows:
- **No destroys** for existing dev resources (state was moved correctly)
- **Rename in-place** or **destroy+create** for resources with changed names (SAs, secrets, etc.)
- **Create** for all new prod resources
- **No changes** to Cloud SQL instance

**CRITICAL:** If the plan shows destroying the Cloud SQL instance or any database with data, STOP. Debug the state migration.

**Step 4: Review the plan carefully**

Resources that will be **destroyed and recreated** due to name changes (SA account_ids, secret IDs, etc. are immutable — can't be renamed):
- All service accounts (old `aha-sicu-*` → new `aha-coms-sicu-*`)
- All secrets (old `aha_sicu_*` → new `aha_coms_sicu_*`)
- Firebase Hosting site (old `aha-sicu-dev` → new `aha-coms-sicu-dev`)
- Artifact Registry (old name → new name)
- WIF pool (old name → new name)
- GCS bucket (old name → new name)
- Cloud Run service (old name → new name)
- Scheduler jobs (old name → new name)
- Databases (old `aha_sicu_dev` → new `aha_coms_sicu_dev`)

Since **everything** gets recreated due to name changes, the state migration in Step 2 is actually unnecessary for renamed resources. Terraform will destroy old + create new regardless.

**Revised approach:** Only use `terraform state mv` for resources whose names DON'T change:
- `google_sql_database_instance.main` (stays in root, same name)
- `google_sql_user.app` (stays in root, same name)
- API enablement resources (stay in root, unchanged)

For everything else, let Terraform destroy old and create new. This is safe because:
- Cloud Run is stateless
- Firebase Hosting is stateless
- Secrets will be re-injected
- SA bindings will be recreated
- GCS bucket contents are ephemeral (24h lifecycle)
- WIF will be recreated (GitHub Actions will use new provider path)
- **Database data must be backed up first** (Task 4)

**Step 5: Commit state backup (do NOT commit tfstate)**

```
chore: backup Terraform state before migration
```

---

### Task 4: Backup dev database and prepare for migration

**Why:** Terraform will destroy `aha_sicu_dev` database and create `aha_coms_sicu_dev`. We need to save the data first.

**Prerequisites:** Cloud SQL instance is running (check with `gcloud sql instances describe aha-sicu-db`).

**Step 1: Start Cloud SQL Auth Proxy**

```bash
cloud-sql-proxy PROJECT_ID:asia-southeast2:aha-sicu-db --port 5432
```

**Step 2: Dump dev database**

```bash
pg_dump -h 127.0.0.1 -p 5432 -U aha_sicu -d aha_sicu_dev -F c -f aha_sicu_dev_backup.dump
```

**Step 3: Verify dump file**

```bash
pg_restore -l aha_sicu_dev_backup.dump | head -20
```

Should show table list (users, brands, evaluations, etc.).

**Step 4: Record row counts for verification**

```bash
psql -h 127.0.0.1 -p 5432 -U aha_sicu -d aha_sicu_dev -c "
SELECT 'users' as tbl, count(*) FROM users
UNION ALL SELECT 'brand_vp_data', count(*) FROM brand_vp_data
UNION ALL SELECT 'evaluations', count(*) FROM evaluations
UNION ALL SELECT 'brand_uploads', count(*) FROM brand_uploads
UNION ALL SELECT 'calculator_results', count(*) FROM calculator_results;
"
```

Save this output — you'll compare after restore.

---

### Task 5: Apply Terraform (create both environments)

**Why:** This creates all new resources with the `aha-coms-sicu` prefix.

**Prerequisites:** Task 3 (state prep) and Task 4 (backup) complete.

**Step 1: Note down current secret values**

Before Terraform destroys old secrets, retrieve their current values:

```bash
gcloud secrets versions access latest --secret=aha_sicu_dev_db_password
gcloud secrets versions access latest --secret=aha_sicu_dev_firebase_admin --format='get(payload.data)' | base64 -d
gcloud secrets versions access latest --secret=aha_sicu_dev_gsheets_credentials --format='get(payload.data)' | base64 -d
gcloud secrets versions access latest --secret=aha_sicu_dev_smtp_password
```

Save these values securely — you'll re-inject them after Terraform apply.

**Step 2: Create `terraform.tfvars`**

```hcl
project_id                     = "YOUR_PROJECT_ID"
region                         = "asia-southeast2"
github_repo                    = "YOUR_ORG/aha_sicu"
cloud_run_image                = "us-docker.pkg.dev/cloudrun/container/hello"
smtp_user                      = "your-email@gmail.com"
gsheets_vp_spreadsheet_id      = "YOUR_SPREADSHEET_ID"
gsheets_meeting_spreadsheet_id = "YOUR_SPREADSHEET_ID"
```

**Step 3: Run `terraform plan`**

```bash
cd infrastructure/terraform
terraform plan -out=tfplan
```

**Review the plan.** Expected:
- Destroy: old `aha-sicu-*` resources (dev)
- Create: new `aha-coms-sicu-dev-*` resources
- Create: new `aha-coms-sicu-prod-*` resources
- Modify: Cloud SQL instance (backup enabled)
- No change: Cloud SQL instance name, user

**CRITICAL CHECK:** Confirm `google_sql_database_instance.main` shows either "no changes" or only the backup config change. If it shows "must be replaced", STOP.

**Step 4: Apply**

```bash
terraform apply tfplan
```

**Step 5: Verify resources created**

```bash
# Check Cloud Run services
gcloud run services list --region=asia-southeast2

# Check Firebase Hosting sites
firebase hosting:sites:list --project YOUR_PROJECT_ID

# Check secrets exist
gcloud secrets list --filter="name:aha_coms_sicu"

# Check databases exist
gcloud sql databases list --instance=aha-sicu-db
```

**Step 6: Commit Terraform changes (NOT state file)**

```
feat: rename GCP resources to aha-coms-sicu prefix with dual environment support
```

---

### Task 6: Restore dev database and inject secrets

**Why:** Terraform created empty `aha_coms_sicu_dev` database. We need to restore the data and re-inject secret values.

**Prerequisites:** Task 5 complete. Cloud SQL Auth Proxy running.

**Step 1: Restore dev database**

```bash
pg_restore -h 127.0.0.1 -p 5432 -U aha_sicu -d aha_coms_sicu_dev --no-owner --no-privileges aha_sicu_dev_backup.dump
```

**Step 2: Verify row counts match**

Run the same count query from Task 4 Step 4, but against `aha_coms_sicu_dev`. Compare numbers.

**Step 3: Re-inject dev secrets**

```bash
echo -n "VALUE" | gcloud secrets versions add aha_coms_sicu_dev_db_password --data-file=-
echo -n "VALUE" | gcloud secrets versions add aha_coms_sicu_dev_smtp_password --data-file=-
gcloud secrets versions add aha_coms_sicu_dev_firebase_admin --data-file=path/to/firebase-admin.json
gcloud secrets versions add aha_coms_sicu_dev_gsheets_credentials --data-file=path/to/gsheets-key.json
```

**Step 4: Inject prod secrets**

Same Firebase and GSheets credentials. **Different DB password for prod:**

```bash
# Generate a new password for prod DB
openssl rand -base64 24

# Set the DB user's password (shared user, new password for prod connections)
# NOTE: Since dev and prod share the same DB user on the same instance,
# you may want to create a separate prod DB user instead.
# For now, use the same user with the same password.
echo -n "SAME_DB_PASSWORD" | gcloud secrets versions add aha_coms_sicu_prod_db_password --data-file=-

echo -n "SMTP_VALUE" | gcloud secrets versions add aha_coms_sicu_prod_smtp_password --data-file=-
gcloud secrets versions add aha_coms_sicu_prod_firebase_admin --data-file=path/to/firebase-admin.json
gcloud secrets versions add aha_coms_sicu_prod_gsheets_credentials --data-file=path/to/gsheets-key.json
```

**Important note on DB password:** The Cloud SQL user `aha_sicu` is shared across both databases. The DB_PASSWORD secret can have the same value for both environments (it authenticates the same PostgreSQL user). If you want different passwords, you'd need separate DB users — not necessary for now.

---

### Task 7: Clone dev database to prod

**Why:** Prod should start as a perfect copy of dev.

**Prerequisites:** Task 6 complete (dev DB restored and verified).

**Step 1: Dump the restored dev database**

```bash
pg_dump -h 127.0.0.1 -p 5432 -U aha_sicu -d aha_coms_sicu_dev -F c -f aha_coms_sicu_dev_for_prod.dump
```

**Step 2: Restore into prod database**

```bash
pg_restore -h 127.0.0.1 -p 5432 -U aha_sicu -d aha_coms_sicu_prod --no-owner --no-privileges aha_coms_sicu_dev_for_prod.dump
```

**Step 3: Verify prod data**

Run the same row count query against `aha_coms_sicu_prod`. Numbers should match dev exactly.

**Step 4: Stop Cloud SQL Auth Proxy**

---

## Phase 2: Firebase + Workflow Updates

### Task 8: Update Firebase configuration

**Files:**
- Modify: `.firebaserc`
- Modify: `firebase.json`

**Step 1: Update `.firebaserc`**

Replace hosting targets with new names:

```json
{
  "projects": {
    "dev": "YOUR_GCP_PROJECT_ID",
    "prod": "YOUR_GCP_PROJECT_ID"
  },
  "targets": {
    "YOUR_GCP_PROJECT_ID": {
      "hosting": {
        "aha-coms-sicu-dev": ["aha-coms-sicu-dev"],
        "aha-coms-sicu-prod": ["aha-coms-sicu-prod"]
      }
    }
  }
}
```

**Step 2: Update `firebase.json`**

Replace target names:

```json
{
  "hosting": [
    {
      "target": "aha-coms-sicu-dev",
      "public": "frontend/dist",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
      "rewrites": [{ "source": "**", "destination": "/index.html" }]
    },
    {
      "target": "aha-coms-sicu-prod",
      "public": "frontend/dist",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
      "rewrites": [{ "source": "**", "destination": "/index.html" }]
    }
  ]
}
```

**Step 3: Commit**

```
feat: update Firebase config for aha-coms-sicu naming
```

---

### Task 9: Add pre-migration backup to prod deploy workflow

**Files:**
- Modify: `.github/workflows/_deploy-backend.yml`

**Step 1: Add backup step before migrations**

Insert after "Ensure Cloud SQL is running" and before "Start Cloud SQL Auth Proxy":

```yaml
      - name: Create pre-migration backup (prod only)
        if: inputs.environment == 'production'
        run: |
          BACKUP_DESC="pre-deploy-$(date +%Y%m%d-%H%M%S)-${GITHUB_SHA::8}"
          echo "Creating backup: $BACKUP_DESC"
          gcloud sql backups create \
            --instance=${{ vars.CLOUD_SQL_INSTANCE_NAME }} \
            --description="$BACKUP_DESC" \
            --project=${{ vars.GCP_PROJECT_ID }}
          echo "Backup created successfully"
```

**Step 2: Add backup cleanup step at the end**

Append after "Cleanup old Cloud Run revisions":

```yaml
      - name: Cleanup old pre-deploy backups (prod only)
        if: inputs.environment == 'production'
        run: |
          echo "Listing pre-deploy backups..."
          BACKUPS=$(gcloud sql backups list \
            --instance=${{ vars.CLOUD_SQL_INSTANCE_NAME }} \
            --project=${{ vars.GCP_PROJECT_ID }} \
            --filter="description~'^pre-deploy-'" \
            --sort-by="~startTime" \
            --format="value(id)")
          COUNT=0
          for BACKUP_ID in $BACKUPS; do
            COUNT=$((COUNT + 1))
            if [ $COUNT -gt 5 ]; then
              echo "Deleting old backup: $BACKUP_ID"
              gcloud sql backups delete "$BACKUP_ID" \
                --instance=${{ vars.CLOUD_SQL_INSTANCE_NAME }} \
                --project=${{ vars.GCP_PROJECT_ID }} --quiet || true
            fi
          done
          echo "Kept $((COUNT < 5 ? COUNT : 5)) backups, deleted $((COUNT > 5 ? COUNT - 5 : 0))"
```

**Step 3: Add `CLOUD_SQL_INSTANCE_NAME` to the workflow header comment**

Add to the "Required GitHub Actions variables" comment:
```
#   CLOUD_SQL_INSTANCE_NAME   – Cloud SQL instance name (for backups and start/stop API)
```

(This variable is already used in the "Ensure Cloud SQL is running" step.)

**Step 4: Commit**

```
feat: add pre-migration backup and cleanup to prod deploy workflow
```

---

### Task 10: Update GitHub environment variables

**Why:** GitHub Actions needs to know the new resource names.

**Step 1: Update `dev` environment variables**

In GitHub repo → Settings → Environments → `dev`, update:

| Variable | New Value |
|----------|-----------|
| `CLOUD_RUN_SERVICE` | `aha-coms-sicu-dev-api` |
| `ARTIFACT_REGISTRY_URL` | `asia-southeast2-docker.pkg.dev/PROJECT_ID/aha-coms-sicu-dev-registry` |
| `WORKLOAD_IDENTITY_PROVIDER` | (from `terraform output dev_workload_identity_provider`) |
| `DEPLOY_SERVICE_ACCOUNT` | (from `terraform output dev_deploy_service_account_email`) |
| `DB_SECRET_NAME` | `aha_coms_sicu_dev_db_password` |
| `DB_NAME` | `aha_coms_sicu_dev` |
| `FIREBASE_HOSTING_SITE` | `aha-coms-sicu-dev` |
| `VITE_API_BASE_URL` | (from `terraform output dev_cloud_run_url`) |

Keep unchanged: `GCP_PROJECT_ID`, `GCP_REGION`, `CLOUD_SQL_INSTANCE_CONNECTION`, `CLOUD_SQL_INSTANCE_NAME`, `DB_USER`, `VITE_FIREBASE_*`

**Step 2: Create `production` environment**

In GitHub repo → Settings → Environments → New environment → `production`.

Set all variables:

| Variable | Value |
|----------|-------|
| `GCP_PROJECT_ID` | Same as dev |
| `GCP_REGION` | `asia-southeast2` |
| `CLOUD_RUN_SERVICE` | `aha-coms-sicu-prod-api` |
| `ARTIFACT_REGISTRY_URL` | `asia-southeast2-docker.pkg.dev/PROJECT_ID/aha-coms-sicu-prod-registry` |
| `WORKLOAD_IDENTITY_PROVIDER` | (from `terraform output prod_workload_identity_provider`) |
| `DEPLOY_SERVICE_ACCOUNT` | (from `terraform output prod_deploy_service_account_email`) |
| `DB_SECRET_NAME` | `aha_coms_sicu_prod_db_password` |
| `DB_NAME` | `aha_coms_sicu_prod` |
| `DB_USER` | `aha_sicu` |
| `CLOUD_SQL_INSTANCE_CONNECTION` | Same as dev (same instance) |
| `CLOUD_SQL_INSTANCE_NAME` | `aha-sicu-db` |
| `FIREBASE_HOSTING_SITE` | `aha-coms-sicu-prod` |
| `VITE_API_BASE_URL` | (from `terraform output prod_cloud_run_url`) |
| `VITE_FIREBASE_API_KEY` | Same as dev (same Firebase project) |
| `VITE_FIREBASE_AUTH_DOMAIN` | Same as dev |
| `VITE_FIREBASE_PROJECT_ID` | Same as dev |

---

## Phase 3: Deploy + Verify

### Task 11: Deploy dev with new naming

**Why:** Verify the renamed dev environment works before touching prod.

**Step 1: Push to develop**

All Terraform + Firebase + workflow changes should be committed and pushed to `develop`. This triggers the deploy workflow with the updated `dev` environment variables.

**Step 2: Monitor deploy**

Watch GitHub Actions → Deploy Backend and Deploy Frontend workflows.

**Step 3: Verify dev**

- Backend health: `curl https://NEW_DEV_CLOUD_RUN_URL/docs`
- Frontend: Visit `https://aha-coms-sicu-dev.web.app`
- Run smoke tests:

```bash
cd smoke-tests
SMOKE_BACKEND_URL=https://NEW_DEV_CLOUD_RUN_URL \
SMOKE_FRONTEND_URL=https://aha-coms-sicu-dev.web.app \
npx playwright test
```

- Log in and test core flows: browse brands, open an evaluation, check calculator results

**Step 4: Fix any issues before proceeding to prod**

---

### Task 12: Initial prod deploy

**Why:** Get prod live with the same code and data as dev.

**Step 1: Create PR from `develop` → `main`**

```bash
git checkout main
git merge develop
git push origin main
```

Or use GitHub PR flow for audit trail.

**Step 2: Monitor deploy**

Watch GitHub Actions → Deploy Backend and Deploy Frontend workflows for `production` environment.

**Step 3: Verify prod**

- Backend health: `curl https://NEW_PROD_CLOUD_RUN_URL/docs`
- Frontend: Visit `https://aha-coms-sicu-prod.web.app`
- Run smoke tests:

```bash
cd smoke-tests
SMOKE_BACKEND_URL=https://NEW_PROD_CLOUD_RUN_URL \
SMOKE_FRONTEND_URL=https://aha-coms-sicu-prod.web.app \
npx playwright test
```

- Log in as domain expert and verify: brands visible, evaluations intact, calculators working
- **Bookmark rollback command:**

```bash
gcloud run services update-traffic aha-coms-sicu-prod-api \
  --region=asia-southeast2 --to-revisions=PREVIOUS_REVISION=100
```

---

### Task 13: Update documentation

**Files:**
- Modify: `docs/engineer/deployment-guide.md`
- Modify: `docs/engineer/architecture-infrastructure.md`

**Step 1: Update resource names**

Replace all `aha-sicu` references with `aha-coms-sicu` in both docs.

**Step 2: Add migration safety rules**

Add to deployment guide:

```markdown
## Database Migration Safety Rules

1. **All migrations MUST be additive** — CREATE TABLE, ADD COLUMN, ADD INDEX only
2. **Destructive changes require two-step release:**
   - Release 1: Add new structure, backfill data, code reads/writes both
   - Release 2: Remove old structure, code uses only new
3. **No exceptions.** Violating this risks prod data loss.
```

**Step 3: Add rollback procedures**

```markdown
## Rollback Procedures

### Cloud Run Revision Rollback (~10 seconds)
gcloud run services update-traffic aha-coms-sicu-prod-api \
  --region=asia-southeast2 --to-revisions=PREVIOUS_REVISION=100

### Code-Level Rollback (~3 minutes)
git revert HEAD on main → push → auto-redeploy

### Pre-deploy backups
Every prod deploy creates a Cloud SQL backup before running migrations.
Retained: last 5 pre-deploy backups.
```

**Step 4: Commit**

```
docs: update deployment guide and architecture for dual environment setup
```

---

### Task 14: Cleanup old databases

**Why:** After verifying both environments work, remove the old databases.

**Prerequisites:** Both dev and prod verified working for at least 1 day.

**Step 1: Drop old databases**

```bash
# Via Cloud SQL Auth Proxy
psql -h 127.0.0.1 -p 5432 -U aha_sicu -d postgres -c "DROP DATABASE aha_sicu_dev;"
psql -h 127.0.0.1 -p 5432 -U aha_sicu -d postgres -c "DROP DATABASE aha_sicu_prod;"
```

**Step 2: Clean up dump files**

Delete `aha_sicu_dev_backup.dump` and `aha_coms_sicu_dev_for_prod.dump`.

---

## Summary: Execution Order

| # | Task | Phase | Estimated Effort |
|---|------|-------|-----------------|
| 1 | Create Terraform environment module | Phase 1 | Medium |
| 2 | Refactor root Terraform to use modules | Phase 1 | Medium |
| 3 | Terraform state migration | Phase 1 | Small (mostly commands) |
| 4 | Backup dev database | Phase 1 | Small |
| 5 | Apply Terraform | Phase 1 | Small (review plan carefully) |
| 6 | Restore dev DB + inject secrets | Phase 1 | Small |
| 7 | Clone dev DB to prod | Phase 1 | Small |
| 8 | Update Firebase config | Phase 2 | Small |
| 9 | Add pre-migration backup to workflow | Phase 2 | Small |
| 10 | Update GitHub environment variables | Phase 2 | Small (manual in GitHub UI) |
| 11 | Deploy dev + verify | Phase 3 | Small |
| 12 | Initial prod deploy + verify | Phase 3 | Small |
| 13 | Update documentation | Phase 3 | Small |
| 14 | Cleanup old databases | Phase 3 | Small (wait 1 day) |

**Critical path:** Tasks 1-7 must be sequential. Tasks 8-9 can be done in parallel with Tasks 4-7. Task 10 depends on Task 5 (need Terraform outputs). Tasks 11-14 are sequential.
