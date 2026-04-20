"""DirectLLMAgent — OpenAI 호환 chat API 로 Java 파일에 javadoc 추가."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx

SYSTEM_PROMPT = (
    "You are a senior Java code assistant. "
    "Add concise Javadoc comment blocks (/** ... */) to public classes, "
    "interfaces, and methods in the given Java file. "
    "Do not change any existing code or formatting; only insert Javadoc blocks. "
    "Return the FULL modified file inside a single ```java fenced code block, "
    "with no other prose."
)

_FENCED_LANG_RE = re.compile(r"```java\s*\n(.*?)\n```", flags=re.DOTALL)
_FENCED_ANY_RE = re.compile(r"```[a-zA-Z0-9_+-]*\s*\n(.*?)\n```", flags=re.DOTALL)


@dataclass(frozen=True)
class AgentRunResult:
    """AgentExecutor.run() 반환값 — AgentExecResult Protocol 만족."""

    exit_code: int
    changed_files: list[str] = field(default_factory=list)
    stdout: str = ""


class DirectLLMAgent:
    """OpenAI-호환 chat API 로 javadoc 을 추가하는 최소 AgentExecutor."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        timeout: float = 120.0,
    ) -> None:
        if not api_key:
            raise ValueError("chat_llm_api_key is required for DirectLLMAgent")
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout

    def run(
        self,
        *,
        work_dir: Path,
        prompt: str,
        changed_files: list[str],
        rag_mcp_url: str,
    ) -> AgentRunResult:
        del prompt, rag_mcp_url
        actually_changed: list[str] = []
        stdout_parts: list[str] = []
        for rel in changed_files:
            if not rel.endswith(".java"):
                continue
            target = work_dir / rel
            if not target.is_file():
                continue
            original = target.read_text(encoding="utf-8")
            updated = self._request_javadoc(rel, original)
            if updated and updated != original:
                target.write_text(updated, encoding="utf-8")
                actually_changed.append(rel)
                stdout_parts.append(f"updated {rel}")
            else:
                stdout_parts.append(f"unchanged {rel}")
        return AgentRunResult(
            exit_code=0,
            changed_files=actually_changed,
            stdout="\n".join(stdout_parts),
        )

    def _request_javadoc(self, rel: str, content: str) -> str | None:
        user = f"File: {rel}\n\n```java\n{content}\n```"
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user},
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
        text = data["choices"][0]["message"]["content"] or ""
        return _extract_java_block(text)


def _extract_java_block(text: str) -> str | None:
    match = _FENCED_LANG_RE.search(text)
    if match is None:
        match = _FENCED_ANY_RE.search(text)
    if match is None:
        return None
    return match.group(1)


__all__ = ["AgentRunResult", "DirectLLMAgent"]
