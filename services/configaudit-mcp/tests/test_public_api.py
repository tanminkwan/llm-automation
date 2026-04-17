"""T-23: public API import 확인."""

import configaudit_mcp


class TestPublicApi:
    """T-23: __init__.py 에서 공개 API 가 모두 import 가능."""

    def test_exports(self) -> None:
        assert hasattr(configaudit_mcp, "Analyzer")
        assert hasattr(configaudit_mcp, "Anomaly")
        assert hasattr(configaudit_mcp, "AnomalyDetector")
        assert hasattr(configaudit_mcp, "AuditContext")
        assert hasattr(configaudit_mcp, "ConfigAuditSettings")
        assert hasattr(configaudit_mcp, "ConfigClient")
        assert hasattr(configaudit_mcp, "ConfigFetcher")
        assert hasattr(configaudit_mcp, "DiffEngine")
        assert hasattr(configaudit_mcp, "DiffResult")
        assert hasattr(configaudit_mcp, "EnvConfig")
        assert hasattr(configaudit_mcp, "create_app")
