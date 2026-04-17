"""FastAPI 앱 + MCP 엔드포인트."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .analyzer import Analyzer
from .anomaly_detector import AnomalyDetector
from .config_fetcher import ConfigFetcher
from .diff_engine import DiffEngine
from .models import AuditContext
from .settings import ConfigAuditSettings


class _ToolRequest(BaseModel):
    work_id: str
    case: str | None = None


def _build_default_analyzer(settings: ConfigAuditSettings) -> Analyzer:  # pragma: no cover
    """운영용 Analyzer 조립 — 테스트에서는 주입."""
    client = ConfigFetcher(
        settings.leebalso_base_url,
        timeout=settings.leebalso_timeout,
    )
    return Analyzer(
        client=client,
        diff_engine=DiffEngine(),
        detector=AnomalyDetector(),
    )


def create_app(
    *,
    analyzer: Analyzer | None = None,
    settings: ConfigAuditSettings | None = None,
) -> FastAPI:
    """팩토리 — 테스트 시 analyzer 주입 (DIP)."""
    _settings = settings or ConfigAuditSettings()
    _analyzer = analyzer or _build_default_analyzer(_settings)

    app = FastAPI(title="configaudit-mcp")

    @app.post("/tools/get_config_context")
    def get_config_context(req: _ToolRequest) -> AuditContext:
        case = req.case or _settings.configaudit_default_case
        try:
            return _analyzer.analyze(req.work_id, case)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
