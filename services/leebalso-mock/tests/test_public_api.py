"""T-19: public API import 테스트."""

from __future__ import annotations


class TestPublicApi:
    """public API 단일 import."""

    def test_single_import(self) -> None:
        """T-19: from leebalso_mock import create_app 등 import 가능."""
        from leebalso_mock import (
            ConfigResponse,
            FixtureLoader,
            FixtureMeta,
            FixtureNotFoundError,
            LeebalsoSettings,
            create_app,
        )

        assert create_app is not None
        assert FixtureLoader is not None
        assert ConfigResponse is not None
        assert FixtureMeta is not None
        assert FixtureNotFoundError is not None
        assert LeebalsoSettings is not None
