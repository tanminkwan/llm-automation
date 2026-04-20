"""HMAC 검증 단위 테스트."""

from __future__ import annotations

import hashlib
import hmac

from trigger_core import verify_signature


def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def test_valid_signature() -> None:
    payload = b'{"a":1}'
    secret = "s3cret"
    assert verify_signature(payload, _sign(payload, secret), secret) is True


def test_invalid_signature_rejected() -> None:
    assert verify_signature(b'{"a":1}', "deadbeef", "s3cret") is False


def test_empty_signature_rejected() -> None:
    assert verify_signature(b"x", "", "s3cret") is False


def test_tampered_payload_rejected() -> None:
    secret = "s3cret"
    sig = _sign(b"original", secret)
    assert verify_signature(b"tampered", sig, secret) is False


def test_wrong_secret_rejected() -> None:
    payload = b"x"
    assert verify_signature(payload, _sign(payload, "right"), "wrong") is False
