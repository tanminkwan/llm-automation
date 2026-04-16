"""leebalso-mock 응답 데이터 모델."""

from __future__ import annotations

from pydantic import BaseModel


class FixtureMeta(BaseModel):
    """fixture 메타 정보."""

    fixture: str
    version: str


class ConfigResponse(BaseModel):
    """GET /config/httpm 응답."""

    env: str
    before: str
    after: str
    meta: FixtureMeta
