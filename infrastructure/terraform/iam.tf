# =============================================================================
# Service Accounts
# =============================================================================

# Scheduler SA (existing from Epic 2) — PRESERVED
resource "google_service_account" "scheduler" {
  account_id   = "aha-sicu-scheduler-sa"
  display_name = "Store ICU Scheduler Service Account"
  description  = "Service account for Cloud Scheduler to invoke Cloud Run sync endpoint"
  project      = var.project_id
}

# Scheduler invoker binding (v1 — existing from Epic 2) — PRESERVED
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = var.cloud_run_service_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
  project  = var.project_id
}

# Cloud Run API service account — dedicated runtime identity
resource "google_service_account" "cloud_run" {
  account_id   = "aha-sicu-api-sa"
  display_name = "Store ICU Cloud Run API"
  description  = "Service account for Cloud Run API runtime (secret access, storage)"
  project      = var.project_id

  depends_on = [google_project_service.iam_api]
}

# Deploy service account — GitHub Actions CI/CD
resource "google_service_account" "deploy" {
  account_id   = "aha-sicu-deploy-sa"
  display_name = "Store ICU Deploy (GitHub Actions)"
  description  = "Service account for CI/CD deployments via GitHub Actions"
  project      = var.project_id

  depends_on = [google_project_service.iam_api]
}

# =============================================================================
# Deploy SA — Project-level roles
# =============================================================================

resource "google_project_iam_member" "deploy_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

resource "google_project_iam_member" "deploy_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

# Deploy SA can impersonate Cloud Run SA (actAs) for deploying services
resource "google_service_account_iam_member" "deploy_acts_as_api" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.deploy.email}"
}
