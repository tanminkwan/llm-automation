"""LLMGateway — alias 기반 라우터.

호출측은 backend 구현체를 모르고 alias 문자열만 안다 (DIP). backend 교체는
``GatewaySettings`` 환경변수만으로 가능 (`CLAUDE.md §5.3`).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from .aliases import CHAT_ALIASES, CHAT_LLM, EMBEDDING, EMBEDDING_ALIASES, REASONING_LLM
from .errors import MissingCredentialsError, UnknownProfileError
from .models import ChatMessage, ChatResponse, EmbeddingResponse
from .openai_backend import OpenAIChatBackend, OpenAIEmbeddingBackend
from .protocols import ChatBackend, EmbeddingBackend
from .settings import EmbeddingProfileSettings, GatewaySettings, ProfileSettings

ChatBackendFactory = Callable[[ProfileSettings], ChatBackend]
EmbeddingBackendFactory = Callable[[EmbeddingProfileSettings], EmbeddingBackend]


def _default_chat_factory(profile: ProfileSettings) -> ChatBackend:
    return OpenAIChatBackend(
        base_url=profile.base_url,
        api_key=profile.api_key,
        default_model=profile.model,
        timeout_seconds=profile.timeout_seconds,
        max_retries=profile.max_retries,
    )


def _default_embedding_factory(
    profile: EmbeddingProfileSettings,
) -> EmbeddingBackend:
    return OpenAIEmbeddingBackend(
        base_url=profile.base_url,
        api_key=profile.api_key,
        default_model=profile.model,
        dim=profile.dim,
        timeout_seconds=profile.timeout_seconds,
        max_retries=profile.max_retries,
    )


class LLMGateway:
    """alias 기반 LLM/Embedding 라우터."""

    def __init__(
        self,
        settings: GatewaySettings,
        *,
        chat_factory: ChatBackendFactory | None = None,
        embedding_factory: EmbeddingBackendFactory | None = None,
    ) -> None:
        self._settings = settings
        self._chat_factory: ChatBackendFactory = chat_factory or _default_chat_factory
        self._embedding_factory: EmbeddingBackendFactory = (
            embedding_factory or _default_embedding_factory
        )
        self._chat_cache: dict[str, ChatBackend] = {}
        self._embedding_cache: dict[str, EmbeddingBackend] = {}

    # ── public API ────────────────────────────────────────────
    def chat(
        self,
        alias: str,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """alias 가 가리키는 chat backend 로 호출 위임.

        ``model`` 미지정 시 alias 의 profile 모델을 명시적으로 전달한다 — backend
        구현이 default_model 을 가지든 말든 호출 의도가 항상 명확.
        """
        if alias not in CHAT_ALIASES:
            raise UnknownProfileError(alias)
        profile = self._chat_profile_for(alias)
        if not profile.api_key:
            raise MissingCredentialsError(alias)
        backend = self._get_or_build_chat_backend(alias, profile)
        return backend.chat(
            messages,
            model=model or profile.model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def embed(self, alias: str, texts: list[str], *, model: str | None = None) -> EmbeddingResponse:
        """alias 가 가리키는 embedding backend 로 호출 위임."""
        if alias not in EMBEDDING_ALIASES:
            raise UnknownProfileError(alias)
        profile = cast(EmbeddingProfileSettings, self._settings.profile(alias))
        if not profile.api_key:
            raise MissingCredentialsError(alias)
        backend = self._get_or_build_embedding_backend(alias, profile)
        return backend.embed(texts, model=model or profile.model)

    # ── internal ──────────────────────────────────────────────
    def _get_or_build_chat_backend(self, alias: str, profile: ProfileSettings) -> ChatBackend:
        cached = self._chat_cache.get(alias)
        if cached is not None:
            return cached
        backend = self._build_chat_backend(profile)
        self._chat_cache[alias] = backend
        return backend

    def _get_or_build_embedding_backend(
        self, alias: str, profile: EmbeddingProfileSettings
    ) -> EmbeddingBackend:
        cached = self._embedding_cache.get(alias)
        if cached is not None:
            return cached
        backend = self._build_embedding_backend(profile)
        self._embedding_cache[alias] = backend
        return backend

    def _chat_profile_for(self, alias: str) -> ProfileSettings:
        # CHAT_ALIASES 멤버십은 호출 전에 검증되므로 두 케이스만 처리.
        if alias == CHAT_LLM:
            return self._settings.chat_profile()
        # alias == REASONING_LLM
        return self._settings.reasoning_profile()

    def _build_chat_backend(self, profile: ProfileSettings) -> ChatBackend:
        """기본 또는 주입된 chat factory 로 backend 생성 (테스트 진입점 겸용)."""
        return self._chat_factory(profile)

    def _build_embedding_backend(self, profile: EmbeddingProfileSettings) -> EmbeddingBackend:
        """기본 또는 주입된 embedding factory 로 backend 생성."""
        return self._embedding_factory(profile)


__all__ = [
    "CHAT_LLM",
    "EMBEDDING",
    "REASONING_LLM",
    "ChatBackendFactory",
    "EmbeddingBackendFactory",
    "LLMGateway",
]
