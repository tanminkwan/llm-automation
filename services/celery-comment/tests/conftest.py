"""공유 fixture — FakeAgent, FakeGitClient."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from celery_comment.models import TaskPayload
from celery_comment.settings import CommentSettings


@dataclass
class FakeAgentResult:
    """AgentExecResult 프로토콜 구현."""

    exit_code: int = 0
    changed_files: list[str] = field(default_factory=lambda: ["src/Main.java"])
    stdout: str = "ok"


class FakeAgent:
    """AgentExecutor 프로토콜 구현."""

    def __init__(self, result: FakeAgentResult | None = None) -> None:
        self._result = result or FakeAgentResult()
        self.calls: list[dict[str, Any]] = []

    def run(
        self,
        *,
        work_dir: Path,
        prompt: str,
        changed_files: list[str],
        rag_mcp_url: str,
    ) -> FakeAgentResult:
        self.calls.append(
            {
                "work_dir": work_dir,
                "prompt": prompt,
                "changed_files": changed_files,
                "rag_mcp_url": rag_mcp_url,
            }
        )
        return self._result


class FailingAgent:
    """항상 exit_code=1 반환."""

    def run(self, **kwargs: Any) -> FakeAgentResult:
        return FakeAgentResult(exit_code=1, changed_files=[], stdout="error")


class NoChangeAgent:
    """exit_code=0 이지만 변경 파일 없음."""

    def run(self, **kwargs: Any) -> FakeAgentResult:
        return FakeAgentResult(exit_code=0, changed_files=[], stdout="no changes")


class FakeGitClient:
    """GitClient 프로토콜 구현."""

    def __init__(self) -> None:
        self.cloned: list[dict[str, Any]] = []
        self.pushed: list[dict[str, Any]] = []

    def clone(self, url: str, dest: Path, ref: str) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        self.cloned.append({"url": url, "dest": dest, "ref": ref})

    def add_commit_push(self, repo_dir: Path, message: str, branch: str) -> None:
        self.pushed.append({"repo_dir": repo_dir, "message": message, "branch": branch})


@pytest.fixture()
def sample_payload() -> TaskPayload:
    return TaskPayload(
        work_id="owner/repo:abc12345",
        repo_url="owner/repo",
        clone_url="http://gitea:3000/owner/repo.git",
        ref="refs/heads/main",
        changed_files=["src/Main.java"],
    )


@pytest.fixture()
def settings() -> CommentSettings:
    return CommentSettings()
