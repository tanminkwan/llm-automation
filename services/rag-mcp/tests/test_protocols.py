"""T-19: Protocol 만족 확인."""

from __future__ import annotations

from rag_mcp.protocols import EmbeddingClient, VectorReader

from .conftest import FakeEmbedder, FakeVectorReader


class TestProtocols:
    def test_fake_embedder_satisfies_protocol(self) -> None:
        """T-19a: FakeEmbedder 는 EmbeddingClient Protocol 을 만족."""
        embedder: EmbeddingClient = FakeEmbedder()
        result = embedder.embed_texts(["hello"])
        assert len(result) == 1

    def test_fake_reader_satisfies_protocol(self) -> None:
        """T-19b: FakeVectorReader 는 VectorReader Protocol 을 만족."""
        reader: VectorReader = FakeVectorReader()
        results = reader.search("col", [0.1] * 8, 5)
        assert results == []
