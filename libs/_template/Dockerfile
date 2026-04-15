# syntax=docker/dockerfile:1.7
# ============================================================
# libs/_template — 표준 multi-stage Dockerfile (Phase 0 reference)
# 후속 모듈은 본 파일을 복사하여 PKG 만 변경한다.
# stages: base / builder / tester / runtime
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

# ─── 3) tester (CI 검증용 — 그라운드 룰 §1, ③) ──────────
FROM builder AS tester
COPY tests ./tests
# editable 설치로 src/ 경로에서 직접 import 되게 하여 coverage 경로 일치
RUN pip install --no-cache-dir -e . \
    pytest pytest-cov ruff "mypy>=1.11"
RUN ruff check src tests \
 && ruff format --check src tests \
 && mypy src \
 && pytest --cov=src/_template --cov-branch --cov-fail-under=95

# ─── 4) runtime (배포 이미지) ───────────────────────────
FROM base AS runtime
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl
USER app
CMD ["python", "-c", "from _template import Greeter; print('_template ok')"]
