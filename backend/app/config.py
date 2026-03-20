"""Application configuration using Pydantic BaseSettings."""

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Store ICU API"
    debug: bool = False
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

    # Email / Brevo
    brevo_api_key: str = ""
    brevo_sender_name: str = "AHA Commerce"
    brevo_sender_email: str = ""
    email_enabled: bool = False
    email_allowed_domains: str = ""  # comma-separated: "ahacommerce.co.id,example.com"

    # Google Sheets API - Credentials
    gsheets_credentials_path: str | None = None
    gsheets_credentials_json: str | None = None

    # VP Sheet (brand_vp_data)
    gsheets_vp_spreadsheet_id: str | None = None
    gsheets_vp_range: str = "VP!A:Y"
    gsheets_vp_brand_column: str = "Nama Brand"

    # 1st Meeting Sheet (brand_meeting_data)
    gsheets_meeting_spreadsheet_id: str | None = None
    gsheets_meeting_range: str = "ZAP: 1st Meeting!A:D"
    gsheets_meeting_brand_column: str = "Brand"

    # Evaluation Status Sheet (write-only, one row per evaluated brand)
    gsheets_eval_spreadsheet_id: str | None = None
    gsheets_eval_tab: str = "SICU"


settings = Settings()
