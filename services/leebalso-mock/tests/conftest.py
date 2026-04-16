"""leebalso-mock 테스트 공통 픽스처."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from leebalso_mock.app import create_app
from leebalso_mock.loader import FixtureLoader


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """환경변수 격리."""
    monkeypatch.delenv("LEEBALSO_FIXTURES_DIR", raising=False)
    monkeypatch.delenv("LEEBALSO_HOST", raising=False)
    monkeypatch.delenv("LEEBALSO_PORT", raising=False)


def _create_fixture_files(fixtures_dir: Path, case: str, env: str) -> None:
    """테스트용 fixture 파일 생성."""
    case_dir = fixtures_dir / case
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / f"{env}.before.httpm").write_text(
        f"# {env} before\nListen 8080\n", encoding="utf-8"
    )
    (case_dir / f"{env}.after.httpm").write_text(f"# {env} after\nListen 9090\n", encoding="utf-8")


@pytest.fixture()
def fixtures_dir(tmp_path: Path) -> Path:
    """3개 환경 fixture 가 있는 임시 디렉터리."""
    for env in ("dev", "stage", "prod"):
        _create_fixture_files(tmp_path, "case-001", env)
    return tmp_path


@pytest.fixture()
def loader(fixtures_dir: Path) -> FixtureLoader:
    return FixtureLoader(fixtures_dir)


@pytest.fixture()
def client(loader: FixtureLoader) -> TestClient:
    application = create_app(loader=loader)
    return TestClient(application)
