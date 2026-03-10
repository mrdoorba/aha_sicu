# Store ICU Infrastructure - Outputs (per-environment from modules)

# =============================================================================
# Dev Environment
# =============================================================================

output "dev_cloud_run_url" {
  description = "Dev Cloud Run API URL"
  value       = module.dev.cloud_run_url
}

output "dev_artifact_registry_url" {
  description = "Dev Docker image push target"
  value       = module.dev.artifact_registry_url
}

output "dev_deploy_service_account_email" {
  description = "Dev deploy service account email"
  value       = module.dev.deploy_service_account_email
}

output "dev_workload_identity_provider" {
  description = "Dev WIF provider path for GitHub Actions"
  value       = module.dev.workload_identity_provider
}

output "dev_gcs_upload_bucket" {
  description = "Dev GCS upload bucket name"
  value       = module.dev.gcs_upload_bucket
}

output "dev_gsheets_service_account_email" {
  description = "Dev Google Sheets sync service account email"
  value       = module.dev.gsheets_service_account_email
}

output "dev_firebase_hosting_site" {
  description = "Dev Firebase Hosting site ID"
  value       = module.dev.firebase_hosting_site
}

# =============================================================================
# Prod Environment
# =============================================================================

output "prod_cloud_run_url" {
  description = "Prod Cloud Run API URL"
  value       = module.prod.cloud_run_url
}

output "prod_artifact_registry_url" {
  description = "Prod Docker image push target"
  value       = module.prod.artifact_registry_url
}

output "prod_deploy_service_account_email" {
  description = "Prod deploy service account email"
  value       = module.prod.deploy_service_account_email
}

output "prod_workload_identity_provider" {
  description = "Prod WIF provider path for GitHub Actions"
  value       = module.prod.workload_identity_provider
}

output "prod_gcs_upload_bucket" {
  description = "Prod GCS upload bucket name"
  value       = module.prod.gcs_upload_bucket
}

output "prod_gsheets_service_account_email" {
  description = "Prod Google Sheets sync service account email"
  value       = module.prod.gsheets_service_account_email
}

output "prod_firebase_hosting_site" {
  description = "Prod Firebase Hosting site ID"
  value       = module.prod.firebase_hosting_site
}

# =============================================================================
# Shared
# =============================================================================

output "cloud_sql_instance_connection_name" {
  description = "Cloud SQL instance connection name for Cloud Run and Auth Proxy"
  value       = google_sql_database_instance.main.connection_name
}

output "cloud_sql_instance_ip" {
  description = "Cloud SQL instance public IP address"
  value       = google_sql_database_instance.main.public_ip_address
}
