"""agent-runner 데이터 모델."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    """MCP 도구 사양 — Agent CLI 에 등록할 tool 정의."""

    name: str
    description: str
    input_schema: dict[str, object]
    server_url: str


class AgentResult(BaseModel):
    """Agent CLI 실행 결과."""

    exit_code: int
    stdout: str
    stderr: str
    changed_files: list[Path] = Field(default_factory=list)
    duration_seconds: float
