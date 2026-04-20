"""GitClient 구현체 선택 팩토리 — ``GIT_CLIENT`` 환경변수 기반."""

from __future__ import annotations

from pathlib import Path

from .fixture_git import FixtureGitClient
from .git_ops import SubprocessGitClient
from .protocols import GitClient
from .settings import CommentSettings


def build_git_client(settings: CommentSettings) -> GitClient:
    """``settings.git_client`` 값에 따라 GitClient 구현체 선택.

    - ``fixture`` → FixtureGitClient (source_root / result_root 필수)
    - 그 외 (``subprocess`` 포함) → SubprocessGitClient
    """
    if settings.git_client == "fixture":
        return FixtureGitClient(
            source_root=Path(settings.fixture_source_dir),
            result_root=Path(settings.fixture_result_dir),
        )
    return SubprocessGitClient(author=settings.git_commit_author)


__all__ = ["build_git_client"]
