# Store ICU - All Environments
# Single tfvars for the shared Terraform state managing both dev and prod.

project_id          = "fbi-dev-484410"
region              = "asia-southeast2"
github_repo         = "mrdoorba/aha_sicu"
firebase_project_id = "fbi-dev-484410"

# Cloud Run - shared sizing
dev_cloud_run_url       = "https://aha-coms-sicu-dev-api-45tyczfska-et.a.run.app"
prod_cloud_run_url      = "https://aha-coms-sicu-prod-api-45tyczfska-et.a.run.app"
cloud_run_image         = "us-docker.pkg.dev/cloudrun/container/hello"
cloud_run_min_instances = 0
cloud_run_max_instances = 2
cloud_run_memory        = "512Mi"
cloud_run_cpu           = "1"

# Google Sheets spreadsheet IDs (shared)
gsheets_vp_spreadsheet_id      = "1AH9-KuHJXLwxuv82LC5stBmvA-Db-mAfZGJfbUKkvWc"
gsheets_meeting_spreadsheet_id = "1AH9-KuHJXLwxuv82LC5stBmvA-Db-mAfZGJfbUKkvWc"

# Google Sheets eval spreadsheet IDs (per-environment)
dev_gsheets_eval_spreadsheet_id  = "1sU6OF8l2YsV5E_InP6rUHVqE_q9cSxN5ovU1PSEFT18"
prod_gsheets_eval_spreadsheet_id = "1RS798qnTYwk8usogqjBaeYUTKQJMsONm4p1Cik92HYM"

# Cloud SQL
cloud_sql_tier          = "db-f1-micro"
cloud_sql_disk_size     = 10
cloud_sql_instance_name = "aha-sicu-db"

# Email — From addresses per environment.
# dev: rich /send sends as bot@ahacommerce.net. Under Gmail DWD the From comes
# from gmail_dwd_sender; this value is the SMTP-path fallback. prod: unchanged.
dev_email_from_email  = "bot@ahacommerce.net"
prod_email_from_email = "noreply@ahabot.ai"

# Gmail SMTP (evaluation "Send Mail" dialog — /send-plain). The app password is
# NOT stored here (this file is tracked) — it is already seeded in Secret
# Manager as aha_coms_sicu_dev_gmail_smtp_app_password and managed via
# ignore_changes. Seed out-of-band, or pass -var="gmail_smtp_app_password=..."
# at apply.
gmail_smtp_user = "marwahkha@ahacommerce.net"

# Feature flags (per-environment)
dev_email_enabled       = true
prod_email_enabled      = true
dev_gmail_smtp_enabled  = true
prod_gmail_smtp_enabled = true

# Rich /send via Gmail API + domain-wide delegation. Both envs send as bot@ via
# the dev DWD SA (the one authorized in Admin Console); prod borrows dev's key
# through gmail_dwd_key_override, so no separate prod authorization is needed.
dev_gmail_dwd_enabled  = true
prod_gmail_dwd_enabled = true

