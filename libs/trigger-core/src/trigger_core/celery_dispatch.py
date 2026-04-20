"""CeleryTriggerDispatcher — TriggerEvent 를 Celery 큐로 발행."""

from __future__ import annotations

from typing import Any, Protocol

from .errors import UnsupportedWorkTypeError
from .models import TriggerEvent, WorkType
from .routing import DEFAULT_TASK_MAP


class _CeleryLike(Protocol):
    """celery.Celery 의 send_task 서브셋 — 실제 celery 의존성 없이 테스트 가능."""

    def send_task(
        self,
        name: str,
        *,
        kwargs: dict[str, Any],
        queue: str,
    ) -> Any: ...


class CeleryTriggerDispatcher:
    """TriggerEvent → ``celery.send_task`` 호출. task_map 주입 가능 (OCP)."""

    def __init__(
        self,
        celery_app: _CeleryLike,
        *,
        task_map: dict[WorkType, tuple[str, str]] | None = None,
    ) -> None:
        self._celery = celery_app
        self._map: dict[WorkType, tuple[str, str]] = (
            dict(task_map) if task_map is not None else dict(DEFAULT_TASK_MAP)
        )

    def dispatch(self, event: TriggerEvent) -> str:
        try:
            task_name, queue = self._map[event.work_type]
        except KeyError as exc:
            raise UnsupportedWorkTypeError(
                f"no task mapping for work_type={event.work_type}"
            ) from exc

        result = self._celery.send_task(
            task_name,
            kwargs=event.to_task_kwargs(),
            queue=queue,
        )
        return str(result.id)
