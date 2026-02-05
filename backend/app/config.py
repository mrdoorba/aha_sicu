"""Application configuration using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Store ICU API"
    debug: bool = False

    # Database (Neon PostgreSQL)
    database_url: str = ""
    database_pool_min: int = 5
    database_pool_max: int = 20

    # Firebase Admin SDK
    firebase_credentials_path: str | None = None
    firebase_credentials_json: str | None = None

    # Google Sheets API - Credentials
    gsheets_credentials_path: str | None = None

    # VP Sheet (brand_vp_data)
    gsheets_vp_spreadsheet_id: str | None = None
    gsheets_vp_range: str = "VP!A:Y"
    gsheets_vp_brand_column: str = "Nama Brand"

    # 1st Meeting Sheet (brand_meeting_data)
    gsheets_meeting_spreadsheet_id: str | None = None
    gsheets_meeting_range: str = "ZAP: 1st Meeting!A:D"
    gsheets_meeting_brand_column: str = "Brand"


settings = Settings()
