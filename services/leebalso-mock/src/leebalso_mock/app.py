"""leebalso-mock FastAPI 애플리케이션."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from .loader import FixtureLoader, FixtureNotFoundError
from .models import ConfigResponse
from .settings import LeebalsoSettings

DEFAULT_CASE = "case-001"


def create_app(*, loader: FixtureLoader | None = None) -> FastAPI:
    """앱 팩토리 — 테스트 시 loader 주입 (DIP)."""
    if loader is None:
        settings = LeebalsoSettings()
        loader = FixtureLoader(Path(settings.leebalso_fixtures_dir))

    application = FastAPI(title="leebalso-mock")
    _loader = loader

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/config/httpm", response_model=ConfigResponse)
    def get_config(
        env: str = Query(..., description="환경: dev|stage|prod"),
        case: str = Query(DEFAULT_CASE, description="픽스처 케이스 ID"),
    ) -> ConfigResponse:
        try:
            return _loader.load(case=case, env=env)
        except FixtureNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return application


app = create_app()
