"""T-20: public API import 확인."""

from __future__ import annotations


def test_public_imports() -> None:
    """T-20: from rag_mcp import ... 가능."""
    from rag_mcp import (
        EmbeddingClient,
        QdrantReader,
        RagMcpSettings,
        SearchEngine,
        SearchHit,
        SearchRequest,
        SearchResult,
        VectorReader,
        create_app,
    )

    assert all(
        cls is not None
        for cls in [
            EmbeddingClient,
            QdrantReader,
            RagMcpSettings,
            SearchEngine,
            SearchHit,
            SearchRequest,
            SearchResult,
            VectorReader,
            create_app,
        ]
    )
