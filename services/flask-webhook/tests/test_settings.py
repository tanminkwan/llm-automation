"""T-18~T-19: WebhookSettings 테스트."""

import pytest

from flask_webhook.settings import WebhookSettings


class TestWebhookSettings:
    """T-18: env 주입, T-19: 기본값."""

    def test_env_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-18: 환경변수로 전체 값 주입."""
        monkeypatch.setenv("WEBHOOK_HOST", "127.0.0.1")
        monkeypatch.setenv("WEBHOOK_PORT", "9999")
        monkeypatch.setenv("WEBHOOK_SECRET", "my-secret")
        monkeypatch.setenv("CELERY_BROKER_URL", "redis://remote:6379/5")
        monkeypatch.setenv("DEDUP_TTL_SECONDS", "600")
        s = WebhookSettings()
        assert s.webhook_host == "127.0.0.1"
        assert s.webhook_port == 9999
        assert s.webhook_secret == "my-secret"
        assert s.celery_broker_url == "redis://remote:6379/5"
        assert s.dedup_ttl_seconds == 600

    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-19: 기본값 로딩."""
        for key in [
            "WEBHOOK_HOST",
            "WEBHOOK_PORT",
            "WEBHOOK_SECRET",
            "CELERY_BROKER_URL",
            "DEDUP_TTL_SECONDS",
        ]:
            monkeypatch.delenv(key, raising=False)
        s = WebhookSettings()
        assert s.webhook_host == "0.0.0.0"  # noqa: S104
        assert s.webhook_port == 8080
        assert s.webhook_secret == ""
        assert s.celery_broker_url == "redis://localhost:6379/0"
        assert s.dedup_ttl_seconds == 300
