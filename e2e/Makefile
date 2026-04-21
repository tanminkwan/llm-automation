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

# 전체 E2E — stack 기동 → pytest → teardown 을 단일 명령으로 실행.
# teardown 은 trap 으로 보장 (pytest 실패 시에도 항상 stack_down 호출).
# 호스트 pytest 가 컨테이너 내부 주소(redis:6379) 가 아니라 localhost 로
# 접근해야 하므로 CELERY_* 를 localhost 로 강제 override 한다.
e2e:
	@set -eu; \
	trap 'bash bin/stack_down.sh' EXIT; \
	bash bin/stack_up.sh; \
	set -a && . ../infra/.env && set +a; \
	export CELERY_BROKER_URL=redis://localhost:6379/0; \
	export CELERY_RESULT_BACKEND=redis://localhost:6379/1; \
	export E2E_ENABLED=1; \
	uv run --project . pytest tests

stack-up:
	bash bin/stack_up.sh

stack-down:
	bash bin/stack_down.sh

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
