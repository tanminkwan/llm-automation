"""T-01~T-03: Snippet, SeedResult 모델 테스트."""

from __future__ import annotations

from rag_seeder.models import SeedResult, Snippet


class TestSnippet:
    def test_create_with_all_fields(self) -> None:
        """T-01: 정상 생성 + 필드 검증."""
        s = Snippet(
            id="svc::method",
            path="pkg/svc.java",
            symbol="method",
            line_range=[10, 20],
            comment="주석 텍스트",
            repo="my-repo",
        )
        assert s.id == "svc::method"
        assert s.path == "pkg/svc.java"
        assert s.symbol == "method"
        assert s.line_range == [10, 20]
        assert s.comment == "주석 텍스트"
        assert s.repo == "my-repo"

    def test_repo_default(self) -> None:
        """T-02: repo 기본값 seed-repo."""
        s = Snippet(
            id="a::b",
            path="a.java",
            symbol="b",
            line_range=[1, 2],
            comment="c",
        )
        assert s.repo == "seed-repo"


class TestSeedResult:
    def test_create(self) -> None:
        """T-03: 정상 생성."""
        r = SeedResult(
            total_loaded=10,
            total_embedded=10,
            total_upserted=10,
            errors=0,
            duration_seconds=1.5,
        )
        assert r.total_loaded == 10
        assert r.total_upserted == 10
        assert r.errors == 0
        assert r.duration_seconds == 1.5
