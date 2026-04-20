"""시나리오 B — ConfigAudit E2E.

실제 docker stack + configaudit-mcp + OpenAI 필요. ``E2E_ENABLED=1`` 미설정이면 skip.
리포트 파일은 JSON 스키마 + 필수 필드 non-empty 로만 검증 (LLM 자연어 변동 흡수).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from celery import Celery  # type: ignore[import-untyped]
from trigger_core import CeleryTriggerDispatcher, MockTriggerEmitter, TriggerEvent

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def _guard() -> None:
    if os.getenv("E2E_ENABLED") != "1":
        pytest.skip("E2E disabled — set E2E_ENABLED=1 with stack + OpenAI to run")


def _find_report(report_root: Path, work_id: str) -> Path | None:
    if not report_root.is_dir():
        return None
    candidates = list(report_root.rglob("*.md")) + list(report_root.rglob("*.json"))
    for p in candidates:
        if work_id.replace(":", "_") in str(p) or work_id in p.read_text(
            encoding="utf-8", errors="ignore"
        ):
            return p
    return None


def test_scenario_b_configaudit_report(
    _guard: None,
    scenario_b_trigger: dict[str, Any],
    report_schema: dict[str, Any],
) -> None:
    broker = os.getenv("E2E_BROKER_URL", "redis://localhost:6379/0")
    report_root = Path(os.environ["REPORT_OUTPUT_DIR"])
    task_timeout = int(os.getenv("E2E_TASK_TIMEOUT", "180"))

    celery = Celery(broker=broker)
    dispatcher = CeleryTriggerDispatcher(celery)
    emitter = MockTriggerEmitter(dispatcher)

    event = TriggerEvent.model_validate(scenario_b_trigger)
    task_id = emitter.emit(event)
    assert task_id

    deadline = time.time() + task_timeout
    report_path: Path | None = None
    while time.time() < deadline:
        report_path = _find_report(report_root, event.work_id)
        if report_path is not None:
            break
        time.sleep(2)
    assert report_path is not None, "worker did not produce report in time"

    if report_path.suffix == ".json":
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        sidecar = report_path.with_suffix(".json")
        if not sidecar.is_file():
            pytest.skip(f"report is markdown and no JSON sidecar at {sidecar}")
        report = json.loads(sidecar.read_text(encoding="utf-8"))

    jsonschema.Draft7Validator(report_schema).validate(report)
    assert str(report["summary"]).strip(), "summary must be non-empty"
    assert isinstance(report["anomalies"], list)
