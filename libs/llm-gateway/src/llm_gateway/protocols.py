"""Backend Protocol 정의 — DIP 의 추상화 경계.

``LLMGateway`` 는 본 Protocol 만족 객체에만 의존한다. 신규 backend 추가는
Protocol 만족 + factory 등록만으로 가능 (OCP).
"""

from __future__ import annotations

from typing import Protocol

from .models import ChatMessage, ChatResponse, EmbeddingResponse


class ChatBackend(Protocol):
    """단발 chat 호출 인터페이스."""

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """주어진 메시지 리스트로 chat 호출을 실행한다.

        ``model`` 미지정 시 backend 의 default_model 을 사용한다.
        """
        ...


class EmbeddingBackend(Protocol):
    """단발 embedding 호출 인터페이스."""

    def embed(self, texts: list[str], *, model: str | None = None) -> EmbeddingResponse:
        """주어진 텍스트 리스트를 임베딩 벡터로 변환한다."""
        ...
