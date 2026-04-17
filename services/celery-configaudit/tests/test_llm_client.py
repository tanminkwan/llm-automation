"""OpenAILLMClient 테스트."""

import json

import httpx
import pytest

from celery_configaudit.llm_client import OpenAILLMClient


class TestOpenAILLMClient:
    def test_chat_with_tool_call(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """tool_call 응답 파싱."""
        api_response = {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "get_config_context",
                                    "arguments": json.dumps({"work_id": "w", "case": "c"}),
                                }
                            }
                        ],
                    }
                }
            ]
        }

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(200, json=api_response, request=request)

        monkeypatch.setattr(httpx, "post", _mock_post)
        client = OpenAILLMClient("http://fake/v1", "model", "key")
        result = client.chat([{"role": "user", "content": "hi"}], [])
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "get_config_context"

    def test_chat_text_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """텍스트만 반환."""
        api_response = {
            "choices": [{"message": {"content": "analysis result", "tool_calls": None}}]
        }

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(200, json=api_response, request=request)

        monkeypatch.setattr(httpx, "post", _mock_post)
        client = OpenAILLMClient("http://fake/v1", "model", "key")
        result = client.chat([{"role": "user", "content": "hi"}], [])
        assert result["content"] == "analysis result"
        assert result["tool_calls"] == []

    def test_empty_choices(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """빈 choices."""

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(200, json={"choices": []}, request=request)

        monkeypatch.setattr(httpx, "post", _mock_post)
        client = OpenAILLMClient("http://fake/v1", "model", "key")
        result = client.chat([], [])
        assert result["content"] == ""

    def test_tools_included_in_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """tools 리스트가 비어있지 않으면 body 에 포함."""
        captured: dict[str, object] = {}

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            captured["json"] = kwargs.get("json")
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok"}}]},
                request=request,
            )

        monkeypatch.setattr(httpx, "post", _mock_post)
        tools = [{"type": "function", "function": {"name": "t", "parameters": {}}}]
        client = OpenAILLMClient("http://fake/v1", "model", "key")
        client.chat([{"role": "user", "content": "hi"}], tools)
        assert "tools" in captured["json"]  # type: ignore[operator]

    def test_api_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """API 에러."""

        def _mock_post(*args: object, **kwargs: object) -> httpx.Response:
            request = httpx.Request("POST", str(args[0]))
            return httpx.Response(500, json={}, request=request)

        monkeypatch.setattr(httpx, "post", _mock_post)
        client = OpenAILLMClient("http://fake/v1", "model", "key")
        with pytest.raises(httpx.HTTPStatusError):
            client.chat([], [])
