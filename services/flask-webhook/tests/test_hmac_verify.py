"""T-01~T-02: HMAC 서명 검증 테스트."""

from flask_webhook.hmac_verify import verify_signature

from .conftest import TEST_SECRET, make_signature


class TestVerifySignature:
    """T-01: 정상 서명, T-02: 불일치 서명."""

    def test_valid_signature(self) -> None:
        """T-01: 정상 서명 → True."""
        payload = b'{"ref":"refs/heads/main"}'
        sig = make_signature(payload)
        assert verify_signature(payload, sig, TEST_SECRET) is True

    def test_invalid_signature(self) -> None:
        """T-02: 불일치 서명 → False."""
        payload = b'{"ref":"refs/heads/main"}'
        assert verify_signature(payload, "bad-signature", TEST_SECRET) is False
