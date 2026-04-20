"""``build_git_client`` — GIT_CLIENT 값 기반 구현체 선택."""

from __future__ import annotations

from celery_comment.factory import build_git_client
from celery_comment.fixture_git import FixtureGitClient
from celery_comment.git_ops import SubprocessGitClient
from celery_comment.settings import CommentSettings


def test_default_subprocess() -> None:
    """설정 미지정 → SubprocessGitClient."""
    settings = CommentSettings(git_client="subprocess")
    client = build_git_client(settings)
    assert isinstance(client, SubprocessGitClient)


def test_fixture() -> None:
    """GIT_CLIENT=fixture → FixtureGitClient + source/result root 주입."""
    settings = CommentSettings(
        git_client="fixture",
        fixture_source_dir="/tmp/src",  # noqa: S108
        fixture_result_dir="/tmp/res",  # noqa: S108
    )
    client = build_git_client(settings)
    assert isinstance(client, FixtureGitClient)


def test_unknown_value_falls_back_to_subprocess() -> None:
    """알 수 없는 값 → SubprocessGitClient (fail-open, 운영 기본 보존)."""
    settings = CommentSettings(git_client="weird")
    client = build_git_client(settings)
    assert isinstance(client, SubprocessGitClient)
