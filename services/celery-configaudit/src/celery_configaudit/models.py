"""데이터 모델 -- TaskPayload, ToolCallRequest, AnalysisReport."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskPayload(BaseModel):
    """Celery 태스크 입력 페이로드."""

    work_id: str
    repo_url: str
    ref: str
    changed_files: list[str]


class ToolCallRequest(BaseModel):
    """LLM 이 반환한 tool call 요청."""

    name: str
    arguments: dict[str, Any]


class AnalysisReport(BaseModel):
    """최종 분석 보고서."""

    work_id: str
    case: str
    summary: str
    details: str
    anomalies: list[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
