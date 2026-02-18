# Store ICU Infrastructure - Variables

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "asia-southeast1"
}

variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string
  default     = "dev"
}

variable "cloud_run_url" {
  description = "Cloud Run service URL for the Store ICU API (e.g., https://aha-sicu-api-xxxx.a.run.app)"
  type        = string
  default     = ""

  validation {
    condition     = var.cloud_run_url == "" || can(regex("^https://", var.cloud_run_url))
    error_message = "cloud_run_url must be empty or start with https://"
  }
}

variable "cloud_run_service_name" {
  description = "Cloud Run v2 service name (e.g., aha-sicu-api)"
  type        = string
  default     = ""
}

# =============================================================================
# New Variables (Story 6.1)
# =============================================================================

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
  description = "Docker image URI for Cloud Run (e.g., asia-southeast1-docker.pkg.dev/PROJECT/aha-sicu-registry/aha-sicu-api:latest)"
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
