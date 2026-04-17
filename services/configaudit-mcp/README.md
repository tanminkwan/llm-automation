# configaudit-mcp

Config Audit MCP 서비스 — `get_config_context` 도구를 통해 리발소 API 에서 dev/stage/prod 3개 환경의 http.m config 를 조회하고, 3-way diff + 이상 패턴 탐지 결과를 반환한다.

## 빠른 시작

```bash
# 테스트
make coverage

# 린트 + 타입체크
make lint

# 빌드
make build
```

## 설정

`sample.env` 참조. `cp sample.env .env` 후 필요 시 값 수정.
