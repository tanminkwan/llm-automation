# ============================================================
# llm-automation — 루트 Makefile (워크스페이스 위임)
# 새 모듈 추가 시 MEMBERS 변수에 추가 (그라운드 룰 §1, ②)
# ============================================================

MEMBERS := libs/_template libs/llm-gateway
# 후속 phase 마다 멤버 추가:
# MEMBERS += libs/agent-runner
# MEMBERS += services/leebalso-mock services/rag-mcp ...

.PHONY: help sync test-all coverage-all lint-all format-all build-all image-all clean-all

help:
	@echo "사용 가능한 타깃:"
	@echo "  make sync           — uv sync (환경 재현)"
	@echo "  make test-all       — 모든 멤버 테스트"
	@echo "  make coverage-all   — 모든 멤버 커버리지 (≥95%)"
	@echo "  make lint-all       — 모든 멤버 린트+포맷체크+타입체크"
	@echo "  make format-all     — 모든 멤버 자동 포맷"
	@echo "  make build-all      — 모든 멤버 wheel 빌드"
	@echo "  make image-all      — 모든 멤버 도커 이미지 빌드"
	@echo "  make clean-all      — 모든 멤버 산출물 청소"
	@echo ""
	@echo "현재 멤버: $(MEMBERS)"

sync:
	uv sync

test-all:
	@for m in $(MEMBERS); do \
		echo "=== test: $$m ==="; \
		$(MAKE) -C $$m test || exit 1; \
	done

coverage-all:
	@for m in $(MEMBERS); do \
		echo "=== coverage: $$m ==="; \
		$(MAKE) -C $$m coverage || exit 1; \
	done

lint-all:
	@for m in $(MEMBERS); do \
		echo "=== lint: $$m ==="; \
		$(MAKE) -C $$m lint || exit 1; \
	done

format-all:
	@for m in $(MEMBERS); do \
		echo "=== format: $$m ==="; \
		$(MAKE) -C $$m format || exit 1; \
	done

build-all:
	@for m in $(MEMBERS); do \
		echo "=== build: $$m ==="; \
		$(MAKE) -C $$m build || exit 1; \
	done

image-all:
	@for m in $(MEMBERS); do \
		echo "=== image: $$m ==="; \
		$(MAKE) -C $$m image || exit 1; \
	done

clean-all:
	@for m in $(MEMBERS); do \
		echo "=== clean: $$m ==="; \
		$(MAKE) -C $$m clean; \
	done
