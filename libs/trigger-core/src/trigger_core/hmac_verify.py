"""HMAC-SHA256 서명 검증."""

from __future__ import annotations

import hashlib
import hmac


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Webhook 서명(HMAC-SHA256 hex digest) 을 상수시간 비교로 검증.

    Args:
        payload: 요청 body (raw bytes).
        signature: 헤더 값 (hex digest).
        secret: HMAC 시크릿.

    Returns:
        True if 서명 일치.
    """
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
