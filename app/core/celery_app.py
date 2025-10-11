"""
Celery application configuration
"""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "localizer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.translation",
        "app.tasks.speech",
        "app.tasks.evaluation",
        "app.tasks.retraining"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000,  # 50 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routes
celery_app.conf.task_routes = {
    "app.tasks.translation.*": {"queue": "translation"},
    "app.tasks.speech.*": {"queue": "speech"},
    "app.tasks.evaluation.*": {"queue": "evaluation"},
    "app.tasks.retraining.*": {"queue": "retraining"},
}

