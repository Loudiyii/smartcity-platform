"""
Configuration management with Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from supabase import create_client, Client


class Settings(BaseSettings):
    """Application settings."""

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # External APIs
    WEATHERAPI_KEY: str = ""
    AQICN_API_TOKEN: str = ""

    # IDFM APIs (optional for Phase 1)
    IDFM_API_KEY: str = ""
    IDFM_BASE_URL: str = "https://prim.iledefrance-mobilites.fr/marketplace"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Application
    APP_NAME: str = "Smart City Platform"
    DEBUG: bool = True

    # Environment
    ENVIRONMENT: str = "development"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # SMTP Configuration (Phase 2)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_RECIPIENTS: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_supabase_client() -> Client:
    """
    Get Supabase client instance.

    Returns:
        Supabase client configured with URL and key from settings
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
