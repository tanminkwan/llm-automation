"""Flask 앱 팩토리 — HTTP 어댑터.

핵심 로직(서명 검증·페이로드 파싱·work_type 판별·큐 발행) 은 ``trigger-core`` 에 위임한다.
Flask 라우트는 HTTP ↔ TriggerEvent 번역만 담당한다.
"""

from __future__ import annotations

from typing import Any

from celery import Celery  # type: ignore[import-untyped]
from flask import Flask, Response, jsonify, request
from trigger_core import (
    CeleryTriggerDispatcher,
    DeliveryCache,
    InvalidPayloadError,
    InvalidSignatureError,
    TriggerDispatcher,
    TriggerSource,
    UnsupportedWorkTypeError,
    WebhookTriggerSource,
)

from .settings import WebhookSettings


def create_app(
    *,
    trigger_source: TriggerSource | None = None,
    dispatcher: TriggerDispatcher | None = None,
    cache: DeliveryCache | None = None,
    settings: WebhookSettings | None = None,
    celery_app: Celery | None = None,
) -> Flask:
    """Flask 팩토리 — 모든 협력자는 Protocol DI.

    편의: ``trigger_source`` 나 ``dispatcher`` 를 생략하면 ``settings`` 기반으로 기본 구현체
    (``WebhookTriggerSource`` + ``CeleryTriggerDispatcher``) 를 자동 구성한다. 테스트는
    ``celery_app`` 에 ``FakeCelery`` 를 주입하거나 ``dispatcher`` 를 직접 주입한다.
    """
    _settings = settings or WebhookSettings()
    _source: TriggerSource = trigger_source or WebhookTriggerSource(secret=_settings.webhook_secret)
    if dispatcher is None:
        _celery = celery_app or Celery(broker=_settings.celery_broker_url)
        _dispatcher: TriggerDispatcher = CeleryTriggerDispatcher(_celery)
    else:
        _dispatcher = dispatcher
    _cache = cache or DeliveryCache(ttl_seconds=_settings.dedup_ttl_seconds)

    app = Flask(__name__)

    @app.post("/webhook/push")
    def webhook_push() -> tuple[Response, int]:
        # 1. 파싱·검증 (서명 → 페이로드 → work_type) 을 TriggerSource 에 일괄 위임
        try:
            event = _source.parse(request.data, dict(request.headers))
        except InvalidSignatureError:
            return jsonify({"error": "invalid signature"}), 401
        except UnsupportedWorkTypeError:
            return jsonify({"status": "skipped", "reason": "no matching files"}), 200
        except InvalidPayloadError:
            return jsonify({"error": "invalid payload"}), 400

        # 2. 멱등키 (파싱 성공 후에만 — HMAC 우회 방지)
        delivery_id = str(event.meta.get("delivery_id", ""))
        if delivery_id and _cache.is_duplicate(delivery_id):
            return jsonify({"status": "duplicate"}), 200

        # 3. 큐 발행
        task_id = _dispatcher.dispatch(event)
        if delivery_id:
            _cache.mark(delivery_id)

        return jsonify(
            {
                "status": "accepted",
                "task_id": task_id,
                "work_type": event.work_type.value,
            }
        ), 200

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _main() -> None:  # pragma: no cover
    settings = WebhookSettings()
    app = create_app(settings=settings)
    app.run(host=settings.webhook_host, port=settings.webhook_port)


if __name__ == "__main__":  # pragma: no cover
    _main()


__all__: list[str] = ["create_app"]


# mypy 상 Any 사용 표식 (celery.Celery 가 Any 로 해석됨 — 경고 방지)
_ = Any
