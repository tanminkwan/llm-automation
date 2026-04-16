"""rag-seeder — RAG 코퍼스 시딩 (one-shot).

corpus YAML → EmbeddingGateway → Qdrant upsert.
"""

from __future__ import annotations

from .corpus_loader import CorpusLoader
from .models import SeedResult, Snippet
from .protocols import EmbeddingClient, VectorStore
from .qdrant_store import QdrantStore
from .seeder import Seeder
from .settings import SeederSettings

__version__ = "0.1.0"

__all__ = [
    "CorpusLoader",
    "EmbeddingClient",
    "QdrantStore",
    "SeedResult",
    "Seeder",
    "SeederSettings",
    "Snippet",
    "VectorStore",
]
