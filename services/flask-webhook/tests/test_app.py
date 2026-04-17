"""T-10~T-14: Flask 앱 엔드포인트 테스트."""

from __future__ import annotations

import json

from flask.testing import FlaskClient

from flask_webhook.app import create_app
from flask_webhook.dedup import DeliveryCache
from flask_webhook.settings import WebhookSettings

from .conftest import TEST_SECRET, FakeCelery, make_push_payload, make_signature


def _make_client(
    celery: FakeCelery | None = None,
    cache: DeliveryCache | None = None,
) -> FlaskClient:
    settings = WebhookSettings(webhook_secret=TEST_SECRET)
    app = create_app(
        celery_app=celery or FakeCelery(),  # type: ignore[arg-type]
        settings=settings,
        cache=cache or DeliveryCache(),
    )
    app.config["TESTING"] = True
    return app.test_client()


class TestWebhookPush:
    """T-10~T-13: POST /webhook/push."""

    def test_success(self) -> None:
        """T-10: 정상 → 200 accepted."""
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

    def test_invalid_hmac(self) -> None:
        """T-11: HMAC 불일치 → 401."""
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
        """T-12: 중복 delivery → 200 duplicate."""
        cache = DeliveryCache()
        cache.mark("d-dup")
        client = _make_client(cache=cache)
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

    def test_skipped_no_matching_files(self) -> None:
        """T-13: 해당 없는 파일 → 200 skipped."""
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


class TestHealth:
    """T-14: 헬스체크."""

    def test_health(self) -> None:
        """T-14: GET /health → 200 ok."""
        client = _make_client()
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}
