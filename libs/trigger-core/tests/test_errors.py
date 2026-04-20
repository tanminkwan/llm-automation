"""예외 계층 검증."""

from __future__ import annotations

from trigger_core.errors import (
    DuplicateTriggerError,
    InvalidPayloadError,
    InvalidSignatureError,
    TriggerError,
    UnsupportedWorkTypeError,
)


def test_all_subclasses_of_trigger_error() -> None:
    for exc_cls in (
        DuplicateTriggerError,
        InvalidPayloadError,
        InvalidSignatureError,
        UnsupportedWorkTypeError,
    ):
        assert issubclass(exc_cls, TriggerError)
        assert issubclass(exc_cls, Exception)


def test_trigger_error_message_preserved() -> None:
    exc = InvalidPayloadError("broken")
    assert str(exc) == "broken"
