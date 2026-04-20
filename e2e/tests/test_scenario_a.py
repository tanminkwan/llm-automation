"""시나리오 A — Java 주석 자동화 E2E.

실제 docker stack + OpenAI 필요. ``E2E_ENABLED=1`` 미설정이면 skip.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest
from celery import Celery  # type: ignore[import-untyped]
from trigger_core import CeleryTriggerDispatcher, MockTriggerEmitter, TriggerEvent

pytestmark = pytest.mark.e2e

JAVADOC_MARKER = "/**"


@pytest.fixture(scope="module")
def _guard() -> None:
    if os.getenv("E2E_ENABLED") != "1":
        pytest.skip("E2E disabled — set E2E_ENABLED=1 with stack + OpenAI to run")


def _count_javadoc_blocks(path: Path) -> int:
    return path.read_text(encoding="utf-8").count(JAVADOC_MARKER)


def _find_snapshot(result_root: Path, branch: str) -> Path:
    branch_dir = result_root / branch
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"no snapshots under {branch_dir}")
    snaps = sorted(branch_dir.iterdir(), key=lambda p: p.name)
    if not snaps:
        raise FileNotFoundError(f"empty branch dir {branch_dir}")
    return snaps[-1]


def test_scenario_a_java_comment_roundtrip(
    _guard: None,
    scenario_a_trigger: dict[str, Any],
    fixtures_dir: Path,
) -> None:
    broker = os.getenv("E2E_BROKER_URL", "redis://localhost:6379/0")
    result_root = Path(os.environ["FIXTURE_RESULT_DIR"])
    task_timeout = int(os.getenv("E2E_TASK_TIMEOUT", "180"))

    celery = Celery(broker=broker)
    dispatcher = CeleryTriggerDispatcher(celery)
    emitter = MockTriggerEmitter(dispatcher)

    event = TriggerEvent.model_validate(scenario_a_trigger)
    task_id = emitter.emit(event)
    assert task_id

    before_path = (
        fixtures_dir
        / "scenario_A"
        / "before"
        / "src"
        / "main"
        / "java"
        / "com"
        / "example"
        / "Calculator.java"
    )
    before_count = _count_javadoc_blocks(before_path)
    branch = event.repo_ref.ref.split("/")[-1]

    deadline = time.time() + task_timeout
    snapshot: Path | None = None
    while time.time() < deadline:
        try:
            snapshot = _find_snapshot(result_root, branch)
            break
        except FileNotFoundError:
            time.sleep(2)
    assert snapshot is not None, "worker did not produce snapshot in time"

    after_path = snapshot / "src" / "main" / "java" / "com" / "example" / "Calculator.java"
    assert after_path.is_file()
    after_count = _count_javadoc_blocks(after_path)
    assert after_count > before_count, (
        f"javadoc blocks did not increase: before={before_count} after={after_count}"
    )

    manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["branch"] == branch
    assert event.work_id in manifest["message"]
