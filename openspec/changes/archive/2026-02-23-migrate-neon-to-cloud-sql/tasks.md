## 1. Terraform: Region & Version Updates

- [x] 1.1 Update `variables.tf`: change default region to `asia-southeast2`, update `required_version` to `>= 1.5`, add new Cloud SQL variables (`cloud_sql_tier`, `cloud_sql_disk_size`, `cloud_sql_instance_name`, `db_user`, `db_name`)
- [x] 1.2 Update `environments/dev.tfvars`: set `region = "asia-southeast2"` and add Cloud SQL variable values
- [x] 1.3 Update `environments/prod.tfvars`: set `region = "asia-southeast2"` and add Cloud SQL variable values

## 2. Terraform: Cloud SQL Provisioning

- [x] 2.1 Update `main.tf`: add `google_project_service` for `sqladmin.googleapis.com`
- [x] 2.2 Create `cloud_sql.tf`: define `google_sql_database_instance` (db-f1-micro, SSD 10GB, public IP, SSL required, no backups, deletion protection conditional on environment)
- [x] 2.3 Add `google_sql_database` resources for `aha_sicu_dev` and `aha_sicu_prod` in `cloud_sql.tf`
- [x] 2.4 Add `google_sql_user` resource in `cloud_sql.tf`

## 3. Terraform: IAM & Secrets

- [x] 3.1 Update `iam.tf`: add `roles/cloudsql.client` for Cloud Run SA and Deploy SA
- [x] 3.2 Update `secrets.tf`: replace `db_url` secret with `db_password` secret, update IAM bindings accordingly

## 4. Terraform: Cloud Run Integration

- [x] 4.1 Update `cloud_run.tf`: add Cloud SQL instance connection annotation, update environment variables (replace `DATABASE_URL` secret ref with `DB_USER`, `DB_PASSWORD` secret ref, `DB_NAME`, `CLOUD_SQL_INSTANCE` env vars)

## 5. Terraform: Scheduled Start/Stop

- [x] 5.1 Add Cloud SQL scheduler service account with `roles/cloudsql.admin` in `cloud_sql.tf`
- [x] 5.2 Add Cloud Scheduler START job (07:30 WIB / `30 0 * * *` UTC) calling SQL Admin API in `cloud_sql.tf`
- [x] 5.3 Add Cloud Scheduler STOP job (19:00 WIB / `0 12 * * *` UTC) calling SQL Admin API in `cloud_sql.tf`

## 6. Terraform: Sync Schedule & Outputs

- [x] 6.1 Update `scheduler.tf`: change daily sync cron from `0 6 * * *` to `0 1 * * *` (08:00 WIB = 01:00 UTC)
- [x] 6.2 Update `outputs.tf`: add Cloud SQL instance connection name and instance IP outputs

## 7. Backend: Connection & Config

- [x] 7.1 Update `config.py`: add `db_user`, `db_password`, `db_name`, `cloud_sql_instance` fields, add `effective_database_url` property, change pool defaults to min=1/max=5, update comments
- [x] 7.2 Update `connection.py`: update docstring from "Neon" to "Cloud SQL", update default pool sizes in `init()` signature
- [x] 7.3 Update `main.py`: use `settings.effective_database_url` instead of `settings.database_url` for pool init
- [x] 7.4 Update `migrations/env.py`: use effective database URL construction (handle both Unix socket and TCP formats for SQLAlchemy)
- [x] 7.5 Update `.env.example`: replace Neon example with Cloud SQL local dev format, update comments, add new variables

## 8. CI/CD: Deploy Workflow

- [x] 8.1 Update `deploy-backend.yml` dev job: add Cloud SQL Auth Proxy download and start step, update migration step to construct DATABASE_URL from components, add proxy cleanup
- [x] 8.2 Update `deploy-backend.yml` prod job: same Auth Proxy changes as dev job
- [x] 8.3 Add comments documenting new required GitHub Actions variables (`CLOUD_SQL_INSTANCE_CONNECTION`, `DB_USER`, `DB_NAME`, `DB_SECRET_NAME`)

## 9. Verification

- [x] 9.1 Run `uv run ruff check .` in backend to verify no lint errors
- [x] 9.2 Run `uv run pytest -v` in backend to verify tests pass
- [x] 9.3 Verify Terraform config is valid with a dry-run review of all changed .tf files
