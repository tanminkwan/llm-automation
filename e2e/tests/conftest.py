"""E2E conftest — 공통 fixture.

실제 docker stack + OpenAI 가 필요한 시나리오 테스트는
``@pytest.mark.e2e`` + ``E2E_ENABLED=1`` 환경변수 없으면 skip.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
E2E_ROOT = HERE.parent
FIXTURES_DIR = E2E_ROOT / "fixtures"


def _e2e_enabled() -> bool:
    return os.getenv("E2E_ENABLED") == "1"


@pytest.fixture(scope="session")
def e2e_enabled() -> bool:
    return _e2e_enabled()


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def scenario_a_trigger(fixtures_dir: Path) -> dict[str, object]:
    raw = (fixtures_dir / "scenario_A" / "trigger.json").read_text(encoding="utf-8")
    data: dict[str, object] = json.loads(raw)
    return data


@pytest.fixture(scope="session")
def scenario_b_trigger(fixtures_dir: Path) -> dict[str, object]:
    raw = (fixtures_dir / "scenario_B" / "case-001" / "trigger.json").read_text(encoding="utf-8")
    data: dict[str, object] = json.loads(raw)
    return data


@pytest.fixture(scope="session")
def report_schema(fixtures_dir: Path) -> dict[str, object]:
    raw = (fixtures_dir / "scenario_B" / "case-001" / "expected" / "report.schema.json").read_text(
        encoding="utf-8"
    )
    data: dict[str, object] = json.loads(raw)
    return data


def _skip_if_disabled() -> None:
    if not _e2e_enabled():
        pytest.skip("E2E disabled — set E2E_ENABLED=1 with stack + OpenAI to run")
