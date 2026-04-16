"""T-15~T-19: OpenCodeRunner 테스트."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner.errors import AgentTimeoutError
from agent_runner.models import AgentResult, ToolSpec
from agent_runner.opencode_runner import OpenCodeRunner
from agent_runner.settings import RunnerSettings


@pytest.fixture()
def runner(default_settings: RunnerSettings) -> OpenCodeRunner:
    return OpenCodeRunner(settings=default_settings)


class TestBuildCommand:
    """T-15~T-17: CLI 인자 조립."""

    def test_prompt_and_files(self, runner: OpenCodeRunner) -> None:
        """T-15: prompt + files → CLI 인자 리스트."""
        cmd = runner._build_command(
            prompt="Add docstrings",
            files=[Path("src/main.py"), Path("src/utils.py")],
            tools=[],
        )
        assert cmd[:3] == ["opencode", "run", "--prompt"]
        assert cmd[3] == "Add docstrings"
        assert "--file" in cmd
        assert "src/main.py" in cmd
        assert "src/utils.py" in cmd

    def test_tools_as_json(self, runner: OpenCodeRunner, sample_tool_spec: ToolSpec) -> None:
        """T-16: tools (ToolSpec) → --tool JSON 인자."""
        cmd = runner._build_command(
            prompt="test",
            files=[],
            tools=[sample_tool_spec],
        )
        assert "--tool" in cmd
        tool_idx = cmd.index("--tool")
        tool_json = cmd[tool_idx + 1]
        parsed = json.loads(tool_json)
        assert parsed["name"] == "search_codebase"
        assert parsed["server_url"] == "http://rag-mcp:9001"

    def test_empty_files_and_tools(self, runner: OpenCodeRunner) -> None:
        """T-17: 빈 files/tools 시 해당 플래그 생략."""
        cmd = runner._build_command(prompt="test", files=[], tools=[])
        assert "--file" not in cmd
        assert "--tool" not in cmd
        assert cmd == ["opencode", "run", "--prompt", "test"]


class TestRun:
    """T-18~T-19: subprocess 실행."""

    def test_success_with_fake(
        self, runner: OpenCodeRunner, tmp_work_dir: Path, sample_tool_spec: ToolSpec
    ) -> None:
        """T-18: fake subprocess 정상 → AgentResult."""
        fake_result = AgentResult(exit_code=0, stdout="annotated", stderr="", duration_seconds=1.0)
        with patch("agent_runner.opencode_runner.run_cli", return_value=fake_result) as mock:
            result = runner.run(
                work_dir=tmp_work_dir,
                prompt="Add docstrings",
                files=[Path("src/main.py")],
                tools=[sample_tool_spec],
                env={"KEY": "val"},
            )
        assert result.exit_code == 0
        assert result.stdout == "annotated"
        call_kwargs = mock.call_args
        cmd = call_kwargs.args[0]
        assert cmd[:3] == ["opencode", "run", "--prompt"]

    def test_timeout_propagation(self, runner: OpenCodeRunner, tmp_work_dir: Path) -> None:
        """T-19: fake subprocess 타임아웃 → AgentTimeoutError."""
        with (
            patch(
                "agent_runner.opencode_runner.run_cli",
                side_effect=AgentTimeoutError("timed out"),
            ),
            pytest.raises(AgentTimeoutError),
        ):
            runner.run(
                work_dir=tmp_work_dir,
                prompt="test",
                files=[],
                tools=[],
                env={},
            )
