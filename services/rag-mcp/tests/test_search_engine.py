"""T-06~T-09: SearchEngine 테스트."""

from __future__ import annotations

import pytest

from rag_mcp.search_engine import SearchEngine

from .conftest import SAMPLE_HITS, FakeEmbedder, FakeVectorReader


class TestSearchEngine:
    def test_happy_path(self) -> None:
        """T-06: embed → search → SearchResult."""
        engine = SearchEngine(
            embedder=FakeEmbedder(),
            reader=FakeVectorReader(SAMPLE_HITS),
            collection="test_col",
        )
        result = engine.search("사용자 생성", 5)
        assert result.query == "사용자 생성"
        assert len(result.hits) == 3
        assert result.hits[0].id == "svc::method1"
        assert result.hits[0].score == 0.95

    def test_empty_results(self) -> None:
        """T-07: 빈 결과 → hits=[]."""
        engine = SearchEngine(
            embedder=FakeEmbedder(),
            reader=FakeVectorReader([]),
            collection="test_col",
        )
        result = engine.search("nothing", 5)
        assert result.hits == []

    def test_k_limits_results(self) -> None:
        """T-08: k=1 → 결과 1건만."""
        engine = SearchEngine(
            embedder=FakeEmbedder(),
            reader=FakeVectorReader(SAMPLE_HITS),
            collection="test_col",
        )
        result = engine.search("test", 1)
        assert len(result.hits) == 1

    def test_hit_with_non_dict_payload(self) -> None:
        """payload 가 dict 가 아닌 경우 빈 값으로 처리."""
        bad_hits: list[dict[str, object]] = [
            {"payload": "not_a_dict", "score": 0.5},
        ]
        engine = SearchEngine(
            embedder=FakeEmbedder(),
            reader=FakeVectorReader(bad_hits),
            collection="test_col",
        )
        result = engine.search("test", 5)
        assert len(result.hits) == 1
        assert result.hits[0].id == ""
        assert result.hits[0].path == ""

    def test_embedding_error_propagates(self) -> None:
        """T-09: 임베딩 실패 → 에러 전파."""

        class FailingEmbedder:
            def embed_texts(self, texts: list[str]) -> list[list[float]]:
                msg = "embedding failed"
                raise RuntimeError(msg)

        engine = SearchEngine(
            embedder=FailingEmbedder(),
            reader=FakeVectorReader(SAMPLE_HITS),
            collection="test_col",
        )
        with pytest.raises(RuntimeError, match="embedding failed"):
            engine.search("test", 5)
