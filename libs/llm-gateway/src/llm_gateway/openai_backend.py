"""OpenAI 호환 어댑터 — vLLM 도 동일 endpoint 규약이라 본 어댑터로 흡수.

생성자 파라미터(base_url/api_key/default_model/timeout/max_retries) 는
모두 ``GatewaySettings`` 에서 흘러온 값. 어댑터 자체에 모델명/URL/타임아웃
하드코딩 없음 (그라운드 룰 §7).
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from .errors import BackendCallError
from .models import ChatMessage, ChatResponse, EmbeddingResponse, TokenUsage
from .retry import build_retry


def _new_openai_client(*, base_url: str, api_key: str, timeout_seconds: float) -> OpenAI:
    """OpenAI 클라이언트 생성 — 테스트는 client 인자로 mock 주입."""
    return OpenAI(base_url=base_url, api_key=api_key, timeout=timeout_seconds)


class OpenAIChatBackend:
    """ChatBackend Protocol 의 OpenAI 호환 구현."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        default_model: str,
        timeout_seconds: float,
        max_retries: int,
        client: Any | None = None,
    ) -> None:
        self._client = client or _new_openai_client(
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self._default_model = default_model
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """OpenAI chat completions 호출.

        transient 실패는 ``max_retries`` 만큼 재시도 후 ``BackendCallError`` 로 래핑.
        """
        target_model = model or self._default_model
        payload: dict[str, Any] = {
            "model": target_model,
            "messages": [m.model_dump() for m in messages],
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        retrying = build_retry(
            timeout_seconds=self._timeout_seconds,
            max_retries=self._max_retries,
        )

        try:
            for attempt in retrying:
                with attempt:
                    raw = self._client.chat.completions.create(**payload)
        except Exception as exc:
            raise BackendCallError(f"chat call failed after {self._max_retries} attempts") from exc

        return _to_chat_response(raw)


class OpenAIEmbeddingBackend:
    """EmbeddingBackend Protocol 의 OpenAI 호환 구현."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        default_model: str,
        dim: int,
        timeout_seconds: float,
        max_retries: int,
        client: Any | None = None,
    ) -> None:
        self._client = client or _new_openai_client(
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self._default_model = default_model
        self._dim = dim
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

    def embed(self, texts: list[str], *, model: str | None = None) -> EmbeddingResponse:
        """OpenAI embeddings 호출. 빈 입력은 외부 호출 없이 빈 응답."""
        target_model = model or self._default_model
        if not texts:
            return EmbeddingResponse(vectors=[], model=target_model, dim=self._dim)

        retrying = build_retry(
            timeout_seconds=self._timeout_seconds,
            max_retries=self._max_retries,
        )

        try:
            for attempt in retrying:
                with attempt:
                    raw = self._client.embeddings.create(model=target_model, input=texts)
        except Exception as exc:
            raise BackendCallError(f"embed call failed after {self._max_retries} attempts") from exc

        vectors = [list(item.embedding) for item in raw.data]
        return EmbeddingResponse(vectors=vectors, model=raw.model, dim=self._dim)


def _to_chat_response(raw: Any) -> ChatResponse:
    """OpenAI ChatCompletion → ChatResponse 매핑."""
    choice = raw.choices[0]
    usage_obj = getattr(raw, "usage", None)
    if usage_obj is not None:
        usage = TokenUsage(
            prompt_tokens=getattr(usage_obj, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage_obj, "completion_tokens", 0) or 0,
            total_tokens=getattr(usage_obj, "total_tokens", 0) or 0,
        )
    else:
        usage = TokenUsage()
    return ChatResponse(
        content=choice.message.content or "",
        model=raw.model,
        finish_reason=choice.finish_reason or "",
        usage=usage,
    )
