"""TemplateSettings 테스트 — 설계서 §10 의 T-04 ~ T-06."""

from __future__ import annotations

import pytest
from _template.settings import TemplateSettings
from pydantic import ValidationError


def test_default_value_when_env_missing() -> None:
    """T-04: env 미설정 시 기본값 'Hello'."""
    settings = TemplateSettings()
    assert settings.greeting_prefix == "Hello"


def test_env_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """T-05: TEMPLATE_GREETING_PREFIX env 가 기본값을 덮어쓴다."""
    monkeypatch.setenv("TEMPLATE_GREETING_PREFIX", "안녕")

    settings = TemplateSettings()

    assert settings.greeting_prefix == "안녕"


def test_explicit_init_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """생성자 인자가 env 보다 우선."""
    monkeypatch.setenv("TEMPLATE_GREETING_PREFIX", "FROM_ENV")

    settings = TemplateSettings(greeting_prefix="FROM_INIT")

    assert settings.greeting_prefix == "FROM_INIT"


def test_invalid_type_raises_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """T-06: 잘못된 타입은 검증 오류 — 명시적 None 입력 거부."""
    with pytest.raises(ValidationError):
        TemplateSettings(greeting_prefix=None)  # type: ignore[arg-type]
