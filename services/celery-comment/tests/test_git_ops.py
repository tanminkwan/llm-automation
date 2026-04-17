"""T-04~T-05: SubprocessGitClient 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from celery_comment.git_ops import SubprocessGitClient, _parse_author


class TestSubprocessGitClient:
    """T-04: clone, T-05: add_commit_push."""

    @patch("celery_comment.git_ops.subprocess.run")
    def test_clone(self, mock_run: MagicMock) -> None:
        """T-04: clone 호출 확인."""
        client = SubprocessGitClient()
        client.clone("http://gitea/repo.git", Path("/tmp/work/repo"), "refs/heads/main")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "git" in args
        assert "clone" in args
        assert "main" in args

    @patch("celery_comment.git_ops.subprocess.run")
    def test_add_commit_push(self, mock_run: MagicMock) -> None:
        """T-05: add → commit → push 3회 호출."""
        client = SubprocessGitClient(author="Test Bot <test@bot.com>")
        client.add_commit_push(Path("/tmp/repo"), "test msg", "main")
        assert mock_run.call_count == 3


class TestParseAuthor:
    """_parse_author 유틸."""

    def test_full_format(self) -> None:
        name, email = _parse_author("AI Bot <ai@local>")
        assert name == "AI Bot"
        assert email == "ai@local"

    def test_name_only(self) -> None:
        name, email = _parse_author("JustName")
        assert name == "JustName"
        assert email == "ai-bot@local"
