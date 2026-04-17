"""공유 fixture — FakeCelery, 샘플 페이로드."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Any

import pytest

from flask_webhook.dedup import DeliveryCache
from flask_webhook.settings import WebhookSettings

TEST_SECRET = "test-secret-key"


@dataclass
class FakeAsyncResult:
    """Celery send_task 반환 모사."""

    id: str = "fake-task-id-001"


@dataclass
class FakeCelery:
    """Celery send_task 기록용 fake."""

    sent: list[dict[str, Any]] = field(default_factory=list)

    def send_task(
        self, name: str, args: Any = None, kwargs: Any = None, queue: str = ""
    ) -> FakeAsyncResult:
        self.sent.append({"name": name, "kwargs": kwargs, "queue": queue})
        return FakeAsyncResult()


def make_signature(payload: bytes, secret: str = TEST_SECRET) -> str:
    """테스트용 HMAC-SHA256 서명 생성."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def make_push_payload(
    files: list[str] | None = None,
    repo_name: str = "owner/repo",
    after: str = "abc12345deadbeef",
) -> dict[str, Any]:
    """Gitea push event 페이로드 생성."""
    _files = files or ["src/Main.java"]
    return {
        "ref": "refs/heads/main",
        "after": after,
        "repository": {"full_name": repo_name, "clone_url": f"http://gitea:3000/{repo_name}.git"},
        "commits": [
            {
                "id": after,
                "message": "test commit",
                "added": _files,
                "removed": [],
                "modified": [],
            }
        ],
    }


@pytest.fixture()
def settings() -> WebhookSettings:
    return WebhookSettings(webhook_secret=TEST_SECRET)


@pytest.fixture()
def fake_celery() -> FakeCelery:
    return FakeCelery()


@pytest.fixture()
def cache() -> DeliveryCache:
    return DeliveryCache(ttl_seconds=300)
