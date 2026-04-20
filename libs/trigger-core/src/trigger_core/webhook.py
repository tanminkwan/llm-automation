"""WebhookTriggerSource — HTTP webhook 원시 요청 → TriggerEvent."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from .errors import (
    InvalidPayloadError,
    InvalidSignatureError,
    UnsupportedWorkTypeError,
)
from .hmac_verify import verify_signature
from .models import RepoRef, TriggerEvent
from .routing import classify_files

DEFAULT_SIGNATURE_HEADER = "X-Gitea-Signature"
DEFAULT_DELIVERY_HEADER = "X-Gitea-Delivery"


class _PushCommit(BaseModel):
    id: str
    message: str = ""
    added: list[str] = []
    removed: list[str] = []
    modified: list[str] = []


class _GiteaPushPayload(BaseModel):
    """Gitea push webhook payload (내부 파싱용)."""

    ref: str
    after: str
    repository: dict[str, Any]
    commits: list[_PushCommit] = []

    def all_changed(self) -> list[str]:
        files: set[str] = set()
        for c in self.commits:
            files.update(c.added)
            files.update(c.modified)
        return sorted(files)


class WebhookTriggerSource:
    """HTTP webhook 원시 요청을 TriggerEvent 로 변환하는 TriggerSource 구현체.

    검증 순서: HMAC 서명 → payload 파싱 → work_type 판별 → TriggerEvent 생성.
    """

    def __init__(
        self,
        *,
        secret: str,
        signature_header: str = DEFAULT_SIGNATURE_HEADER,
        delivery_header: str = DEFAULT_DELIVERY_HEADER,
    ) -> None:
        self._secret = secret
        self._signature_header = signature_header
        self._delivery_header = delivery_header

    def parse(self, raw: bytes, headers: Mapping[str, str]) -> TriggerEvent:
        signature = headers.get(self._signature_header, "")
        if not verify_signature(raw, signature, self._secret):
            raise InvalidSignatureError("HMAC signature mismatch")

        try:
            data = json.loads(raw or b"{}")
            payload = _GiteaPushPayload(**data)
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            raise InvalidPayloadError(f"cannot parse webhook payload: {exc}") from exc

        changed = payload.all_changed()
        work_type = classify_files(changed)
        if work_type is None:
            raise UnsupportedWorkTypeError("no matching changed files")

        repo_full_name = str(payload.repository.get("full_name", ""))
        clone_url = str(payload.repository.get("clone_url", ""))
        short = payload.after[:8]
        work_id = f"{repo_full_name}:{short}"

        return TriggerEvent(
            work_type=work_type,
            work_id=work_id,
            repo_ref=RepoRef(
                full_name=repo_full_name,
                clone_url=clone_url,
                ref=payload.ref,
            ),
            changed_files=changed,
            meta={"delivery_id": headers.get(self._delivery_header, "")},
        )
