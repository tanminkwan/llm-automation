"""변경 파일 → WorkType 라우팅 + 기본 태스크 맵."""

from __future__ import annotations

from collections.abc import Iterable

from .models import WorkType

_JAVA_EXTS: frozenset[str] = frozenset({".java"})
_HTTPM_NAMES: frozenset[str] = frozenset({"http.m", ".httpm"})


def classify_files(files: Iterable[str]) -> WorkType | None:
    """변경 파일 목록에서 WorkType 판별.

    - Java 확장자 → COMMENT
    - ``http.m`` / ``.httpm`` → CONFIGAUDIT
    - 혼합 시 CONFIGAUDIT 우선 (설정 변경이 주석보다 운영 영향이 큼)
    - 매칭 없음 → None
    """
    has_java = False
    has_httpm = False

    for f in files:
        lower = f.lower()
        if any(lower.endswith(ext) for ext in _JAVA_EXTS):
            has_java = True
        if any(lower.endswith(name) for name in _HTTPM_NAMES):
            has_httpm = True

    if has_httpm:
        return WorkType.CONFIGAUDIT
    if has_java:
        return WorkType.COMMENT
    return None


DEFAULT_TASK_MAP: dict[WorkType, tuple[str, str]] = {
    WorkType.COMMENT: ("comment.process", "comment_queue"),
    WorkType.CONFIGAUDIT: ("configaudit.process", "configaudit_queue"),
}
