"""rag-seeder 테스트 공통 픽스처."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from rag_seeder.models import Snippet

# 환경변수 격리 대상 키
_ENV_KEYS = [
    "SEEDER_CORPUS_DIR",
    "SEEDER_COLLECTION_NAME",
    "SEEDER_BATCH_SIZE",
    "SEEDER_REPO_NAME",
    "QDRANT_URL",
    "QDRANT_TIMEOUT",
    "EMBEDDING_DIM",
    # llm-gateway 키 (cli 테스트 등에서 누출 방지)
    "EMBEDDING_BASE_URL",
    "EMBEDDING_MODEL",
    "EMBEDDING_API_KEY",
    "CHAT_LLM_BASE_URL",
    "CHAT_LLM_MODEL",
    "CHAT_LLM_API_KEY",
    "REASONING_LLM_BASE_URL",
    "REASONING_LLM_MODEL",
    "REASONING_LLM_API_KEY",
]


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """환경변수 격리."""
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture()
def seeder_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict[str, str]:
    """SeederSettings 에 필요한 최소 환경변수."""
    env = {
        "SEEDER_CORPUS_DIR": str(tmp_path / "corpus"),
        "SEEDER_COLLECTION_NAME": "test_collection",
        "SEEDER_BATCH_SIZE": "2",
        "SEEDER_REPO_NAME": "test-repo",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_TIMEOUT": "5.0",
        "EMBEDDING_DIM": "8",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return env


@pytest.fixture()
def sample_snippet() -> Snippet:
    return Snippet(
        id="svc::method1",
        path="pkg/svc.java",
        symbol="method1",
        line_range=[10, 20],
        comment="테스트 주석",
    )


@pytest.fixture()
def sample_snippets() -> list[Snippet]:
    return [
        Snippet(
            id=f"svc::method{i}",
            path=f"pkg/svc{i}.java",
            symbol=f"method{i}",
            line_range=[i * 10, i * 10 + 10],
            comment=f"테스트 주석 {i}",
        )
        for i in range(5)
    ]


class FakeEmbedder:
    """EmbeddingClient fake — 고정 차원 벡터 반환."""

    def __init__(self, dim: int = 8, *, fail: bool = False) -> None:
        self._dim = dim
        self._fail = fail
        self.call_count = 0
        self.last_texts: list[str] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.call_count += 1
        self.last_texts = texts
        if self._fail:
            msg = "fake embedding error"
            raise RuntimeError(msg)
        return [[0.1] * self._dim for _ in texts]


class FakeVectorStore:
    """VectorStore fake — 메모리 저장."""

    def __init__(self) -> None:
        self.collections: dict[str, int] = {}
        self.points: dict[str, list[dict[str, Any]]] = {}
        self.upsert_count = 0

    def ensure_collection(self, name: str, dim: int) -> None:
        self.collections[name] = dim

    def upsert(
        self,
        collection: str,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, object]],
    ) -> int:
        self.upsert_count += 1
        if collection not in self.points:
            self.points[collection] = []
        for point_id, vector, payload in zip(ids, vectors, payloads, strict=True):
            self.points[collection].append({"id": point_id, "vector": vector, "payload": payload})
        return len(ids)
