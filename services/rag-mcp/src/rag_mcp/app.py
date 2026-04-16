"""FastAPI 앱 — search_codebase MCP 엔드포인트 + 헬스체크."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .models import SearchRequest, SearchResult
from .search_engine import SearchEngine
from .settings import RagMcpSettings


def _build_default_engine(settings: RagMcpSettings) -> SearchEngine:  # pragma: no cover
    """Production 용 기본 SearchEngine 조립 (외부 의존 필요)."""
    from llm_gateway import EMBEDDING, LLMGateway
    from llm_gateway.settings import GatewaySettings

    gw_settings = GatewaySettings()  # type: ignore[call-arg]
    gateway = LLMGateway(gw_settings)

    class _GatewayEmbedder:
        def embed_texts(self, texts: list[str]) -> list[list[float]]:
            resp = gateway.embed(EMBEDDING, texts)
            vectors: list[list[float]] = resp.vectors
            return vectors

    from .qdrant_reader import QdrantReader

    reader = QdrantReader(
        settings.qdrant_url,
        timeout=settings.qdrant_timeout,
    )
    return SearchEngine(
        embedder=_GatewayEmbedder(),
        reader=reader,
        collection=settings.rag_mcp_collection_name,
    )


def create_app(
    *,
    engine: SearchEngine | None = None,
    settings: RagMcpSettings | None = None,
) -> FastAPI:
    """팩토리 — 테스트 시 engine 주입 (DIP)."""
    resolved_settings = settings or RagMcpSettings()

    if engine is None:  # pragma: no cover
        engine = _build_default_engine(resolved_settings)

    _engine = engine
    _settings = resolved_settings

    application = FastAPI(title="rag-mcp")

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/tools/search_codebase", response_model=SearchResult)
    def search_codebase(request: SearchRequest) -> SearchResult:
        k = request.k if request.k is not None else _settings.rag_mcp_default_k
        if k > _settings.rag_mcp_max_k:
            raise HTTPException(
                status_code=400,
                detail=f"k={k} exceeds max_k={_settings.rag_mcp_max_k}",
            )
        return _engine.search(request.query, k)

    return application
