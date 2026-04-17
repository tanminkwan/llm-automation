"""AnomalyDetector — 환경 간 이상 패턴 탐지."""

from .models import Anomaly, DiffResult, EnvConfig


class AnomalyDetector:
    """환경 간 이상 패턴 탐지.

    규칙: 한 환경만 나머지 2개와 다르면 anomaly 로 보고.
    """

    def detect(self, configs: list[EnvConfig], cross_diffs: list[DiffResult]) -> list[Anomaly]:
        """cross_env_diffs 에서 이상 후보 추출."""
        if len(configs) < 2:
            return []

        anomalies: list[Anomaly] = []
        after_by_env = {c.env: c.after for c in configs}
        envs = list(after_by_env.keys())

        for i, env in enumerate(envs):
            others = [e for j, e in enumerate(envs) if j != i]
            others_same = all(after_by_env[o] == after_by_env[others[0]] for o in others)
            differs_from_others = all(after_by_env[env] != after_by_env[o] for o in others)
            if others_same and differs_from_others:
                anomalies.append(
                    Anomaly(
                        env=env,
                        description=f"{env} 환경의 after 설정이 나머지 환경({', '.join(others)})과 다릅니다.",
                    )
                )

        return anomalies
