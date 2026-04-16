# rag-seeder

RAG 코퍼스 시딩 서비스 — `corpus/**/*.comments.yaml` 을 읽어 임베딩 벡터로 변환하고 Qdrant `code_comments` 컬렉션에 upsert 하는 one-shot 컨테이너.

## 빠른 시작

```bash
# 의존성 설치
uv sync --all-packages

# 테스트
make -C services/rag-seeder coverage

# 실행 (Qdrant + Embedding API 필요)
cd services/rag-seeder
cp sample.env .env
# .env 에 실제 값 채움
uv run rag-seeder
```

## 설정

`sample.env` 참조. 상세는 `docs/설계서.md §6`.
