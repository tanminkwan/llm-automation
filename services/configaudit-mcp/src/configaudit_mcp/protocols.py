"""Protocol 정의 — ConfigClient."""

from typing import Protocol

from .models import EnvConfig


class ConfigClient(Protocol):
    """리발소 API 클라이언트 인터페이스."""

    def fetch_config(self, env: str, case: str) -> EnvConfig: ...
