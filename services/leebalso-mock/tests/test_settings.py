"""T-03, T-04: LeebalsoSettings 테스트."""

from __future__ import annotations

import pytest

from leebalso_mock.settings import LeebalsoSettings


class TestLeebalsoSettings:
    """환경변수 기반 설정 로딩."""

    def test_load_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-03: 모든 키 env 주입 시 정상 로딩."""
        monkeypatch.setenv("LEEBALSO_FIXTURES_DIR", "/custom/fixtures")
        monkeypatch.setenv("LEEBALSO_HOST", "127.0.0.1")
        monkeypatch.setenv("LEEBALSO_PORT", "8000")

        s = LeebalsoSettings()
        assert s.leebalso_fixtures_dir == "/custom/fixtures"
        assert s.leebalso_host == "127.0.0.1"
        assert s.leebalso_port == 8000

    def test_defaults(self) -> None:
        """T-04: 기본값만으로 로딩."""
        s = LeebalsoSettings()
        assert s.leebalso_fixtures_dir == "fixtures"
        assert s.leebalso_host == "0.0.0.0"  # noqa: S104
        assert s.leebalso_port == 9100
