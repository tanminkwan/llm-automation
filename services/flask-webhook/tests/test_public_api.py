"""T-20: public API import 확인."""


class TestPublicAPI:
    """T-20: __init__ 에서 export 된 심볼 확인."""

    def test_all_exports(self) -> None:
        """T-20: 모든 public 심볼 import 가능."""
        from flask_webhook import (
            DeliveryCache,
            PushCommit,
            WebhookPayload,
            WebhookSettings,
            WorkType,
            classify_files,
            create_app,
            dispatch,
            verify_signature,
        )

        assert all(
            [
                DeliveryCache,
                PushCommit,
                WebhookPayload,
                WebhookSettings,
                WorkType,
                classify_files,
                create_app,
                dispatch,
                verify_signature,
            ]
        )
