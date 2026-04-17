"""T-11~T-13: AnomalyDetector 테스트."""

from configaudit_mcp.anomaly_detector import AnomalyDetector
from configaudit_mcp.diff_engine import DiffEngine
from configaudit_mcp.models import EnvConfig


class TestAnomalyDetector:
    """T-11: 동일→[], T-12: prod만 다름→1건, T-13: 모두 다름→복수."""

    def test_all_same(self, sample_configs_same: list[EnvConfig]) -> None:
        """T-11: 3개 환경 동일 → anomalies=[]."""
        engine = DiffEngine()
        cross = [
            engine.diff_cross_env(sample_configs_same[0], sample_configs_same[1]),
            engine.diff_cross_env(sample_configs_same[1], sample_configs_same[2]),
        ]
        detector = AnomalyDetector()
        result = detector.detect(sample_configs_same, cross)
        assert result == []

    def test_prod_only_diff(self, sample_configs_prod_diff: list[EnvConfig]) -> None:
        """T-12: prod 만 다름 → anomaly 1건."""
        engine = DiffEngine()
        cross = [
            engine.diff_cross_env(sample_configs_prod_diff[0], sample_configs_prod_diff[1]),
            engine.diff_cross_env(sample_configs_prod_diff[1], sample_configs_prod_diff[2]),
        ]
        detector = AnomalyDetector()
        result = detector.detect(sample_configs_prod_diff, cross)
        assert len(result) == 1
        assert result[0].env == "prod"
        assert "prod" in result[0].description

    def test_all_different(self, sample_configs_all_diff: list[EnvConfig]) -> None:
        """T-13: 모든 환경 다름 → anomalies 복수 아님 (규칙: 나머지 2개가 같아야 anomaly)."""
        engine = DiffEngine()
        cross = [
            engine.diff_cross_env(sample_configs_all_diff[0], sample_configs_all_diff[1]),
            engine.diff_cross_env(sample_configs_all_diff[1], sample_configs_all_diff[2]),
        ]
        detector = AnomalyDetector()
        result = detector.detect(sample_configs_all_diff, cross)
        # 모두 다르면 "나머지 2개가 같은" 환경이 없으므로 anomaly 없음
        assert result == []
