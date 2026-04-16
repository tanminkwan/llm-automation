"""agent-runner 예외 모델."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import AgentResult


class RunnerError(Exception):
    """agent-runner 모든 예외의 base."""


class UnknownRunnerError(RunnerError):
    """build_runner 에 등록되지 않은 kind."""


class AgentTimeoutError(RunnerError):
    """subprocess 실행이 AGENT_TIMEOUT_SECONDS 초과."""


class AgentExecutionError(RunnerError):
    """Agent CLI 가 비정상 종료 (exit_code != 0)."""

    def __init__(self, message: str, result: AgentResult) -> None:
        super().__init__(message)
        self.result = result
