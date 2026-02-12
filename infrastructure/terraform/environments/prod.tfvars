# Store ICU - Production Environment Variables

project_id          = "YOUR_GCP_PROJECT_ID"
region              = "asia-southeast1"
environment         = "prod"
github_repo         = "HandersThe/aha_sicu"
firebase_project_id = "YOUR_GCP_PROJECT_ID"

# Cloud Run - prod sizing
cloud_run_url           = ""
cloud_run_image         = "asia-docker.pkg.dev/cloudrun/container/hello"
cloud_run_min_instances = 1
cloud_run_max_instances = 4
cloud_run_memory        = "512Mi"
cloud_run_cpu           = "1"
