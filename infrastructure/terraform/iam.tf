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

resource "google_project_iam_member" "deploy_firebase_hosting" {
  project = var.project_id
  role    = "roles/firebasehosting.admin"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

# Deploy SA can impersonate Cloud Run SA (actAs) for deploying services
resource "google_service_account_iam_member" "deploy_acts_as_api" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.deploy.email}"
}

# Cloud Run SA can sign its own tokens (required for GCS signed URLs)
resource "google_service_account_iam_member" "api_sa_token_creator" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Run SA can manage Firebase Auth users (create, update, delete)
resource "google_project_iam_member" "cloud_run_firebase_auth_admin" {
  project = var.project_id
  role    = "roles/firebaseauth.admin"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Run SA can connect to Cloud SQL via built-in connector
resource "google_project_iam_member" "cloud_run_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Deploy SA can connect to Cloud SQL for CI/CD migrations via Auth Proxy
resource "google_project_iam_member" "deploy_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

# Deploy SA can start Cloud SQL instance if stopped (for off-hours deployments)
resource "google_project_iam_member" "deploy_cloudsql_editor" {
  project = var.project_id
  role    = "roles/cloudsql.editor"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}
