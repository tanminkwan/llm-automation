"""Trigger 도메인 모델 — SCM/이벤트 소스에 중립."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkType(StrEnum):
    """변경 파일 유형 — 발행할 Celery 태스크 결정."""

    COMMENT = "comment"
    CONFIGAUDIT = "configaudit"


class RepoRef(BaseModel):
    """저장소 참조. clone_url 은 fixture 모드에서 ``fixture://<key>`` 형식도 허용."""

    full_name: str
    clone_url: str
    ref: str


class TriggerEvent(BaseModel):
    """이벤트 소스에 무관한 작업 트리거.

    ``meta`` 는 추적/로깅 용 부가 정보 (delivery_id 등) — 워커 태스크 kwargs 에 미포함.
    """

    work_type: WorkType
    work_id: str
    repo_ref: RepoRef
    changed_files: list[str]
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_task_kwargs(self) -> dict[str, Any]:
        """기존 워커(celery-comment / celery-configaudit) 시그니처에 맞춘 kwargs 로 변환."""
        return {
            "work_id": self.work_id,
            "repo_url": self.repo_ref.full_name,
            "clone_url": self.repo_ref.clone_url,
            "ref": self.repo_ref.ref,
            "changed_files": list(self.changed_files),
        }
