"""T-22: Protocol 만족 확인."""

from configaudit_mcp.models import EnvConfig
from configaudit_mcp.protocols import ConfigClient


class FakeConfigClient:
    """ConfigClient Protocol 을 구현하는 fake."""

    def fetch_config(self, env: str, case: str) -> EnvConfig:
        return EnvConfig(env=env, before="", after="")


class TestConfigClientProtocol:
    """T-22: FakeConfigClient 가 Protocol 만족."""

    def test_satisfies_protocol(self) -> None:
        client: ConfigClient = FakeConfigClient()
        result = client.fetch_config("dev", "case-001")
        assert isinstance(result, EnvConfig)
        assert result.env == "dev"
