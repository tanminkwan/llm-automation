"""T-01~T-04: 데이터 모델 테스트."""

from configaudit_mcp.models import Anomaly, AuditContext, DiffResult, EnvConfig


class TestEnvConfig:
    """T-01: EnvConfig 정상 생성."""

    def test_create(self) -> None:
        cfg = EnvConfig(env="dev", before="a", after="b")
        assert cfg.env == "dev"
        assert cfg.before == "a"
        assert cfg.after == "b"


class TestDiffResult:
    """T-02: DiffResult has_changes."""

    def test_has_changes_true(self) -> None:
        dr = DiffResult(label="test", diff="--- a\n+++ b\n", has_changes=True)
        assert dr.has_changes is True
        assert dr.label == "test"

    def test_has_changes_false(self) -> None:
        dr = DiffResult(label="test", diff="", has_changes=False)
        assert dr.has_changes is False
        assert dr.diff == ""


class TestAnomaly:
    """T-03: Anomaly 정상 생성."""

    def test_create(self) -> None:
        a = Anomaly(env="prod", description="prod differs")
        assert a.env == "prod"
        assert a.description == "prod differs"


class TestAuditContext:
    """T-04: AuditContext 전체 필드 검증."""

    def test_full_fields(self) -> None:
        ctx = AuditContext(
            work_id="abc-123",
            case="case-001",
            configs=[EnvConfig(env="dev", before="a", after="b")],
            change_diffs=[DiffResult(label="l", diff="d", has_changes=True)],
            cross_env_diffs=[],
            anomalies=[Anomaly(env="dev", description="desc")],
        )
        assert ctx.work_id == "abc-123"
        assert ctx.case == "case-001"
        assert len(ctx.configs) == 1
        assert len(ctx.change_diffs) == 1
        assert len(ctx.cross_env_diffs) == 0
        assert len(ctx.anomalies) == 1
