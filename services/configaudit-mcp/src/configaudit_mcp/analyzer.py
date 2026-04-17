"""Analyzer — 오케스트레이션: fetch → diff → detect → AuditContext."""

from .anomaly_detector import AnomalyDetector
from .diff_engine import DiffEngine
from .models import AuditContext
from .protocols import ConfigClient

ENVS = ["dev", "stage", "prod"]


class Analyzer:
    """오케스트레이션: fetch → diff → detect → AuditContext."""

    def __init__(
        self,
        *,
        client: ConfigClient,
        diff_engine: DiffEngine,
        detector: AnomalyDetector,
    ) -> None:
        self._client = client
        self._diff_engine = diff_engine
        self._detector = detector

    def analyze(self, work_id: str, case: str) -> AuditContext:
        """3개 환경 fetch → diff → anomaly detect → AuditContext 반환."""
        configs = [self._client.fetch_config(env, case) for env in ENVS]

        change_diffs = [self._diff_engine.diff_before_after(c) for c in configs]

        cross_env_diffs = []
        for i in range(len(configs) - 1):
            cross_env_diffs.append(self._diff_engine.diff_cross_env(configs[i], configs[i + 1]))

        anomalies = self._detector.detect(configs, cross_env_diffs)

        return AuditContext(
            work_id=work_id,
            case=case,
            configs=configs,
            change_diffs=change_diffs,
            cross_env_diffs=cross_env_diffs,
            anomalies=anomalies,
        )
