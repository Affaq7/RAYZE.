from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase
    supabase_db_url: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # Resend
    resend_api_key: str
    resend_from_email: str
    team_notification_email: str

    # App
    environment: str = "development"
    allowed_origins: str = ""

    # Storage
    portfolio_bucket: str = "portfolio-images"
    resume_bucket: str = "resumes"

    # Uploads
    max_image_size_mb: int = 5
    max_resume_size_mb: int = 5

    # Google Sheets sync (optional, future)
    google_service_account_json: str = ""
    google_sheet_id: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
