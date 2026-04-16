"""GatewaySettings / ProfileSettings 테스트 — 설계서 §8 의 T-01 ~ T-07."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from llm_gateway.aliases import CHAT_LLM, EMBEDDING, REASONING_LLM
from llm_gateway.errors import UnknownProfileError
from llm_gateway.settings import (
    EmbeddingProfileSettings,
    GatewaySettings,
    ProfileSettings,
)


def test_settings_loads_all_required_fields(full_env: dict[str, str]) -> None:
    """T-01: 모든 표준 키 env 주입 시 정상 로딩."""
    settings = GatewaySettings()

    assert settings.chat_llm_base_url == full_env["CHAT_LLM_BASE_URL"]
    assert settings.chat_llm_model == full_env["CHAT_LLM_MODEL"]
    assert settings.chat_llm_api_key == full_env["CHAT_LLM_API_KEY"]
    assert settings.reasoning_llm_base_url == full_env["REASONING_LLM_BASE_URL"]
    assert settings.embedding_dim == int(full_env["EMBEDDING_DIM"])


def test_settings_raises_when_required_missing() -> None:
    """T-02: 필수 키 누락 시 ValidationError (env 0개 — autouse 격리)."""
    with pytest.raises(ValidationError):
        GatewaySettings()


def test_settings_uses_default_for_optional_fields(required_env: dict[str, str]) -> None:
    """T-03: 타임아웃/재시도 기본값 (env 미설정 시 60.0 / 3)."""
    _ = required_env  # 필수만 채움, 비필수는 미설정
    settings = GatewaySettings()

    assert settings.chat_llm_timeout_seconds == 60.0
    assert settings.chat_llm_max_retries == 3
    assert settings.reasoning_llm_timeout_seconds == 60.0
    assert settings.reasoning_llm_max_retries == 3
    assert settings.embedding_timeout_seconds == 60.0
    assert settings.embedding_max_retries == 3


def test_settings_api_key_defaults_to_empty(required_env: dict[str, str]) -> None:
    """api_key 는 env 미설정 시 빈 문자열 — 호출 시점에 검증."""
    _ = required_env
    settings = GatewaySettings()

    assert settings.chat_llm_api_key == ""
    assert settings.reasoning_llm_api_key == ""
    assert settings.embedding_api_key == ""


def test_profile_chat_llm_returns_chat_profile(full_env: dict[str, str]) -> None:
    """T-04: chat-llm alias → ProfileSettings 매핑."""
    settings = GatewaySettings()

    profile = settings.profile(CHAT_LLM)

    assert isinstance(profile, ProfileSettings)
    assert profile.base_url == full_env["CHAT_LLM_BASE_URL"]
    assert profile.model == full_env["CHAT_LLM_MODEL"]
    assert profile.api_key == full_env["CHAT_LLM_API_KEY"]
    assert profile.timeout_seconds == float(full_env["CHAT_LLM_TIMEOUT_SECONDS"])
    assert profile.max_retries == int(full_env["CHAT_LLM_MAX_RETRIES"])


def test_profile_reasoning_llm_returns_reasoning_profile(full_env: dict[str, str]) -> None:
    """T-05: reasoning-llm alias → ProfileSettings."""
    settings = GatewaySettings()

    profile = settings.profile(REASONING_LLM)

    assert profile.base_url == full_env["REASONING_LLM_BASE_URL"]
    assert profile.model == full_env["REASONING_LLM_MODEL"]
    assert profile.timeout_seconds == float(full_env["REASONING_LLM_TIMEOUT_SECONDS"])


def test_profile_embedding_returns_embedding_profile(full_env: dict[str, str]) -> None:
    """T-06: embedding alias → EmbeddingProfileSettings (dim 포함)."""
    settings = GatewaySettings()

    profile = settings.profile(EMBEDDING)

    assert isinstance(profile, EmbeddingProfileSettings)
    assert profile.base_url == full_env["EMBEDDING_BASE_URL"]
    assert profile.dim == int(full_env["EMBEDDING_DIM"])


def test_profile_unknown_alias_raises(full_env: dict[str, str]) -> None:
    """T-07: 미등록 alias → UnknownProfileError."""
    _ = full_env
    settings = GatewaySettings()

    with pytest.raises(UnknownProfileError, match="not-a-real-alias"):
        settings.profile("not-a-real-alias")
