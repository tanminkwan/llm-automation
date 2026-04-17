"""celery-comment — 코드 주석 자동화 Celery 워커."""

from .app import celery_app, create_celery_app
from .git_ops import SubprocessGitClient
from .models import CommentResult, TaskPayload
from .prompt import build_prompt
from .protocols import AgentExecResult, AgentExecutor, GitClient
from .settings import CommentSettings
from .task import create_celery_task, process_comment

__all__ = [
    "AgentExecResult",
    "AgentExecutor",
    "CommentResult",
    "CommentSettings",
    "GitClient",
    "SubprocessGitClient",
    "TaskPayload",
    "build_prompt",
    "celery_app",
    "create_celery_app",
    "create_celery_task",
    "process_comment",
]
