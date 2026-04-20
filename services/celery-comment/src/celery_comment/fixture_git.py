"""FixtureGitClient — 파일 복사 기반의 ``GitClient`` 구현.

E2E 에서 실제 Gitea 를 쓰지 않고 사전 준비된 디렉터리를 clone 소스로,
작업 결과 스냅샷을 별도 디렉터리에 기록하기 위해 사용한다.

- ``clone_url`` 은 ``fixture://<key>`` 스킴을 사용 (실 URL 아님).
- ``clone`` 은 ``{source_root}/<key>/`` 트리를 ``dest`` 로 복사.
- ``add_commit_push`` 는 ``repo_dir`` 을 ``{result_root}/<branch>/<ts>/`` 로 스냅샷하고
  ``manifest.json`` (message/branch/timestamp) 을 함께 기록.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


class FixtureGitClient:
    """파일 복사 기반 GitClient Protocol 구현."""

    FIXTURE_SCHEME = "fixture://"
    MANIFEST_NAME = "manifest.json"

    def __init__(self, source_root: Path | str, result_root: Path | str) -> None:
        self._source_root = Path(source_root)
        self._result_root = Path(result_root)

    def clone(self, url: str, dest: Path, ref: str) -> None:
        """``fixture://<key>`` 를 해석하여 소스 트리를 ``dest`` 로 복사.

        - ``ref`` 는 레퍼런스로만 보관 (실제 checkout 은 없음).
        - ``dest`` 가 이미 존재하면 덮어쓰기.
        """
        key = self._extract_key(url)
        src = self._source_root / key
        if not src.is_dir():
            raise FileNotFoundError(f"fixture source not found: {src}")

        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest)

    def add_commit_push(self, repo_dir: Path, message: str, branch: str) -> None:
        """``repo_dir`` 트리를 스냅샷 디렉터리로 복사 + manifest 기록."""
        if not repo_dir.is_dir():
            raise FileNotFoundError(f"repo_dir not found: {repo_dir}")

        ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S%fZ")
        snapshot_dir = self._result_root / branch / ts
        snapshot_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(repo_dir, snapshot_dir)

        manifest = {
            "message": message,
            "branch": branch,
            "timestamp": ts,
            "source_repo_dir": str(repo_dir),
        }
        (snapshot_dir / self.MANIFEST_NAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def _extract_key(cls, url: str) -> str:
        if not url.startswith(cls.FIXTURE_SCHEME):
            raise ValueError(f"invalid fixture url (expected {cls.FIXTURE_SCHEME}...): {url}")
        return url[len(cls.FIXTURE_SCHEME) :].strip("/")


__all__ = ["FixtureGitClient"]
