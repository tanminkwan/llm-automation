"""CLI 엔트리포인트 — Settings 로드 → 의존성 조립 → Seeder.run()."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from llm_gateway import EMBEDDING, LLMGateway
from llm_gateway.settings import GatewaySettings

from .corpus_loader import CorpusLoader
from .models import SeedResult
from .protocols import EmbeddingClient
from .qdrant_store import QdrantStore
from .seeder import Seeder
from .settings import SeederSettings


class GatewayEmbeddingAdapter:
    """LLMGateway.embed() 를 EmbeddingClient Protocol 에 맞춘다."""

    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """embedding alias 로 벡터화."""
        resp = self._gateway.embed(EMBEDDING, texts)
        vectors: list[list[float]] = resp.vectors
        return vectors


def _build_embedder(gw_settings: GatewaySettings) -> EmbeddingClient:
    gateway = LLMGateway(gw_settings)
    return GatewayEmbeddingAdapter(gateway)


def main() -> None:
    """메인 엔트리포인트."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    settings = SeederSettings()  # type: ignore[call-arg]
    gw_settings = GatewaySettings()  # type: ignore[call-arg]

    loader = CorpusLoader(Path(settings.seeder_corpus_dir))
    embedder = _build_embedder(gw_settings)
    store = QdrantStore(settings.qdrant_url, timeout=settings.qdrant_timeout)

    seeder = Seeder(
        loader=loader,
        embedder=embedder,
        store=store,
        settings=settings,
    )

    result: SeedResult = seeder.run()
    logger.info("Result: %s", result.model_dump_json())

    if result.errors > 0:
        logger.warning("Completed with %d errors", result.errors)
        sys.exit(1)

    sys.exit(0)
