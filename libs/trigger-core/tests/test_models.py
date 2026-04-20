"""TriggerEvent / RepoRef / WorkType 단위 테스트."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from trigger_core import RepoRef, TriggerEvent, WorkType


def test_work_type_values() -> None:
    assert WorkType.COMMENT.value == "comment"
    assert WorkType.CONFIGAUDIT.value == "configaudit"


def test_trigger_event_to_task_kwargs() -> None:
    event = TriggerEvent(
        work_type=WorkType.COMMENT,
        work_id="owner/repo:abcdef12",
        repo_ref=RepoRef(
            full_name="owner/repo",
            clone_url="https://example.com/repo.git",
            ref="refs/heads/main",
        ),
        changed_files=["src/A.java"],
        meta={"delivery_id": "d-1"},
    )

    kwargs = event.to_task_kwargs()

    assert kwargs == {
        "work_id": "owner/repo:abcdef12",
        "repo_url": "owner/repo",
        "clone_url": "https://example.com/repo.git",
        "ref": "refs/heads/main",
        "changed_files": ["src/A.java"],
    }
    # meta 는 kwargs 에 노출되지 않는다 (추적/로깅 전용).
    assert "meta" not in kwargs


def test_trigger_event_requires_valid_work_type() -> None:
    with pytest.raises(ValidationError):
        TriggerEvent(
            work_type="unknown",  # type: ignore[arg-type]
            work_id="x",
            repo_ref=RepoRef(full_name="a/b", clone_url="", ref="r"),
            changed_files=[],
        )


def test_trigger_event_meta_default_empty() -> None:
    event = TriggerEvent(
        work_type=WorkType.COMMENT,
        work_id="x",
        repo_ref=RepoRef(full_name="a/b", clone_url="", ref="r"),
        changed_files=[],
    )
    assert event.meta == {}


def test_task_kwargs_changed_files_is_copy() -> None:
    event = TriggerEvent(
        work_type=WorkType.COMMENT,
        work_id="x",
        repo_ref=RepoRef(full_name="a/b", clone_url="", ref="r"),
        changed_files=["a.java"],
    )
    kwargs = event.to_task_kwargs()
    kwargs["changed_files"].append("b.java")
    assert event.changed_files == ["a.java"]
