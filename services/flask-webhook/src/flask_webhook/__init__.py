"""flask-webhook — HTTP webhook 어댑터.

핵심 도메인(TriggerEvent/Source/Dispatcher) 은 ``trigger_core`` 에서 제공.
본 서비스는 Flask 라우트 + Settings 만 정의한다.
"""

from .app import create_app
from .settings import WebhookSettings

__all__ = ["WebhookSettings", "create_app"]
