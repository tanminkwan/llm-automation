"""pytest 공통 픽스처 — env 격리 및 표준 환경변수 주입."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

# 본 라이브러리가 읽는 모든 표준 환경변수.
# host 환경의 값이 새지 않도록 매 테스트마다 격리한다.
GATEWAY_ENV_VARS: tuple[str, ...] = (
    "CHAT_LLM_BASE_URL",
    "CHAT_LLM_MODEL",
    "CHAT_LLM_API_KEY",
    "CHAT_LLM_TIMEOUT_SECONDS",
    "CHAT_LLM_MAX_RETRIES",
    "REASONING_LLM_BASE_URL",
    "REASONING_LLM_MODEL",
    "REASONING_LLM_API_KEY",
    "REASONING_LLM_TIMEOUT_SECONDS",
    "REASONING_LLM_MAX_RETRIES",
    "EMBEDDING_BASE_URL",
    "EMBEDDING_MODEL",
    "EMBEDDING_API_KEY",
    "EMBEDDING_DIM",
    "EMBEDDING_TIMEOUT_SECONDS",
    "EMBEDDING_MAX_RETRIES",
)

# 필수 키만 채운 최소 환경 (테스트가 직접 override 가능).
REQUIRED_ENV: dict[str, str] = {
    "CHAT_LLM_BASE_URL": "https://chat.example.com/v1",
    "CHAT_LLM_MODEL": "test-chat-model",
    "REASONING_LLM_BASE_URL": "https://reason.example.com/v1",
    "REASONING_LLM_MODEL": "test-reason-model",
    "EMBEDDING_BASE_URL": "https://embed.example.com/v1",
    "EMBEDDING_MODEL": "test-embed-model",
    "EMBEDDING_DIM": "8",
}


@pytest.fixture(autouse=True)
def _isolate_gateway_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
) -> Iterator[None]:
    """모든 gateway 표준 env 를 호스트로부터 격리.

    pydantic-settings 의 ``env_file=".env"`` 동작이 cwd 의 실제 ``.env`` 를
    흡수하지 않도록, 매 테스트마다 빈 임시 디렉터리로 cwd 를 옮긴다.
    """
    for key in GATEWAY_ENV_VARS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)
    yield


@pytest.fixture
def required_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """필수 env 만 주입한 최소 구성."""
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    return dict(REQUIRED_ENV)


@pytest.fixture
def full_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """필수 + api_key + 비필수 키까지 모두 주입한 구성."""
    full: dict[str, str] = {
        **REQUIRED_ENV,
        "CHAT_LLM_API_KEY": "sk-chat-test",
        "REASONING_LLM_API_KEY": "sk-reason-test",
        "EMBEDDING_API_KEY": "sk-embed-test",
        "CHAT_LLM_TIMEOUT_SECONDS": "10",
        "CHAT_LLM_MAX_RETRIES": "2",
        "REASONING_LLM_TIMEOUT_SECONDS": "20",
        "REASONING_LLM_MAX_RETRIES": "5",
        "EMBEDDING_TIMEOUT_SECONDS": "15",
        "EMBEDDING_MAX_RETRIES": "4",
    }
    for key, value in full.items():
        monkeypatch.setenv(key, value)
    return full
