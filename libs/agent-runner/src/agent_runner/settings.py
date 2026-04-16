"""agent-runner 환경변수 설정 (pydantic-settings)."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunnerSettings(BaseSettings):
    """Agent Runner 환경변수 — 설계서 §6 설정 항목 표와 1:1."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    agent_runner_kind: str = Field(
        alias="AGENT_RUNNER_KIND",
        default="opencode",
    )
    agent_timeout_seconds: float = Field(
        alias="AGENT_TIMEOUT_SECONDS",
        default=300.0,
    )
    agent_work_dir_prefix: str = Field(
        alias="AGENT_WORK_DIR_PREFIX",
        default="/tmp/agent-runner",  # noqa: S108
    )
