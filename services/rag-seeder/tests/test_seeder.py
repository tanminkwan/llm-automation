"""T-12~T-15: Seeder 오케스트레이션 테스트."""

from __future__ import annotations

from pathlib import Path

from rag_seeder.corpus_loader import CorpusLoader
from rag_seeder.seeder import Seeder
from rag_seeder.settings import SeederSettings

from .conftest import FakeEmbedder, FakeVectorStore


def _write_corpus(corpus_dir: Path, count: int) -> None:
    """임시 코퍼스 YAML 생성."""
    corpus_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for i in range(count):
        items.append(
            f"- id: svc::m{i}\n"
            f"  path: pkg/svc.java\n"
            f"  symbol: m{i}\n"
            f"  line_range: [{i * 10}, {i * 10 + 10}]\n"
            f'  comment: "comment {i}"'
        )
    content = "\n".join(items) + "\n"
    (corpus_dir / "test.comments.yaml").write_text(content, encoding="utf-8")


class TestSeeder:
    def test_happy_path(self, seeder_env: dict[str, str], tmp_path: Path) -> None:
        """T-12: load → embed → upsert → SeedResult."""
        corpus_dir = tmp_path / "corpus"
        _write_corpus(corpus_dir, 3)

        settings = SeederSettings()  # type: ignore[call-arg]
        embedder = FakeEmbedder(dim=8)
        store = FakeVectorStore()
        loader = CorpusLoader(corpus_dir)

        seeder = Seeder(loader=loader, embedder=embedder, store=store, settings=settings)
        result = seeder.run()

        assert result.total_loaded == 3
        assert result.total_embedded == 3
        assert result.total_upserted == 3
        assert result.errors == 0
        assert result.duration_seconds > 0
        assert "test_collection" in store.collections

    def test_empty_corpus(self, seeder_env: dict[str, str], tmp_path: Path) -> None:
        """T-13: 빈 코퍼스 → SeedResult(0,0,0,0)."""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir(parents=True, exist_ok=True)

        settings = SeederSettings()  # type: ignore[call-arg]
        embedder = FakeEmbedder(dim=8)
        store = FakeVectorStore()
        loader = CorpusLoader(corpus_dir)

        seeder = Seeder(loader=loader, embedder=embedder, store=store, settings=settings)
        result = seeder.run()

        assert result.total_loaded == 0
        assert result.total_embedded == 0
        assert result.total_upserted == 0
        assert result.errors == 0

    def test_batch_splitting(self, seeder_env: dict[str, str], tmp_path: Path) -> None:
        """T-14: batch_size=2, snippets=5 → 3회 embed/upsert."""
        corpus_dir = tmp_path / "corpus"
        _write_corpus(corpus_dir, 5)

        settings = SeederSettings()  # type: ignore[call-arg]
        assert settings.seeder_batch_size == 2  # seeder_env 에서 설정

        embedder = FakeEmbedder(dim=8)
        store = FakeVectorStore()
        loader = CorpusLoader(corpus_dir)

        seeder = Seeder(loader=loader, embedder=embedder, store=store, settings=settings)
        result = seeder.run()

        assert result.total_loaded == 5
        assert result.total_embedded == 5
        assert result.total_upserted == 5
        assert embedder.call_count == 3  # ceil(5/2)
        assert store.upsert_count == 3

    def test_embedding_error_continues(self, seeder_env: dict[str, str], tmp_path: Path) -> None:
        """T-15: 임베딩 에러 → errors 카운트, 나머지 배치 계속."""
        corpus_dir = tmp_path / "corpus"
        _write_corpus(corpus_dir, 4)

        settings = SeederSettings()  # type: ignore[call-arg]
        # batch_size=2, 4 snippets → 2 batches
        # 첫 배치 실패, 두 번째 성공
        call_num = 0

        class FailOnceEmbedder:
            def embed_texts(self, texts: list[str]) -> list[list[float]]:
                nonlocal call_num
                call_num += 1
                if call_num == 1:
                    msg = "first batch fails"
                    raise RuntimeError(msg)
                return [[0.1] * 8 for _ in texts]

        store = FakeVectorStore()
        loader = CorpusLoader(corpus_dir)

        seeder = Seeder(
            loader=loader,
            embedder=FailOnceEmbedder(),
            store=store,
            settings=settings,
        )
        result = seeder.run()

        assert result.total_loaded == 4
        assert result.errors == 2  # first batch (2 items) failed
        assert result.total_embedded == 2  # second batch succeeded
        assert result.total_upserted == 2
