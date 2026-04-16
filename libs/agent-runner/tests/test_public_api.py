"""T-29: public API import 테스트."""

from __future__ import annotations


class TestPublicApi:
    """public API 단일 import."""

    def test_single_import(self) -> None:
        """T-29: from agent_runner import ... 한 줄 import 가능."""
        from agent_runner import (
            AgentExecutionError,
            AgentResult,
            AgentRunner,
            AgentTimeoutError,
            RunnerError,
            RunnerSettings,
            ToolSpec,
            UnknownRunnerError,
            build_runner,
            register_runner,
        )

        # 모든 심볼이 존재하는지 검증
        assert AgentRunner is not None
        assert AgentResult is not None
        assert ToolSpec is not None
        assert RunnerSettings is not None
        assert build_runner is not None
        assert register_runner is not None
        assert RunnerError is not None
        assert UnknownRunnerError is not None
        assert AgentTimeoutError is not None
        assert AgentExecutionError is not None
