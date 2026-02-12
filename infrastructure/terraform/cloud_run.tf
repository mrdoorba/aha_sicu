# Cloud Run v2: API service for Store ICU backend

resource "google_cloud_run_v2_service" "api" {
  name                = var.cloud_run_service_name != "" ? var.cloud_run_service_name : "aha-sicu-${var.environment}-api"
  location            = var.region
  project             = var.project_id
  deletion_protection = var.environment == "prod" ? true : false

  template {
    service_account = google_service_account.cloud_run.email

    containers {
      image = var.cloud_run_image

      ports {
        container_port = 8080
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GSHEETS_CREDENTIALS"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gsheets_credentials.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "FIREBASE_ADMIN_CREDENTIALS"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.firebase_admin.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
      }
    }

    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }
  }

  depends_on = [
    google_project_service.run_api,
    google_secret_manager_secret_iam_member.api_sa_db_url,
    google_secret_manager_secret_iam_member.api_sa_gsheets,
    google_secret_manager_secret_iam_member.api_sa_firebase,
  ]
}

# Allow unauthenticated access — auth handled at app layer via Firebase JWT
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
  project  = var.project_id
}

# Scheduler invoker on Cloud Run v2 service
resource "google_cloud_run_v2_service_iam_member" "scheduler_invoker_v2" {
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
  project  = var.project_id
}
