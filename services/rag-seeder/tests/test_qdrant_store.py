"""T-08~T-11: QdrantStore 테스트 (qdrant-client mock)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from rag_seeder.qdrant_store import QdrantStore, snippet_id_to_uuid


class TestSnippetIdToUuid:
    def test_deterministic(self) -> None:
        """T-11 보조: 같은 id → 같은 UUID."""
        u1 = snippet_id_to_uuid("svc::method1")
        u2 = snippet_id_to_uuid("svc::method1")
        assert u1 == u2

    def test_different_ids_different_uuids(self) -> None:
        u1 = snippet_id_to_uuid("svc::method1")
        u2 = snippet_id_to_uuid("svc::method2")
        assert u1 != u2


class TestQdrantStore:
    @patch("rag_seeder.qdrant_store.QdrantClient")
    def test_ensure_collection_creates_when_missing(self, mock_cls: MagicMock) -> None:
        """T-08: 컬렉션 미존재 → 생성 호출."""
        client = mock_cls.return_value
        client.get_collection.side_effect = UnexpectedResponse(
            status_code=404, reason_phrase="Not found", content=b"", headers={}
        )

        store = QdrantStore("http://localhost:6333")
        store.ensure_collection("test_col", 1024)

        client.create_collection.assert_called_once_with(
            collection_name="test_col",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

    @patch("rag_seeder.qdrant_store.QdrantClient")
    def test_ensure_collection_skips_when_exists(self, mock_cls: MagicMock) -> None:
        """T-09: 컬렉션 존재 → 생성 스킵."""
        client = mock_cls.return_value
        client.get_collection.return_value = MagicMock()

        store = QdrantStore("http://localhost:6333")
        store.ensure_collection("test_col", 1024)

        client.create_collection.assert_not_called()

    @patch("rag_seeder.qdrant_store.QdrantClient")
    def test_upsert_returns_count(self, mock_cls: MagicMock) -> None:
        """T-10: 정상 upsert — 반환 건수 검증."""
        client = mock_cls.return_value
        store = QdrantStore("http://localhost:6333")

        count = store.upsert(
            "test_col",
            ids=["id1", "id2"],
            vectors=[[0.1] * 8, [0.2] * 8],
            payloads=[{"a": "1"}, {"b": "2"}],
        )
        assert count == 2
        client.upsert.assert_called_once()

    @patch("rag_seeder.qdrant_store.QdrantClient")
    def test_upsert_deterministic_id(self, mock_cls: MagicMock) -> None:
        """T-11: 같은 id 2회 → 동일 point UUID."""
        client = mock_cls.return_value
        store = QdrantStore("http://localhost:6333")

        store.upsert("col", ["svc::m"], [[0.1] * 8], [{"x": "1"}])
        call1_points = client.upsert.call_args_list[0][1]["points"]

        store.upsert("col", ["svc::m"], [[0.2] * 8], [{"x": "2"}])
        call2_points = client.upsert.call_args_list[1][1]["points"]

        assert call1_points[0].id == call2_points[0].id
