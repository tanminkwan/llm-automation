"""공유 fixture — FakeConfigClient, 샘플 데이터."""

import pytest

from configaudit_mcp.models import EnvConfig


class FakeConfigClient:
    """테스트용 ConfigClient — 고정 데이터 반환."""

    def __init__(self, configs: dict[str, EnvConfig] | None = None) -> None:
        self._configs = configs or {}

    def fetch_config(self, env: str, case: str) -> EnvConfig:
        key = env
        if key not in self._configs:
            raise RuntimeError(f"no fixture for env={env}, case={case}")
        return self._configs[key]


class FailingConfigClient:
    """fetch_config 호출 시 항상 예외 발생."""

    def fetch_config(self, env: str, case: str) -> EnvConfig:
        raise ConnectionError(f"API unavailable for env={env}")


BEFORE_COMMON = "Listen 80\nServerName example.com\n"
AFTER_COMMON = "Listen 8080\nServerName example.com\n"
AFTER_DIFFERENT = "Listen 8080\nServerName different.com\n"


@pytest.fixture()
def sample_configs_same() -> list[EnvConfig]:
    """3개 환경 after 동일."""
    return [
        EnvConfig(env="dev", before=BEFORE_COMMON, after=AFTER_COMMON),
        EnvConfig(env="stage", before=BEFORE_COMMON, after=AFTER_COMMON),
        EnvConfig(env="prod", before=BEFORE_COMMON, after=AFTER_COMMON),
    ]


@pytest.fixture()
def sample_configs_prod_diff() -> list[EnvConfig]:
    """prod 만 after 다름."""
    return [
        EnvConfig(env="dev", before=BEFORE_COMMON, after=AFTER_COMMON),
        EnvConfig(env="stage", before=BEFORE_COMMON, after=AFTER_COMMON),
        EnvConfig(env="prod", before=BEFORE_COMMON, after=AFTER_DIFFERENT),
    ]


@pytest.fixture()
def sample_configs_all_diff() -> list[EnvConfig]:
    """모든 환경 after 다름."""
    return [
        EnvConfig(env="dev", before=BEFORE_COMMON, after="Listen 80\n"),
        EnvConfig(env="stage", before=BEFORE_COMMON, after="Listen 8080\n"),
        EnvConfig(env="prod", before=BEFORE_COMMON, after="Listen 9090\n"),
    ]


@pytest.fixture()
def fake_client_same(sample_configs_same: list[EnvConfig]) -> FakeConfigClient:
    return FakeConfigClient({c.env: c for c in sample_configs_same})


@pytest.fixture()
def fake_client_prod_diff(sample_configs_prod_diff: list[EnvConfig]) -> FakeConfigClient:
    return FakeConfigClient({c.env: c for c in sample_configs_prod_diff})
