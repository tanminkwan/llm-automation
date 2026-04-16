"""T-05, T-06: 에러 모델 테스트."""

from __future__ import annotations

from pathlib import Path

from agent_runner.errors import (
    AgentExecutionError,
    AgentTimeoutError,
    RunnerError,
    UnknownRunnerError,
)
from agent_runner.models import AgentResult


class TestErrorHierarchy:
    """T-05: 예외 계층 검증."""

    def test_unknown_runner_is_runner_error(self) -> None:
        assert issubclass(UnknownRunnerError, RunnerError)

    def test_agent_timeout_is_runner_error(self) -> None:
        assert issubclass(AgentTimeoutError, RunnerError)

    def test_agent_execution_is_runner_error(self) -> None:
        assert issubclass(AgentExecutionError, RunnerError)

    def test_all_are_exceptions(self) -> None:
        assert issubclass(RunnerError, Exception)


class TestAgentExecutionError:
    """T-06: AgentExecutionError.result 속성."""

    def test_result_attribute(self) -> None:
        result = AgentResult(
            exit_code=1,
            stdout="",
            stderr="segfault",
            changed_files=[Path("a.py")],
            duration_seconds=5.0,
        )
        err = AgentExecutionError("Agent failed", result)
        assert err.result is result
        assert err.result.exit_code == 1
        assert err.result.stderr == "segfault"
        assert str(err) == "Agent failed"
