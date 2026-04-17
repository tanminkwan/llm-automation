"""태스크 페이로드 + 결과 모델."""

from __future__ import annotations

from pydantic import BaseModel


class TaskPayload(BaseModel):
    """flask-webhook 에서 발행한 comment task 페이로드."""

    work_id: str
    repo_url: str
    clone_url: str
    ref: str
    changed_files: list[str]


class CommentResult(BaseModel):
    """태스크 실행 결과."""

    work_id: str
    status: str  # "success" | "no_changes" | "error"
    changed_files: list[str] = []
    message: str = ""
