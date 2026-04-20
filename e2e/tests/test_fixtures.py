"""오프라인 테스트 — fixture 파일의 구조적 유효성만 검증.

실제 stack/OpenAI 를 쓰지 않으므로 기본 실행에서 항상 수행.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema
from trigger_core import TriggerEvent


class TestScenarioATrigger:
    """scenario_A trigger.json 의 스키마 검증."""

    def test_parses_as_trigger_event(self, scenario_a_trigger: dict[str, Any]) -> None:
        event = TriggerEvent.model_validate(scenario_a_trigger)
        assert event.work_type.value == "comment"
        assert event.repo_ref.clone_url.startswith("fixture://scenario_A/")
        assert event.changed_files and all(f.endswith(".java") for f in event.changed_files)

    def test_before_tree_exists(self, fixtures_dir: Path) -> None:
        src = fixtures_dir / "scenario_A" / "before"
        assert src.is_dir()
        assert (src / "src" / "main" / "java" / "com" / "example" / "Calculator.java").is_file()


class TestScenarioBTrigger:
    """scenario_B case-001 trigger.json 검증."""

    def test_parses_as_trigger_event(self, scenario_b_trigger: dict[str, Any]) -> None:
        event = TriggerEvent.model_validate(scenario_b_trigger)
        assert event.work_type.value == "configaudit"
        assert event.changed_files == ["conf/http.m"]

    def test_report_schema_is_draft07(self, report_schema: dict[str, Any]) -> None:
        assert report_schema.get("$schema", "").endswith("draft-07/schema#")
        jsonschema.Draft7Validator.check_schema(report_schema)

    def test_schema_rejects_missing_required(self, report_schema: dict[str, Any]) -> None:
        validator = jsonschema.Draft7Validator(report_schema)
        errors = list(validator.iter_errors({"work_id": "x"}))
        assert errors, "스키마가 필수 필드 누락을 탐지해야 함"
