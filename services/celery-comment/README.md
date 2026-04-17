# celery-comment

`comment_queue` 소비 → AgentRunner(OpenCode) 실행 → Java 주석 삽입 → Git commit/push.

## 빠른 시작

```bash
make test       # 단위 테스트
make coverage   # 커버리지 ≥ 95%
make lint       # ruff + mypy
make build      # wheel 빌드
```
