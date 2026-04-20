"""Flask 앱 엔드포인트 테스트 — TriggerSource/Dispatcher DI 경로."""

from __future__ import annotations

import json
from typing import Any

from flask.testing import FlaskClient
from trigger_core import DeliveryCache

from flask_webhook.app import create_app
from flask_webhook.settings import WebhookSettings

from .conftest import TEST_SECRET, FakeCelery, make_push_payload, make_signature


def _make_client(
    celery: FakeCelery | None = None,
    cache: DeliveryCache | None = None,
    dispatcher: Any = None,
) -> FlaskClient:
    settings = WebhookSettings(webhook_secret=TEST_SECRET)
    app = create_app(
        celery_app=celery or FakeCelery(),  # type: ignore[arg-type]
        dispatcher=dispatcher,
        settings=settings,
        cache=cache or DeliveryCache(),
    )
    app.config["TESTING"] = True
    return app.test_client()


class TestWebhookPush:
    """POST /webhook/push."""

    def test_success(self) -> None:
        """정상 Java push → 200 accepted + Celery enqueue 1회."""
        celery = FakeCelery()
        client = _make_client(celery=celery)
        payload = make_push_payload(files=["src/Main.java"])
        body = json.dumps(payload).encode()
        sig = make_signature(body)

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": sig, "X-Gitea-Delivery": "d-001"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "accepted"
        assert data["work_type"] == "comment"
        assert len(celery.sent) == 1
        assert celery.sent[0]["name"] == "comment.process"
        assert celery.sent[0]["queue"] == "comment_queue"
        kwargs = celery.sent[0]["kwargs"]
        assert kwargs["work_id"] == "owner/repo:abc12345"
        assert kwargs["changed_files"] == ["src/Main.java"]

    def test_configaudit_priority(self) -> None:
        """Java + http.m 혼합 → configaudit 큐로 라우팅."""
        celery = FakeCelery()
        client = _make_client(celery=celery)
        payload = make_push_payload(files=["src/Main.java", "conf/http.m"])
        body = json.dumps(payload).encode()
        sig = make_signature(body)

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": sig},
        )
        assert resp.status_code == 200
        assert resp.get_json()["work_type"] == "configaudit"
        assert celery.sent[0]["queue"] == "configaudit_queue"

    def test_invalid_hmac(self) -> None:
        """HMAC 불일치 → 401."""
        client = _make_client()
        payload = make_push_payload()
        body = json.dumps(payload).encode()

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": "bad-sig"},
        )
        assert resp.status_code == 401

    def test_duplicate_delivery(self) -> None:
        """이미 마크된 delivery_id → 200 duplicate + enqueue 없음."""
        celery = FakeCelery()
        cache = DeliveryCache()
        cache.mark("d-dup")
        client = _make_client(celery=celery, cache=cache)
        payload = make_push_payload()
        body = json.dumps(payload).encode()
        sig = make_signature(body)

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": sig, "X-Gitea-Delivery": "d-dup"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "duplicate"
        assert celery.sent == []

    def test_skipped_no_matching_files(self) -> None:
        """매칭 파일 없음 → 200 skipped."""
        client = _make_client()
        payload = make_push_payload(files=["README.md"])
        body = json.dumps(payload).encode()
        sig = make_signature(body)

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": sig},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "skipped"

    def test_invalid_payload_schema(self) -> None:
        """서명은 유효하지만 페이로드 스키마 불일치 → 400."""
        client = _make_client()
        body = b'{"not_expected": true}'
        sig = make_signature(body)

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": sig},
        )
        assert resp.status_code == 400

    def test_dispatcher_override(self) -> None:
        """``dispatcher`` 직접 주입 시 Celery 경로 미사용."""
        calls: list[Any] = []

        class _RecDispatcher:
            def dispatch(self, event: Any) -> str:
                calls.append(event)
                return "custom-task"

        client = _make_client(dispatcher=_RecDispatcher())
        payload = make_push_payload()
        body = json.dumps(payload).encode()
        sig = make_signature(body)

        resp = client.post(
            "/webhook/push",
            data=body,
            content_type="application/json",
            headers={"X-Gitea-Signature": sig},
        )
        assert resp.status_code == 200
        assert resp.get_json()["task_id"] == "custom-task"
        assert len(calls) == 1


class TestHealth:
    """헬스체크."""

    def test_health(self) -> None:
        client = _make_client()
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}
