"""Application configuration using Pydantic BaseSettings."""

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # extra="ignore": tolerate leftover env keys (e.g. retired SENDGRID_* vars)
    # so a stale .env doesn't crash startup during transport migrations.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    log_level: str = "INFO"

    # Database (Cloud SQL PostgreSQL)
    # When DATABASE_URL is set (local dev), it takes precedence.
    # Otherwise, URL is constructed from individual components (Cloud Run / CI).
    database_url: str = ""
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""
    cloud_sql_instance: str = ""
    database_pool_min: int = 1
    database_pool_max: int = 5

    @property
    def effective_database_url(self) -> str:
        """Return the database URL, constructing from components if needed."""
        if self.database_url:
            return self.database_url
        if self.db_user and self.db_password and self.db_name and self.cloud_sql_instance:
            password = quote_plus(self.db_password)
            return f"postgresql://{self.db_user}:{password}@/{self.db_name}?host=/cloudsql/{self.cloud_sql_instance}"
        return ""

    # Firebase Admin SDK
    firebase_credentials_path: str | None = None

    # Cloud Run service URL (for OIDC audience validation)
    # Set in production; empty in local dev (disables audience check)
    cloud_run_url: str = ""

    # Allowed service account emails for OIDC scheduler auth (comma-separated)
    # When empty, any valid OIDC token with correct audience is accepted
    allowed_scheduler_emails: str = ""

    # CORS origins (comma-separated). Defaults cover local dev.
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list, stripping whitespace."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # GCS Upload Bucket (empty = local dev fallback)
    gcs_upload_bucket: str = ""

    # Upload guards (defensive OOM caps). Largest legit prod upload seen is ~9 MB
    # (order_export ZIP); these are generous headroom, tune down post-launch.
    upload_max_file_mb: int = 100
    upload_max_zip_uncompressed_mb: int = 200
    upload_max_zip_entries: int = 50

    # Email — rich /send evaluation report (POST /api/v1/email/send).
    # Sent over its OWN SMTP account, distinct from /send-plain's gmail_smtp_*.
    # email_smtp_user defaults to email_from_email when left blank.
    email_from_name: str = "AHAbot™"
    email_from_email: str = ""
    email_enabled: bool = False
    email_allowed_domains: str = ""
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_smtp_user: str = ""
    email_smtp_app_password: str = ""

    # Rich /send transport via Gmail API + domain-wide delegation. When enabled,
    # the rich /send path sends through the Gmail API impersonating
    # gmail_dwd_sender (its SA client ID must be authorized for scope gmail.send
    # in the Workspace Admin Console) instead of SMTP app-password auth.
    gmail_dwd_enabled: bool = False
    gmail_dwd_credentials_json: str = ""
    gmail_dwd_sender: str = ""

    # Gmail SMTP transport (used by /api/v1/email/send-plain)
    # Independent of email_enabled — that flag gates the rich /send path and
    # the dashboard's Send Email button. This flag gates only the
    # evaluation-detail Send Mail dialog's SMTP send.
    gmail_smtp_enabled: bool = False
    gmail_smtp_user: str = ""
    gmail_smtp_app_password: str = ""
    gmail_smtp_host: str = "smtp.gmail.com"
    gmail_smtp_port: int = 587

    # Google Sheets API - Credentials
    gsheets_credentials_path: str | None = None
    gsheets_credentials_json: str | None = None

    # VP Sheet - Indonesia (brand_vp_data, marketplace='ID')
    gsheets_vp_spreadsheet_id: str | None = None
    gsheets_vp_range: str = "Brands Data!A:Z"
    gsheets_vp_brand_column: str = "Brand"

    # VP Sheet - Thailand (brand_vp_data, marketplace='TH')
    gsheets_vp_spreadsheet_id_th: str | None = None
    gsheets_vp_range_th: str = "Brands Data!A:Z"
    gsheets_vp_brand_column_th: str = "Brand"

    # 1st Meeting Sheet - Indonesia (brand_meeting_data, marketplace='ID')
    gsheets_meeting_spreadsheet_id: str | None = None
    gsheets_meeting_range: str = "1st Meeting!A:N"
    gsheets_meeting_brand_column: str = "Brand"

    # 1st Meeting Sheet - Thailand (brand_meeting_data, marketplace='TH')
    gsheets_meeting_spreadsheet_id_th: str | None = None
    gsheets_meeting_range_th: str = "1st Meeting!A:N"
    gsheets_meeting_brand_column_th: str = "Brand"

    # Evaluation Status Sheet (write-only, one row per evaluated brand)
    gsheets_eval_spreadsheet_id: str | None = None
    gsheets_eval_tab: str = "SICU - bronze"


settings = Settings()
