# ============================================================
# services/flask-webhook — multi-stage Dockerfile
# ============================================================
# Stage 1: base
FROM python:3.12-slim AS base
RUN pip install --no-cache-dir uv
WORKDIR /app

# Stage 2: builder — 의존성 설치 + wheel 빌드
FROM base AS builder
COPY pyproject.toml ./
COPY src/ src/
COPY --from=trigger-core-wheel /wheels/ /wheels/
RUN uv pip install --system /wheels/*.whl && \
    uv pip install --system . && \
    uv build --wheel

# Stage 3: tester — 테스트 실행용
FROM builder AS tester
COPY tests/ tests/
RUN uv pip install --system pytest pytest-cov pytest-asyncio && \
    uv pip install --system dist/*.whl && \
    pytest --cov=flask_webhook --cov-branch --cov-fail-under=95

# Stage 4: runtime — 최소 이미지
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl /tmp/
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
EXPOSE 8080
CMD ["python", "-m", "flask_webhook.app"]
