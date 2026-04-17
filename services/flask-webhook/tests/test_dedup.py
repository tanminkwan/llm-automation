"""T-07~T-09: DeliveryCache 테스트."""

import time
from unittest.mock import patch

from flask_webhook.dedup import DeliveryCache


class TestDeliveryCache:
    """T-07: 새 ID, T-08: 중복, T-09: TTL 만료."""

    def test_new_id(self) -> None:
        """T-07: 새 ID → not duplicate."""
        cache = DeliveryCache(ttl_seconds=300)
        assert cache.is_duplicate("delivery-001") is False

    def test_duplicate_id(self) -> None:
        """T-08: 동일 ID 재전송 → duplicate."""
        cache = DeliveryCache(ttl_seconds=300)
        cache.mark("delivery-001")
        assert cache.is_duplicate("delivery-001") is True

    def test_ttl_expiry(self) -> None:
        """T-09: TTL 만료 후 → not duplicate."""
        cache = DeliveryCache(ttl_seconds=1)
        cache.mark("delivery-001")
        assert cache.is_duplicate("delivery-001") is True

        # monotonic 시간을 2초 앞으로
        original_time = time.monotonic()
        with patch("flask_webhook.dedup.time") as mock_time:
            mock_time.monotonic.return_value = original_time + 2.0
            assert cache.is_duplicate("delivery-001") is False
