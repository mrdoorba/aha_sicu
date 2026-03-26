# Cloud SQL PostgreSQL: Shared instance across environments
# Per-environment databases are created by the environment module.

resource "google_sql_database_instance" "main" {
  name                = var.cloud_sql_instance_name
  database_version    = "POSTGRES_18"
  region              = var.region
  project             = var.project_id
  deletion_protection = true

  settings {
    tier              = var.cloud_sql_tier
    disk_size         = var.cloud_sql_disk_size
    disk_type         = "PD_SSD"
    availability_type = "ZONAL"
    edition           = "ENTERPRISE"

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_statement"
      value = "mod"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }

    ip_configuration {
      ipv4_enabled = true
      ssl_mode     = "ENCRYPTED_ONLY"

      dynamic "authorized_networks" {
        for_each = var.authorized_networks
        content {
          name  = authorized_networks.value.name
          value = authorized_networks.value.value
        }
      }
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }
  }

  depends_on = [google_project_service.sqladmin_api]
}

# Old shared DB user — removed from Terraform management without destroying.
# Per-environment users now created in modules/environment/main.tf.
# Clean up the old "aha_sicu" user manually after verifying per-env users work.
removed {
  from = google_sql_user.app
  lifecycle {
    destroy = false
  }
}

removed {
  from = random_password.db
  lifecycle {
    destroy = false
  }
}

# =============================================================================
# Scheduled Start/Stop — Cloud Scheduler → SQL Admin API
# =============================================================================

resource "google_service_account" "cloud_sql_scheduler" {
  account_id   = "aha-coms-sicu-sql-sched-sa"
  display_name = "Store ICU Cloud SQL Scheduler"
  description  = "Service account for Cloud Scheduler to start/stop Cloud SQL instance"
  project      = var.project_id
}

resource "google_project_iam_member" "cloud_sql_scheduler_admin" {
  project = var.project_id
  role    = "roles/cloudsql.admin"
  member  = "serviceAccount:${google_service_account.cloud_sql_scheduler.email}"
}

# START job — 07:45 WIB, weekdays only
resource "google_cloud_scheduler_job" "cloud_sql_start" {
  name        = "aha-coms-sicu-sql-start"
  description = "Start Cloud SQL instance at 07:45 WIB"
  schedule    = "45 7 * * 1-5"
  time_zone   = "Asia/Jakarta"
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

# STOP job — 19:00 WIB, weekdays only
resource "google_cloud_scheduler_job" "cloud_sql_stop" {
  name        = "aha-coms-sicu-sql-stop"
  description = "Stop Cloud SQL instance at 19:00 WIB"
  schedule    = "0 19 * * 1-5"
  time_zone   = "Asia/Jakarta"
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
