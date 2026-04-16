# rag-mcp

RAG 벡터 검색 MCP 서비스 — `search_codebase(query, k)` 도구를 FastAPI 엔드포인트로 노출하여 AI Agent 가 Qdrant 코퍼스를 검색할 수 있게 한다.

## 빠른 시작

```bash
# 의존성 설치
uv sync --all-packages

# 테스트
make -C services/rag-mcp coverage

# 실행 (Qdrant + Embedding API 필요)
cd services/rag-mcp
cp sample.env .env
# .env 에 실제 값 채움
uv run uvicorn rag_mcp.app:app --host 0.0.0.0 --port 9001
```

## 설정

`sample.env` 참조. 상세는 `docs/설계서.md §6`.
