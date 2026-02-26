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
├── main.tf                # Provider config (google ~> 7.0) + API enablement
├── variables.tf           # All input variables
├── outputs.tf             # Outputs for downstream workflows (CI/CD, etc.)
├── iam.tf                 # Service accounts + IAM bindings
├── cloud_run.tf           # Cloud Run v2 API service
├── cloud_sql.tf           # Cloud SQL PostgreSQL instance + databases
├── artifact_registry.tf   # Docker container registry
├── secrets.tf             # Secret Manager secrets (resource only, no values)
├── storage.tf             # GCS upload bucket
├── firebase.tf            # Firebase Hosting site
├── workload_identity.tf   # GitHub Actions OIDC federation
├── scheduler.tf           # Cloud Scheduler daily sync + SQL start/stop
├── README.md
└── environments/
    ├── dev.tfvars          # Development environment values
    └── prod.tfvars         # Production environment values
```

## Bootstrap Sequence

Resources have dependencies. Terraform handles ordering automatically, but for initial understanding:

1. **APIs** — Enable required GCP APIs (main.tf)
2. **Service Accounts** — Create SAs before resources that reference them (iam.tf)
3. **Secrets** — Create secret resources + IAM bindings (secrets.tf)
4. **Storage** — GCS bucket + IAM binding (storage.tf)
5. **Artifact Registry** — Docker repository (artifact_registry.tf)
6. **Cloud Run** — Service referencing secrets, SA, and image (cloud_run.tf)
7. **Workload Identity** — GitHub Actions OIDC federation (workload_identity.tf)
8. **Firebase Hosting** — Frontend hosting site (firebase.tf)
9. **Cloud Scheduler** — Daily sync job targeting Cloud Run URL (scheduler.tf)

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

### 2. Plan with environment-specific values

```bash
# Development
terraform plan -var-file=environments/dev.tfvars

# Production
terraform plan -var-file=environments/prod.tfvars
```

### 3. Apply

```bash
terraform apply -var-file=environments/dev.tfvars
```

### 4. Inject secret values (after apply)

Secret **resources** are created by Terraform, but **values** must be injected manually.

Secret names include the environment prefix: `aha_sicu_{env}_*`

```bash
# === Development environment ===

# Database password (Cloud SQL)
echo -n "YOUR_DB_PASSWORD" | \
  gcloud secrets versions add aha_sicu_dev_db_password --data-file=-

# Google Sheets service account credentials (JSON key file)
gcloud secrets versions add aha_sicu_dev_gsheets_credentials \
  --data-file=path/to/gsheets-service-account.json

# Firebase Admin SDK credentials (JSON key file)
gcloud secrets versions add aha_sicu_dev_firebase_admin \
  --data-file=path/to/firebase-admin-credentials.json

# === Production environment ===

echo -n "YOUR_DB_PASSWORD" | \
  gcloud secrets versions add aha_sicu_prod_db_password --data-file=-

gcloud secrets versions add aha_sicu_prod_gsheets_credentials \
  --data-file=path/to/gsheets-service-account.json

gcloud secrets versions add aha_sicu_prod_firebase_admin \
  --data-file=path/to/firebase-admin-credentials.json
```

## Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| Cloud Run v2 (`aha-sicu-api`) | `google_cloud_run_v2_service` | Backend API |
| Cloud SQL (`aha-sicu-db`) | `google_sql_database_instance` | PostgreSQL database |
| Cloud SQL DBs (dev + prod) | `google_sql_database` | Per-environment databases |
| Artifact Registry (`aha-sicu-registry`) | `google_artifact_registry_repository` | Docker images |
| Secret Manager (3 secrets) | `google_secret_manager_secret` | DB password, Sheets creds, Firebase creds |
| GCS Bucket (`{project_id}-aha-sicu-{env}-uploads`) | `google_storage_bucket` | Temporary file uploads (24h lifecycle) |
| Firebase Hosting (`aha-sicu`) | `google_firebase_hosting_site` | Frontend hosting |
| Workload Identity Pool | `google_iam_workload_identity_pool` | GitHub Actions OIDC |
| Cloud Scheduler (sync) | `google_cloud_scheduler_job` | Daily brand sync |
| Cloud Scheduler (SQL start/stop) | `google_cloud_scheduler_job` | Cost optimization |

## Service Accounts

| Service Account | Purpose | Key Permissions |
|-----------------|---------|-----------------|
| `aha-sicu-{env}-api-sa` | Cloud Run runtime | Secret accessor, storage objectAdmin, cloudsql.client, firebaseauth.admin |
| `aha-sicu-{env}-deploy-sa` | GitHub Actions CI/CD | run.admin, artifactregistry.writer, cloudsql.client, secretmanager.secretAccessor |
| `aha-sicu-{env}-scheduler-sa` | Cloud Scheduler sync | run.invoker on Cloud Run service |
| `aha-sicu-sql-scheduler-sa` | Cloud SQL start/stop | cloudsql.admin |

## Outputs

| Output | Description |
|--------|-------------|
| `cloud_run_url` | API URL |
| `cloud_sql_connection_name` | Cloud SQL connection name |
| `artifact_registry_url` | Docker image push target |
| `gcs_upload_bucket` | Upload bucket name (`{project_id}-aha-sicu-{env}-uploads`) |
| `workload_identity_provider` | Full provider path for GitHub Actions |
| `deploy_service_account_email` | Deploy SA email for CI/CD config |

## Security Notes

- **Never commit** `terraform.tfvars` or `*.tfstate` files (excluded via `.gitignore`)
- **Never commit** service account key files
- Secret values are NOT in Terraform state — inject via `gcloud` CLI
- Workload Identity Federation provides keyless GitHub Actions auth (no SA keys for CI/CD)
- Each service account follows least-privilege principle — no project-wide editor/owner roles
- GCS bucket uses uniform bucket-level access (no ACLs)
