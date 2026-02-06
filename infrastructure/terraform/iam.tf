# IAM: Scheduler service account with least-privilege Cloud Run invoker role

resource "google_service_account" "scheduler" {
  account_id   = "aha-sicu-scheduler-sa"
  display_name = "Store ICU Scheduler Service Account"
  description  = "Service account for Cloud Scheduler to invoke Cloud Run sync endpoint"
  project      = var.project_id
}

resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = var.cloud_run_service_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
  project  = var.project_id
}
