"""DeliveryCache 단위 테스트."""

from __future__ import annotations

import pytest

from trigger_core import DeliveryCache


def test_first_delivery_not_duplicate() -> None:
    cache = DeliveryCache(ttl_seconds=60)
    assert cache.is_duplicate("d-1") is False


def test_marked_delivery_is_duplicate() -> None:
    cache = DeliveryCache(ttl_seconds=60)
    cache.mark("d-1")
    assert cache.is_duplicate("d-1") is True


def test_different_deliveries_independent() -> None:
    cache = DeliveryCache(ttl_seconds=60)
    cache.mark("d-1")
    assert cache.is_duplicate("d-2") is False


def test_ttl_eviction(monkeypatch: pytest.MonkeyPatch) -> None:
    """TTL 초과 시 엔트리 제거 후 is_duplicate False."""
    current: dict[str, float] = {"t": 100.0}

    def _fake_monotonic() -> float:
        return current["t"]

    monkeypatch.setattr("trigger_core.dedup.time.monotonic", _fake_monotonic)

    cache = DeliveryCache(ttl_seconds=10)
    cache.mark("d-1")

    # TTL 이내 → 중복
    current["t"] = 105.0
    assert cache.is_duplicate("d-1") is True

    # TTL 초과 → 엔트리 증발
    current["t"] = 120.0
    assert cache.is_duplicate("d-1") is False
