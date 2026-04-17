"""T-07: 모델 테스트."""

from celery_comment.models import CommentResult, TaskPayload


class TestModels:
    """T-07: TaskPayload, CommentResult."""

    def test_task_payload(self) -> None:
        p = TaskPayload(
            work_id="a/b:abc",
            repo_url="a/b",
            clone_url="http://git/a/b.git",
            ref="refs/heads/main",
            changed_files=["A.java"],
        )
        assert p.work_id == "a/b:abc"

    def test_comment_result_defaults(self) -> None:
        r = CommentResult(work_id="a", status="success")
        assert r.changed_files == []
        assert r.message == ""

    def test_comment_result_full(self) -> None:
        r = CommentResult(
            work_id="a",
            status="success",
            changed_files=["X.java"],
            message="done",
        )
        assert r.changed_files == ["X.java"]
