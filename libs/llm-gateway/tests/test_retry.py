"""재시도 정책 테스트 — 설계서 §8 의 T-11 ~ T-13."""

from __future__ import annotations

import httpx
import pytest
from openai import APIConnectionError, BadRequestError, RateLimitError

from llm_gateway.retry import build_retry, is_retryable_exception


def _make_api_connection_error() -> APIConnectionError:
    """openai SDK 의 APIConnectionError 를 테스트용으로 합성."""
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    return APIConnectionError(request=request)


def _make_bad_request_error() -> BadRequestError:
    """4xx — 재시도 비대상."""
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(400, request=request)
    return BadRequestError(message="bad", response=response, body=None)


def _make_rate_limit_error() -> RateLimitError:
    """429 — transient. 재시도 대상."""
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(429, request=request)
    return RateLimitError(message="slow down", response=response, body=None)


def test_is_retryable_for_transient_errors() -> None:
    """T-12 (분류): APIConnectionError, RateLimitError 는 재시도 대상."""
    assert is_retryable_exception(_make_api_connection_error()) is True
    assert is_retryable_exception(_make_rate_limit_error()) is True


def test_not_retryable_for_4xx_errors() -> None:
    """T-13 (분류): BadRequestError 는 즉시 raise — 재시도 X."""
    assert is_retryable_exception(_make_bad_request_error()) is False


def test_not_retryable_for_unrelated_exceptions() -> None:
    """라이브러리 외 일반 예외도 재시도 안 함."""
    assert is_retryable_exception(ValueError("oops")) is False


def test_build_retry_retries_until_max_attempts() -> None:
    """T-11: max_retries 만큼 재시도 후 마지막 예외 raise."""
    calls: list[int] = []

    def always_fail() -> None:
        calls.append(1)
        raise _make_api_connection_error()

    retrying = build_retry(timeout_seconds=0.1, max_retries=3)

    with pytest.raises(APIConnectionError):
        for attempt in retrying:
            with attempt:
                always_fail()

    assert len(calls) == 3


def test_build_retry_stops_on_non_retryable() -> None:
    """T-13: 비대상 예외는 첫 시도에서 즉시 raise (재시도 X)."""
    calls: list[int] = []

    def fail_with_bad_request() -> None:
        calls.append(1)
        raise _make_bad_request_error()

    retrying = build_retry(timeout_seconds=0.1, max_retries=5)

    with pytest.raises(BadRequestError):
        for attempt in retrying:
            with attempt:
                fail_with_bad_request()

    assert len(calls) == 1


def test_build_retry_returns_value_when_eventually_succeeds() -> None:
    """transient 후 성공 — 정상 반환 흐름."""
    state = {"n": 0}

    def flaky() -> str:
        state["n"] += 1
        if state["n"] < 2:
            raise _make_api_connection_error()
        return "ok"

    retrying = build_retry(timeout_seconds=0.1, max_retries=3)

    result: str | None = None
    for attempt in retrying:
        with attempt:
            result = flaky()

    assert result == "ok"
    assert state["n"] == 2
