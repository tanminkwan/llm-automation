"""SearchEngine — 검색 코어 로직: 쿼리 임베딩 → 벡터 검색 → SearchResult."""

from __future__ import annotations

from .models import SearchHit, SearchResult
from .protocols import EmbeddingClient, VectorReader


class SearchEngine:
    """query 임베딩 → Qdrant 검색 → SearchResult 변환."""

    def __init__(
        self,
        *,
        embedder: EmbeddingClient,
        reader: VectorReader,
        collection: str,
    ) -> None:
        self._embedder = embedder
        self._reader = reader
        self._collection = collection

    def search(self, query: str, k: int) -> SearchResult:
        """쿼리를 임베딩하고 벡터 검색하여 결과 반환."""
        vectors = self._embedder.embed_texts([query])
        query_vector = vectors[0]

        raw_hits = self._reader.search(
            self._collection,
            query_vector,
            k,
        )

        hits = [self._to_hit(h) for h in raw_hits]
        return SearchResult(query=query, hits=hits)

    def _to_hit(self, raw: dict[str, object]) -> SearchHit:
        """Qdrant raw hit → SearchHit."""
        payload = raw.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        return SearchHit(
            id=str(payload.get("snippet_id", "")),
            path=str(payload.get("path", "")),
            symbol=str(payload.get("symbol", "")),
            line_range=list(payload.get("line_range", [])),
            comment=str(payload.get("comment", "")),
            score=float(str(raw.get("score", 0.0))),
        )
