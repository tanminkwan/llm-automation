"""데이터 모델 — EnvConfig, DiffResult, Anomaly, AuditContext."""

from pydantic import BaseModel


class EnvConfig(BaseModel):
    """한 환경의 before/after config."""

    env: str
    before: str
    after: str


class DiffResult(BaseModel):
    """diff 결과 — 환경별 또는 환경 간."""

    label: str
    diff: str
    has_changes: bool


class Anomaly(BaseModel):
    """이상 패턴 한 건."""

    env: str
    description: str


class AuditContext(BaseModel):
    """get_config_context 최종 응답."""

    work_id: str
    case: str
    configs: list[EnvConfig]
    change_diffs: list[DiffResult]
    cross_env_diffs: list[DiffResult]
    anomalies: list[Anomaly]
