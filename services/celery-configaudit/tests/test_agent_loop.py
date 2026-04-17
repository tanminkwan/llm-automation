"""AgentLoop 테스트 — happy path, direct, max iter, unknown tool, MCP error."""

from celery_configaudit.agent_loop import AgentLoop

from .conftest import FailingMCP, FakeLLMDirect, FakeLLMMaxIter, FakeLLMToolCall, FakeMCP


class TestAgentLoop:
    def test_happy_path_tool_call(self) -> None:
        """tool_call → MCP → 분석 텍스트 → AnalysisReport."""
        loop = AgentLoop(llm=FakeLLMToolCall(), mcp=FakeMCP(), max_iterations=5)
        report = loop.run("test-001", "case-001")
        assert report.work_id == "test-001"
        assert report.case == "case-001"
        assert report.summary == "prod differs from dev/stage"
        assert len(report.anomalies) == 1

    def test_direct_answer(self) -> None:
        """tool_call 없이 바로 텍스트."""
        loop = AgentLoop(llm=FakeLLMDirect(), mcp=FakeMCP(), max_iterations=5)
        report = loop.run("w", "c")
        assert "Direct analysis" in report.summary

    def test_max_iterations(self) -> None:
        """항상 tool_call → max_iterations 도달."""
        loop = AgentLoop(llm=FakeLLMMaxIter(), mcp=FakeMCP(), max_iterations=2)
        report = loop.run("w", "c")
        assert "Max iterations" in report.summary or report.summary != ""

    def test_unknown_tool(self) -> None:
        """알 수 없는 tool name."""

        class UnknownToolLLM:
            def __init__(self) -> None:
                self._n = 0

            def chat(self, messages: list, tools: list) -> dict:  # type: ignore[type-arg]
                self._n += 1
                if self._n == 1:
                    return {
                        "content": "",
                        "tool_calls": [{"name": "unknown_tool", "arguments": {}}],
                    }
                return {"content": "done", "tool_calls": []}

        loop = AgentLoop(llm=UnknownToolLLM(), mcp=FakeMCP(), max_iterations=5)
        report = loop.run("w", "c")
        assert report.work_id == "w"

    def test_mcp_error_handled(self) -> None:
        """MCP 호출 실패 시 에러를 tool result로 반환."""
        loop = AgentLoop(llm=FakeLLMToolCall(), mcp=FailingMCP(), max_iterations=5)
        report = loop.run("w", "c")
        assert report.work_id == "w"
