"""표준 alias 상수 테스트 — 설계서 §8 의 T-08 ~ T-09."""

from __future__ import annotations

from llm_gateway.aliases import (
    CHAT_ALIASES,
    CHAT_LLM,
    EMBEDDING,
    EMBEDDING_ALIASES,
    REASONING_LLM,
)


def test_alias_string_values() -> None:
    """T-08: 표준 alias 문자열 — production 과 동일 (CLAUDE.md §5.1)."""
    assert CHAT_LLM == "chat-llm"
    assert REASONING_LLM == "reasoning-llm"
    assert EMBEDDING == "embedding"


def test_chat_alias_set_membership() -> None:
    """T-09a: chat 그룹 멤버십."""
    assert CHAT_LLM in CHAT_ALIASES
    assert REASONING_LLM in CHAT_ALIASES
    assert EMBEDDING not in CHAT_ALIASES


def test_embedding_alias_set_membership() -> None:
    """T-09b: embedding 그룹 멤버십."""
    assert EMBEDDING in EMBEDDING_ALIASES
    assert CHAT_LLM not in EMBEDDING_ALIASES
    assert REASONING_LLM not in EMBEDDING_ALIASES


def test_alias_sets_are_disjoint() -> None:
    """T-09c: chat 과 embedding 그룹은 상호 배타적."""
    assert CHAT_ALIASES.isdisjoint(EMBEDDING_ALIASES)
