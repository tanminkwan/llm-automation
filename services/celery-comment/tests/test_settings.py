"""T-08~T-09: CommentSettings 테스트."""

import pytest

from celery_comment.settings import CommentSettings


class TestCommentSettings:
    """T-08: env 주입, T-09: 기본값."""

    def test_env_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-08: 환경변수 주입."""
        monkeypatch.setenv("CELERY_BROKER_URL", "redis://remote:6379/5")
        monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://remote:6379/6")
        monkeypatch.setenv("COMMENT_WORK_DIR", "/opt/work")
        monkeypatch.setenv("RAG_MCP_URL", "http://rag:9001")
        monkeypatch.setenv("AGENT_RUNNER_KIND", "claude")
        monkeypatch.setenv("AGENT_TIMEOUT_SECONDS", "600")
        monkeypatch.setenv("GIT_COMMIT_AUTHOR", "Bot <b@b>")
        monkeypatch.setenv("GIT_CLIENT", "fixture")
        monkeypatch.setenv("FIXTURE_SOURCE_DIR", "/opt/fx/src")
        monkeypatch.setenv("FIXTURE_RESULT_DIR", "/opt/fx/res")
        s = CommentSettings()
        assert s.celery_broker_url == "redis://remote:6379/5"
        assert s.comment_work_dir == "/opt/work"
        assert s.agent_runner_kind == "claude"
        assert s.git_client == "fixture"
        assert s.fixture_source_dir == "/opt/fx/src"
        assert s.fixture_result_dir == "/opt/fx/res"

    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-09: 기본값."""
        for key in [
            "CELERY_BROKER_URL",
            "CELERY_RESULT_BACKEND",
            "COMMENT_WORK_DIR",
            "RAG_MCP_URL",
            "AGENT_RUNNER_KIND",
            "AGENT_TIMEOUT_SECONDS",
            "GIT_COMMIT_AUTHOR",
            "GIT_CLIENT",
            "FIXTURE_SOURCE_DIR",
            "FIXTURE_RESULT_DIR",
        ]:
            monkeypatch.delenv(key, raising=False)
        s = CommentSettings()
        assert s.celery_broker_url == "redis://localhost:6379/0"
        assert s.agent_timeout_seconds == 300
        assert s.git_client == "subprocess"
