"""rag-mcp 테스트 공통 픽스처."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from rag_mcp.app import create_app
from rag_mcp.search_engine import SearchEngine
from rag_mcp.settings import RagMcpSettings

# 환경변수 격리 대상 키
_ENV_KEYS = [
    "RAG_MCP_HOST",
    "RAG_MCP_PORT",
    "RAG_MCP_COLLECTION_NAME",
    "RAG_MCP_DEFAULT_K",
    "RAG_MCP_MAX_K",
    "QDRANT_URL",
    "QDRANT_TIMEOUT",
    # llm-gateway 키 (누출 방지)
    "EMBEDDING_BASE_URL",
    "EMBEDDING_MODEL",
    "EMBEDDING_API_KEY",
    "EMBEDDING_DIM",
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


class FakeEmbedder:
    """EmbeddingClient fake — 고정 차원 벡터 반환."""

    def __init__(self, dim: int = 8) -> None:
        self._dim = dim

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self._dim for _ in texts]


class FakeVectorReader:
    """VectorReader fake — 고정 결과 반환."""

    def __init__(self, hits: list[dict[str, object]] | None = None) -> None:
        self._hits = hits or []

    def search(
        self,
        collection: str,
        vector: list[float],
        limit: int,
    ) -> list[dict[str, object]]:
        return self._hits[:limit]


SAMPLE_HITS: list[dict[str, object]] = [
    {
        "payload": {
            "snippet_id": "svc::method1",
            "path": "pkg/svc.java",
            "symbol": "method1",
            "line_range": [10, 20],
            "comment": "주석 1",
        },
        "score": 0.95,
    },
    {
        "payload": {
            "snippet_id": "svc::method2",
            "path": "pkg/svc2.java",
            "symbol": "method2",
            "line_range": [30, 40],
            "comment": "주석 2",
        },
        "score": 0.85,
    },
    {
        "payload": {
            "snippet_id": "svc::method3",
            "path": "pkg/svc3.java",
            "symbol": "method3",
            "line_range": [50, 60],
            "comment": "주석 3",
        },
        "score": 0.75,
    },
]


@pytest.fixture()
def settings(monkeypatch: pytest.MonkeyPatch) -> RagMcpSettings:
    """테스트용 설정."""
    monkeypatch.setenv("RAG_MCP_DEFAULT_K", "5")
    monkeypatch.setenv("RAG_MCP_MAX_K", "20")
    monkeypatch.setenv("RAG_MCP_COLLECTION_NAME", "test_collection")
    return RagMcpSettings()  # type: ignore[call-arg]


@pytest.fixture()
def engine() -> SearchEngine:
    """SAMPLE_HITS 를 반환하는 SearchEngine."""
    return SearchEngine(
        embedder=FakeEmbedder(),
        reader=FakeVectorReader(SAMPLE_HITS),
        collection="test_collection",
    )


@pytest.fixture()
def client(engine: SearchEngine, settings: RagMcpSettings) -> TestClient:
    application = create_app(engine=engine, settings=settings)
    return TestClient(application)
