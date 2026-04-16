"""에러 계층 테스트 — 설계서 §8 의 T-10."""

from __future__ import annotations

import pytest

from llm_gateway.errors import (
    BackendCallError,
    GatewayError,
    MissingCredentialsError,
    UnknownProfileError,
)


@pytest.mark.parametrize(
    "exc_cls",
    [UnknownProfileError, MissingCredentialsError, BackendCallError],
)
def test_all_errors_inherit_gateway_error(exc_cls: type[Exception]) -> None:
    """T-10: 모든 도메인 예외가 GatewayError 한 우산 아래 — 호출측 단일 except 가능."""
    assert issubclass(exc_cls, GatewayError)


def test_unknown_profile_error_carries_alias() -> None:
    """UnknownProfileError 는 어떤 alias 가 문제였는지 메시지에 포함."""
    err = UnknownProfileError("foo-bar")
    assert "foo-bar" in str(err)


def test_missing_credentials_error_carries_alias() -> None:
    """MissingCredentialsError 도 alias 식별 가능."""
    err = MissingCredentialsError("chat-llm")
    assert "chat-llm" in str(err)


def test_backend_call_error_wraps_cause() -> None:
    """BackendCallError 는 원본 예외를 __cause__ 로 보존 (디버깅 용이)."""
    cause = RuntimeError("upstream boom")
    try:
        raise BackendCallError("call failed") from cause
    except BackendCallError as err:
        assert err.__cause__ is cause
