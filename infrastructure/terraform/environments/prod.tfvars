# Store ICU - Production Environment Variables

project_id          = "REPLACE_WITH_PROD_PROJECT_ID"
region              = "asia-southeast1"
environment         = "prod"
github_repo         = "AHA-Indonesia/store-icu"
firebase_project_id = "REPLACE_WITH_PROD_PROJECT_ID"

# Cloud Run - prod sizing
cloud_run_url           = "REPLACE_WITH_CLOUD_RUN_URL"
cloud_run_image         = "asia-southeast1-docker.pkg.dev/REPLACE_WITH_PROD_PROJECT_ID/aha-sicu-registry/aha-sicu-api:latest"
cloud_run_min_instances = 1
cloud_run_max_instances = 4
cloud_run_memory        = "512Mi"
cloud_run_cpu           = "1"
