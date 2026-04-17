"""T-01~T-03: process_comment 태스크 테스트."""

from __future__ import annotations

import tempfile

import pytest

from celery_comment.models import TaskPayload
from celery_comment.task import process_comment

from .conftest import FailingAgent, FakeAgent, FakeGitClient, NoChangeAgent


class TestProcessComment:
    """T-01: happy path, T-02: agent 실패, T-03: 변경 없음."""

    def test_happy_path(self, sample_payload: TaskPayload) -> None:
        """T-01: agent 성공 + 변경 있음 → commit/push."""
        git = FakeGitClient()
        agent = FakeAgent()
        with tempfile.TemporaryDirectory() as work_dir:
            result = process_comment(
                payload=sample_payload,
                git_client=git,
                agent=agent,
                rag_mcp_url="http://rag:9001",
                work_dir_base=work_dir,
            )
        assert result.status == "success"
        assert result.changed_files == ["src/Main.java"]
        assert len(git.cloned) == 1
        assert len(git.pushed) == 1
        assert "[skip ci]" in git.pushed[0]["message"]

    def test_agent_failure(self, sample_payload: TaskPayload) -> None:
        """T-02: agent exit_code != 0 → error."""
        git = FakeGitClient()
        agent = FailingAgent()
        with tempfile.TemporaryDirectory() as work_dir:
            result = process_comment(
                payload=sample_payload,
                git_client=git,
                agent=agent,
                rag_mcp_url="http://rag:9001",
                work_dir_base=work_dir,
            )
        assert result.status == "error"
        assert "exit code" in result.message.lower()
        assert len(git.pushed) == 0

    def test_no_changes(self, sample_payload: TaskPayload) -> None:
        """T-03: 변경 파일 없음 → no_changes."""
        git = FakeGitClient()
        agent = NoChangeAgent()
        with tempfile.TemporaryDirectory() as work_dir:
            result = process_comment(
                payload=sample_payload,
                git_client=git,
                agent=agent,
                rag_mcp_url="http://rag:9001",
                work_dir_base=work_dir,
            )
        assert result.status == "no_changes"
        assert len(git.pushed) == 0

    def test_exception_propagation(self, sample_payload: TaskPayload) -> None:
        """clone 예외 시 propagation."""

        class ErrorGit:
            def clone(self, *a: object, **k: object) -> None:
                raise ConnectionError("git clone failed")

            def add_commit_push(self, *a: object, **k: object) -> None:
                pass

        with tempfile.TemporaryDirectory() as work_dir:
            with pytest.raises(ConnectionError, match="git clone failed"):
                process_comment(
                    payload=sample_payload,
                    git_client=ErrorGit(),
                    agent=FakeAgent(),
                    rag_mcp_url="http://rag:9001",
                    work_dir_base=work_dir,
                )
