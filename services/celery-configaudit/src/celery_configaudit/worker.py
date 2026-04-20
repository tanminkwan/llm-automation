"""워커 부팅 엔트리포인트 — celery -A celery_configaudit.worker:celery_app worker ...

``task`` 를 import 해서 ``@celery_app.task`` 데코레이터가 실행되게 한 뒤
워커에 노출한다. 테스트에서는 이 모듈을 import 하지 않는다.
"""

from __future__ import annotations

from . import task as _task  # noqa: F401 — 데코레이터 등록 side-effect
from .app import celery_app

__all__ = ["celery_app"]
