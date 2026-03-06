# Secret Manager: Secret resources for Cloud Run environment variables
# NOTE: Secret VALUES are NOT managed by Terraform. Inject via:
#   echo -n "VALUE" | gcloud secrets versions add SECRET_NAME --data-file=-

resource "google_secret_manager_secret" "db_password" {
  secret_id = "aha_sicu_${var.environment}_db_password"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret" "gsheets_credentials" {
  secret_id = "aha_sicu_${var.environment}_gsheets_credentials"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret" "firebase_admin" {
  secret_id = "aha_sicu_${var.environment}_firebase_admin"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secret_manager_api]
}

# IAM: Grant Cloud Run SA access to each secret

resource "google_secret_manager_secret_iam_member" "api_sa_db_password" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

# Deploy SA needs DB password to run migrations during CI/CD
resource "google_secret_manager_secret_iam_member" "deploy_sa_db_password" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_gsheets" {
  secret_id = google_secret_manager_secret.gsheets_credentials.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret" "smtp_password" {
  secret_id = "aha_sicu_${var.environment}_smtp_password"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_iam_member" "api_sa_smtp_password" {
  secret_id = google_secret_manager_secret.smtp_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_firebase" {
  secret_id = google_secret_manager_secret.firebase_admin.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}
