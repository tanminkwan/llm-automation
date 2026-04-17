"""공유 fixture — FakeLLM, FakeMCP."""

from __future__ import annotations

import json
from typing import Any

import pytest

from celery_configaudit.models import TaskPayload
from celery_configaudit.settings import CeleryConfigAuditSettings

FAKE_CONTEXT: dict[str, Any] = {
    "work_id": "test-001",
    "case": "case-001",
    "configs": [],
    "change_diffs": [],
    "cross_env_diffs": [],
    "anomalies": [{"env": "prod", "description": "prod differs"}],
}


class FakeLLMToolCall:
    """첫 호출: tool_call, 두 번째 호출: 분석 텍스트."""

    def __init__(self) -> None:
        self._call_count = 0

    def chat(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        self._call_count += 1
        if self._call_count == 1:
            return {
                "content": "",
                "tool_calls": [
                    {
                        "name": "get_config_context",
                        "arguments": {"work_id": "test-001", "case": "case-001"},
                    }
                ],
            }
        return {
            "content": json.dumps(
                {
                    "summary": "prod differs from dev/stage",
                    "details": "Detailed analysis here.",
                    "anomalies": ["prod env anomaly"],
                }
            ),
            "tool_calls": [],
        }


class FakeLLMDirect:
    """tool_call 없이 바로 텍스트 반환."""

    def chat(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        return {"content": "Direct analysis without tool call.", "tool_calls": []}


class FakeLLMMaxIter:
    """항상 tool_call만 반환 (max iterations 테스트)."""

    def chat(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "content": "",
            "tool_calls": [
                {
                    "name": "get_config_context",
                    "arguments": {"work_id": "w", "case": "c"},
                }
            ],
        }


class FakeMCP:
    """ConfigAuditClient Protocol 구현."""

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        self._context = context or FAKE_CONTEXT
        self.calls: list[tuple[str, str]] = []

    def get_config_context(self, work_id: str, case: str) -> dict[str, Any]:
        self.calls.append((work_id, case))
        return self._context


class FailingMCP:
    """항상 예외 발생."""

    def get_config_context(self, work_id: str, case: str) -> dict[str, Any]:
        raise ConnectionError("MCP unavailable")


@pytest.fixture()
def sample_payload() -> TaskPayload:
    return TaskPayload(
        work_id="test-001",
        repo_url="owner/repo",
        ref="refs/heads/main",
        changed_files=["cfg/http.m"],
    )


@pytest.fixture()
def settings() -> CeleryConfigAuditSettings:
    return CeleryConfigAuditSettings()
