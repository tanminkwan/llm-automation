"""Protocol 인터페이스 — GitClient, AgentRunner."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class GitClient(Protocol):
    """Git 작업 추상화."""

    def clone(self, url: str, dest: Path, ref: str) -> None:
        """원격 repo 를 dest 에 clone."""
        ...

    def add_commit_push(self, repo_dir: Path, message: str, branch: str) -> None:
        """변경 파일 add → commit → push."""
        ...


class AgentExecutor(Protocol):
    """AI Agent 실행 추상화 (libs/agent-runner 와 유사)."""

    def run(
        self,
        *,
        work_dir: Path,
        prompt: str,
        changed_files: list[str],
        rag_mcp_url: str,
    ) -> AgentExecResult:
        """Agent 실행 → 결과 반환."""
        ...


class AgentExecResult(Protocol):
    """Agent 실행 결과."""

    @property
    def exit_code(self) -> int: ...

    @property
    def changed_files(self) -> list[str]: ...

    @property
    def stdout(self) -> str: ...
