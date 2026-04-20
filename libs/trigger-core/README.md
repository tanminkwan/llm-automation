# `trigger-core` — Trigger 추상화 라이브러리

워크플로우 진입 이벤트(webhook, 파일, 스케줄 등) 를 **SCM-중립 도메인 모델** (`TriggerEvent`) 로 변환하고 **작업 큐** (Celery 등) 로 발행하는 계층을 추상화한다.

서비스(flask-webhook, e2e harness 등) 는 `TriggerSource` / `TriggerDispatcher` Protocol 만 의존한다. 새 이벤트 소스를 추가해도 기존 코드를 수정하지 않는다 (OCP).

## 핵심

```python
from trigger_core import (
    CeleryTriggerDispatcher,
    DeliveryCache,
    MockTriggerEmitter,
    TriggerEvent,
    WebhookTriggerSource,
    WorkType,
)

# 1) 프로덕션: HTTP webhook 수신
source = WebhookTriggerSource(secret="...")
dispatcher = CeleryTriggerDispatcher(celery_app)

event = source.parse(raw_bytes, headers)
task_id = dispatcher.dispatch(event)

# 2) 테스트/로컬: TriggerEvent 직접 발행
emitter = MockTriggerEmitter(dispatcher)
emitter.emit_from_json("e2e/fixtures/scenario_A/trigger.json")
```

## 구성 요소

| 클래스 / 함수 | 역할 |
|---|---|
| `TriggerEvent`, `RepoRef`, `WorkType` | SCM-중립 도메인 모델 |
| `TriggerSource` (Protocol) | 원시 이벤트 → `TriggerEvent` 변환 + 검증 |
| `TriggerDispatcher` (Protocol) | `TriggerEvent` → 작업 큐 발행 |
| `WebhookTriggerSource` | HTTP webhook (HMAC + Gitea payload) 구현 |
| `CeleryTriggerDispatcher` | `celery.send_task` 래퍼 |
| `MockTriggerEmitter` | 테스트/로컬용. `TriggerSource` 우회 |
| `DeliveryCache` | 멱등키 TTL 캐시 |
| `verify_signature` | HMAC-SHA256 유틸 |
| `classify_files` | 변경 파일 → `WorkType` 판별 |

## 예외

`TriggerError` 최상위. `InvalidSignatureError` / `InvalidPayloadError` / `UnsupportedWorkTypeError` / `DuplicateTriggerError`.

## 표준 타깃

```bash
make lint           # ruff + ruff format --check + mypy strict
make coverage       # pytest --cov-fail-under=95
make image          # docker build runtime stage
make image-test     # docker build tester stage (CI 게이트)
```

## 산출물

- `docs/요구사항.md` — FR/NFR
- `docs/설계서.md` — Protocol/구현체/테스트
- `docs/테스트결과서.md` — 실행 결과 + DoD 매핑

상세 Phase 문서: `docs/P06_{요구사항,설계서}.md`.
