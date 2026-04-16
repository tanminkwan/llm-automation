"""환경변수 기반 게이트웨이 설정 (그라운드 룰 §7).

표준 키 목록은 ``architecture_test.md §12.2`` 와 본 모듈 ``docs/설계서.md §6``
에서 단일 출처로 관리된다. 코드는 ``os.environ`` 을 직접 읽지 않고 본 객체를
통해서만 값을 참조한다.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .aliases import CHAT_LLM, EMBEDDING, REASONING_LLM
from .errors import UnknownProfileError


class ProfileSettings(BaseModel):
    """단일 backend profile (chat-llm / reasoning-llm) 의 호출 파라미터."""

    model_config = ConfigDict(frozen=True)

    base_url: str
    model: str
    api_key: str
    timeout_seconds: float
    max_retries: int


class EmbeddingProfileSettings(ProfileSettings):
    """embedding profile — Qdrant 컬렉션 차원(``dim``) 추가."""

    dim: int


class GatewaySettings(BaseSettings):
    """``architecture_test.md §12.2`` 의 표준 키를 그대로 흡수한다.

    필수(``*_BASE_URL``, ``*_MODEL``, ``EMBEDDING_DIM``) 가 누락되면
    ``ValidationError``. ``*_API_KEY`` 는 빈 문자열을 허용하고 호출 시점에
    ``MissingCredentialsError`` 로 검증한다 (부팅 시 즉시 실패하지 않게).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # ── chat-llm ────────────────────────────────────────────────
    chat_llm_base_url: str = Field(alias="CHAT_LLM_BASE_URL")
    chat_llm_model: str = Field(alias="CHAT_LLM_MODEL")
    chat_llm_api_key: str = Field(alias="CHAT_LLM_API_KEY", default="")
    chat_llm_timeout_seconds: float = Field(alias="CHAT_LLM_TIMEOUT_SECONDS", default=60.0)
    chat_llm_max_retries: int = Field(alias="CHAT_LLM_MAX_RETRIES", default=3)

    # ── reasoning-llm ───────────────────────────────────────────
    reasoning_llm_base_url: str = Field(alias="REASONING_LLM_BASE_URL")
    reasoning_llm_model: str = Field(alias="REASONING_LLM_MODEL")
    reasoning_llm_api_key: str = Field(alias="REASONING_LLM_API_KEY", default="")
    reasoning_llm_timeout_seconds: float = Field(
        alias="REASONING_LLM_TIMEOUT_SECONDS", default=60.0
    )
    reasoning_llm_max_retries: int = Field(alias="REASONING_LLM_MAX_RETRIES", default=3)

    # ── embedding ───────────────────────────────────────────────
    embedding_base_url: str = Field(alias="EMBEDDING_BASE_URL")
    embedding_model: str = Field(alias="EMBEDDING_MODEL")
    embedding_api_key: str = Field(alias="EMBEDDING_API_KEY", default="")
    embedding_dim: int = Field(alias="EMBEDDING_DIM")
    embedding_timeout_seconds: float = Field(alias="EMBEDDING_TIMEOUT_SECONDS", default=60.0)
    embedding_max_retries: int = Field(alias="EMBEDDING_MAX_RETRIES", default=3)

    # ── alias → profile 매핑 ───────────────────────────────────
    def chat_profile(self) -> ProfileSettings:
        """chat-llm profile."""
        return ProfileSettings(
            base_url=self.chat_llm_base_url,
            model=self.chat_llm_model,
            api_key=self.chat_llm_api_key,
            timeout_seconds=self.chat_llm_timeout_seconds,
            max_retries=self.chat_llm_max_retries,
        )

    def reasoning_profile(self) -> ProfileSettings:
        """reasoning-llm profile."""
        return ProfileSettings(
            base_url=self.reasoning_llm_base_url,
            model=self.reasoning_llm_model,
            api_key=self.reasoning_llm_api_key,
            timeout_seconds=self.reasoning_llm_timeout_seconds,
            max_retries=self.reasoning_llm_max_retries,
        )

    def embedding_profile(self) -> EmbeddingProfileSettings:
        """embedding profile (dim 포함)."""
        return EmbeddingProfileSettings(
            base_url=self.embedding_base_url,
            model=self.embedding_model,
            api_key=self.embedding_api_key,
            timeout_seconds=self.embedding_timeout_seconds,
            max_retries=self.embedding_max_retries,
            dim=self.embedding_dim,
        )

    def profile(self, alias: str) -> ProfileSettings:
        """alias 문자열을 ProfileSettings (또는 서브타입) 로 dispatch."""
        if alias == CHAT_LLM:
            return self.chat_profile()
        if alias == REASONING_LLM:
            return self.reasoning_profile()
        if alias == EMBEDDING:
            return self.embedding_profile()
        raise UnknownProfileError(alias)
