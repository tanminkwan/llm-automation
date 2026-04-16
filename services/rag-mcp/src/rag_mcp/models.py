"""데이터 모델 — SearchHit, SearchResult, SearchRequest."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    """Qdrant 검색 결과 한 건."""

    id: str
    path: str
    symbol: str
    line_range: list[int]
    comment: str
    score: float


class SearchResult(BaseModel):
    """search_codebase 응답."""

    query: str
    hits: list[SearchHit]


class SearchRequest(BaseModel):
    """search_codebase 요청."""

    query: str = Field(..., min_length=1)
    k: int | None = None
