# Cloud SQL PostgreSQL: Shared instance across environments
# Per-environment databases are created by the environment module.

resource "google_sql_database_instance" "main" {
  name                = var.cloud_sql_instance_name
  database_version    = "POSTGRES_18"
  region              = var.region
  project             = var.project_id
  deletion_protection = true

  settings {
    activation_policy = "ALWAYS"
    tier              = var.cloud_sql_tier
    disk_size         = var.cloud_sql_disk_size
    disk_type         = "PD_SSD"
    availability_type = "ZONAL"
    edition           = "ENTERPRISE"

    # Cloud SQL maintenance windows use UTC. Saturday 18:00 UTC = Sunday 01:00 WIB.
    maintenance_window {
      day          = 6
      hour         = 18
      update_track = "stable"
    }

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
