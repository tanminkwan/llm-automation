"""멱등키 TTL 캐시 — delivery_id 중복 방지."""

from __future__ import annotations

import time


class DeliveryCache:
    """In-memory TTL 캐시. 프로세스 재시작 시 초기화 허용."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, float] = {}

    def _evict(self) -> None:
        """만료 엔트리 제거."""
        now = time.monotonic()
        expired = [k for k, v in self._store.items() if now - v > self._ttl]
        for k in expired:
            del self._store[k]

    def is_duplicate(self, delivery_id: str) -> bool:
        """이미 처리된 delivery_id 인지 확인."""
        self._evict()
        return delivery_id in self._store

    def mark(self, delivery_id: str) -> None:
        """delivery_id 를 처리 완료로 기록."""
        self._store[delivery_id] = time.monotonic()
