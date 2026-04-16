"""OpenCode Agent CLI Runner."""

from __future__ import annotations

import json
from pathlib import Path

from ._subprocess import run_cli
from .models import AgentResult, ToolSpec
from .settings import RunnerSettings


class OpenCodeRunner:
    """OpenCode CLI subprocess 어댑터 (architecture_test.md §6)."""

    def __init__(self, *, settings: RunnerSettings) -> None:
        self._settings = settings

    def run(
        self,
        *,
        work_dir: Path,
        prompt: str,
        files: list[Path],
        tools: list[ToolSpec],
        env: dict[str, str],
    ) -> AgentResult:
        cmd = self._build_command(prompt=prompt, files=files, tools=tools)
        return run_cli(
            cmd,
            cwd=work_dir,
            env=env,
            timeout_seconds=self._settings.agent_timeout_seconds,
        )

    def _build_command(
        self,
        *,
        prompt: str,
        files: list[Path],
        tools: list[ToolSpec],
    ) -> list[str]:
        cmd = ["opencode", "run", "--prompt", prompt]
        for f in files:
            cmd.extend(["--file", str(f)])
        for tool in tools:
            cmd.extend(["--tool", self._tool_to_arg(tool)])
        return cmd

    @staticmethod
    def _tool_to_arg(tool: ToolSpec) -> str:
        """ToolSpec → JSON 인라인 CLI 인자 (설계서 Q-02)."""
        return json.dumps(tool.model_dump(), ensure_ascii=False)
