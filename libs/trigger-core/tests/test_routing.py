"""classify_files + DEFAULT_TASK_MAP 단위 테스트."""

from __future__ import annotations

from trigger_core import WorkType, classify_files
from trigger_core.routing import DEFAULT_TASK_MAP


def test_java_only_is_comment() -> None:
    assert classify_files(["src/Foo.java", "pom.xml"]) is WorkType.COMMENT


def test_httpm_name_is_configaudit() -> None:
    assert classify_files(["conf/http.m"]) is WorkType.CONFIGAUDIT


def test_httpm_extension_is_configaudit() -> None:
    assert classify_files(["a/b.httpm"]) is WorkType.CONFIGAUDIT


def test_mixed_configaudit_priority() -> None:
    assert classify_files(["src/A.java", "conf/http.m"]) is WorkType.CONFIGAUDIT


def test_no_match_returns_none() -> None:
    assert classify_files(["README.md", "Makefile"]) is None


def test_empty_returns_none() -> None:
    assert classify_files([]) is None


def test_case_insensitive_java() -> None:
    assert classify_files(["src/Foo.JAVA"]) is WorkType.COMMENT


def test_default_task_map_shape() -> None:
    assert set(DEFAULT_TASK_MAP) == {WorkType.COMMENT, WorkType.CONFIGAUDIT}
    assert DEFAULT_TASK_MAP[WorkType.COMMENT] == ("comment.process", "comment_queue")
    assert DEFAULT_TASK_MAP[WorkType.CONFIGAUDIT] == (
        "configaudit.process",
        "configaudit_queue",
    )
