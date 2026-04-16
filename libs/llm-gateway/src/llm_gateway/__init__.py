"""LLM/Embedding 추상화 게이트웨이 — public API.

상세는 ``docs/설계서.md``. alias 와 환경변수 표준은 ``CLAUDE.md §5`` /
``architecture_test.md §5·§12``.
"""

from __future__ import annotations

from .aliases import CHAT_ALIASES, CHAT_LLM, EMBEDDING, EMBEDDING_ALIASES, REASONING_LLM
from .errors import (
    BackendCallError,
    GatewayError,
    MissingCredentialsError,
    UnknownProfileError,
)
from .gateway import LLMGateway
from .models import ChatMessage, ChatResponse, EmbeddingResponse, TokenUsage
from .openai_backend import OpenAIChatBackend, OpenAIEmbeddingBackend
from .protocols import ChatBackend, EmbeddingBackend
from .settings import EmbeddingProfileSettings, GatewaySettings, ProfileSettings

__version__ = "0.1.0"

__all__ = [
    "CHAT_ALIASES",
    "CHAT_LLM",
    "EMBEDDING",
    "EMBEDDING_ALIASES",
    "REASONING_LLM",
    "BackendCallError",
    "ChatBackend",
    "ChatMessage",
    "ChatResponse",
    "EmbeddingBackend",
    "EmbeddingProfileSettings",
    "EmbeddingResponse",
    "GatewayError",
    "GatewaySettings",
    "LLMGateway",
    "MissingCredentialsError",
    "OpenAIChatBackend",
    "OpenAIEmbeddingBackend",
    "ProfileSettings",
    "TokenUsage",
    "UnknownProfileError",
]
