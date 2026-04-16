"""게이트웨이 입출력 데이터 모델 — backend 변경이 호출측에 새지 않게 박제."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ChatRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(BaseModel):
    """LLM 대화 메시지 한 건."""

    role: ChatRole
    content: str


class TokenUsage(BaseModel):
    """토큰 사용량. provider 가 보고하는 값 그대로."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """단발 chat 호출의 정규화된 응답."""

    content: str
    model: str
    finish_reason: str
    usage: TokenUsage = Field(default_factory=TokenUsage)


class EmbeddingResponse(BaseModel):
    """단발 embedding 호출의 정규화된 응답.

    ``dim`` 은 Qdrant collection 차원과 일치 — `architecture_test.md §5.4`.
    """

    vectors: list[list[float]]
    model: str
    dim: int
