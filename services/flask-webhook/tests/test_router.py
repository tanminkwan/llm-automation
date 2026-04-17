"""T-03~T-06, T-16~T-17: 파일 분류 + Celery 발행 테스트."""

from flask_webhook.router import WorkType, classify_files, dispatch

from .conftest import FakeCelery


class TestClassifyFiles:
    """T-03~T-06: work_type 판별."""

    def test_java_files(self) -> None:
        """T-03: .java → COMMENT."""
        assert classify_files(["src/Main.java"]) == WorkType.COMMENT

    def test_httpm_files(self) -> None:
        """T-04: .httpm → CONFIGAUDIT."""
        assert classify_files(["config/server.httpm"]) == WorkType.CONFIGAUDIT

    def test_mixed_files(self) -> None:
        """T-05: 혼합 → CONFIGAUDIT 우선."""
        assert classify_files(["A.java", "cfg/http.m"]) == WorkType.CONFIGAUDIT

    def test_no_matching_files(self) -> None:
        """T-06: 해당 없는 파일 → None."""
        assert classify_files(["readme.md", "build.gradle"]) is None


class TestDispatch:
    """T-16~T-17: Celery 발행."""

    def test_dispatch_comment(self) -> None:
        """T-16: comment task 발행."""
        celery = FakeCelery()
        task_id = dispatch(
            celery,  # type: ignore[arg-type]
            WorkType.COMMENT,
            work_id="owner/repo:abc12345",
            repo_url="owner/repo",
            clone_url="http://gitea:3000/owner/repo.git",
            ref="refs/heads/main",
            changed_files=["src/Main.java"],
        )
        assert task_id == "fake-task-id-001"
        assert len(celery.sent) == 1
        assert celery.sent[0]["name"] == "comment.process"
        assert celery.sent[0]["queue"] == "comment_queue"

    def test_dispatch_configaudit(self) -> None:
        """T-17: configaudit task 발행."""
        celery = FakeCelery()
        task_id = dispatch(
            celery,  # type: ignore[arg-type]
            WorkType.CONFIGAUDIT,
            work_id="owner/repo:abc12345",
            repo_url="owner/repo",
            clone_url="http://gitea:3000/owner/repo.git",
            ref="refs/heads/main",
            changed_files=["cfg/http.m"],
        )
        assert task_id == "fake-task-id-001"
        assert celery.sent[0]["name"] == "configaudit.process"
        assert celery.sent[0]["queue"] == "configaudit_queue"
