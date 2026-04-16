"""T-19: Protocol 만족 확인."""

from __future__ import annotations

from rag_seeder.protocols import EmbeddingClient, VectorStore

from .conftest import FakeEmbedder, FakeVectorStore


class TestProtocols:
    def test_fake_embedder_satisfies_protocol(self) -> None:
        """T-19a: FakeEmbedder 는 EmbeddingClient Protocol 을 만족."""
        embedder: EmbeddingClient = FakeEmbedder()
        result = embedder.embed_texts(["hello"])
        assert len(result) == 1

    def test_fake_store_satisfies_protocol(self) -> None:
        """T-19b: FakeVectorStore 는 VectorStore Protocol 을 만족."""
        store: VectorStore = FakeVectorStore()
        store.ensure_collection("col", 8)
        count = store.upsert("col", ["id1"], [[0.1] * 8], [{"a": "b"}])
        assert count == 1
