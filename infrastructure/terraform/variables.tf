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
  description = "Cloud Run service name for IAM binding (e.g., aha-sicu-api)"
  type        = string
  default     = "aha-sicu-api"
}
