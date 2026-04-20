"""Celery app 인스턴스 + task 등록."""

from __future__ import annotations

from celery import Celery  # type: ignore[import-untyped]

from .factory import build_agent_executor, build_git_client
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


def build_worker_app() -> Celery:
    """운영용 Celery app 조립 — env 기반 GitClient + AgentExecutor 주입.

    워커 부팅 시점에만 호출된다 (``celery_comment.worker`` 모듈에서 사용).
    테스트에서는 import 부작용이 없도록 별도 모듈로 분리했다.
    """
    from .task import create_celery_task

    settings = CommentSettings()
    app = create_celery_app(settings)
    create_celery_task(
        app,
        git_client=build_git_client(settings),
        agent=build_agent_executor(settings),
        rag_mcp_url=settings.rag_mcp_url,
        work_dir_base=settings.comment_work_dir,
    )
    return app


celery_app = create_celery_app()
