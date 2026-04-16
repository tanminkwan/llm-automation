"""rag-mcp — RAG 벡터 검색 MCP 서비스.

search_codebase(query, k) → 임베딩 → Qdrant 검색 → top-k 결과 반환.
"""

from __future__ import annotations

from .app import create_app
from .models import SearchHit, SearchRequest, SearchResult
from .protocols import EmbeddingClient, VectorReader
from .qdrant_reader import QdrantReader
from .search_engine import SearchEngine
from .settings import RagMcpSettings

__version__ = "0.1.0"

__all__ = [
    "EmbeddingClient",
    "QdrantReader",
    "RagMcpSettings",
    "SearchEngine",
    "SearchHit",
    "SearchRequest",
    "SearchResult",
    "VectorReader",
    "create_app",
]
