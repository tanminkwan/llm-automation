"""T-20: public API import 확인."""

from __future__ import annotations


def test_public_imports() -> None:
    """T-20: from rag_seeder import ... 가능."""
    from rag_seeder import (
        CorpusLoader,
        EmbeddingClient,
        QdrantStore,
        Seeder,
        SeederSettings,
        SeedResult,
        Snippet,
        VectorStore,
    )

    assert all(
        cls is not None
        for cls in [
            CorpusLoader,
            EmbeddingClient,
            QdrantStore,
            SeedResult,
            Seeder,
            SeederSettings,
            Snippet,
            VectorStore,
        ]
    )
