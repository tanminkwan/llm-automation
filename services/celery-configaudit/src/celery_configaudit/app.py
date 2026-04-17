"""Celery app 인스턴스."""

from celery import Celery  # type: ignore[import-untyped]

from .settings import CeleryConfigAuditSettings

settings = CeleryConfigAuditSettings()

celery_app: Celery = Celery(
    "configaudit",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
