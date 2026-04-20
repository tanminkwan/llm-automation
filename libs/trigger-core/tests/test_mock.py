"""MockTriggerEmitter 단위 테스트."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from trigger_core import MockTriggerEmitter, RepoRef, TriggerEvent, WorkType


@dataclass
class _RecDispatcher:
    events: list[TriggerEvent] = field(default_factory=list)

    def dispatch(self, event: TriggerEvent) -> str:
        self.events.append(event)
        return f"t-{len(self.events)}"


def _event_dict() -> dict[str, Any]:
    return {
        "work_type": "comment",
        "work_id": "owner/repo:abcd1234",
        "repo_ref": {
            "full_name": "owner/repo",
            "clone_url": "fixture://scenario_A/before",
            "ref": "refs/heads/main",
        },
        "changed_files": ["src/A.java"],
        "meta": {"scenario": "A"},
    }


def test_emit_event_object() -> None:
    dispatcher = _RecDispatcher()
    emitter = MockTriggerEmitter(dispatcher)
    event = TriggerEvent(**_event_dict())

    task_id = emitter.emit(event)

    assert task_id == "t-1"
    assert dispatcher.events == [event]


def test_emit_from_dict() -> None:
    dispatcher = _RecDispatcher()
    emitter = MockTriggerEmitter(dispatcher)

    task_id = emitter.emit_from_dict(_event_dict())

    assert task_id == "t-1"
    assert dispatcher.events[0].work_type is WorkType.COMMENT
    assert dispatcher.events[0].meta == {"scenario": "A"}


def test_emit_from_json(tmp_path: Path) -> None:
    path = tmp_path / "trigger.json"
    path.write_text(json.dumps(_event_dict()), encoding="utf-8")

    dispatcher = _RecDispatcher()
    emitter = MockTriggerEmitter(dispatcher)

    task_id = emitter.emit_from_json(path)

    assert task_id == "t-1"
    assert dispatcher.events[0].repo_ref == RepoRef(
        full_name="owner/repo",
        clone_url="fixture://scenario_A/before",
        ref="refs/heads/main",
    )


def test_emit_from_json_accepts_str_path(tmp_path: Path) -> None:
    path = tmp_path / "trigger.json"
    path.write_text(json.dumps(_event_dict()), encoding="utf-8")

    dispatcher = _RecDispatcher()
    emitter = MockTriggerEmitter(dispatcher)

    emitter.emit_from_json(str(path))
    assert len(dispatcher.events) == 1
