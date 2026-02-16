# Artifact Registry: Docker repository for container images

resource "google_artifact_registry_repository" "registry" {
  location      = var.region
  repository_id = "aha-sicu-${var.environment}-registry"
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

  depends_on = [google_project_service.artifact_registry_api]
}
