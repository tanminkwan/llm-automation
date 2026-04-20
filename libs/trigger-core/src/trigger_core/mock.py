"""MockTriggerEmitter — TriggerSource 를 우회해 TriggerEvent 를 직접 Dispatcher 로 발행."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import TriggerEvent
from .protocols import TriggerDispatcher


class MockTriggerEmitter:
    """테스트/로컬용. HTTP 서버/서명 없이 Dispatcher 에 직접 주입한다.

    입력 형식 3가지:
    - ``TriggerEvent`` 인스턴스 → :meth:`emit`
    - ``dict`` → :meth:`emit_from_dict`
    - JSON 파일 경로 → :meth:`emit_from_json`
    """

    def __init__(self, dispatcher: TriggerDispatcher) -> None:
        self._dispatcher = dispatcher

    def emit(self, event: TriggerEvent) -> str:
        return self._dispatcher.dispatch(event)

    def emit_from_dict(self, data: dict[str, Any]) -> str:
        return self.emit(TriggerEvent(**data))

    def emit_from_json(self, path: str | Path) -> str:
        raw = Path(path).read_text(encoding="utf-8")
        return self.emit_from_dict(json.loads(raw))
