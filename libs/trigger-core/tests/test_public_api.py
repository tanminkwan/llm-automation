"""공개 API 계약 검증 — ``__all__`` 와 re-export 일관성."""

from __future__ import annotations

import trigger_core
from trigger_core import TriggerDispatcher, TriggerSource


def test_all_names_are_exposed() -> None:
    for name in trigger_core.__all__:
        assert hasattr(trigger_core, name), f"missing export: {name}"


def test_protocols_are_runtime_checkable() -> None:
    # mypy strict + runtime_checkable 동시 호환 검증
    class _HasParse:
        def parse(self, raw: bytes, headers: dict[str, str]) -> None:  # noqa: D401
            """stub."""

    class _HasDispatch:
        def dispatch(self, event: object) -> str:
            return ""

    assert isinstance(_HasParse(), TriggerSource)
    assert isinstance(_HasDispatch(), TriggerDispatcher)
