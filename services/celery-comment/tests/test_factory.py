"""``build_git_client`` / ``build_agent_executor`` — env 기반 구현체 선택."""

from __future__ import annotations

import pytest

from celery_comment.direct_llm_agent import DirectLLMAgent
from celery_comment.factory import build_agent_executor, build_git_client
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


def test_build_agent_executor_direct_llm() -> None:
    """chat_llm_* 값이 채워져 있으면 DirectLLMAgent 생성."""
    settings = CommentSettings(
        chat_llm_base_url="https://api.openai.com/v1",
        chat_llm_model="gpt-4o-mini",
        chat_llm_api_key="sk-test-abc",
    )
    agent = build_agent_executor(settings)
    assert isinstance(agent, DirectLLMAgent)


def test_build_agent_executor_missing_key_raises() -> None:
    """API key 누락 시 ValueError — 설정 오류를 워커 부팅 시점에 즉시 드러낸다."""
    settings = CommentSettings(chat_llm_api_key="")
    with pytest.raises(ValueError, match="chat_llm_api_key"):
        build_agent_executor(settings)
