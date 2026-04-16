"""T-24~T-28: build_runner 팩토리 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_runner.claude_code_runner import ClaudeCodeRunner
from agent_runner.errors import UnknownRunnerError
from agent_runner.factory import build_runner, register_runner
from agent_runner.opencode_runner import OpenCodeRunner
from agent_runner.settings import RunnerSettings

from .conftest import FakeRunner


class TestBuildRunner:
    """build_runner 팩토리."""

    def test_opencode(self, default_settings: RunnerSettings) -> None:
        """T-24: 'opencode' → OpenCodeRunner 인스턴스."""
        runner = build_runner("opencode", settings=default_settings)
        assert isinstance(runner, OpenCodeRunner)

    def test_claude_code(self, default_settings: RunnerSettings) -> None:
        """T-25: 'claude-code' → ClaudeCodeRunner 인스턴스."""
        runner = build_runner("claude-code", settings=default_settings)
        assert isinstance(runner, ClaudeCodeRunner)

    def test_unknown_kind(self) -> None:
        """T-26: 미등록 kind → UnknownRunnerError."""
        with pytest.raises(UnknownRunnerError, match="Unknown runner kind"):
            build_runner("nonexistent")

    def test_default_settings(self) -> None:
        """T-28: settings 미전달 시 기본 RunnerSettings 사용."""
        runner = build_runner("opencode")
        assert isinstance(runner, OpenCodeRunner)


class TestRegisterRunner:
    """T-27: 외부 Runner 등록."""

    def test_register_and_build(self, default_settings: RunnerSettings) -> None:
        """T-27: 외부 Runner 등록 후 build_runner 로 생성."""
        register_runner("fake", FakeRunner)
        try:
            runner = build_runner("fake", settings=default_settings)
            assert isinstance(runner, FakeRunner)
        finally:
            # cleanup: registry 오염 방지
            from agent_runner.factory import _REGISTRY

            _REGISTRY.pop("fake", None)

    def test_registered_runner_satisfies_protocol(self, default_settings: RunnerSettings) -> None:
        """등록된 FakeRunner 가 Protocol 을 만족하는지 런타임 검증."""
        register_runner("fake2", FakeRunner)
        try:
            runner = build_runner("fake2", settings=default_settings)
            result = runner.run(
                work_dir=Path("/tmp"),  # noqa: S108
                prompt="test",
                files=[],
                tools=[],
                env={},
            )
            assert result.exit_code == 0
        finally:
            from agent_runner.factory import _REGISTRY

            _REGISTRY.pop("fake2", None)
