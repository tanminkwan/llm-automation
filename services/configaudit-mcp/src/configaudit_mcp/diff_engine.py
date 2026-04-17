"""DiffEngine — unified diff 생성기."""

import difflib

from .models import DiffResult, EnvConfig


class DiffEngine:
    """unified diff 생성기."""

    def diff_before_after(self, config: EnvConfig) -> DiffResult:
        """한 환경의 before→after diff."""
        label = f"{config.env}:before→after"
        diff_text = self._unified_diff(
            config.before,
            config.after,
            fromfile=f"{config.env}/before",
            tofile=f"{config.env}/after",
        )
        return DiffResult(label=label, diff=diff_text, has_changes=bool(diff_text))

    def diff_cross_env(self, left: EnvConfig, right: EnvConfig) -> DiffResult:
        """두 환경의 after 간 diff."""
        label = f"after:{left.env}↔{right.env}"
        diff_text = self._unified_diff(
            left.after,
            right.after,
            fromfile=f"{left.env}/after",
            tofile=f"{right.env}/after",
        )
        return DiffResult(label=label, diff=diff_text, has_changes=bool(diff_text))

    @staticmethod
    def _unified_diff(a: str, b: str, *, fromfile: str, tofile: str) -> str:
        """unified diff 텍스트 생성."""
        a_lines = a.splitlines(keepends=True)
        b_lines = b.splitlines(keepends=True)
        diff_lines = difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile)
        return "".join(diff_lines)
