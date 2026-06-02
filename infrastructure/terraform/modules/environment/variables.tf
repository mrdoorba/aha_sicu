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

variable "gsheets_vp_spreadsheet_id_th" {
  description = "Google Sheets spreadsheet ID for VP brand data (Thailand)"
  type        = string
  default     = ""
}

variable "cloud_run_url" {
  description = "Cloud Run service URL override for scheduler"
  type        = string
  default     = ""
}

variable "email_from_email" {
  description = "Verified sender email address for outgoing emails (SendGrid)"
  type        = string
}

variable "sendgrid_api_key" {
  description = "SendGrid API key for sending emails"
  type        = string
  sensitive   = true
}

variable "sendgrid_webhook_secret" {
  description = "SendGrid Event Webhook verification key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "email_enabled" {
  description = "Whether to enable the send-email feature"
  type        = bool
  default     = false
}

variable "email_allowed_domains" {
  description = "Comma-separated list of allowed email recipient domains"
  type        = string
  default     = ""
}

variable "gmail_smtp_enabled" {
  description = "Whether the Gmail SMTP send-plain path is enabled (independent of email_enabled)"
  type        = bool
  default     = false
}

variable "gmail_smtp_user" {
  description = "Gmail account used as the SMTP sender (also the From address)"
  type        = string
  default     = ""
}

variable "gmail_smtp_app_password" {
  description = "Gmail App Password for SMTP auth. Seeded out-of-band; ignore_changes preserves rotations."
  type        = string
  sensitive   = true
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

variable "wif_allowed_branch" {
  description = "Git branch allowed to authenticate via WIF (e.g., main, develop)"
  type        = string
  default     = "main"
}

variable "enable_scheduler" {
  description = "Whether to create the daily sync Cloud Scheduler resources for this environment"
  type        = bool
  default     = true
}
