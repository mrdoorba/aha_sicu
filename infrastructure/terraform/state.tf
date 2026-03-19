# Terraform State Bucket — GCS backend for shared state and locking.
# This bucket must be created manually (via gcloud) BEFORE terraform init -migrate-state.
# The resource declaration here is for ongoing Terraform management after import.

resource "google_storage_bucket" "terraform_state" {
  name                        = "aha-coms-sicu-terraform-state"
  location                    = var.region
  project                     = var.project_id
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 5
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }
}
