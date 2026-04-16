"""T-17~T-18: RagMcpSettings 테스트."""

from __future__ import annotations

import pytest

from rag_mcp.settings import RagMcpSettings


class TestRagMcpSettings:
    def test_full_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-17: 모든 키 env 주입 시 정상 로딩."""
        monkeypatch.setenv("RAG_MCP_HOST", "127.0.0.1")
        monkeypatch.setenv("RAG_MCP_PORT", "8888")
        monkeypatch.setenv("RAG_MCP_COLLECTION_NAME", "my_col")
        monkeypatch.setenv("RAG_MCP_DEFAULT_K", "10")
        monkeypatch.setenv("RAG_MCP_MAX_K", "50")
        monkeypatch.setenv("QDRANT_URL", "http://qdrant:6333")
        monkeypatch.setenv("QDRANT_TIMEOUT", "60.0")

        settings = RagMcpSettings()  # type: ignore[call-arg]
        assert settings.rag_mcp_host == "127.0.0.1"
        assert settings.rag_mcp_port == 8888
        assert settings.rag_mcp_collection_name == "my_col"
        assert settings.rag_mcp_default_k == 10
        assert settings.rag_mcp_max_k == 50
        assert settings.qdrant_url == "http://qdrant:6333"
        assert settings.qdrant_timeout == 60.0

    def test_defaults(self) -> None:
        """T-18: 기본값만으로 로딩."""
        settings = RagMcpSettings()  # type: ignore[call-arg]
        assert settings.rag_mcp_host == "0.0.0.0"  # noqa: S104
        assert settings.rag_mcp_port == 9001
        assert settings.rag_mcp_collection_name == "code_comments"
        assert settings.rag_mcp_default_k == 5
        assert settings.rag_mcp_max_k == 20
