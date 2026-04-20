.PHONY: help test test-offline e2e stack-up stack-down lint format

help:
	@echo "Targets:"
	@echo "  test-offline  — fixture/CLI 구조적 검증만 (기본)"
	@echo "  e2e           — 실제 stack 기동 + 시나리오 A/B 실행 (E2E_ENABLED=1)"
	@echo "  stack-up      — docker stack deploy"
	@echo "  stack-down    — docker stack rm (teardown)"
	@echo "  lint / format — ruff"

test: test-offline

test-offline:
	uv run --project . pytest tests -m "not e2e"

# 전체 E2E — teardown 은 trap 으로 보장
e2e:
	@set -eu; \
	trap 'bash bin/stack_down.sh' EXIT; \
	bash bin/stack_up.sh; \
	E2E_ENABLED=1 uv run --project . pytest tests

stack-up:
	bash bin/stack_up.sh

stack-down:
	bash bin/stack_down.sh

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
