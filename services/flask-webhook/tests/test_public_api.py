"""public API 축약 확인 — flask-webhook 은 HTTP 어댑터만 export."""

from __future__ import annotations


def test_public_exports() -> None:
    """서비스 public API 는 ``create_app`` 과 ``WebhookSettings`` 만."""
    import flask_webhook

    assert set(flask_webhook.__all__) == {"create_app", "WebhookSettings"}
    assert callable(flask_webhook.create_app)
    assert flask_webhook.WebhookSettings is not None


def test_trigger_core_is_source_of_truth() -> None:
    """과거 flask_webhook 에 있던 trigger 유틸은 trigger_core 에서만 import 가능."""
    from trigger_core import (
        CeleryTriggerDispatcher,
        DeliveryCache,
        WebhookTriggerSource,
        WorkType,
        classify_files,
        verify_signature,
    )

    assert all(
        [
            CeleryTriggerDispatcher,
            DeliveryCache,
            WebhookTriggerSource,
            WorkType,
            classify_files,
            verify_signature,
        ]
    )
