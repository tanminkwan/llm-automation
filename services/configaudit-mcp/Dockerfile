# ============================================================
# services/configaudit-mcp — multi-stage Dockerfile
# ============================================================
# Stage 1: base
FROM python:3.12-slim AS base
RUN pip install --no-cache-dir uv
WORKDIR /app

# Stage 2: builder — 의존성 설치 + wheel 빌드
FROM base AS builder
COPY pyproject.toml README.md ./
COPY src/ src/
RUN uv pip install --system . && \
    uv build --wheel

# Stage 3: tester — 테스트 실행용
FROM builder AS tester
COPY tests/ tests/
RUN uv pip install --system pytest pytest-cov pytest-asyncio httpx && \
    uv pip install --system dist/*.whl && \
    pytest --cov=configaudit_mcp --cov-branch --cov-fail-under=95

# Stage 4: runtime — 최소 이미지
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl /tmp/
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
EXPOSE 9002
CMD ["python", "-m", "uvicorn", "configaudit_mcp.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "9002"]
