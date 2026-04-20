"""GitClient / AgentExecutor 구현체 선택 팩토리 — 환경변수 기반."""

from __future__ import annotations

from pathlib import Path

from .direct_llm_agent import DirectLLMAgent
from .fixture_git import FixtureGitClient
from .git_ops import SubprocessGitClient
from .protocols import AgentExecutor, GitClient
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


def build_agent_executor(settings: CommentSettings) -> AgentExecutor:
    """기본 AgentExecutor — chat-llm alias 로 DirectLLMAgent 를 생성."""
    return DirectLLMAgent(
        base_url=settings.chat_llm_base_url,
        model=settings.chat_llm_model,
        api_key=settings.chat_llm_api_key,
        timeout=float(settings.chat_llm_timeout_seconds),
    )


__all__ = ["build_agent_executor", "build_git_client"]
