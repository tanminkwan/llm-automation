"""T-20~T-23: ClaudeCodeRunner 테스트."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner.claude_code_runner import ClaudeCodeRunner
from agent_runner.models import AgentResult, ToolSpec
from agent_runner.settings import RunnerSettings


@pytest.fixture()
def runner(default_settings: RunnerSettings) -> ClaudeCodeRunner:
    return ClaudeCodeRunner(settings=default_settings)


class TestBuildCommand:
    """T-20~T-22: CLI 인자 조립."""

    def test_prompt(self, runner: ClaudeCodeRunner) -> None:
        """T-20: prompt → claude --print 인자 리스트."""
        cmd = runner._build_command(
            prompt="Analyze code",
            files=[],
            tools=[],
        )
        assert cmd[:2] == ["claude", "--print"]
        assert "--prompt" in cmd
        assert "Analyze code" in cmd

    def test_tools_as_mcp_config(
        self, runner: ClaudeCodeRunner, sample_tool_spec: ToolSpec
    ) -> None:
        """T-21: tools → --mcp-config 인자."""
        cmd = runner._build_command(
            prompt="test",
            files=[],
            tools=[sample_tool_spec],
        )
        assert "--mcp-config" in cmd
        mcp_idx = cmd.index("--mcp-config")
        mcp_json = cmd[mcp_idx + 1]
        parsed = json.loads(mcp_json)
        assert parsed["name"] == "search_codebase"

    def test_empty_files_and_tools(self, runner: ClaudeCodeRunner) -> None:
        """T-22: 빈 files/tools 시 해당 플래그 생략."""
        cmd = runner._build_command(prompt="test", files=[], tools=[])
        assert "--file" not in cmd
        assert "--mcp-config" not in cmd
        assert cmd == ["claude", "--print", "--prompt", "test"]


class TestRun:
    """T-23: subprocess 실행."""

    def test_success_with_fake(
        self, runner: ClaudeCodeRunner, tmp_work_dir: Path, sample_tool_spec: ToolSpec
    ) -> None:
        """T-23: fake subprocess 정상 → AgentResult."""
        fake_result = AgentResult(exit_code=0, stdout="result", stderr="", duration_seconds=0.5)
        with patch("agent_runner.claude_code_runner.run_cli", return_value=fake_result) as mock:
            result = runner.run(
                work_dir=tmp_work_dir,
                prompt="Analyze",
                files=[Path("src/app.py")],
                tools=[sample_tool_spec],
                env={"API_KEY": "test"},
            )
        assert result.exit_code == 0
        assert result.stdout == "result"
        call_kwargs = mock.call_args
        cmd = call_kwargs.args[0]
        assert cmd[:2] == ["claude", "--print"]
