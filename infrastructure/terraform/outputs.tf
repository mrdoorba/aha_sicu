# Store ICU Infrastructure - Outputs for downstream workflows

output "cloud_run_url" {
  description = "The production Cloud Run API URL"
  value       = google_cloud_run_v2_service.api.uri
}

output "artifact_registry_url" {
  description = "Docker image push target for Artifact Registry"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.registry.repository_id}"
}

output "gcs_upload_bucket" {
  description = "GCS upload bucket name"
  value       = google_storage_bucket.uploads.name
}

output "workload_identity_provider" {
  description = "Full Workload Identity Pool Provider path for GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "deploy_service_account_email" {
  description = "Deploy service account email for GitHub Actions workflow config"
  value       = google_service_account.deploy.email
}
