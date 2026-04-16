"""TemplateSettings — pydantic-settings 기반 환경변수 로딩 (그라운드 룰 §7)."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TemplateSettings(BaseSettings):
    """Phase 0 검증용 설정.

    환경변수는 ``TEMPLATE_`` prefix 를 통해서만 주입된다.
    코드는 ``os.environ`` 을 직접 읽지 않고 본 객체를 통해서만
    값을 참조한다 (그라운드 룰 §7).
    """

    model_config = SettingsConfigDict(
        env_prefix="TEMPLATE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    greeting_prefix: str = Field(
        default="Hello",
        description="인사말 접두어. env: TEMPLATE_GREETING_PREFIX",
    )
