# ============================================================
# libs/llm-gateway — 표준 Makefile (P00 reference 기반)
# ============================================================

UV ?= uv
SVC := llm-gateway
PKG := llm_gateway
IMAGE := llm-gateway

.PHONY: help test coverage lint format build image image-test clean

help:
	@echo "타깃: test coverage lint format build image image-test clean"

test:
	$(UV) run pytest

coverage:
	$(UV) run pytest \
		--cov=src/$(PKG) \
		--cov-branch \
		--cov-report=term-missing \
		--cov-fail-under=95

lint:
	$(UV) run ruff check src tests
	$(UV) run ruff format --check src tests
	$(UV) run mypy src

format:
	$(UV) run ruff format src tests
	$(UV) run ruff check --fix src tests

build:
	$(UV) build --wheel

image:
	docker build --target runtime -t $(IMAGE):latest .

image-test:
	docker build --target tester -t $(IMAGE):test .

clean:
	rm -rf dist build .pytest_cache .coverage htmlcov .ruff_cache .mypy_cache *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
