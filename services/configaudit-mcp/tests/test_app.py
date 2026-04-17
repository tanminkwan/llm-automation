"""T-16~T-19: App 엔드포인트 테스트."""

from fastapi.testclient import TestClient

from configaudit_mcp.analyzer import Analyzer
from configaudit_mcp.anomaly_detector import AnomalyDetector
from configaudit_mcp.app import create_app
from configaudit_mcp.diff_engine import DiffEngine
from configaudit_mcp.models import EnvConfig
from configaudit_mcp.settings import ConfigAuditSettings

from .conftest import AFTER_COMMON, AFTER_DIFFERENT, BEFORE_COMMON, FakeConfigClient


def _make_test_app(configs: dict[str, EnvConfig] | None = None) -> TestClient:
    """테스트용 앱 생성 (fake client 주입)."""
    _configs = configs or {
        "dev": EnvConfig(env="dev", before=BEFORE_COMMON, after=AFTER_COMMON),
        "stage": EnvConfig(env="stage", before=BEFORE_COMMON, after=AFTER_COMMON),
        "prod": EnvConfig(env="prod", before=BEFORE_COMMON, after=AFTER_DIFFERENT),
    }
    client = FakeConfigClient(_configs)
    analyzer = Analyzer(
        client=client,
        diff_engine=DiffEngine(),
        detector=AnomalyDetector(),
    )
    settings = ConfigAuditSettings()
    app = create_app(analyzer=analyzer, settings=settings)
    return TestClient(app)


class TestGetConfigContext:
    """T-16: 정상, T-17: work_id 누락, T-18: case 미전달."""

    def test_success(self) -> None:
        """T-16: 정상 200 응답."""
        tc = _make_test_app()
        resp = tc.post(
            "/tools/get_config_context",
            json={
                "work_id": "abc-123",
                "case": "case-001",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["work_id"] == "abc-123"
        assert data["case"] == "case-001"
        assert len(data["configs"]) == 3
        assert len(data["change_diffs"]) == 3
        assert len(data["cross_env_diffs"]) == 2
        assert len(data["anomalies"]) == 1

    def test_missing_work_id(self) -> None:
        """T-17: work_id 누락 → 422."""
        tc = _make_test_app()
        resp = tc.post(
            "/tools/get_config_context",
            json={
                "case": "case-001",
            },
        )
        assert resp.status_code == 422

    def test_default_case(self) -> None:
        """T-18: case 미전달 → 기본값 사용."""
        tc = _make_test_app()
        resp = tc.post(
            "/tools/get_config_context",
            json={
                "work_id": "abc-123",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # case 미전달 시 기본값 "case-001" 사용
        assert data["case"] == "case-001"

    def test_api_error_502(self) -> None:
        """fetch 실패 시 502 반환."""
        from .conftest import FailingConfigClient

        failing = FailingConfigClient()
        analyzer = Analyzer(
            client=failing,
            diff_engine=DiffEngine(),
            detector=AnomalyDetector(),
        )
        app = create_app(analyzer=analyzer, settings=ConfigAuditSettings())
        tc = TestClient(app)
        resp = tc.post(
            "/tools/get_config_context",
            json={
                "work_id": "abc-123",
                "case": "case-001",
            },
        )
        assert resp.status_code == 502


class TestHealth:
    """T-19: 헬스체크."""

    def test_health(self) -> None:
        """T-19: GET /health → 200 + ok."""
        tc = _make_test_app()
        resp = tc.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
