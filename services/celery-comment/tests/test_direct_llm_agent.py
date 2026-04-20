"""DirectLLMAgent — httpx.Client mocking 으로 OpenAI 호환 응답 처리."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from celery_comment.direct_llm_agent import DirectLLMAgent, _extract_java_block


class _FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeClient:
    """httpx.Client 와 호환되는 최소 테스트 더블."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.last_url: str | None = None
        self.last_json: dict[str, Any] | None = None

    def __enter__(self) -> _FakeClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],  # noqa: ARG002
        json: dict[str, Any],
    ) -> _FakeResponse:
        self.last_url = url
        self.last_json = json
        return _FakeResponse(self._payload)


def _build_payload(content: str) -> dict[str, Any]:
    return {"choices": [{"message": {"content": content}}]}


def test_require_api_key() -> None:
    with pytest.raises(ValueError, match="chat_llm_api_key"):
        DirectLLMAgent(base_url="https://x", model="m", api_key="")


def test_run_updates_java_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    java_src = "public class Foo {\n  public void bar() {}\n}\n"
    (tmp_path / "src/main/java/com/example").mkdir(parents=True)
    target = tmp_path / "src/main/java/com/example/Foo.java"
    target.write_text(java_src, encoding="utf-8")

    updated = "/** javadoc */\n" + java_src
    fake = _FakeClient(_build_payload(f"```java\n{updated}\n```"))
    monkeypatch.setattr(
        "celery_comment.direct_llm_agent.httpx.Client",
        lambda **_: fake,
    )

    agent = DirectLLMAgent(
        base_url="https://api.example.com/v1/",
        model="gpt-4o-mini",
        api_key="sk-x",
    )
    result = agent.run(
        work_dir=tmp_path,
        prompt="add javadoc",
        changed_files=["src/main/java/com/example/Foo.java"],
        rag_mcp_url="http://rag:9001",
    )
    assert result.exit_code == 0
    assert result.changed_files == ["src/main/java/com/example/Foo.java"]
    assert target.read_text(encoding="utf-8") == updated
    assert fake.last_url == "https://api.example.com/v1/chat/completions"
    assert fake.last_json is not None
    assert fake.last_json["model"] == "gpt-4o-mini"


def test_run_skips_non_java_and_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "a.txt").write_text("ignore me", encoding="utf-8")
    fake = _FakeClient(_build_payload("```java\nshould not be called\n```"))
    monkeypatch.setattr(
        "celery_comment.direct_llm_agent.httpx.Client",
        lambda **_: fake,
    )

    agent = DirectLLMAgent(base_url="https://x", model="m", api_key="sk-x")
    result = agent.run(
        work_dir=tmp_path,
        prompt="",
        changed_files=["a.txt", "does-not-exist.java"],
        rag_mcp_url="",
    )
    assert result.exit_code == 0
    assert result.changed_files == []
    assert fake.last_url is None


def test_run_leaves_file_untouched_when_no_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    java_src = "public class Same {}\n"
    target = tmp_path / "Same.java"
    target.write_text(java_src, encoding="utf-8")
    fake = _FakeClient(_build_payload(f"```java\n{java_src}\n```"))
    monkeypatch.setattr(
        "celery_comment.direct_llm_agent.httpx.Client",
        lambda **_: fake,
    )

    agent = DirectLLMAgent(base_url="https://x", model="m", api_key="sk-x")
    result = agent.run(
        work_dir=tmp_path,
        prompt="",
        changed_files=["Same.java"],
        rag_mcp_url="",
    )
    assert result.changed_files == []
    assert target.read_text(encoding="utf-8") == java_src


def test_run_skips_when_llm_returns_no_fenced_block(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "X.java").write_text("public class X {}\n", encoding="utf-8")
    fake = _FakeClient(_build_payload("no code here"))
    monkeypatch.setattr(
        "celery_comment.direct_llm_agent.httpx.Client",
        lambda **_: fake,
    )

    agent = DirectLLMAgent(base_url="https://x", model="m", api_key="sk-x")
    result = agent.run(
        work_dir=tmp_path,
        prompt="",
        changed_files=["X.java"],
        rag_mcp_url="",
    )
    assert result.changed_files == []


def test_extract_java_block_prefers_language_tag() -> None:
    text = "pre\n```java\nclass A {}\n```\npost"
    assert _extract_java_block(text) == "class A {}"


def test_extract_java_block_falls_back_to_generic() -> None:
    text = "pre\n```\nclass B {}\n```\n"
    assert _extract_java_block(text) == "class B {}"


def test_extract_java_block_returns_none_when_absent() -> None:
    assert _extract_java_block("just prose") is None
