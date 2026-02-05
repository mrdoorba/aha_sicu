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

    # Google Sheets API
    gsheets_credentials_path: str | None = None
    gsheets_spreadsheet_id: str | None = None
    gsheets_range: str = "Sheet1!A:Z"


settings = Settings()
