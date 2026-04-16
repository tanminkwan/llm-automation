"""T-01~T-04: ToolSpec, AgentResult 데이터 모델 테스트."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agent_runner.models import AgentResult, ToolSpec


class TestToolSpec:
    """T-01, T-02: ToolSpec 생성 및 직렬화."""

    def test_create_and_serialize(self) -> None:
        """T-01: 정상 생성 + JSON 직렬화."""
        spec = ToolSpec(
            name="search_codebase",
            description="Search code",
            input_schema={"type": "object"},
            server_url="http://rag-mcp:9001",
        )
        assert spec.name == "search_codebase"
        assert spec.description == "Search code"
        assert spec.input_schema == {"type": "object"}
        assert spec.server_url == "http://rag-mcp:9001"

        data = json.loads(spec.model_dump_json())
        assert data["name"] == "search_codebase"
        assert data["server_url"] == "http://rag-mcp:9001"

    def test_missing_required_field(self) -> None:
        """T-02: 필수 필드 누락 시 ValidationError."""
        with pytest.raises(ValidationError):
            ToolSpec(name="test", description="desc", input_schema={})  # type: ignore[call-arg]


class TestAgentResult:
    """T-03, T-04: AgentResult 생성."""

    def test_create_with_all_fields(self) -> None:
        """T-03: 정상 생성 (모든 필드 포함)."""
        result = AgentResult(
            exit_code=0,
            stdout="output",
            stderr="",
            changed_files=[Path("a.py"), Path("b.py")],
            duration_seconds=2.5,
        )
        assert result.exit_code == 0
        assert result.stdout == "output"
        assert result.stderr == ""
        assert result.changed_files == [Path("a.py"), Path("b.py")]
        assert result.duration_seconds == 2.5

    def test_default_changed_files(self) -> None:
        """T-04: changed_files 빈 리스트 기본값."""
        result = AgentResult(
            exit_code=1,
            stdout="",
            stderr="error",
            duration_seconds=0.5,
        )
        assert result.changed_files == []

    def test_json_round_trip(self) -> None:
        """AgentResult JSON 직렬화/역직렬화."""
        result = AgentResult(
            exit_code=0,
            stdout="done",
            stderr="",
            changed_files=[Path("src/main.py")],
            duration_seconds=1.0,
        )
        restored = AgentResult.model_validate_json(result.model_dump_json())
        assert restored.exit_code == result.exit_code
        assert restored.stdout == result.stdout
        assert restored.changed_files == result.changed_files
