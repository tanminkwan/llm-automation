# ============================================================
# services/rag-mcp — multi-stage Dockerfile
# ============================================================
# Stage 1: base
FROM python:3.12-slim AS base
RUN pip install --no-cache-dir uv
WORKDIR /app

# Stage 2: builder — 의존성 설치 + wheel 빌드
FROM base AS builder
COPY pyproject.toml ./
COPY src/ src/
COPY --from=llm-gateway-wheel /wheels/ /wheels/
RUN uv pip install --system /wheels/*.whl && \
    uv build --wheel

# Stage 3: tester — 테스트 실행용
FROM builder AS tester
COPY tests/ tests/
RUN uv pip install --system pytest pytest-cov pytest-asyncio httpx && \
    uv pip install --system dist/*.whl && \
    pytest --cov=rag_mcp --cov-branch --cov-fail-under=95

# Stage 4: runtime — 최소 이미지
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl /tmp/
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
EXPOSE 9001
CMD ["uvicorn", "rag_mcp.app:app", "--host", "0.0.0.0", "--port", "9001"]
