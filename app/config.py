from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - Default to localhost for development
    database_url: str = "postgresql://webhook_user:password@localhost:5432/webhook_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    def __init__(self, **values):
        super().__init__(**values)
        # Fix for Railway/Heroku which often provides 'postgres://' 
        # but SQLAlchemy requires 'postgresql://'
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Map environment variables like DATABASE_URL to settings.database_url
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
