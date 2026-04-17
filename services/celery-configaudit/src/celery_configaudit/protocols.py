"""Protocol 정의 -- ConfigAuditClient, LLMClient."""

from typing import Any, Protocol


class ConfigAuditClient(Protocol):
    """configaudit-mcp 클라이언트 인터페이스."""

    def get_config_context(self, work_id: str, case: str) -> dict[str, Any]: ...


class LLMClient(Protocol):
    """LLM 클라이언트 인터페이스 (OpenAI 호환)."""

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]: ...
