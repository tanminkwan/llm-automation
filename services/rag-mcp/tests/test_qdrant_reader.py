"""T-04~T-05: QdrantReader 테스트 (qdrant-client mock)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from rag_mcp.qdrant_reader import QdrantReader


class TestQdrantReader:
    @patch("rag_mcp.qdrant_reader.QdrantClient")
    def test_search_returns_hits(self, mock_cls: MagicMock) -> None:
        """T-04: 정상 검색 — 결과 반환."""
        client = mock_cls.return_value
        mock_hit = MagicMock()
        mock_hit.payload = {"snippet_id": "svc::m1", "path": "a.java", "comment": "test"}
        mock_hit.score = 0.9
        mock_response = MagicMock()
        mock_response.points = [mock_hit]
        client.query_points.return_value = mock_response

        reader = QdrantReader("http://localhost:6333")
        results = reader.search("test_col", [0.1] * 8, 5)

        assert len(results) == 1
        assert results[0]["score"] == 0.9
        assert results[0]["payload"]["snippet_id"] == "svc::m1"  # type: ignore[index]

    @patch("rag_mcp.qdrant_reader.QdrantClient")
    def test_search_empty(self, mock_cls: MagicMock) -> None:
        """T-05: 빈 결과."""
        client = mock_cls.return_value
        mock_response = MagicMock()
        mock_response.points = []
        client.query_points.return_value = mock_response

        reader = QdrantReader("http://localhost:6333")
        results = reader.search("test_col", [0.1] * 8, 5)

        assert results == []

    @patch("rag_mcp.qdrant_reader.QdrantClient")
    def test_search_empty_payload(self, mock_cls: MagicMock) -> None:
        """payload 가 None 인 경우 빈 dict 로 처리."""
        client = mock_cls.return_value
        mock_hit = MagicMock()
        mock_hit.payload = None
        mock_hit.score = 0.5
        mock_response = MagicMock()
        mock_response.points = [mock_hit]
        client.query_points.return_value = mock_response

        reader = QdrantReader("http://localhost:6333")
        results = reader.search("test_col", [0.1] * 8, 5)

        assert results[0]["payload"] == {}
