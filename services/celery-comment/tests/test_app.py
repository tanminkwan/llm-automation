"""T-11: Celery app 테스트."""

from celery_comment.app import create_celery_app
from celery_comment.settings import CommentSettings


class TestCeleryApp:
    """T-11: Celery app 생성."""

    def test_create_app(self) -> None:
        """Celery app 인스턴스 생성 확인."""
        settings = CommentSettings()
        app = create_celery_app(settings)
        assert app.main == "comment"
        assert app.conf.task_default_queue == "comment_queue"
