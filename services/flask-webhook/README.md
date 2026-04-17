# flask-webhook

Gitea push webhook 수신 → HMAC 검증 → work_type 라우팅 → Celery task 발행.

## 빠른 시작

```bash
make test       # 단위 테스트
make coverage   # 커버리지 ≥ 95%
make lint       # ruff + mypy
make build      # wheel 빌드
```
