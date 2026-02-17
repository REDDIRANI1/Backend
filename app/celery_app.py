from celery import Celery
from app.config import get_settings

settings = get_settings()

# Create Celery application using settings from environment
celery_app = Celery(
    "webhook_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    # These help with common deployment issues
    broker_connection_retry_on_startup=True
)
