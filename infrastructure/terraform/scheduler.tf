# Cloud Scheduler: Daily automatic brand data sync
# Triggers POST /api/v1/sync at 06:00 WIB (Asia/Jakarta) daily

# Enable Cloud Scheduler API
resource "google_project_service" "scheduler_api" {
  project            = var.project_id
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

resource "google_cloud_scheduler_job" "daily_sync" {
  name        = "aha_sicu_daily_sync"
  description = "Daily brand data sync from Google Sheets"
  schedule    = "0 6 * * *"
  time_zone   = "Asia/Jakarta"
  project     = var.project_id
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "${var.cloud_run_url}/api/v1/sync"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = var.cloud_run_url
    }
  }

  retry_config {
    retry_count          = 3
    min_backoff_duration = "30s"
    max_backoff_duration = "300s"
  }

  depends_on = [google_project_service.scheduler_api]
}
