# Store ICU Infrastructure - Variables (shared across environments)

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "asia-southeast2"
}

variable "github_repo" {
  description = "GitHub repository in format 'owner/repo' for Workload Identity Federation"
  type        = string
}

variable "firebase_project_id" {
  description = "Firebase project ID (usually same as GCP project_id)"
  type        = string
  default     = ""
}

variable "cloud_run_image" {
  description = "Docker image URI for Cloud Run initial deployment"
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "cloud_run_min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 2
}

variable "cloud_run_memory" {
  description = "Memory limit for Cloud Run container"
  type        = string
  default     = "1Gi"
}

variable "cloud_run_cpu" {
  description = "CPU limit for Cloud Run container"
  type        = string
  default     = "1"
}

variable "gsheets_vp_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for VP brand data"
  type        = string
  default     = ""
}

variable "gsheets_meeting_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for 1st Meeting brand data"
  type        = string
  default     = ""
}

# =============================================================================
# Email / SMTP Variables
# =============================================================================

variable "smtp_user" {
  description = "Gmail address for SMTP sending"
  type        = string
  default     = ""
}

variable "smtp_from_name" {
  description = "Display name for sent emails"
  type        = string
  default     = "AHA Commerce"
}

# =============================================================================
# Cloud SQL Variables (shared instance)
# =============================================================================

variable "cloud_sql_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-f1-micro"
}

variable "cloud_sql_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 10
}

variable "cloud_sql_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "aha-sicu-db"
}

variable "db_user" {
  description = "Cloud SQL database user"
  type        = string
  default     = "aha_sicu"
}
