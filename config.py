"""
Application configuration using environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    # If DATABASE_URL is set (e.g., PostgreSQL), use it; otherwise default to SQLite for local development
    # PostgreSQL format: postgresql://user:password@host:port/database
    # SQLite format: sqlite:///./gebeyaalert.db
    DATABASE_URL: Optional[str] = None
    
    # JWT
    # Defaults to a development key - MUST be changed in production!
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: Optional[str] = None  # Frontend URL for CORS (e.g., "http://localhost:3000")
    PORT: int = 8080  # Server port (can be overridden by PORT env var for deployment)
    
    # SMS Configuration
    SMS_PROVIDER: str = "console"  # Options: "console" (demo) or "twilio" (production)
    SMS_ENABLED: bool = False  # Set to True to enable SMS sending (for Twilio)
    
    # Twilio SMS (only required if SMS_PROVIDER=twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
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
        Get the appropriate database URL based on environment variables.
        - If DATABASE_URL is set (e.g., PostgreSQL), use it
        - Otherwise, default to SQLite for local development
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Default to SQLite for local development
        return "sqlite:///./gebeyaalert.db"


settings = Settings()


