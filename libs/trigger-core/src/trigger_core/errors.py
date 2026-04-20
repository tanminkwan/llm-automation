"""trigger-core 공통 예외."""

from __future__ import annotations


class TriggerError(Exception):
    """trigger-core 최상위 예외."""


class InvalidSignatureError(TriggerError):
    """HMAC 서명 불일치."""


class InvalidPayloadError(TriggerError):
    """원시 페이로드 파싱/스키마 실패."""


class UnsupportedWorkTypeError(TriggerError):
    """work_type 판별 불가 또는 태스크 매핑 누락."""


class DuplicateTriggerError(TriggerError):
    """delivery_id 중복 — 멱등 처리 필요."""
