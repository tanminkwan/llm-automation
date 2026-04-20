"""trigger-core — SCM-중립 이벤트 수신/큐 발행 추상화."""

from .celery_dispatch import CeleryTriggerDispatcher
from .dedup import DeliveryCache
from .errors import (
    DuplicateTriggerError,
    InvalidPayloadError,
    InvalidSignatureError,
    TriggerError,
    UnsupportedWorkTypeError,
)
from .hmac_verify import verify_signature
from .mock import MockTriggerEmitter
from .models import RepoRef, TriggerEvent, WorkType
from .protocols import TriggerDispatcher, TriggerSource
from .routing import DEFAULT_TASK_MAP, classify_files
from .webhook import WebhookTriggerSource

__all__ = [
    "DEFAULT_TASK_MAP",
    "CeleryTriggerDispatcher",
    "DeliveryCache",
    "DuplicateTriggerError",
    "InvalidPayloadError",
    "InvalidSignatureError",
    "MockTriggerEmitter",
    "RepoRef",
    "TriggerDispatcher",
    "TriggerError",
    "TriggerEvent",
    "TriggerSource",
    "UnsupportedWorkTypeError",
    "WebhookTriggerSource",
    "WorkType",
    "classify_files",
    "verify_signature",
]
