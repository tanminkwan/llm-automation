# ============================================================
# libs/_template — 멤버용 표준 Makefile
# 후속 모듈은 본 파일을 복사하여 SVC/PKG 만 변경한다.
# ============================================================

UV ?= uv
SVC := _template
PKG := _template
# Docker tag 은 밑줄로 시작할 수 없음 → 배포명(seed-template) 사용
IMAGE := seed-template

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
