"""agent-runner 테스트 공통 픽스처."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agent_runner.models import AgentResult, ToolSpec
from agent_runner.settings import RunnerSettings


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """환경변수 격리 — 테스트 간 오염 방지."""
    monkeypatch.delenv("AGENT_RUNNER_KIND", raising=False)
    monkeypatch.delenv("AGENT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("AGENT_WORK_DIR_PREFIX", raising=False)


@pytest.fixture()
def default_settings() -> RunnerSettings:
    return RunnerSettings()


@pytest.fixture()
def sample_tool_spec() -> ToolSpec:
    return ToolSpec(
        name="search_codebase",
        description="Search code by semantic query",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        server_url="http://rag-mcp:9001",
    )


@pytest.fixture()
def sample_result() -> AgentResult:
    return AgentResult(
        exit_code=0,
        stdout="done",
        stderr="",
        changed_files=[Path("src/main.py")],
        duration_seconds=1.5,
    )


@pytest.fixture()
def tmp_work_dir(tmp_path: Path) -> Path:
    work_dir = tmp_path / "workspace"
    work_dir.mkdir()
    return work_dir


class FakeRunner:
    """Protocol 만족 fake — LSP 검증용."""

    def __init__(self, *, settings: Any = None) -> None:
        self._settings = settings
        self.calls: list[dict[str, Any]] = []

    def run(
        self,
        *,
        work_dir: Path,
        prompt: str,
        files: list[Path],
        tools: list[ToolSpec],
        env: dict[str, str],
    ) -> AgentResult:
        self.calls.append(
            {"work_dir": work_dir, "prompt": prompt, "files": files, "tools": tools, "env": env}
        )
        return AgentResult(
            exit_code=0,
            stdout="fake output",
            stderr="",
            duration_seconds=0.1,
        )
