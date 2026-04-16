"""Runner 팩토리 + registry (OCP)."""

from __future__ import annotations

from typing import Any

from .claude_code_runner import ClaudeCodeRunner
from .errors import UnknownRunnerError
from .opencode_runner import OpenCodeRunner
from .protocols import AgentRunner
from .settings import RunnerSettings

_REGISTRY: dict[str, type[Any]] = {
    "opencode": OpenCodeRunner,
    "claude-code": ClaudeCodeRunner,
}


def build_runner(
    kind: str,
    *,
    settings: RunnerSettings | None = None,
) -> AgentRunner:
    """kind 로 Runner 구현체 생성.

    미등록 kind → UnknownRunnerError.
    settings 미전달 시 기본 RunnerSettings 사용.
    """
    if kind not in _REGISTRY:
        raise UnknownRunnerError(f"Unknown runner kind: {kind!r}")
    resolved_settings = settings or RunnerSettings()
    return _REGISTRY[kind](settings=resolved_settings)  # type: ignore[no-any-return]


def register_runner(kind: str, cls: type[Any]) -> None:
    """OCP — 외부 Runner 등록."""
    _REGISTRY[kind] = cls
