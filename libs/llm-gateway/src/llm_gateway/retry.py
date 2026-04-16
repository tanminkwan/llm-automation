"""tenacity 기반 재시도 정책.

OpenAI 호환 backend 의 transient 에러만 재시도 대상 — 4xx 인증/요청 오류는
즉시 raise 하여 호출자 코드의 결함을 빠르게 노출시킨다 (설계서 §3.6).
"""

from __future__ import annotations

import openai
from tenacity import (
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

# 재시도 대상 — 네트워크/5xx/rate limit (transient).
_RETRYABLE_EXCEPTION_TYPES: tuple[type[BaseException], ...] = (
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.RateLimitError,
    openai.InternalServerError,
)

# 지수 백오프 최소/최대 대기 (초). 환경별 조정 필요 시 별도 함수로 분리.
_BACKOFF_MIN_SECONDS = 1.0
_BACKOFF_MAX_SECONDS = 10.0


def is_retryable_exception(exc: BaseException) -> bool:
    """주어진 예외가 재시도 대상인지 판정."""
    return isinstance(exc, _RETRYABLE_EXCEPTION_TYPES)


def build_retry(*, timeout_seconds: float, max_retries: int) -> Retrying:
    """tenacity Retrying 인스턴스를 빌드.

    ``timeout_seconds`` 는 인터페이스 일관성을 위해 받지만, 단발 호출의
    실제 timeout 은 OpenAI 클라이언트의 ``timeout`` 으로 위임한다.

    Returns:
        Retrying — for-loop 형태로 사용.
    """
    _ = timeout_seconds  # 클라이언트 측에서 사용. 본 빌더는 시도 횟수만 제어.
    return Retrying(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=_BACKOFF_MIN_SECONDS, max=_BACKOFF_MAX_SECONDS),
        reraise=True,
    )
