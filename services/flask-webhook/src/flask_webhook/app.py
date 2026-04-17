"""Flask 앱 팩토리 — webhook 수신 + HMAC 검증 + Celery 발행."""

from __future__ import annotations

from typing import Any

from celery import Celery  # type: ignore[import-untyped]
from flask import Flask, Response, jsonify, request

from .dedup import DeliveryCache
from .hmac_verify import verify_signature
from .models import WebhookPayload
from .router import classify_files, dispatch
from .settings import WebhookSettings


def create_app(
    *,
    celery_app: Celery | None = None,
    settings: WebhookSettings | None = None,
    cache: DeliveryCache | None = None,
) -> Flask:
    """팩토리 — 테스트 시 celery_app / cache 주입 (DIP)."""
    _settings = settings or WebhookSettings()
    _celery: Celery = celery_app or Celery(broker=_settings.celery_broker_url)
    _cache = cache or DeliveryCache(ttl_seconds=_settings.dedup_ttl_seconds)

    app = Flask(__name__)

    @app.post("/webhook/push")
    def webhook_push() -> tuple[Response, int]:
        # 1. HMAC 검증
        signature = request.headers.get("X-Gitea-Signature", "")
        if not verify_signature(request.data, signature, _settings.webhook_secret):
            return jsonify({"error": "invalid signature"}), 401

        # 2. 멱등키 확인
        delivery_id = request.headers.get("X-Gitea-Delivery", "")
        if delivery_id and _cache.is_duplicate(delivery_id):
            return jsonify({"status": "duplicate"}), 200

        # 3. 페이로드 파싱
        data: dict[str, Any] = request.get_json(silent=True) or {}
        payload = WebhookPayload(**data)
        changed = payload.all_changed_files()

        # 4. work_type 판별
        work_type = classify_files(changed)
        if work_type is None:
            return jsonify({"status": "skipped", "reason": "no matching files"}), 200

        # 5. Celery 발행
        work_id = f"{payload.repo_full_name}:{payload.after[:8]}"
        task_id = dispatch(
            _celery,
            work_type,
            work_id=work_id,
            repo_url=payload.repo_full_name,
            clone_url=payload.clone_url,
            ref=payload.ref,
            changed_files=changed,
        )

        # 6. 멱등키 기록
        if delivery_id:
            _cache.mark(delivery_id)

        return jsonify(
            {"status": "accepted", "task_id": task_id, "work_type": work_type.value}
        ), 200

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


if __name__ == "__main__":  # pragma: no cover
    _settings = WebhookSettings()
    _app = create_app(settings=_settings)
    _app.run(host=_settings.webhook_host, port=_settings.webhook_port)
