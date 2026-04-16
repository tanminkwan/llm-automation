# syntax=docker/dockerfile:1.7
# ============================================================
# services/leebalso-mock — 표준 multi-stage Dockerfile
# ============================================================
ARG PYTHON_VERSION=3.12

# ─── 1) base ────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN useradd -m -u 1000 app
WORKDIR /app

# ─── 2) builder ─────────────────────────────────────────
FROM python:${PYTHON_VERSION} AS builder
RUN pip install --no-cache-dir uv hatchling
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv build --wheel --out-dir /build/dist

# ─── 3) tester ──────────────────────────────────────────
FROM builder AS tester
COPY tests ./tests
COPY fixtures ./fixtures
RUN pip install --no-cache-dir -e ".[dev]" \
    pytest pytest-cov httpx ruff "mypy>=1.11"
RUN ruff check src tests \
 && ruff format --check src tests \
 && mypy src \
 && pytest --cov=src/leebalso_mock --cov-branch --cov-fail-under=95

# ─── 4) runtime ─────────────────────────────────────────
FROM base AS runtime
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
COPY fixtures /app/fixtures
USER app
EXPOSE 9100
CMD ["uvicorn", "leebalso_mock.app:app", "--host", "0.0.0.0", "--port", "9100"]
