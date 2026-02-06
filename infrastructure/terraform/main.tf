# Store ICU Infrastructure - Terraform Configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
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

# Service Account Key (for local development ONLY)
# WARNING: This key is stored in Terraform state in plaintext.
# For production, use Workload Identity or Secret Manager instead.
resource "google_service_account_key" "gsheets_sync_key" {
  service_account_id = google_service_account.gsheets_sync.name
}

# Output the service account email (share this with Google Sheet)
output "gsheets_service_account_email" {
  description = "Email of the service account - share this with your Google Sheet"
  value       = google_service_account.gsheets_sync.email
}

# Output the service account key (base64 encoded JSON)
# WARNING: Sensitive value stored in Terraform state. Use only for local dev.
output "gsheets_service_account_key" {
  description = "Service account key (base64 encoded) - decode and save to credentials file"
  value       = google_service_account_key.gsheets_sync_key.private_key
  sensitive   = true
}
