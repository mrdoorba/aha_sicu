# Environment Module - Per-environment resources
# All resources use aha-coms-sicu-{env} naming pattern.

# =============================================================================
# Service Accounts
# =============================================================================

resource "google_service_account" "cloud_run" {
  account_id   = "aha-coms-sicu-${var.environment}-api-sa"
  display_name = "Store ICU ${var.environment} Cloud Run API"
  description  = "Service account for Cloud Run API runtime (secret access, storage)"
  project      = var.project_id
}

resource "google_service_account" "deploy" {
  account_id   = "aha-coms-sicu-${var.environment}-deploy-sa"
  display_name = "Store ICU ${var.environment} Deploy (GitHub Actions)"
  description  = "Service account for CI/CD deployments via GitHub Actions"
  project      = var.project_id
}

resource "google_service_account" "scheduler" {
  account_id   = "aha-coms-sicu-${var.environment}-sched-sa"
  display_name = "Store ICU ${var.environment} Scheduler Service Account"
  description  = "Service account for Cloud Scheduler to invoke Cloud Run sync endpoint"
  project      = var.project_id
}

resource "google_service_account" "gsheets_sync" {
  account_id   = "aha-coms-sicu-${var.environment}-sheets-sa"
  display_name = "Store ICU ${var.environment} Google Sheets Sync"
  description  = "Service account for syncing brand data from Google Sheets"
  project      = var.project_id
}

# =============================================================================
# IAM Bindings — Deploy SA
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

resource "google_service_account_iam_member" "deploy_acts_as_api" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.deploy.email}"
}

resource "google_project_iam_member" "deploy_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

resource "google_project_iam_member" "deploy_cloudsql_admin" {
  project = var.project_id
  role    = "roles/cloudsql.admin"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

# =============================================================================
# IAM Bindings — Cloud Run SA
# =============================================================================

resource "google_service_account_iam_member" "api_sa_token_creator" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_firebase_auth_admin" {
  project = var.project_id
  role    = "roles/firebaseauth.admin"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# =============================================================================
# Database Credentials (per-environment)
# =============================================================================

resource "random_password" "db" {
  length  = 24
  special = true
}

resource "google_sql_user" "app" {
  name     = "aha_sicu_${var.environment}"
  instance = var.cloud_sql_instance_name
  password = random_password.db.result
  project  = var.project_id
}

# =============================================================================
# Secrets
# =============================================================================

resource "google_secret_manager_secret" "db_password" {
  secret_id = "aha_coms_sicu_${var.environment}_db_password"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db.result

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_secret_manager_secret" "gsheets_credentials" {
  secret_id = "aha_coms_sicu_${var.environment}_gsheets_credentials"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_service_account_key" "gsheets_sync" {
  service_account_id = google_service_account.gsheets_sync.name
}

resource "google_secret_manager_secret_version" "gsheets_credentials" {
  secret      = google_secret_manager_secret.gsheets_credentials.id
  secret_data = base64decode(google_service_account_key.gsheets_sync.private_key)
}

resource "google_secret_manager_secret" "sendgrid_api_key" {
  secret_id = "aha_coms_sicu_${var.environment}_sendgrid_api_key"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "sendgrid_webhook_secret" {
  secret_id = "aha_coms_sicu_${var.environment}_sendgrid_webhook_secret"
  project   = var.project_id

  replication {
    auto {}
  }
}


# IAM: Grant Cloud Run SA access to secrets

resource "google_secret_manager_secret_iam_member" "api_sa_db_password" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_db_password" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_db_password_viewer" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.viewer"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_sendgrid_api_key" {
  secret_id = google_secret_manager_secret.sendgrid_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_sendgrid_api_key_viewer" {
  secret_id = google_secret_manager_secret.sendgrid_api_key.secret_id
  role      = "roles/secretmanager.viewer"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_sendgrid_webhook_secret" {
  secret_id = google_secret_manager_secret.sendgrid_webhook_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_sendgrid_webhook_secret_viewer" {
  secret_id = google_secret_manager_secret.sendgrid_webhook_secret.secret_id
  role      = "roles/secretmanager.viewer"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_gsheets" {
  secret_id = google_secret_manager_secret.gsheets_credentials.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_sendgrid_api_key" {
  secret_id = google_secret_manager_secret.sendgrid_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_sendgrid_webhook_secret" {
  secret_id = google_secret_manager_secret.sendgrid_webhook_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}


# =============================================================================
# Database (per-environment on shared instance)
# =============================================================================

resource "google_sql_database" "main" {
  name     = "aha_coms_sicu_${var.environment}"
  instance = var.cloud_sql_instance_name
  project  = var.project_id
}

# =============================================================================
# Cloud Run v2
# =============================================================================

locals {
  cloud_run_service_name = var.cloud_run_service_name != "" ? var.cloud_run_service_name : "aha-coms-sicu-${var.environment}-api"
  scheduler_target_url   = var.cloud_run_url != "" ? var.cloud_run_url : google_cloud_run_v2_service.api.uri
}

resource "google_cloud_run_v2_service" "api" {
  name                = local.cloud_run_service_name
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
        value = google_sql_user.app.name
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
        value = "aha_coms_sicu_${var.environment}"
      }

      env {
        name  = "CLOUD_SQL_INSTANCE"
        value = var.cloud_sql_instance_connection_name
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
        name  = "GCS_UPLOAD_BUCKET"
        value = google_storage_bucket.uploads.name
      }

      env {
        name = "SENDGRID_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.sendgrid_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "EMAIL_FROM_NAME"
        value = "AHA Commerce"
      }

      env {
        name  = "EMAIL_FROM_EMAIL"
        value = var.email_from_email
      }

      env {
        name = "SENDGRID_WEBHOOK_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.sendgrid_webhook_secret.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "EMAIL_ENABLED"
        value = tostring(var.email_enabled)
      }

      env {
        name  = "EMAIL_ALLOWED_DOMAINS"
        value = var.email_allowed_domains
      }

      env {
        name  = "GSHEETS_VP_SPREADSHEET_ID"
        value = var.gsheets_vp_spreadsheet_id
      }

      env {
        name  = "GSHEETS_MEETING_SPREADSHEET_ID"
        value = var.gsheets_meeting_spreadsheet_id
      }

      env {
        name  = "GSHEETS_EVAL_SPREADSHEET_ID"
        value = var.gsheets_eval_spreadsheet_id
      }

      env {
        name  = "GSHEETS_VP_SPREADSHEET_ID_TH"
        value = var.gsheets_vp_spreadsheet_id_th
      }

      env {
        name  = "CLOUD_RUN_URL"
        value = var.cloud_run_url
      }

      env {
        name  = "ALLOWED_SCHEDULER_EMAILS"
        value = google_service_account.scheduler.email
      }

      env {
        name  = "CORS_ORIGINS"
        value = join(",", var.cors_origins)
      }

      resources {
        cpu_idle = true
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
        instances = [var.cloud_sql_instance_connection_name]
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
    google_sql_user.app,
    google_secret_manager_secret_iam_member.api_sa_db_password,
    google_secret_manager_secret_iam_member.api_sa_gsheets,
    google_secret_manager_secret_iam_member.api_sa_sendgrid_api_key,
    google_secret_manager_secret_iam_member.api_sa_sendgrid_webhook_secret,
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

# =============================================================================
# Firebase Hosting
# =============================================================================

resource "google_firebase_hosting_site" "frontend" {
  provider = google-beta
  project  = var.firebase_project_id != "" ? var.firebase_project_id : var.project_id
  site_id  = "aha-coms-sicu-${var.environment}"
}

# =============================================================================
# Artifact Registry
# =============================================================================

resource "google_artifact_registry_repository" "registry" {
  location      = var.region
  repository_id = "aha-coms-sicu-${var.environment}-registry"
  description   = "Docker container images for Store ICU"
  format        = "DOCKER"
  project       = var.project_id

  cleanup_policy_dry_run = false

  cleanup_policies {
    id     = "delete-old-versions"
    action = "DELETE"

    condition {
      older_than = "86400s" # 1 day
    }
  }

  cleanup_policies {
    id     = "keep-latest-2"
    action = "KEEP"

    most_recent_versions {
      keep_count = 2
    }
  }
}

# =============================================================================
# GCS Upload Bucket
# =============================================================================

resource "google_storage_bucket" "uploads" {
  name                        = "${var.project_id}-aha-coms-sicu-${var.environment}-uploads"
  location                    = var.region
  project                     = var.project_id
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = var.environment == "dev" ? true : false

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = var.cors_origins
    method          = ["PUT"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_member" "api_sa_uploads" {
  bucket = google_storage_bucket.uploads.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}

# =============================================================================
# Workload Identity Federation
# =============================================================================

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "aha-coms-sicu-${var.environment}-github-pool"
  display_name              = "Aha SICU ${var.environment} GitHub Pool"
  description               = "Workload Identity Pool for GitHub Actions CI/CD"
  project                   = var.project_id
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub OIDC Provider"
  project                            = var.project_id

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  attribute_condition = "assertion.repository == \"${var.github_repo}\" && assertion.ref == \"refs/heads/${var.wif_allowed_branch}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "deploy_wi_user" {
  service_account_id = google_service_account.deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repo}"
}

# =============================================================================
# Cloud Scheduler — Daily Sync
# =============================================================================

resource "google_cloud_scheduler_job" "daily_sync" {
  name        = "aha-coms-sicu-${var.environment}-daily-sync"
  description = "Daily brand data sync from Google Sheets (08:30 WIB, weekdays)"
  schedule    = "30 8 * * 1-5"
  time_zone   = "Asia/Jakarta"
  project     = var.project_id
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "${local.scheduler_target_url}/api/v1/sync"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = local.scheduler_target_url
    }
  }

  retry_config {
    retry_count          = 3
    min_backoff_duration = "30s"
    max_backoff_duration = "300s"
  }
}
