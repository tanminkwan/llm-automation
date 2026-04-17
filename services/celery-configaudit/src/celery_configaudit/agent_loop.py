"""AgentLoop -- LLM + ConfigAudit MCP tool call 루프."""

import json
from datetime import UTC, datetime
from typing import Any

from .models import AnalysisReport, ToolCallRequest
from .protocols import ConfigAuditClient, LLMClient

_SYSTEM_PROMPT = (
    "You are a config audit analyst. "
    "Use the get_config_context tool to retrieve configuration diffs across environments. "
    "Analyze the results and produce a structured report with summary, details, and anomalies."
)

_TOOL_DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_config_context",
        "description": "Retrieve 3-way config diff context for dev/stage/prod environments.",
        "parameters": {
            "type": "object",
            "properties": {
                "work_id": {"type": "string", "description": "Work ID"},
                "case": {"type": "string", "description": "Case ID"},
            },
            "required": ["work_id", "case"],
        },
    },
}

_DEFAULT_MAX_ITERATIONS = 5


class AgentLoop:
    """LLM + MCP tool call 오케스트레이션 루프.

    DIP: LLMClient, ConfigAuditClient Protocol 에만 의존.
    """

    def __init__(
        self,
        *,
        llm: LLMClient,
        mcp: ConfigAuditClient,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self._llm = llm
        self._mcp = mcp
        self._max_iterations = max_iterations

    def run(self, work_id: str, case: str) -> AnalysisReport:
        """에이전트 루프 실행 -> AnalysisReport 반환."""
        messages: list[dict[str, str]] = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Analyze config changes for work_id={work_id}, case={case}.",
            },
        ]
        tools: list[dict[str, Any]] = [_TOOL_DEFINITION]

        last_content = ""
        for _ in range(self._max_iterations):
            response = self._llm.chat(messages, tools)
            content: str = response.get("content", "")
            tool_calls: list[dict[str, Any]] = response.get("tool_calls", [])

            if not tool_calls:
                # LLM 이 최종 텍스트를 반환
                last_content = content
                break

            # tool call 처리
            for tc in tool_calls:
                tool_req = ToolCallRequest(
                    name=tc.get("name", ""),
                    arguments=tc.get("arguments", {}),
                )
                tool_result = self._execute_tool(tool_req, work_id, case)
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"Tool call: {tool_req.name}({json.dumps(tool_req.arguments)})",
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Tool result: {json.dumps(tool_result)}",
                    }
                )

            if content:
                last_content = content
        else:
            # max_iterations 도달 -- 현재까지 내용으로 보고서 생성
            if not last_content:
                last_content = "Max iterations reached. Partial analysis based on collected data."

        return self._parse_report(work_id, case, last_content)

    def _execute_tool(
        self,
        tool_req: ToolCallRequest,
        work_id: str,
        case: str,
    ) -> dict[str, Any]:
        """tool call 실행 -- get_config_context 만 지원."""
        if tool_req.name == "get_config_context":
            tw = str(tool_req.arguments.get("work_id", work_id))
            tc = str(tool_req.arguments.get("case", case))
            try:
                return self._mcp.get_config_context(tw, tc)
            except Exception as exc:
                return {"error": str(exc)}
        return {"error": f"Unknown tool: {tool_req.name}"}

    def _parse_report(
        self,
        work_id: str,
        case: str,
        content: str,
    ) -> AnalysisReport:
        """LLM 텍스트 응답을 AnalysisReport 로 변환."""
        # 구조화된 JSON 응답 시도
        try:
            data: dict[str, Any] = json.loads(content)
            return AnalysisReport(
                work_id=work_id,
                case=case,
                summary=str(data.get("summary", "")),
                details=str(data.get("details", "")),
                anomalies=[str(a) for a in data.get("anomalies", [])],
                generated_at=datetime.now(UTC),
            )
        except (json.JSONDecodeError, TypeError):
            pass

        # 일반 텍스트 폴백
        return AnalysisReport(
            work_id=work_id,
            case=case,
            summary=content[:200] if content else "No analysis produced.",
            details=content,
            anomalies=[],
            generated_at=datetime.now(UTC),
        )
