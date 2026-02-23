# Cloud Scheduler: Daily automatic brand data sync
# Triggers POST /api/v1/sync at 08:00 WIB (01:00 UTC) daily — after Cloud SQL starts at 07:30
# Only created when cloud_run_url is set (prod) or Cloud Run v2 service exists

locals {
  # Use explicitly provided URL if set, otherwise use Cloud Run v2 service URI
  scheduler_target_url = var.cloud_run_url != "" ? var.cloud_run_url : google_cloud_run_v2_service.api.uri
}

resource "google_cloud_scheduler_job" "daily_sync" {
  name        = "aha-sicu-${var.environment}-daily-sync"
  description = "Daily brand data sync from Google Sheets"
  schedule    = "0 1 * * *"
  time_zone   = "UTC"
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

  depends_on = [google_project_service.scheduler_api]
}
