# =============================================================================
# Service Accounts
# =============================================================================

# Scheduler SA (existing from Epic 2) — PRESERVED
resource "google_service_account" "scheduler" {
  account_id   = "aha-sicu-${var.environment}-scheduler-sa"
  display_name = "Store ICU ${var.environment} Scheduler Service Account"
  description  = "Service account for Cloud Scheduler to invoke Cloud Run sync endpoint"
  project      = var.project_id
}

# NOTE: v1 scheduler invoker binding removed during code review.
# The v2 binding is in cloud_run.tf (scheduler_invoker_v2).

# Cloud Run API service account — dedicated runtime identity
resource "google_service_account" "cloud_run" {
  account_id   = "aha-sicu-${var.environment}-api-sa"
  display_name = "Store ICU ${var.environment} Cloud Run API"
  description  = "Service account for Cloud Run API runtime (secret access, storage)"
  project      = var.project_id

  depends_on = [google_project_service.iam_api]
}

# Deploy service account — GitHub Actions CI/CD
resource "google_service_account" "deploy" {
  account_id   = "aha-sicu-${var.environment}-deploy-sa"
  display_name = "Store ICU ${var.environment} Deploy (GitHub Actions)"
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
