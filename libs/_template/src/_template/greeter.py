"""Greeter — DIP/SRP 시연용 인사말 생성기."""

from __future__ import annotations

from typing import Protocol


class Clock(Protocol):
    """시간 의존성 추상화 (DIP).

    Greeter 는 구체적 시계 구현이 아니라 본 Protocol 에 의존한다.
    테스트에서 결정성 보장을 위해 fake 구현을 주입할 수 있다.
    """

    def now_iso(self) -> str:
        """ISO-8601 형식의 현재 시각 문자열을 반환."""
        ...


class Greeter:
    """인사말 생성 (SRP — 인사말 포맷팅만 담당)."""

    def __init__(self, clock: Clock, prefix: str) -> None:
        self._clock = clock
        self._prefix = prefix

    def greet(self, name: str) -> str:
        """``[<iso>] <prefix>, <name>!`` 형식의 인사말을 생성."""
        if not name:
            raise ValueError("name must not be empty")
        return f"[{self._clock.now_iso()}] {self._prefix}, {name}!"
