# Store ICU Infrastructure - Terraform Configuration

terraform {
  required_version = ">= 1.5"

  backend "gcs" {
    bucket = "aha-coms-sicu-terraform-state"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 7.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
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
# GCP API Enablement (shared)
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

resource "google_project_service" "sqladmin_api" {
  project            = var.project_id
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "sheets_api" {
  project            = var.project_id
  service            = "sheets.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "gmail_api" {
  project            = var.project_id
  service            = "gmail.googleapis.com"
  disable_on_destroy = false
}

# =============================================================================
# Environment Modules
# =============================================================================

module "dev" {
  source      = "./modules/environment"
  environment = "dev"
  project_id  = var.project_id
  region      = var.region

  cloud_sql_instance_name            = google_sql_database_instance.main.name
  cloud_sql_instance_connection_name = google_sql_database_instance.main.connection_name

  github_repo         = var.github_repo
  wif_allowed_branch  = "develop"
  firebase_project_id = var.firebase_project_id
  cloud_run_image     = var.cloud_run_image

  cloud_run_min_instances = var.cloud_run_min_instances
  cloud_run_max_instances = var.cloud_run_max_instances
  cloud_run_memory        = var.cloud_run_memory
  cloud_run_cpu           = var.cloud_run_cpu

  email_from_email        = var.dev_email_from_email
  email_enabled           = var.dev_email_enabled
  email_allowed_domains   = var.dev_email_allowed_domains
  sendgrid_api_key        = var.sendgrid_api_key
  sendgrid_webhook_secret = var.sendgrid_webhook_secret
  email_smtp_app_password = var.email_smtp_app_password
  gmail_smtp_user         = var.gmail_smtp_user
  gmail_smtp_app_password = var.gmail_smtp_app_password
  gmail_smtp_enabled      = var.dev_gmail_smtp_enabled
  gmail_dwd_enabled       = var.dev_gmail_dwd_enabled
  cloud_run_url           = var.dev_cloud_run_url

  gsheets_vp_spreadsheet_id      = var.gsheets_vp_spreadsheet_id
  gsheets_meeting_spreadsheet_id = var.gsheets_meeting_spreadsheet_id
  gsheets_eval_spreadsheet_id    = var.dev_gsheets_eval_spreadsheet_id
  gsheets_vp_spreadsheet_id_th   = var.gsheets_vp_spreadsheet_id_th
  enable_scheduler               = false

  cors_origins = [
    "https://aha-coms-sicu-dev.web.app",
    "http://localhost:5173"
  ]
}

module "prod" {
  source      = "./modules/environment"
  environment = "prod"
  project_id  = var.project_id
  region      = var.region

  cloud_sql_instance_name            = google_sql_database_instance.main.name
  cloud_sql_instance_connection_name = google_sql_database_instance.main.connection_name

  github_repo         = var.github_repo
  wif_allowed_branch  = "production"
  firebase_project_id = var.firebase_project_id
  cloud_run_image     = var.cloud_run_image

  cloud_run_min_instances = var.cloud_run_min_instances
  cloud_run_max_instances = var.cloud_run_max_instances
  cloud_run_memory        = var.cloud_run_memory
  cloud_run_cpu           = var.cloud_run_cpu

  email_from_email        = var.prod_email_from_email
  email_enabled           = var.prod_email_enabled
  email_allowed_domains   = var.prod_email_allowed_domains
  sendgrid_api_key        = var.sendgrid_api_key
  sendgrid_webhook_secret = var.sendgrid_webhook_secret
  email_smtp_app_password = var.email_smtp_app_password
  gmail_smtp_user         = var.gmail_smtp_user
  gmail_smtp_app_password = var.gmail_smtp_app_password
  gmail_smtp_enabled      = var.prod_gmail_smtp_enabled
  gmail_dwd_enabled       = var.prod_gmail_dwd_enabled
  cloud_run_url           = var.prod_cloud_run_url

  gsheets_vp_spreadsheet_id      = var.gsheets_vp_spreadsheet_id
  gsheets_meeting_spreadsheet_id = var.gsheets_meeting_spreadsheet_id
  gsheets_eval_spreadsheet_id    = var.prod_gsheets_eval_spreadsheet_id
  gsheets_vp_spreadsheet_id_th   = var.gsheets_vp_spreadsheet_id_th
  enable_scheduler               = true

  cors_origins = [
    "https://aha-coms-sicu-prod.web.app",
    "https://sicu.ahabot.ai"
  ]
}
