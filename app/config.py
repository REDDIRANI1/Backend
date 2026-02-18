from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings forced to load from environment variables."""
    
    # We use Field(alias=...) to ensure Pydantic looks for the EXACT name Railway provides
    database_url: str = Field(
        default="postgresql://webhook_user:password@localhost:5432/webhook_db",
        validation_alias="DATABASE_URL"
    )
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL"
    )
    
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_RESULT_BACKEND"
    )

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    def __init__(self, **values):
        super().__init__(**values)
        # Force the postgresql:// prefix for SQLAlchemy compatibility
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        # Debug print (will show in Railway logs to confirm it's not localhost)
        # We hide the password for safety
        masked_url = self.database_url.split('@')[-1] if '@' in self.database_url else self.database_url
        print(f"--- DB CONFIG LOADED. TARGET: {masked_url} ---")

    class Config:
        case_sensitive = False
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
