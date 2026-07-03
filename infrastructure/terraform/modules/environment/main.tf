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
  count        = var.enable_scheduler ? 1 : 0
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

# Dedicated SA for sending mail as ${var.gmail_dwd_sender} via the Gmail API
# using domain-wide delegation. Kept separate from gsheets_sync so a leaked key
# can't reach Sheets and vice-versa. Its client_id (unique_id) must be
# authorized in the Workspace Admin Console for scope gmail.send — that DWD
# grant is a Workspace object and lives outside this GCP stack.
resource "google_service_account" "email_dwd" {
  account_id   = "aha-coms-sicu-${var.environment}-email-sa"
  display_name = "Store ICU ${var.environment} Gmail DWD Sender"
  description  = "Service account for sending evaluation email via Gmail API (domain-wide delegation)"
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

resource "google_secret_manager_secret" "gmail_dwd_credentials" {
  secret_id = "aha_coms_sicu_${var.environment}_gmail_dwd_credentials"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_service_account_key" "email_dwd" {
  service_account_id = google_service_account.email_dwd.name
}

resource "google_secret_manager_secret_version" "gmail_dwd_credentials" {
  secret = google_secret_manager_secret.gmail_dwd_credentials.id
  # Borrow an already-authorized SA key when an override is supplied (prod reuses
  # dev's DWD SA, which is the one authorized in the Admin Console), else use
  # this env's own SA key.
  secret_data = var.gmail_dwd_key_override != "" ? var.gmail_dwd_key_override : base64decode(google_service_account_key.email_dwd.private_key)
}

# Gmail SMTP App Password — backs the evaluation "Send Mail" dialog
# (POST /api/v1/email/send-plain). Value is seeded out-of-band via gcloud;
# ignore_changes keeps Terraform from clobbering manual rotations.
resource "google_secret_manager_secret" "gmail_smtp_app_password" {
  secret_id = "aha_coms_sicu_${var.environment}_gmail_smtp_app_password"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gmail_smtp_app_password" {
  secret      = google_secret_manager_secret.gmail_smtp_app_password.id
  secret_data = var.gmail_smtp_app_password != "" ? var.gmail_smtp_app_password : "placeholder"

  lifecycle {
    ignore_changes = [secret_data]
  }
}

# Email SMTP App Password — backs the rich /send evaluation report
# (POST /api/v1/email/send), which migrated off SendGrid onto its own Gmail
# SMTP account, distinct from /send-plain's gmail_smtp_app_password. Value is
# seeded out-of-band via gcloud; ignore_changes keeps Terraform from clobbering
# manual rotations.
resource "google_secret_manager_secret" "email_smtp_app_password" {
  secret_id = "aha_coms_sicu_${var.environment}_email_smtp_app_password"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "email_smtp_app_password" {
  secret      = google_secret_manager_secret.email_smtp_app_password.id
  secret_data = var.email_smtp_app_password != "" ? var.email_smtp_app_password : "placeholder"

  lifecycle {
    ignore_changes = [secret_data]
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

resource "google_secret_manager_secret_iam_member" "deploy_sa_gmail_smtp_app_password" {
  secret_id = google_secret_manager_secret.gmail_smtp_app_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_gmail_smtp_app_password_viewer" {
  secret_id = google_secret_manager_secret.gmail_smtp_app_password.secret_id
  role      = "roles/secretmanager.viewer"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_gmail_smtp_app_password" {
  secret_id = google_secret_manager_secret.gmail_smtp_app_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "api_sa_email_smtp_app_password" {
  secret_id = google_secret_manager_secret.email_smtp_app_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_email_smtp_app_password" {
  secret_id = google_secret_manager_secret.email_smtp_app_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.deploy.email}"
  project   = var.project_id
}

resource "google_secret_manager_secret_iam_member" "deploy_sa_email_smtp_app_password_viewer" {
  secret_id = google_secret_manager_secret.email_smtp_app_password.secret_id
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

resource "google_secret_manager_secret_iam_member" "api_sa_gmail_dwd" {
  secret_id = google_secret_manager_secret.gmail_dwd_credentials.secret_id
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
  cloud_run_service_name          = var.cloud_run_service_name != "" ? var.cloud_run_service_name : "aha-coms-sicu-${var.environment}-api"
  scheduler_target_url            = var.cloud_run_url != "" ? var.cloud_run_url : google_cloud_run_v2_service.api.uri
  scheduler_service_account_email = try(google_service_account.scheduler[0].email, "")
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

      # Gmail API domain-wide-delegation transport for the rich /send path.
      # Inert until GMAIL_DWD_ENABLED is true; then /send goes through the Gmail
      # API impersonating GMAIL_DWD_SENDER instead of SMTP app-password auth.
      env {
        name  = "GMAIL_DWD_ENABLED"
        value = tostring(var.gmail_dwd_enabled)
      }

      env {
        name  = "GMAIL_DWD_SENDER"
        value = var.gmail_dwd_sender
      }

      env {
        name = "GMAIL_DWD_CREDENTIALS_JSON"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gmail_dwd_credentials.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "GCS_UPLOAD_BUCKET"
        value = google_storage_bucket.uploads.name
      }

      env {
        name  = "EMAIL_FROM_NAME"
        value = "AHAbot™"
      }

      env {
        name  = "EMAIL_FROM_EMAIL"
        value = var.email_from_email
      }

      env {
        name  = "EMAIL_ENABLED"
        value = tostring(var.email_enabled)
      }

      env {
        name  = "EMAIL_ALLOWED_DOMAINS"
        value = var.email_allowed_domains
      }

      # Gmail SMTP transport — gated independently of EMAIL_ENABLED.
      # Host/port fall back to the app's Settings defaults (smtp.gmail.com:587).
      env {
        name  = "GMAIL_SMTP_ENABLED"
        value = tostring(var.gmail_smtp_enabled)
      }

      env {
        name  = "GMAIL_SMTP_USER"
        value = var.gmail_smtp_user
      }

      env {
        name = "GMAIL_SMTP_APP_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gmail_smtp_app_password.secret_id
            version = "latest"
          }
        }
      }

      # Rich /send transport. EMAIL_SMTP_USER defaults to EMAIL_FROM_EMAIL in
      # the app; host/port fall back to smtp.gmail.com:587.
      env {
        name = "EMAIL_SMTP_APP_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.email_smtp_app_password.secret_id
            version = "latest"
          }
        }
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
        name  = "GSHEETS_MEETING_SPREADSHEET_ID_TH"
        value = var.gsheets_meeting_spreadsheet_id_th
      }

      env {
        name  = "CLOUD_RUN_URL"
        value = var.cloud_run_url
      }

      env {
        name  = "ALLOWED_SCHEDULER_EMAILS"
        value = local.scheduler_service_account_email
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
    google_secret_manager_secret_iam_member.api_sa_gmail_dwd,
    google_secret_manager_secret_version.gmail_dwd_credentials,
    google_secret_manager_secret_iam_member.api_sa_gmail_smtp_app_password,
    google_secret_manager_secret_iam_member.api_sa_email_smtp_app_password,
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
  count    = var.enable_scheduler ? 1 : 0
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${local.scheduler_service_account_email}"
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
  # prod reuses the develop-built image digest from the dev registry (promote
  # never rebuilds), so the prod registry is unused — created only where wanted.
  count = var.create_registry ? 1 : 0

  location      = var.region
  repository_id = "aha-coms-sicu-${var.environment}-registry"
  description   = "Docker container images for Store ICU"
  format        = "DOCKER"
  project       = var.project_id

  cleanup_policy_dry_run = false

  # Delete ONLY dangling untagged manifests, and only after a long buffer. Every
  # deploy/promote target is tagged (:<sha> + :latest), so tagged images — incl.
  # the digest prod pins from this registry — are never GC'd out from under a
  # running service. (A `tag_state = ANY` + 1-day rule previously deleted the
  # prod-pinned image while it was still in use, taking prod down.)
  # Keep the 20 most recent versions; delete everything else (tagged included).
  # ponytail: deliberate ceiling — a build pushes ~3 digests, so this protects
  # only ~6-7 recent builds. If prod goes more than that many dev builds without
  # a re-promote, its pinned digest can age out of the window and be deleted,
  # reprising the 2026-06-24 "image not found" outage. Raise keep_count or add an
  # age-based tagged rule if promotes ever lag dev builds.
  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"

    most_recent_versions {
      keep_count = 20
    }
  }

  cleanup_policies {
    id     = "delete-old"
    action = "DELETE"

    condition {
      tag_state = "ANY"
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
  count       = var.enable_scheduler ? 1 : 0
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
      service_account_email = local.scheduler_service_account_email
      audience              = local.scheduler_target_url
    }
  }

  retry_config {
    retry_count          = 3
    min_backoff_duration = "30s"
    max_backoff_duration = "300s"
  }
}
