# Workload Identity Federation: Keyless GitHub Actions → GCP authentication

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "aha-sicu-${var.environment}-github-pool"
  display_name              = "Aha SICU ${var.environment} GitHub Pool"
  description               = "Workload Identity Pool for GitHub Actions CI/CD"
  project                   = var.project_id

  depends_on = [google_project_service.iam_api]
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
  }

  attribute_condition = "assertion.repository == \"${var.github_repo}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Allow the deploy SA to be impersonated via the Workload Identity Pool
resource "google_service_account_iam_member" "deploy_wi_user" {
  service_account_id = google_service_account.deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repo}"
}
