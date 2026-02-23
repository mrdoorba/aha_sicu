# Cloud SQL PostgreSQL: Single instance with dual databases
# One db-f1-micro instance hosts both aha_sicu_dev and aha_sicu_prod databases.

resource "google_sql_database_instance" "main" {
  name                = var.cloud_sql_instance_name
  database_version    = "POSTGRES_18"
  region              = var.region
  project             = var.project_id
  deletion_protection = var.environment == "prod" ? true : false

  settings {
    tier              = var.cloud_sql_tier
    disk_size         = var.cloud_sql_disk_size
    disk_type         = "PD_SSD"
    availability_type = "ZONAL"
    edition           = "ENTERPRISE"

    ip_configuration {
      ipv4_enabled = true
      ssl_mode     = "ENCRYPTED_ONLY"
    }

    backup_configuration {
      enabled = false
    }
  }

  depends_on = [google_project_service.sqladmin_api]
}

# Databases — both on the same instance
resource "google_sql_database" "dev" {
  name     = "aha_sicu_dev"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

resource "google_sql_database" "prod" {
  name     = "aha_sicu_prod"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

# Database user — password managed via Secret Manager, not Terraform
resource "google_sql_user" "app" {
  name     = var.db_user
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

# =============================================================================
# Scheduled Start/Stop — Cloud Scheduler → SQL Admin API
# =============================================================================

# Dedicated SA for Cloud Scheduler to call SQL Admin API
resource "google_service_account" "cloud_sql_scheduler" {
  account_id   = "aha-sicu-sql-scheduler-sa"
  display_name = "Store ICU Cloud SQL Scheduler"
  description  = "Service account for Cloud Scheduler to start/stop Cloud SQL instance"
  project      = var.project_id
}

resource "google_project_iam_member" "cloud_sql_scheduler_admin" {
  project = var.project_id
  role    = "roles/cloudsql.admin"
  member  = "serviceAccount:${google_service_account.cloud_sql_scheduler.email}"
}

# START job — 07:30 WIB (30 0 * * * UTC)
resource "google_cloud_scheduler_job" "cloud_sql_start" {
  name        = "aha-sicu-cloud-sql-start"
  description = "Start Cloud SQL instance at 07:30 WIB"
  schedule    = "30 0 * * *"
  time_zone   = "UTC"
  project     = var.project_id
  region      = var.region

  http_target {
    http_method = "PATCH"
    uri         = "https://sqladmin.googleapis.com/v1/projects/${var.project_id}/instances/${google_sql_database_instance.main.name}"
    body        = base64encode(jsonencode({ settings = { activationPolicy = "ALWAYS" } }))

    headers = {
      "Content-Type" = "application/json"
    }

    oauth_token {
      service_account_email = google_service_account.cloud_sql_scheduler.email
    }
  }

  depends_on = [google_project_service.scheduler_api]
}

# STOP job — 19:00 WIB (0 12 * * * UTC)
resource "google_cloud_scheduler_job" "cloud_sql_stop" {
  name        = "aha-sicu-cloud-sql-stop"
  description = "Stop Cloud SQL instance at 19:00 WIB"
  schedule    = "0 12 * * *"
  time_zone   = "UTC"
  project     = var.project_id
  region      = var.region

  http_target {
    http_method = "PATCH"
    uri         = "https://sqladmin.googleapis.com/v1/projects/${var.project_id}/instances/${google_sql_database_instance.main.name}"
    body        = base64encode(jsonencode({ settings = { activationPolicy = "NEVER" } }))

    headers = {
      "Content-Type" = "application/json"
    }

    oauth_token {
      service_account_email = google_service_account.cloud_sql_scheduler.email
    }
  }

  depends_on = [google_project_service.scheduler_api]
}
