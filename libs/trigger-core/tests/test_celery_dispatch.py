"""CeleryTriggerDispatcher 단위 테스트."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from trigger_core import (
    CeleryTriggerDispatcher,
    RepoRef,
    TriggerEvent,
    UnsupportedWorkTypeError,
    WorkType,
)


@dataclass
class _AsyncResult:
    id: str


@dataclass
class _FakeCelery:
    calls: list[dict[str, Any]] = field(default_factory=list)

    def send_task(
        self,
        name: str,
        *,
        kwargs: dict[str, Any],
        queue: str,
    ) -> _AsyncResult:
        self.calls.append({"name": name, "kwargs": kwargs, "queue": queue})
        return _AsyncResult(id=f"task-{len(self.calls)}")


def _event(
    work_type: WorkType = WorkType.COMMENT,
    files: list[str] | None = None,
) -> TriggerEvent:
    return TriggerEvent(
        work_type=work_type,
        work_id="owner/repo:abcd1234",
        repo_ref=RepoRef(
            full_name="owner/repo",
            clone_url="http://x",
            ref="refs/heads/main",
        ),
        changed_files=files or ["a.java"],
        meta={"delivery_id": "d"},
    )


def test_dispatch_comment_default_map() -> None:
    fake = _FakeCelery()
    dispatcher = CeleryTriggerDispatcher(fake)

    task_id = dispatcher.dispatch(_event(WorkType.COMMENT))

    assert task_id == "task-1"
    assert fake.calls == [
        {
            "name": "comment.process",
            "queue": "comment_queue",
            "kwargs": {
                "work_id": "owner/repo:abcd1234",
                "repo_url": "owner/repo",
                "clone_url": "http://x",
                "ref": "refs/heads/main",
                "changed_files": ["a.java"],
            },
        }
    ]


def test_dispatch_configaudit_default_map() -> None:
    fake = _FakeCelery()
    dispatcher = CeleryTriggerDispatcher(fake)

    dispatcher.dispatch(_event(WorkType.CONFIGAUDIT, files=["http.m"]))

    assert fake.calls[0]["name"] == "configaudit.process"
    assert fake.calls[0]["queue"] == "configaudit_queue"


def test_custom_task_map_overrides_default() -> None:
    fake = _FakeCelery()
    dispatcher = CeleryTriggerDispatcher(
        fake,
        task_map={WorkType.COMMENT: ("custom.task", "custom_q")},
    )

    dispatcher.dispatch(_event(WorkType.COMMENT))

    assert fake.calls[0]["name"] == "custom.task"
    assert fake.calls[0]["queue"] == "custom_q"


def test_missing_mapping_raises_unsupported() -> None:
    fake = _FakeCelery()
    dispatcher = CeleryTriggerDispatcher(fake, task_map={})

    with pytest.raises(UnsupportedWorkTypeError):
        dispatcher.dispatch(_event(WorkType.COMMENT))

    # 태스크가 발행되지 않았음을 확인
    assert fake.calls == []


def test_custom_task_map_is_copied() -> None:
    fake = _FakeCelery()
    source_map = {WorkType.COMMENT: ("a", "b")}
    dispatcher = CeleryTriggerDispatcher(fake, task_map=source_map)

    # 원본 맵 변이가 dispatcher 내부 상태에 영향 없어야 함
    source_map[WorkType.CONFIGAUDIT] = ("c", "d")
    with pytest.raises(UnsupportedWorkTypeError):
        dispatcher.dispatch(_event(WorkType.CONFIGAUDIT, files=["http.m"]))
