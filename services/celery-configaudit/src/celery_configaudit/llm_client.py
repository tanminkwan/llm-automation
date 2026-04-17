"""LLM HTTP 클라이언트 -- OpenAILLMClient."""

import json
from typing import Any

import httpx


class OpenAILLMClient:
    """OpenAI 호환 API HTTP 클라이언트.

    LLMClient Protocol 을 만족한다.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str,
        *,
        timeout: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """POST /chat/completions 호출 -- tool_call 파싱 포함."""
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
        }
        if tools:
            body["tools"] = tools
        response = httpx.post(url, json=body, headers=headers, timeout=self._timeout)
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        # 응답에서 첫 번째 choice 의 message 추출
        choices = data.get("choices", [])
        if not choices:
            return {"content": "", "tool_calls": []}

        message = choices[0].get("message", {})
        content = message.get("content") or ""
        raw_tool_calls: list[dict[str, Any]] = message.get("tool_calls") or []

        tool_calls: list[dict[str, Any]] = []
        for tc in raw_tool_calls:
            fn = tc.get("function", {})
            args_str = fn.get("arguments", "{}")
            parsed_args: dict[str, Any] = (
                json.loads(args_str) if isinstance(args_str, str) else args_str
            )
            tool_calls.append(
                {
                    "name": fn.get("name", ""),
                    "arguments": parsed_args,
                }
            )

        result: dict[str, Any] = {"content": content, "tool_calls": tool_calls}
        return result
