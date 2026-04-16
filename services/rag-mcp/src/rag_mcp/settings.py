"""RagMcpSettings — 환경변수 기반 설정 (pydantic-settings)."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RagMcpSettings(BaseSettings):
    """rag-mcp 설정."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    rag_mcp_host: str = Field(alias="RAG_MCP_HOST", default="0.0.0.0")  # noqa: S104
    rag_mcp_port: int = Field(alias="RAG_MCP_PORT", default=9001)
    rag_mcp_collection_name: str = Field(alias="RAG_MCP_COLLECTION_NAME", default="code_comments")
    rag_mcp_default_k: int = Field(alias="RAG_MCP_DEFAULT_K", default=5)
    rag_mcp_max_k: int = Field(alias="RAG_MCP_MAX_K", default=20)
    qdrant_url: str = Field(alias="QDRANT_URL", default="http://localhost:6333")
    qdrant_timeout: float = Field(alias="QDRANT_TIMEOUT", default=30.0)
