# leebalso-mock

리발소 REST API Mock 서버 — 결정성 보장 fixture 기반 config 응답.

## API

```
GET /config/httpm?env=dev|stage|prod[&case=case-001]
GET /health
```

## 개발

```bash
make test       # 단위 테스트
make coverage   # 커버리지 (≥95%)
make lint       # ruff + mypy
make image      # Docker runtime image
```
