"""표준 alias 상수 (CLAUDE.md §5.1 — production 과 동일).

호출측은 본 모듈의 상수 또는 동등한 문자열 리터럴로 alias 를 지정한다.
"""

from __future__ import annotations

from typing import Final

CHAT_LLM: Final[str] = "chat-llm"
REASONING_LLM: Final[str] = "reasoning-llm"
EMBEDDING: Final[str] = "embedding"

CHAT_ALIASES: Final[frozenset[str]] = frozenset({CHAT_LLM, REASONING_LLM})
EMBEDDING_ALIASES: Final[frozenset[str]] = frozenset({EMBEDDING})
