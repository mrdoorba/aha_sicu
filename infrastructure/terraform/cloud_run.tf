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
        name  = "DB_USER"
        value = var.db_user
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "DB_NAME"
        value = var.db_name
      }

      env {
        name  = "CLOUD_SQL_INSTANCE"
        value = google_sql_database_instance.main.connection_name
      }

      env {
        name = "GSHEETS_CREDENTIALS_JSON"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gsheets_credentials.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "FIREBASE_CREDENTIALS_JSON"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.firebase_admin.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "GCS_UPLOAD_BUCKET"
        value = google_storage_bucket.uploads.name
      }

      env {
        name  = "SMTP_HOST"
        value = "smtp.gmail.com"
      }

      env {
        name  = "SMTP_PORT"
        value = "587"
      }

      env {
        name  = "SMTP_USER"
        value = var.smtp_user
      }

      env {
        name = "SMTP_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.smtp_password.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "SMTP_FROM_NAME"
        value = var.smtp_from_name
      }

      env {
        name  = "SMTP_FROM_EMAIL"
        value = var.smtp_user
      }

      env {
        name  = "EMAIL_ENABLED"
        value = "true"
      }

      env {
        name  = "GSHEETS_VP_SPREADSHEET_ID"
        value = var.gsheets_vp_spreadsheet_id
      }

      env {
        name  = "GSHEETS_MEETING_SPREADSHEET_ID"
        value = var.gsheets_meeting_spreadsheet_id
      }

      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.main.connection_name]
      }
    }

    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      template[0].labels,
      client,
      client_version,
      build_config,
    ]
  }

  depends_on = [
    google_project_service.run_api,
    google_secret_manager_secret_iam_member.api_sa_db_password,
    google_secret_manager_secret_iam_member.api_sa_gsheets,
    google_secret_manager_secret_iam_member.api_sa_firebase,
    google_secret_manager_secret_iam_member.api_sa_smtp_password,
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
