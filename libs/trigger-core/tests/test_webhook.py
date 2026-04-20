"""WebhookTriggerSource 단위 테스트."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

import pytest

from trigger_core import (
    InvalidPayloadError,
    InvalidSignatureError,
    RepoRef,
    UnsupportedWorkTypeError,
    WebhookTriggerSource,
    WorkType,
)


def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def _gitea_push(
    *,
    added: list[str] | None = None,
    modified: list[str] | None = None,
    after: str = "abcdef1234567890",
) -> dict[str, Any]:
    return {
        "ref": "refs/heads/main",
        "after": after,
        "repository": {
            "full_name": "demo/seed-repo",
            "clone_url": "http://gitea:3000/demo/seed-repo.git",
        },
        "commits": [
            {
                "id": "c1",
                "message": "m",
                "added": added or [],
                "removed": [],
                "modified": modified or [],
            }
        ],
    }


def test_parse_ok_comment() -> None:
    secret = "s"
    data = _gitea_push(added=["src/Foo.java"])
    raw = json.dumps(data).encode()
    source = WebhookTriggerSource(secret=secret)

    event = source.parse(
        raw,
        {"X-Gitea-Signature": _sign(raw, secret), "X-Gitea-Delivery": "d-1"},
    )

    assert event.work_type is WorkType.COMMENT
    assert event.work_id == "demo/seed-repo:abcdef12"
    assert event.repo_ref == RepoRef(
        full_name="demo/seed-repo",
        clone_url="http://gitea:3000/demo/seed-repo.git",
        ref="refs/heads/main",
    )
    assert event.changed_files == ["src/Foo.java"]
    assert event.meta["delivery_id"] == "d-1"


def test_parse_mixed_prefers_configaudit() -> None:
    secret = "s"
    data = _gitea_push(modified=["src/Foo.java", "conf/http.m"])
    raw = json.dumps(data).encode()
    source = WebhookTriggerSource(secret=secret)

    event = source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})

    assert event.work_type is WorkType.CONFIGAUDIT
    assert event.changed_files == ["conf/http.m", "src/Foo.java"]


def test_missing_delivery_header_defaults_to_empty() -> None:
    secret = "s"
    data = _gitea_push(added=["x.java"])
    raw = json.dumps(data).encode()
    source = WebhookTriggerSource(secret=secret)

    event = source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})

    assert event.meta["delivery_id"] == ""


def test_invalid_signature_raises() -> None:
    source = WebhookTriggerSource(secret="s")
    with pytest.raises(InvalidSignatureError):
        source.parse(b'{"a":1}', {"X-Gitea-Signature": "bad"})


def test_missing_signature_header_raises() -> None:
    source = WebhookTriggerSource(secret="s")
    with pytest.raises(InvalidSignatureError):
        source.parse(b'{"a":1}', {})


def test_invalid_payload_not_json() -> None:
    secret = "s"
    raw = b"not json"
    source = WebhookTriggerSource(secret=secret)
    with pytest.raises(InvalidPayloadError):
        source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})


def test_invalid_payload_schema_mismatch() -> None:
    secret = "s"
    raw = b'{"not_expected": true}'
    source = WebhookTriggerSource(secret=secret)
    with pytest.raises(InvalidPayloadError):
        source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})


def test_unsupported_work_type_when_no_matching_files() -> None:
    secret = "s"
    data = _gitea_push(added=["README.md"])
    raw = json.dumps(data).encode()
    source = WebhookTriggerSource(secret=secret)

    with pytest.raises(UnsupportedWorkTypeError):
        source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})


def test_custom_signature_and_delivery_headers() -> None:
    secret = "s"
    data = _gitea_push(added=["x.java"])
    raw = json.dumps(data).encode()
    source = WebhookTriggerSource(
        secret=secret,
        signature_header="X-Custom-Sig",
        delivery_header="X-Custom-Delivery",
    )

    event = source.parse(
        raw,
        {
            "X-Custom-Sig": _sign(raw, secret),
            "X-Custom-Delivery": "d-42",
        },
    )
    assert event.work_type is WorkType.COMMENT
    assert event.meta["delivery_id"] == "d-42"


def test_empty_raw_body_rejected_by_schema() -> None:
    secret = "s"
    raw = b""
    source = WebhookTriggerSource(secret=secret)
    with pytest.raises(InvalidPayloadError):
        source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})


def test_work_id_short_after_hash() -> None:
    secret = "s"
    data = _gitea_push(added=["a.java"], after="1234567890abcdef")
    raw = json.dumps(data).encode()
    source = WebhookTriggerSource(secret=secret)
    event = source.parse(raw, {"X-Gitea-Signature": _sign(raw, secret)})
    assert event.work_id == "demo/seed-repo:12345678"
