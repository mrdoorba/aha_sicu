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
  default     = "512Mi"
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

variable "dev_gsheets_eval_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for evaluated brand status (dev)"
  type        = string
  default     = ""
}

variable "prod_gsheets_eval_spreadsheet_id" {
  description = "Google Sheets spreadsheet ID for evaluated brand status (prod)"
  type        = string
  default     = ""
}

variable "gsheets_vp_spreadsheet_id_th" {
  description = "Google Sheets spreadsheet ID for VP brand data (Thailand)"
  type        = string
  default     = ""
}

# =============================================================================
# Email Variables
# =============================================================================

variable "dev_email_from_email" {
  description = "From address for the rich /send path in dev. Over Gmail SMTP this must equal the authenticated SMTP account (email_smtp_user defaults to it when blank); under Gmail DWD it is superseded by gmail_dwd_sender."
  type        = string
}

variable "prod_email_from_email" {
  description = "From address for the rich /send path in prod."
  type        = string
}

variable "dev_email_enabled" {
  description = "Whether to enable the send-email feature in dev"
  type        = bool
  default     = false
}

variable "prod_email_enabled" {
  description = "Whether to enable the send-email feature in prod"
  type        = bool
  default     = false
}

variable "dev_email_allowed_domains" {
  description = "Comma-separated allowed email recipient domains for dev"
  type        = string
  default     = ""
}

variable "prod_email_allowed_domains" {
  description = "Comma-separated allowed email recipient domains for prod"
  type        = string
  default     = ""
}

# Gmail SMTP (evaluation "Send Mail" dialog — POST /api/v1/email/send-plain).
# User + app password are shared across environments, mirroring sendgrid_api_key.
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

variable "dev_gmail_smtp_enabled" {
  description = "Whether the Gmail SMTP send-plain path is enabled in dev"
  type        = bool
  default     = false
}

variable "prod_gmail_smtp_enabled" {
  description = "Whether the Gmail SMTP send-plain path is enabled in prod"
  type        = bool
  default     = false
}

variable "dev_gmail_dwd_enabled" {
  description = "Whether the rich /send path uses Gmail API + domain-wide delegation in dev"
  type        = bool
  default     = false
}

variable "prod_gmail_dwd_enabled" {
  description = "Whether the rich /send path uses Gmail API + domain-wide delegation in prod"
  type        = bool
  default     = false
}

# =============================================================================
# Cloud Run URL (per-environment, for OIDC audience validation)
# =============================================================================

variable "dev_cloud_run_url" {
  description = "Cloud Run service URL for dev (set after first deploy)"
  type        = string
  default     = ""
}

variable "prod_cloud_run_url" {
  description = "Cloud Run service URL for prod (set after first deploy)"
  type        = string
  default     = ""
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

variable "authorized_networks" {
  description = "List of authorized networks for Cloud SQL public IP access. Empty = no public access."
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

