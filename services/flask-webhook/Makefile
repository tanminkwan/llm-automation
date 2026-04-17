UV ?= uv
SVC := flask-webhook
PKG := flask_webhook
IMAGE := $(SVC)

.PHONY: help test coverage lint format build image image-test clean

help:
	@echo "Targets: test coverage lint format build image image-test clean"

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
	rm -rf dist build .pytest_cache .coverage .mypy_cache .ruff_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
