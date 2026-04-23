"""
Celery Configuration - DocuLens AI v4.0
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "doculens",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.worker.tasks.analyze",
        "app.worker.tasks.batch",
        "app.worker.tasks.ingest",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

if settings.celery_enabled:
    celery_app.conf.update(
        task_always_eager=False,
    )
else:
    celery_app.conf.update(
        task_always_eager=True,
    )