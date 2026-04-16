"""pytest 공통 픽스처."""

from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _isolate_template_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """TEMPLATE_* 환경변수가 호스트에서 새지 않도록 격리."""
    monkeypatch.delenv("TEMPLATE_GREETING_PREFIX", raising=False)
    yield
