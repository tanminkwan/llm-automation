FROM python:3.12-slim AS base
RUN pip install --no-cache-dir uv
WORKDIR /app

FROM base AS builder
COPY pyproject.toml ./
COPY src/ src/
RUN uv pip install --system . && \
    uv build --wheel

FROM builder AS tester
COPY tests/ tests/
RUN uv pip install --system pytest pytest-cov pytest-asyncio httpx && \
    uv pip install --system dist/*.whl && \
    pytest --cov=celery_configaudit --cov-branch --cov-fail-under=95

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl /tmp/
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
CMD ["celery", "-A", "celery_configaudit.app:celery_app", "worker", "-Q", "configaudit_queue", "--loglevel=info"]
