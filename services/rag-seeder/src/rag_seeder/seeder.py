"""Seeder — 오케스트레이션: load → batch embed → batch upsert."""

from __future__ import annotations

import logging
import time

from .corpus_loader import CorpusLoader
from .models import SeedResult, Snippet
from .protocols import EmbeddingClient, VectorStore
from .settings import SeederSettings

logger = logging.getLogger(__name__)


class Seeder:
    """코퍼스 시딩 오케스트레이터."""

    def __init__(
        self,
        *,
        loader: CorpusLoader,
        embedder: EmbeddingClient,
        store: VectorStore,
        settings: SeederSettings,
    ) -> None:
        self._loader = loader
        self._embedder = embedder
        self._store = store
        self._settings = settings

    def run(self) -> SeedResult:
        """코퍼스 로드 → 배치 임베딩 → 배치 upsert → 결과 반환."""
        start = time.monotonic()

        snippets = self._loader.load()
        total_loaded = len(snippets)
        logger.info("Loaded %d snippets from corpus", total_loaded)

        if total_loaded == 0:
            elapsed = time.monotonic() - start
            return SeedResult(
                total_loaded=0,
                total_embedded=0,
                total_upserted=0,
                errors=0,
                duration_seconds=elapsed,
            )

        self._store.ensure_collection(
            self._settings.seeder_collection_name,
            self._settings.embedding_dim,
        )

        total_embedded = 0
        total_upserted = 0
        errors = 0
        batch_size = self._settings.seeder_batch_size

        for i in range(0, total_loaded, batch_size):
            batch = snippets[i : i + batch_size]
            try:
                vectors = self._embedder.embed_texts([s.comment for s in batch])
                total_embedded += len(vectors)
            except Exception:
                logger.exception("Embedding failed for batch starting at %d", i)
                errors += len(batch)
                continue

            payloads = [self._snippet_to_payload(s) for s in batch]
            ids = [s.id for s in batch]
            upserted = self._store.upsert(
                self._settings.seeder_collection_name,
                ids,
                vectors,
                payloads,
            )
            total_upserted += upserted

        elapsed = time.monotonic() - start
        logger.info(
            "Seeding complete: loaded=%d embedded=%d upserted=%d errors=%d (%.2fs)",
            total_loaded,
            total_embedded,
            total_upserted,
            errors,
            elapsed,
        )
        return SeedResult(
            total_loaded=total_loaded,
            total_embedded=total_embedded,
            total_upserted=total_upserted,
            errors=errors,
            duration_seconds=elapsed,
        )

    def _snippet_to_payload(self, snippet: Snippet) -> dict[str, object]:
        """Snippet → Qdrant payload dict."""
        return {
            "snippet_id": snippet.id,
            "path": snippet.path,
            "symbol": snippet.symbol,
            "line_range": snippet.line_range,
            "comment": snippet.comment,
            "repo": self._settings.seeder_repo_name,
        }
