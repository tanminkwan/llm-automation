"""agent-runner Protocol 정의."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import AgentResult, ToolSpec


class AgentRunner(Protocol):
    """AI Agent CLI 실행 인터페이스 (architecture_test.md §6)."""

    def run(
        self,
        *,
        work_dir: Path,
        prompt: str,
        files: list[Path],
        tools: list[ToolSpec],
        env: dict[str, str],
    ) -> AgentResult: ...
