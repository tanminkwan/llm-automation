"""워커 부팅 엔트리포인트 — celery -A celery_comment.worker:celery_app worker ...

``app`` 모듈과 달리 이 모듈은 import 시점에 settings 를 읽고 GitClient/
AgentExecutor 를 주입한 fully-wired Celery app 을 생성한다. 테스트에서는 이
모듈을 import 하지 않는다.
"""

from __future__ import annotations

from .app import build_worker_app

celery_app = build_worker_app()  # pragma: no cover — 워커 부팅 엔트리포인트

__all__ = ["celery_app"]
