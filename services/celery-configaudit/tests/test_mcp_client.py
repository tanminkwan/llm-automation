"""HttpConfigAuditClient 테스트."""

import httpx
import pytest

from celery_configaudit.mcp_client import HttpConfigAuditClient


class TestHttpConfigAuditClient:
    def test_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """정상 조회."""
        response_data = {"work_id": "w", "case": "c", "configs": []}

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(200, json=response_data, request=request)

        monkeypatch.setattr(httpx, "post", _mock_post)
        client = HttpConfigAuditClient("http://fake:9002")
        result = client.get_config_context("w", "c")
        assert result["work_id"] == "w"

    def test_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """API 에러."""

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(500, json={"error": "fail"}, request=request)

        monkeypatch.setattr(httpx, "post", _mock_post)
        client = HttpConfigAuditClient("http://fake:9002")
        with pytest.raises(httpx.HTTPStatusError):
            client.get_config_context("w", "c")
