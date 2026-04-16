"""T-05~T-10: FixtureLoader 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from leebalso_mock.loader import FixtureLoader, FixtureNotFoundError


class TestLoad:
    """fixture 로드 테스트."""

    def test_load_success(self, loader: FixtureLoader) -> None:
        """T-05: 정상 로드 — before/after 내용 일치."""
        resp = loader.load(case="case-001", env="dev")
        assert resp.env == "dev"
        assert "before" in resp.before
        assert "after" in resp.after
        assert resp.meta.fixture == "case-001"
        assert resp.meta.version == "v1"

    def test_unknown_case(self, loader: FixtureLoader) -> None:
        """T-06: 미지 case → FixtureNotFoundError."""
        with pytest.raises(FixtureNotFoundError, match="Case not found"):
            loader.load(case="nonexistent", env="dev")

    def test_unknown_env(self, fixtures_dir: Path) -> None:
        """T-07: 미지 env → FixtureNotFoundError."""
        loader = FixtureLoader(fixtures_dir)
        with pytest.raises(FixtureNotFoundError, match="Env fixture not found"):
            loader.load(case="case-001", env="unknown")

    def test_deterministic(self, loader: FixtureLoader) -> None:
        """T-08: 결정성 — 동일 요청 2회 byte-equal."""
        r1 = loader.load(case="case-001", env="dev")
        r2 = loader.load(case="case-001", env="dev")
        assert r1.model_dump_json() == r2.model_dump_json()


class TestExistence:
    """case/env 존재 확인."""

    def test_case_exists(self, loader: FixtureLoader) -> None:
        """T-09: case 존재/미존재."""
        assert loader.case_exists("case-001") is True
        assert loader.case_exists("nonexistent") is False

    def test_env_exists(self, loader: FixtureLoader) -> None:
        """T-10: env 존재/미존재."""
        assert loader.env_exists("case-001", "dev") is True
        assert loader.env_exists("case-001", "unknown") is False
