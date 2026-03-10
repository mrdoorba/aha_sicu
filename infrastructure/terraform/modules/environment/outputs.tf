# Environment Module - Outputs

output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.api.uri
}

output "artifact_registry_url" {
  description = "Docker image push target for Artifact Registry"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.registry.repository_id}"
}

output "deploy_service_account_email" {
  description = "Deploy service account email"
  value       = google_service_account.deploy.email
}

output "workload_identity_provider" {
  description = "Full Workload Identity Pool Provider path"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "gcs_upload_bucket" {
  description = "GCS upload bucket name"
  value       = google_storage_bucket.uploads.name
}

output "gsheets_service_account_email" {
  description = "Google Sheets sync service account email"
  value       = google_service_account.gsheets_sync.email
}

output "firebase_hosting_site" {
  description = "Firebase Hosting site ID"
  value       = google_firebase_hosting_site.frontend.site_id
}
