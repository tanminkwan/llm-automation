"""leebalso-mock 환경변수 설정."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LeebalsoSettings(BaseSettings):
    """설계서 §6 설정 항목 표와 1:1."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    leebalso_fixtures_dir: str = Field(
        alias="LEEBALSO_FIXTURES_DIR",
        default="fixtures",
    )
    leebalso_host: str = Field(
        alias="LEEBALSO_HOST",
        default="0.0.0.0",  # noqa: S104
    )
    leebalso_port: int = Field(
        alias="LEEBALSO_PORT",
        default=9100,
    )
