"""Claude Code Agent CLI Runner."""

from __future__ import annotations

import json
from pathlib import Path

from ._subprocess import run_cli
from .models import AgentResult, ToolSpec
from .settings import RunnerSettings


class ClaudeCodeRunner:
    """Claude Code CLI subprocess 어댑터."""

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
        cmd = ["claude", "--print", "--prompt", prompt]
        for f in files:
            cmd.extend(["--file", str(f)])
        for tool in tools:
            cmd.extend(["--mcp-config", self._tool_to_arg(tool)])
        return cmd

    @staticmethod
    def _tool_to_arg(tool: ToolSpec) -> str:
        """ToolSpec → JSON 인라인 CLI 인자."""
        return json.dumps(tool.model_dump(), ensure_ascii=False)
