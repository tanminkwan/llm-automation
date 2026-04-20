"""``emit_trigger.py`` CLI — fake Celery 로 구조적 동작 검증 (offline)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="module")
def emit_module() -> Any:
    path = Path(__file__).resolve().parents[1] / "bin" / "emit_trigger.py"
    spec = importlib.util.spec_from_file_location("emit_trigger", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeCelery:
    """send_task 호출을 기록하는 celery 대역."""

    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    def send_task(self, name: str, *, kwargs: dict[str, Any] | None = None, queue: str = "") -> Any:
        self.sent.append({"name": name, "kwargs": kwargs, "queue": queue})

        class _R:
            id = "fake-e2e-task-id"

        return _R()


class TestEmitTriggerCLI:
    """CLI 가 파일을 읽어 dispatcher.dispatch() 를 호출하는지만 검증."""

    def test_scenario_a_dispatches_to_comment_queue(
        self,
        emit_module: Any,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        fake = _FakeCelery()
        monkeypatch.setattr(emit_module, "Celery", lambda **_: fake)

        trigger_path = (
            Path(__file__).resolve().parents[1] / "fixtures" / "scenario_A" / "trigger.json"
        )
        rc = emit_module.main([str(trigger_path)])

        assert rc == 0
        assert len(fake.sent) == 1
        assert fake.sent[0]["name"] == "comment.process"
        assert fake.sent[0]["queue"] == "comment_queue"
        assert "fake-e2e-task-id" in capsys.readouterr().out

    def test_scenario_b_dispatches_to_configaudit_queue(
        self, emit_module: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeCelery()
        monkeypatch.setattr(emit_module, "Celery", lambda **_: fake)

        trigger_path = (
            Path(__file__).resolve().parents[1]
            / "fixtures"
            / "scenario_B"
            / "case-001"
            / "trigger.json"
        )
        rc = emit_module.main([str(trigger_path)])

        assert rc == 0
        assert fake.sent[0]["queue"] == "configaudit_queue"

    def test_missing_file_returns_2(self, emit_module: Any, tmp_path: Path) -> None:
        rc = emit_module.main([str(tmp_path / "nope.json")])
        assert rc == 2
