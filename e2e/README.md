# e2e — Phase 6 E2E Harness

실제 Gitea/git I/O 없이 **사전 준비된 파일(fixture)** 로 워크플로우 A/B 를 재현하는 E2E 검증 harness.

## 빠른 시작

```bash
# 1) fixture/CLI 구조적 검증만 (stack 없이 실행 가능)
make e2e-offline           # 루트에서
# or
cd e2e && make test-offline

# 2) 실제 stack + OpenAI E2E
export OPENAI_API_KEY=sk-...
export FIXTURE_RESULT_DIR=$(pwd)/.fixtures/results
export REPORT_OUTPUT_DIR=$(pwd)/.reports
make e2e                   # 루트에서 — stack_up → pytest → stack_down (trap)
```

## 디렉터리

- `fixtures/scenario_A/` — Java 주석 시나리오 (입력 트리 + trigger.json + expected)
- `fixtures/scenario_B/case-001/` — ConfigAudit 시나리오 (trigger.json + JSON Schema)
- `bin/emit_trigger.py` — `trigger.json` 을 Celery 큐에 발행하는 CLI
- `bin/stack_up.sh` / `bin/stack_down.sh` — docker stack 기동/정리
- `tests/` — offline(`test_fixtures.py`, `test_emit_trigger.py`) + e2e(`test_scenario_a/b.py`)

## 환경변수

자세한 내용은 `docs/설계서.md §4` 참고. 주요 키:

| 키 | 기본값 |
|---|---|
| `E2E_ENABLED` | unset (설정 시에만 e2e scenario 실행) |
| `E2E_BROKER_URL` | `redis://localhost:6379/0` |
| `E2E_STACK_NAME` | `llmauto-e2e` |
| `FIXTURE_RESULT_DIR` | `/fixtures/results` |
| `REPORT_OUTPUT_DIR` | `/reports` |
