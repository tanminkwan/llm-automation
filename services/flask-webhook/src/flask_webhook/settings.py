"""WebhookSettings — 환경변수 기반 설정."""

from pydantic_settings import BaseSettings


class WebhookSettings(BaseSettings):
    """flask-webhook 서비스 설정."""

    webhook_host: str = "0.0.0.0"  # noqa: S104
    webhook_port: int = 8080
    webhook_secret: str = ""
    celery_broker_url: str = "redis://localhost:6379/0"
    dedup_ttl_seconds: int = 300
