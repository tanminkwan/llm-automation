"""agent-runner — AI Agent CLI 추상화 라이브러리.

Public API:
    - AgentRunner: Protocol (인터페이스)
    - AgentResult: 실행 결과 모델
    - ToolSpec: MCP 도구 사양 모델
    - RunnerSettings: 환경변수 설정
    - build_runner: 팩토리 함수
    - register_runner: 외부 Runner 등록 (OCP)
    - Errors: RunnerError, UnknownRunnerError, AgentTimeoutError, AgentExecutionError
"""

from .errors import (
    AgentExecutionError,
    AgentTimeoutError,
    RunnerError,
    UnknownRunnerError,
)
from .factory import build_runner, register_runner
from .models import AgentResult, ToolSpec
from .protocols import AgentRunner
from .settings import RunnerSettings

__all__ = [
    "AgentExecutionError",
    "AgentResult",
    "AgentRunner",
    "AgentTimeoutError",
    "RunnerError",
    "RunnerSettings",
    "ToolSpec",
    "UnknownRunnerError",
    "build_runner",
    "register_runner",
]
