# Environment Module - Variables
# Each variable is passed from the root module per environment (dev/prod).

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
}

variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "cloud_sql_instance_name" {
  description = "Shared Cloud SQL instance name"
  type        = string
}

variable "cloud_sql_instance_connection_name" {
  description = "Shared Cloud SQL instance connection name"
  type        = string
}

variable "db_user" {
  description = "Database user name"
  type        = string
}

variable "db_password" {
  description = "Database password (from random_password)"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository in format 'owner/repo'"
  type        = string
}

variable "firebase_project_id" {
  description = "Firebase project ID (usually same as GCP project_id)"
  type        = string
}

variable "cloud_run_image" {
  description = "Docker image URI for Cloud Run"
  type        = string
}

variable "cloud_run_min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
}

variable "cloud_run_memory" {
  description = "Memory limit for Cloud Run container"
  type        = string
}

variable "cloud_run_cpu" {
  description = "CPU limit for Cloud Run container"
  type        = string
}

variable "cloud_run_service_name" {
  description = "Cloud Run service name override"
  type        = string
  default     = ""
}

variable "smtp_user" {
  description = "Gmail address for SMTP sending"
  type        = string
}

variable "smtp_from_name" {
  description = "Display name for sent emails"
  type        = string
}

variable "gsheets_vp_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for VP brand data"
  type        = string
}

variable "gsheets_meeting_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for 1st Meeting brand data"
  type        = string
}

variable "gsheets_eval_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for evaluated brand status (write-only)"
  type        = string
}

variable "cloud_run_url" {
  description = "Cloud Run service URL override for scheduler"
  type        = string
  default     = ""
}

variable "cors_origins" {
  description = "Allowed CORS origins for GCS upload bucket"
  type        = list(string)
}

variable "depends_on_apis" {
  description = "API enablement resources to depend on"
  type        = list(any)
  default     = []
}
