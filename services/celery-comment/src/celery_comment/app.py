"""Celery app 인스턴스 + task 등록."""

from __future__ import annotations

from celery import Celery  # type: ignore[import-untyped]

from .factory import build_git_client
from .settings import CommentSettings


def create_celery_app(settings: CommentSettings | None = None) -> Celery:
    """Celery app 팩토리."""
    _settings = settings or CommentSettings()
    app = Celery(
        "comment",
        broker=_settings.celery_broker_url,
        backend=_settings.celery_result_backend,
    )
    app.conf.task_default_queue = "comment_queue"
    return app


# pragma: no cover — 운영 진입점
def _build_app() -> Celery:  # pragma: no cover
    """운영용 Celery app 조립 — GIT_CLIENT 값에 따라 구현체 선택."""
    from .task import create_celery_task

    settings = CommentSettings()
    app = create_celery_app(settings)
    git_client = build_git_client(settings)
    # AgentRunner 는 host subprocess — 여기서는 stub
    # 실제 연동은 E2E Phase 에서 완성
    create_celery_task(
        app,
        git_client=git_client,
        agent=None,
        rag_mcp_url=settings.rag_mcp_url,
        work_dir_base=settings.comment_work_dir,
    )
    return app


celery_app = create_celery_app()
