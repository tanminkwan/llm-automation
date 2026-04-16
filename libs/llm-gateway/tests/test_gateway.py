"""LLMGateway alias 라우터 테스트 — 설계서 §8 의 T-20 ~ T-27."""

from __future__ import annotations

from typing import Any

import pytest

from llm_gateway.aliases import CHAT_LLM, EMBEDDING, REASONING_LLM
from llm_gateway.errors import MissingCredentialsError, UnknownProfileError
from llm_gateway.gateway import LLMGateway
from llm_gateway.models import ChatMessage, ChatResponse, EmbeddingResponse, TokenUsage
from llm_gateway.settings import (
    EmbeddingProfileSettings,
    GatewaySettings,
    ProfileSettings,
)


class _FakeChatBackend:
    """LSP 검증용 fake — ChatBackend Protocol 만족."""

    def __init__(self, profile: ProfileSettings) -> None:
        self.profile = profile
        self.calls: list[dict[str, Any]] = []

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        self.calls.append(
            {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        return ChatResponse(
            content=f"echo:{messages[-1].content}",
            model=model or self.profile.model,
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        )


class _FakeEmbeddingBackend:
    """EmbeddingBackend Protocol 만족 fake."""

    def __init__(self, profile: EmbeddingProfileSettings) -> None:
        self.profile = profile
        self.calls: list[dict[str, Any]] = []

    def embed(self, texts: list[str], *, model: str | None = None) -> EmbeddingResponse:
        self.calls.append({"texts": texts, "model": model})
        return EmbeddingResponse(
            vectors=[[float(i)] * self.profile.dim for i in range(len(texts))],
            model=model or self.profile.model,
            dim=self.profile.dim,
        )


def _build_gateway_with_fakes(
    full_env: dict[str, str],
) -> tuple[LLMGateway, dict[str, _FakeChatBackend | _FakeEmbeddingBackend]]:
    """공통 헬퍼: fake factory 를 주입한 gateway."""
    _ = full_env
    settings = GatewaySettings()
    created: dict[str, _FakeChatBackend | _FakeEmbeddingBackend] = {}

    def chat_factory(profile: ProfileSettings) -> _FakeChatBackend:
        backend = _FakeChatBackend(profile)
        created[f"chat:{profile.base_url}"] = backend
        return backend

    def embedding_factory(profile: EmbeddingProfileSettings) -> _FakeEmbeddingBackend:
        backend = _FakeEmbeddingBackend(profile)
        created[f"embed:{profile.base_url}"] = backend
        return backend

    gateway = LLMGateway(
        settings,
        chat_factory=chat_factory,
        embedding_factory=embedding_factory,
    )
    return gateway, created


def test_chat_routes_chat_llm_alias_to_chat_backend(full_env: dict[str, str]) -> None:
    """T-20: chat-llm 호출 → chat profile + factory + chat 호출."""
    gateway, created = _build_gateway_with_fakes(full_env)

    resp = gateway.chat(CHAT_LLM, [ChatMessage(role="user", content="ping")])

    assert resp.content == "echo:ping"
    backend = created[f"chat:{full_env['CHAT_LLM_BASE_URL']}"]
    assert isinstance(backend, _FakeChatBackend)
    assert backend.profile.model == full_env["CHAT_LLM_MODEL"]
    assert backend.calls[0]["model"] == full_env["CHAT_LLM_MODEL"]


def test_chat_routes_reasoning_llm_alias_to_reasoning_profile(
    full_env: dict[str, str],
) -> None:
    """T-21: reasoning-llm 호출 시 reasoning profile 사용."""
    gateway, created = _build_gateway_with_fakes(full_env)

    gateway.chat(REASONING_LLM, [ChatMessage(role="user", content="x")])

    backend = created[f"chat:{full_env['REASONING_LLM_BASE_URL']}"]
    assert isinstance(backend, _FakeChatBackend)
    assert backend.profile.model == full_env["REASONING_LLM_MODEL"]
    assert backend.profile.timeout_seconds == float(full_env["REASONING_LLM_TIMEOUT_SECONDS"])


def test_chat_with_embedding_alias_raises_unknown_profile(
    full_env: dict[str, str],
) -> None:
    """T-22: chat 메서드에 embedding alias 전달 → UnknownProfileError."""
    gateway, _ = _build_gateway_with_fakes(full_env)

    with pytest.raises(UnknownProfileError, match="embedding"):
        gateway.chat(EMBEDDING, [ChatMessage(role="user", content="x")])


def test_chat_raises_missing_credentials_when_api_key_empty(
    required_env: dict[str, str],
) -> None:
    """T-23: api_key 빈 문자열 → MissingCredentialsError. factory 호출되지 않음."""
    _ = required_env  # api_key 미설정
    settings = GatewaySettings()
    factory_called = False

    def chat_factory(profile: ProfileSettings) -> _FakeChatBackend:
        nonlocal factory_called
        factory_called = True
        return _FakeChatBackend(profile)

    gateway = LLMGateway(settings, chat_factory=chat_factory)

    with pytest.raises(MissingCredentialsError, match="chat-llm"):
        gateway.chat(CHAT_LLM, [ChatMessage(role="user", content="x")])

    assert factory_called is False


def test_embed_routes_embedding_alias_to_embedding_backend(
    full_env: dict[str, str],
) -> None:
    """T-24: embedding 호출 → embedding factory 사용."""
    gateway, created = _build_gateway_with_fakes(full_env)

    resp = gateway.embed(EMBEDDING, ["a", "b", "c"])

    assert len(resp.vectors) == 3
    assert resp.dim == int(full_env["EMBEDDING_DIM"])
    backend = created[f"embed:{full_env['EMBEDDING_BASE_URL']}"]
    assert isinstance(backend, _FakeEmbeddingBackend)


def test_embed_with_chat_alias_raises_unknown_profile(full_env: dict[str, str]) -> None:
    """T-25: embed 메서드에 chat alias → UnknownProfileError."""
    gateway, _ = _build_gateway_with_fakes(full_env)

    with pytest.raises(UnknownProfileError, match="chat-llm"):
        gateway.embed(CHAT_LLM, ["x"])


def test_embed_raises_missing_credentials_when_api_key_empty(
    required_env: dict[str, str],
) -> None:
    """embed 도 api_key 빈 값에서 MissingCredentialsError."""
    _ = required_env
    settings = GatewaySettings()
    gateway = LLMGateway(settings)

    with pytest.raises(MissingCredentialsError, match="embedding"):
        gateway.embed(EMBEDDING, ["x"])


def test_factory_injection_satisfies_lsp(full_env: dict[str, str]) -> None:
    """T-26: 임의 fake backend (Protocol 만족) 로 동작 — DIP/LSP 검증."""
    gateway, created = _build_gateway_with_fakes(full_env)

    gateway.chat(CHAT_LLM, [ChatMessage(role="user", content="dip")])
    gateway.embed(EMBEDDING, ["x"])

    assert any(k.startswith("chat:") for k in created)
    assert any(k.startswith("embed:") for k in created)


def test_default_factory_uses_openai_backend(full_env: dict[str, str]) -> None:
    """T-27: factory 미주입 시 OpenAIChatBackend / OpenAIEmbeddingBackend 생성 (lazy)."""
    from llm_gateway.openai_backend import OpenAIChatBackend, OpenAIEmbeddingBackend

    settings = GatewaySettings()
    gateway = LLMGateway(settings)

    chat_backend = gateway._build_chat_backend(settings.profile(CHAT_LLM))  # type: ignore[arg-type]
    embed_backend = gateway._build_embedding_backend(
        settings.profile(EMBEDDING)  # type: ignore[arg-type]
    )

    assert isinstance(chat_backend, OpenAIChatBackend)
    assert isinstance(embed_backend, OpenAIEmbeddingBackend)
    _ = full_env


def test_gateway_caches_backend_per_alias(full_env: dict[str, str]) -> None:
    """반복 호출 시 동일 alias 의 backend 를 재사용 (factory 1회만 호출)."""
    _ = full_env
    settings = GatewaySettings()
    factory_calls: list[ProfileSettings] = []

    def chat_factory(profile: ProfileSettings) -> _FakeChatBackend:
        factory_calls.append(profile)
        return _FakeChatBackend(profile)

    gateway = LLMGateway(settings, chat_factory=chat_factory)

    gateway.chat(CHAT_LLM, [ChatMessage(role="user", content="1")])
    gateway.chat(CHAT_LLM, [ChatMessage(role="user", content="2")])

    assert len(factory_calls) == 1
