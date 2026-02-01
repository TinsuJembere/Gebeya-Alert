"""
Application configuration using environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    # Defaults to SQLite for development, use PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./gebeyaalert.db"
    
    # JWT
    # Defaults to a development key - MUST be changed in production!
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Optional: PostgreSQL URL for production (overrides DATABASE_URL if set)
    DATABASE_URL_PROD: Optional[str] = None
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: Optional[str] = None  # Frontend URL for CORS (e.g., "http://localhost:3000")
    PORT: int = 8080  # Server port (can be overridden by PORT env var for deployment)
    
    # Twilio SMS
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    SMS_ENABLED: bool = False  # Set to True to enable SMS sending
    
    # Celery (optional, defaults to Redis)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    
    def get_database_url(self) -> str:
        """
        Get the appropriate database URL based on environment.
        - Development: Uses SQLite (default)
        - Production: Uses DATABASE_URL_PROD if set, otherwise DATABASE_URL
        """
        if self.ENVIRONMENT == "production" and self.DATABASE_URL_PROD:
            return self.DATABASE_URL_PROD
        return self.DATABASE_URL


settings = Settings()


