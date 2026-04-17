"""T-14~T-15: Analyzer 테스트."""

import pytest

from configaudit_mcp.analyzer import Analyzer
from configaudit_mcp.anomaly_detector import AnomalyDetector
from configaudit_mcp.diff_engine import DiffEngine

from .conftest import FailingConfigClient, FakeConfigClient


class TestAnalyzer:
    """T-14: happy path, T-15: fetch 실패."""

    def test_happy_path(self, fake_client_prod_diff: FakeConfigClient) -> None:
        """T-14: 3 env fetch → diffs + anomalies."""
        analyzer = Analyzer(
            client=fake_client_prod_diff,
            diff_engine=DiffEngine(),
            detector=AnomalyDetector(),
        )
        ctx = analyzer.analyze("work-001", "case-001")
        assert ctx.work_id == "work-001"
        assert ctx.case == "case-001"
        assert len(ctx.configs) == 3
        assert len(ctx.change_diffs) == 3
        assert len(ctx.cross_env_diffs) == 2
        # prod 만 다르므로 anomaly 1건
        assert len(ctx.anomalies) == 1
        assert ctx.anomalies[0].env == "prod"

    def test_fetch_failure(self) -> None:
        """T-15: fetch 실패 → 예외 전파."""
        analyzer = Analyzer(
            client=FailingConfigClient(),
            diff_engine=DiffEngine(),
            detector=AnomalyDetector(),
        )
        with pytest.raises(ConnectionError, match="API unavailable"):
            analyzer.analyze("work-002", "case-001")
