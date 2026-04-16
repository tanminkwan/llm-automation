"""fixture 파일 로더."""

from __future__ import annotations

from pathlib import Path

from .models import ConfigResponse, FixtureMeta

FIXTURE_VERSION = "v1"


class FixtureNotFoundError(Exception):
    """요청한 case 또는 env fixture 가 존재하지 않음."""


class FixtureLoader:
    """파일시스템 기반 fixture 로더 (SRP — 파일 I/O 만 담당)."""

    def __init__(self, fixtures_dir: Path) -> None:
        self._fixtures_dir = fixtures_dir

    def case_exists(self, case: str) -> bool:
        """case 디렉터리 존재 여부."""
        return (self._fixtures_dir / case).is_dir()

    def env_exists(self, case: str, env: str) -> bool:
        """해당 env 의 before/after fixture 파일 존재 여부."""
        case_dir = self._fixtures_dir / case
        return (case_dir / f"{env}.before.httpm").is_file() and (
            case_dir / f"{env}.after.httpm"
        ).is_file()

    def load(self, case: str, env: str) -> ConfigResponse:
        """fixture 파일에서 before/after 로드.

        Raises:
            FixtureNotFoundError: case 또는 env fixture 미존재.
        """
        if not self.case_exists(case):
            raise FixtureNotFoundError(f"Case not found: {case!r}")
        if not self.env_exists(case, env):
            raise FixtureNotFoundError(f"Env fixture not found: case={case!r}, env={env!r}")

        case_dir = self._fixtures_dir / case
        before = (case_dir / f"{env}.before.httpm").read_text(encoding="utf-8")
        after = (case_dir / f"{env}.after.httpm").read_text(encoding="utf-8")

        return ConfigResponse(
            env=env,
            before=before,
            after=after,
            meta=FixtureMeta(fixture=case, version=FIXTURE_VERSION),
        )
