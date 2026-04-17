"""Webhook 페이로드 모델."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PushCommit(BaseModel):
    """Gitea push event 의 커밋 한 건."""

    id: str
    message: str
    added: list[str] = []
    removed: list[str] = []
    modified: list[str] = []


class WebhookPayload(BaseModel):
    """Gitea push webhook 페이로드."""

    ref: str
    after: str
    repository: dict[str, Any]
    commits: list[PushCommit] = []

    def all_changed_files(self) -> list[str]:
        """모든 커밋의 변경 파일 목록 (중복 제거)."""
        files: set[str] = set()
        for c in self.commits:
            files.update(c.added)
            files.update(c.modified)
        return sorted(files)

    @property
    def repo_full_name(self) -> str:
        """repository.full_name 반환."""
        return str(self.repository.get("full_name", ""))

    @property
    def clone_url(self) -> str:
        """repository.clone_url 반환."""
        return str(self.repository.get("clone_url", ""))
