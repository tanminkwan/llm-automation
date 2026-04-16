"""T-01~T-03: SearchHit, SearchResult 모델 테스트."""

from __future__ import annotations

from rag_mcp.models import SearchHit, SearchResult


class TestSearchHit:
    def test_create(self) -> None:
        """T-01: 정상 생성 + 필드 검증."""
        hit = SearchHit(
            id="svc::method1",
            path="pkg/svc.java",
            symbol="method1",
            line_range=[10, 20],
            comment="주석 텍스트",
            score=0.95,
        )
        assert hit.id == "svc::method1"
        assert hit.score == 0.95
        assert hit.line_range == [10, 20]


class TestSearchResult:
    def test_empty_hits(self) -> None:
        """T-02: 빈 hits 리스트."""
        result = SearchResult(query="test", hits=[])
        assert result.query == "test"
        assert result.hits == []

    def test_multiple_hits(self) -> None:
        """T-03: 다수 hits."""
        hits = [
            SearchHit(
                id=f"svc::m{i}",
                path=f"pkg/svc{i}.java",
                symbol=f"m{i}",
                line_range=[i * 10, i * 10 + 10],
                comment=f"주석 {i}",
                score=0.9 - i * 0.1,
            )
            for i in range(3)
        ]
        result = SearchResult(query="test", hits=hits)
        assert len(result.hits) == 3
        assert result.hits[0].score > result.hits[2].score
