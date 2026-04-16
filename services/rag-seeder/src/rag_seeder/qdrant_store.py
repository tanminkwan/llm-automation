"""QdrantStore — VectorStore Protocol 구현 (qdrant-client)."""

from __future__ import annotations

import hashlib
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams


def snippet_id_to_uuid(snippet_id: str) -> str:
    """snippet.id → deterministic UUID (SHA-256 앞 32 hex → UUID5 형식).

    동일 snippet.id 는 항상 같은 point ID 를 생성하여 멱등 upsert 를 보장한다.
    """
    hex_digest = hashlib.sha256(snippet_id.encode()).hexdigest()[:32]
    return str(uuid.UUID(hex_digest))


class QdrantStore:
    """Qdrant 벡터 저장소 어댑터."""

    def __init__(self, url: str, *, timeout: float = 30.0) -> None:
        self._client = QdrantClient(url=url, timeout=int(timeout))

    def ensure_collection(self, name: str, dim: int) -> None:
        """컬렉션이 없으면 cosine distance 로 생성."""
        try:
            self._client.get_collection(name)
        except (UnexpectedResponse, Exception):
            self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(
        self,
        collection: str,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, object]],
    ) -> int:
        """벡터 + payload 를 upsert. 성공 건수 반환."""
        points = [
            PointStruct(
                id=snippet_id_to_uuid(point_id),
                vector=vector,
                payload=payload,
            )
            for point_id, vector, payload in zip(ids, vectors, payloads, strict=True)
        ]
        self._client.upsert(collection_name=collection, points=points)
        return len(points)
