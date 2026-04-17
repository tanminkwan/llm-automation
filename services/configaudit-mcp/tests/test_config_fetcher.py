"""T-05~T-06: ConfigFetcher 테스트."""

import httpx
import pytest

from configaudit_mcp.config_fetcher import ConfigFetcher
from configaudit_mcp.models import EnvConfig


class TestConfigFetcher:
    """T-05: 정상 조회, T-06: API 에러."""

    def test_fetch_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-05: 정상 조회 — httpx mock."""
        response_body = {
            "env": "dev",
            "before": "Listen 80\n",
            "after": "Listen 8080\n",
            "meta": {"fixture": "case-001", "version": "v1"},
        }

        def _mock_get(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("GET", str(args[0]))
            return httpx.Response(200, json=response_body, request=request)

        monkeypatch.setattr(httpx, "get", _mock_get)

        fetcher = ConfigFetcher("http://fake:9100", timeout=5.0)
        result = fetcher.fetch_config("dev", "case-001")
        assert isinstance(result, EnvConfig)
        assert result.env == "dev"
        assert result.before == "Listen 80\n"
        assert result.after == "Listen 8080\n"

    def test_fetch_api_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-06: API 에러 → 예외 전파."""

        def _mock_get(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("GET", str(args[0]))
            return httpx.Response(500, json={"detail": "server error"}, request=request)

        monkeypatch.setattr(httpx, "get", _mock_get)

        fetcher = ConfigFetcher("http://fake:9100", timeout=5.0)
        with pytest.raises(httpx.HTTPStatusError):
            fetcher.fetch_config("dev", "case-001")
