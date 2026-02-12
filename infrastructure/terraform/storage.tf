# GCS: Upload bucket for temporary file storage (parsed data files)

resource "google_storage_bucket" "uploads" {
  name                        = "${var.project_id}-aha-sicu-uploads"
  location                    = var.region
  project                     = var.project_id
  uniform_bucket_level_access = true
  force_destroy               = var.environment == "dev" ? true : false

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }
}

# IAM: Cloud Run SA gets objectAdmin on this bucket only (not project-wide)
resource "google_storage_bucket_iam_member" "api_sa_uploads" {
  bucket = google_storage_bucket.uploads.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}
