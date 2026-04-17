"""T-20~T-21: ConfigAuditSettings 테스트."""

import pytest

from configaudit_mcp.settings import ConfigAuditSettings


class TestConfigAuditSettings:
    """T-20: 전체 env 주입, T-21: 기본값 로딩."""

    def test_env_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-20: 환경변수로 전체 값 주입."""
        monkeypatch.setenv("CONFIGAUDIT_HOST", "127.0.0.1")
        monkeypatch.setenv("CONFIGAUDIT_PORT", "8888")
        monkeypatch.setenv("CONFIGAUDIT_DEFAULT_CASE", "case-999")
        monkeypatch.setenv("LEEBALSO_BASE_URL", "http://remote:9100")
        monkeypatch.setenv("LEEBALSO_TIMEOUT", "30.0")
        s = ConfigAuditSettings()
        assert s.configaudit_host == "127.0.0.1"
        assert s.configaudit_port == 8888
        assert s.configaudit_default_case == "case-999"
        assert s.leebalso_base_url == "http://remote:9100"
        assert s.leebalso_timeout == 30.0

    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-21: 기본값 로딩."""
        # 기존 환경변수 제거
        for key in [
            "CONFIGAUDIT_HOST",
            "CONFIGAUDIT_PORT",
            "CONFIGAUDIT_DEFAULT_CASE",
            "LEEBALSO_BASE_URL",
            "LEEBALSO_TIMEOUT",
        ]:
            monkeypatch.delenv(key, raising=False)
        s = ConfigAuditSettings()
        assert s.configaudit_host == "0.0.0.0"  # noqa: S104
        assert s.configaudit_port == 9002
        assert s.configaudit_default_case == "case-001"
        assert s.leebalso_base_url == "http://localhost:9100"
        assert s.leebalso_timeout == 10.0
