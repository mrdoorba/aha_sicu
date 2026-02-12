# Store ICU Infrastructure - Terraform Configuration

terraform {
  required_version = ">= 1.0"

  # Local backend for initial bootstrap. Migrate to GCS when team collaboration needed:
  # backend "gcs" { bucket = "aha-sicu-terraform-state" prefix = "terraform/state" }
  backend "local" {}

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 7.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# =============================================================================
# GCP API Enablement
# =============================================================================

resource "google_project_service" "run_api" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry_api" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secret_manager_api" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam_api" {
  project            = var.project_id
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firebase_api" {
  project            = var.project_id
  service            = "firebase.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firebase_hosting_api" {
  project            = var.project_id
  service            = "firebasehosting.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "scheduler_api" {
  project            = var.project_id
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

# =============================================================================
# Google Sheets API & Service Account (Epic 2 - Brand Data Availability)
# =============================================================================

# Enable Google Sheets API
resource "google_project_service" "sheets_api" {
  project = var.project_id
  service = "sheets.googleapis.com"

  disable_on_destroy = false
}

# Service Account for Google Sheets access
# Naming follows architecture convention: aha-sicu-{purpose}-sa
resource "google_service_account" "gsheets_sync" {
  account_id   = "aha-sicu-sheets-sa"
  display_name = "Store ICU Google Sheets Sync"
  description  = "Service account for syncing brand data from Google Sheets"
  project      = var.project_id
}

# NOTE: SA key generation removed during code review — use Secret Manager instead.
# Inject gsheets credentials via: gcloud secrets versions add aha_sicu_gsheets_credentials --data-file=path/to/key.json

# Output the service account email (share this with Google Sheet)
output "gsheets_service_account_email" {
  description = "Email of the service account - share this with your Google Sheet"
  value       = google_service_account.gsheets_sync.email
}
