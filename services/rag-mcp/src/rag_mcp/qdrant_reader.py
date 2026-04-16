"""QdrantReader — VectorReader Protocol 구현 (qdrant-client)."""

from __future__ import annotations

from qdrant_client import QdrantClient


class QdrantReader:
    """Qdrant 벡터 검색 어댑터."""

    def __init__(self, url: str, *, timeout: float = 30.0) -> None:
        self._client = QdrantClient(url=url, timeout=int(timeout))

    def search(
        self,
        collection: str,
        vector: list[float],
        limit: int,
    ) -> list[dict[str, object]]:
        """Qdrant 에서 cosine similarity 검색."""
        response = self._client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
        )
        return [
            {
                "payload": dict(hit.payload) if hit.payload else {},
                "score": hit.score,
            }
            for hit in response.points
        ]
