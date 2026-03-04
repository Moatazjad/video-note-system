from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "video_note_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.autodiscover_tasks(["app.tasks"])

import app.tasks.processing_tasks


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,

    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    worker_max_tasks_per_child=1000,

    result_expires=3600,
)

app = celery_app
