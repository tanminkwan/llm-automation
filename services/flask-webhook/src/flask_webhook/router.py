"""work_type 판별 + Celery task 발행."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from celery import Celery  # type: ignore[import-untyped]


class WorkType(StrEnum):
    """변경 파일 유형."""

    COMMENT = "comment"
    CONFIGAUDIT = "configaudit"


_JAVA_EXTS = {".java"}
_HTTPM_NAMES = {"http.m", ".httpm"}


def classify_files(files: list[str]) -> WorkType | None:
    """변경 파일 목록에서 work_type 판별.

    혼합 시 우선순위: CONFIGAUDIT > COMMENT.
    해당 없으면 None.
    """
    has_java = False
    has_httpm = False

    for f in files:
        lower = f.lower()
        if any(lower.endswith(ext) for ext in _JAVA_EXTS):
            has_java = True
        if any(lower.endswith(name) for name in _HTTPM_NAMES):
            has_httpm = True

    if has_httpm:
        return WorkType.CONFIGAUDIT
    if has_java:
        return WorkType.COMMENT
    return None


_TASK_MAP: dict[WorkType, tuple[str, str]] = {
    WorkType.COMMENT: ("comment.process", "comment_queue"),
    WorkType.CONFIGAUDIT: ("configaudit.process", "configaudit_queue"),
}


def dispatch(
    celery_app: Celery,
    work_type: WorkType,
    *,
    work_id: str,
    repo_url: str,
    clone_url: str,
    ref: str,
    changed_files: list[str],
) -> str:
    """Celery send_task 로 큐에 발행. task_id 반환."""
    task_name, queue = _TASK_MAP[work_type]
    payload: dict[str, Any] = {
        "work_id": work_id,
        "repo_url": repo_url,
        "clone_url": clone_url,
        "ref": ref,
        "changed_files": changed_files,
    }
    result = celery_app.send_task(task_name, kwargs=payload, queue=queue)
    return str(result.id)
