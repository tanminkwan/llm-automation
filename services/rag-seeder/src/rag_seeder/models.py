"""데이터 모델 — Snippet (코퍼스 항목) + SeedResult (실행 결과)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Snippet(BaseModel):
    """코퍼스 snippet 한 건 — YAML 에서 로드."""

    id: str
    path: str
    symbol: str
    line_range: list[int]
    comment: str
    repo: str = Field(default="seed-repo")


class SeedResult(BaseModel):
    """시딩 실행 결과 요약."""

    total_loaded: int
    total_embedded: int
    total_upserted: int
    errors: int
    duration_seconds: float
