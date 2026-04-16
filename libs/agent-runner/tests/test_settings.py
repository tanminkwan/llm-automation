"""T-07~T-09: RunnerSettings 테스트."""

from __future__ import annotations

import pytest

from agent_runner.settings import RunnerSettings


class TestRunnerSettings:
    """환경변수 기반 설정 로딩."""

    def test_load_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-07: 모든 키 env 주입 시 정상 로딩."""
        monkeypatch.setenv("AGENT_RUNNER_KIND", "claude-code")
        monkeypatch.setenv("AGENT_TIMEOUT_SECONDS", "600")
        monkeypatch.setenv("AGENT_WORK_DIR_PREFIX", "/workspace/custom")

        s = RunnerSettings()
        assert s.agent_runner_kind == "claude-code"
        assert s.agent_timeout_seconds == 600.0
        assert s.agent_work_dir_prefix == "/workspace/custom"

    def test_defaults(self) -> None:
        """T-08: 기본값만으로 로딩 (env 미설정)."""
        s = RunnerSettings()
        assert s.agent_runner_kind == "opencode"
        assert s.agent_timeout_seconds == 300.0
        assert s.agent_work_dir_prefix == "/tmp/agent-runner"  # noqa: S108

    def test_custom_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-09: 타임아웃 커스텀 값."""
        monkeypatch.setenv("AGENT_TIMEOUT_SECONDS", "120.5")
        s = RunnerSettings()
        assert s.agent_timeout_seconds == 120.5
