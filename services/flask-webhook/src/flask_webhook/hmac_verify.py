"""HMAC-SHA256 서명 검증."""

import hashlib
import hmac


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Gitea X-Gitea-Signature HMAC-SHA256 검증.

    Args:
        payload: 요청 body (raw bytes).
        signature: X-Gitea-Signature 헤더 값 (hex digest).
        secret: HMAC 시크릿.

    Returns:
        True if 서명 일치.
    """
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
