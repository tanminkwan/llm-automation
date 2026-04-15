"""Greeter 테스트 — 설계서 §10 의 T-01 ~ T-03."""

from __future__ import annotations

import pytest
from _template.greeter import Clock, Greeter


class _FakeClock:
    """결정성 보장용 fake clock (DIP 시연)."""

    def __init__(self, value: str) -> None:
        self._value = value

    def now_iso(self) -> str:
        return self._value


def test_greet_returns_formatted_string() -> None:
    """T-01: 정상 입력 → '[<iso>] <prefix>, <name>!' 형식."""
    clock = _FakeClock("2026-04-15T16:00:00")
    greeter = Greeter(clock=clock, prefix="Hello")

    result = greeter.greet("Alice")

    assert result == "[2026-04-15T16:00:00] Hello, Alice!"


def test_greet_raises_on_empty_name() -> None:
    """T-02: 빈 이름 → ValueError."""
    greeter = Greeter(clock=_FakeClock("t"), prefix="Hi")

    with pytest.raises(ValueError, match="name must not be empty"):
        greeter.greet("")


def test_greeter_uses_injected_clock_each_call() -> None:
    """T-03: Clock 의존성 주입 — 외부 시계에 의존하지 않음."""
    clock = _FakeClock("FIXED")
    greeter = Greeter(clock=clock, prefix="P")

    assert greeter.greet("a") == "[FIXED] P, a!"
    assert greeter.greet("b") == "[FIXED] P, b!"


def test_clock_protocol_is_runtime_substitutable() -> None:
    """LSP: Protocol 만족하는 임의 구현 사용 가능."""

    class AnotherClock:
        def now_iso(self) -> str:
            return "X"

    clock: Clock = AnotherClock()
    greeter = Greeter(clock=clock, prefix="P")
    assert greeter.greet("z") == "[X] P, z!"
