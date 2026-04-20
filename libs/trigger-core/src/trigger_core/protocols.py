"""TriggerSource / TriggerDispatcher Protocol."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from .models import TriggerEvent


@runtime_checkable
class TriggerSource(Protocol):
    """원시 이벤트 → TriggerEvent 변환 + 검증."""

    def parse(self, raw: bytes, headers: Mapping[str, str]) -> TriggerEvent:
        """원시 요청을 TriggerEvent 로 변환한다.

        검증 실패는 ``trigger_core.errors.TriggerError`` 하위 예외로 raise.
        """
        ...


@runtime_checkable
class TriggerDispatcher(Protocol):
    """TriggerEvent → 작업 큐 발행."""

    def dispatch(self, event: TriggerEvent) -> str:
        """이벤트를 큐에 발행하고 task_id 를 반환한다."""
        ...
