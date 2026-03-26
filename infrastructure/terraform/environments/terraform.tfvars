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
cloud_run_memory        = "1Gi"
cloud_run_cpu           = "1"

# Google Sheets spreadsheet IDs (shared)
gsheets_vp_spreadsheet_id      = "1zKXRL0Luqo9_rN3vtZWdfX2mMm86GCh87nrLlTCp0BU"
gsheets_meeting_spreadsheet_id = "1bPxm-aEcjHH9DyShf1CysqzNfueBebSc2N-B1qX0YoM"

# Google Sheets eval spreadsheet IDs (per-environment)
dev_gsheets_eval_spreadsheet_id  = "1sU6OF8l2YsV5E_InP6rUHVqE_q9cSxN5ovU1PSEFT18"
prod_gsheets_eval_spreadsheet_id = "1RS798qnTYwk8usogqjBaeYUTKQJMsONm4p1Cik92HYM"

# Cloud SQL
cloud_sql_tier          = "db-f1-micro"
cloud_sql_disk_size     = 10
cloud_sql_instance_name = "aha-sicu-db"

# SMTP (Gmail)
smtp_user       = "handers.the@ahacommerce.net"
smtp_from_email = "handers.the@ahacommerce.net"

# Feature flags (per-environment)
dev_email_enabled  = true
prod_email_enabled = false

