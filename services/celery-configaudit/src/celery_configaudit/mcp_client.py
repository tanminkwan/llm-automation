"""ConfigAudit MCP HTTP 클라이언트 -- HttpConfigAuditClient."""

from typing import Any

import httpx


class HttpConfigAuditClient:
    """configaudit-mcp 서비스 HTTP 클라이언트.

    ConfigAuditClient Protocol 을 만족한다.
    """

    def __init__(self, base_url: str, *, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def get_config_context(self, work_id: str, case: str) -> dict[str, Any]:
        """POST /tools/get_config_context 호출."""
        url = f"{self._base_url}/tools/get_config_context"
        payload = {"work_id": work_id, "case": case}
        response = httpx.post(url, json=payload, timeout=self._timeout)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result
