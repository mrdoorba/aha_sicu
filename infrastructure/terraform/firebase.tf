# Firebase Hosting: Static frontend hosting site
# NOTE: Actual deployment via Firebase CLI (firebase deploy --only hosting), not Terraform

resource "google_firebase_hosting_site" "frontend" {
  provider = google-beta
  project  = var.firebase_project_id != "" ? var.firebase_project_id : var.project_id
  site_id  = "aha-sicu-${var.environment}"

  depends_on = [google_project_service.firebase_hosting_api]
}
