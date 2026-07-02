# Store ICU Infrastructure - Terraform

GCP infrastructure provisioning for Store ICU (Aha SICU) using Terraform.

## Prerequisites

1. [Terraform](https://www.terraform.io/downloads) >= 1.5
2. GCP account with billing enabled
3. `gcloud` CLI authenticated (`gcloud auth application-default login`)
4. GCP project created with billing enabled

## File Structure

```
infrastructure/terraform/
├── main.tf                        # Provider config (google ~> 7.0) + API enablement + module calls
├── variables.tf                   # Shared input variables
├── outputs.tf                     # Per-environment outputs (dev_ / prod_ prefixed) + shared outputs
├── cloud_sql.tf                   # Shared Cloud SQL instance, app user, SQL scheduler SA, start/stop jobs
├── modules/
│   └── environment/
│       ├── main.tf                # All per-environment resources (SAs, IAM, secrets, Cloud Run, etc.)
│       ├── variables.tf           # Module input variables
│       └── outputs.tf             # Module outputs
├── setup.sh                       # Interactive bootstrap script
├── README.md
└── environments/
    └── terraform.tfvars.example   # Example variable values
```

## Bootstrap Sequence

A single `terraform apply` provisions both dev and prod environments using the module pattern:

```hcl
module "dev"  { source = "./modules/environment"; environment = "dev";  enable_scheduler = false; ... }
module "prod" { source = "./modules/environment"; environment = "prod"; enable_scheduler = true;  ... }
```

Resources have dependencies. Terraform handles ordering automatically, but for initial understanding:

1. **APIs** — Enable required GCP APIs (main.tf)
2. **Service Accounts** — Create SAs before resources that reference them (environment module)
3. **Secrets** — Create secret resources + IAM bindings (environment module)
4. **Storage** — GCS bucket + IAM binding (environment module)
5. **Artifact Registry** — Docker repository (environment module)
6. **Cloud SQL** — Shared instance (cloud_sql.tf) + per-env databases (environment module)
7. **Cloud Run** — Service referencing secrets, SA, and image (environment module)
8. **Workload Identity** — GitHub Actions OIDC federation (environment module)
9. **Firebase Hosting** — Frontend hosting site (environment module)
10. **Cloud Scheduler** — Prod daily sync only (environment module)

## Quick Setup

Run the interactive setup script — it handles init, plan, apply, and secret injection:

```bash
cd infrastructure/terraform
./setup.sh
```

## Manual Setup

### 1. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init -upgrade
```

### 2. Plan and Apply

```bash
terraform plan
terraform apply
```

### 3. Inject secret values (after apply)

Secret **resources** are created by Terraform, but **values** must be injected manually.

Secret names use the prefix: `aha_coms_sicu_{env}_*`

```bash
# === Development environment ===

# Database password (Cloud SQL)
echo -n "YOUR_DB_PASSWORD" | \
  gcloud secrets versions add aha_coms_sicu_dev_db_password --data-file=-

# Google Sheets service account credentials (JSON key file)
gcloud secrets versions add aha_coms_sicu_dev_gsheets_credentials \
  --data-file=path/to/gsheets-service-account.json

# Firebase Admin SDK credentials (JSON key file)
gcloud secrets versions add aha_coms_sicu_dev_firebase_admin \
  --data-file=path/to/firebase-admin-credentials.json

# === Production environment ===

echo -n "YOUR_DB_PASSWORD" | \
  gcloud secrets versions add aha_coms_sicu_prod_db_password --data-file=-

gcloud secrets versions add aha_coms_sicu_prod_gsheets_credentials \
  --data-file=path/to/gsheets-service-account.json

gcloud secrets versions add aha_coms_sicu_prod_firebase_admin \
  --data-file=path/to/firebase-admin-credentials.json
```

The Gmail-DWD credentials (`aha_coms_sicu_{env}_gmail_dwd_credentials`) are
generated and seeded by Terraform from the `email_dwd` service-account key — no
manual seeding needed. Its client ID (`terraform output {env}_email_dwd_client_id`)
must be authorized in the Workspace Admin Console for scope `gmail.send`.

## Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| Cloud Run v2 (`aha-coms-sicu-{env}-api`) | `google_cloud_run_v2_service` | Backend API |
| Cloud SQL (`aha-sicu-db`) | `google_sql_database_instance` | PostgreSQL database (shared) |
| Cloud SQL DBs (`aha_coms_sicu_dev` + `aha_coms_sicu_prod`) | `google_sql_database` | Per-environment databases |
| Artifact Registry (`aha-coms-sicu-{env}-registry`) | `google_artifact_registry_repository` | Docker images |
| Secret Manager (per env) | `google_secret_manager_secret` | DB password, Sheets creds, Firebase creds, Gmail SMTP + rich /send app passwords, Gmail-DWD credentials |
| GCS Bucket (`{project_id}-aha-coms-sicu-{env}-uploads`) | `google_storage_bucket` | Raw uploaded files (kept until user replaces the upload) |
| Firebase Hosting (`aha-coms-sicu-{env}`) | `google_firebase_hosting_site` | Frontend hosting |
| Workload Identity Pool (`aha-coms-sicu-{env}-github-pool`) | `google_iam_workload_identity_pool` | GitHub Actions OIDC |
| Cloud Scheduler (daily sync, prod only) | `google_cloud_scheduler_job` | Daily brand sync |

## Service Accounts

| Service Account | Purpose | Key Permissions |
|-----------------|---------|-----------------|
| `aha-coms-sicu-{env}-api-sa` | Cloud Run runtime | Secret accessor, storage objectAdmin, cloudsql.client, firebaseauth.admin |
| `aha-coms-sicu-{env}-deploy-sa` | GitHub Actions CI/CD | run.admin, artifactregistry.writer, cloudsql.client, secretmanager.secretAccessor |
| `aha-coms-sicu-prod-sched-sa` | Cloud Scheduler sync | run.invoker on Cloud Run service |
| `aha-coms-sicu-{env}-sheets-sa` | Google Sheets API | (Share target Sheet with this SA email) |

## Outputs

| Output | Description |
|--------|-------------|
| `dev_cloud_run_url` / `prod_cloud_run_url` | API URL |
| `cloud_sql_instance_connection_name` | Cloud SQL connection name (shared) |
| `dev_artifact_registry_url` / `prod_artifact_registry_url` | Docker image push target |
| `dev_gcs_upload_bucket` / `prod_gcs_upload_bucket` | Upload bucket name |
| `dev_workload_identity_provider` / `prod_workload_identity_provider` | Full provider path for GitHub Actions |
| `dev_deploy_service_account_email` / `prod_deploy_service_account_email` | Deploy SA email for CI/CD config |

## Security Notes

- **Never commit** `terraform.tfvars` or `*.tfstate` files (excluded via `.gitignore`)
- **Never commit** service account key files
- Secret values are NOT in Terraform state — inject via `gcloud` CLI
- Workload Identity Federation provides keyless GitHub Actions auth (no SA keys for CI/CD)
- Each service account follows least-privilege principle — no project-wide editor/owner roles
- GCS bucket uses uniform bucket-level access (no ACLs)
- Upload bucket has no age-based lifecycle delete; the app deletes the old GCS object when a user replaces a brand/file-type upload
