# `_template` — 표준 검증용 reference 모듈

> ⚠️ **운영 코드 아닙니다.** 본 모듈은 워크스페이스 표준
> (uv workspace · ruff · mypy · pytest · 4-stage Dockerfile · `Makefile` 표준 타깃)
> 이 정상 동작함을 증명하는 카나리아입니다. 후속 모듈은 본 모듈의 구조를 복사해 시작합니다.

## 구조

```
libs/_template/
├── pyproject.toml   # 패키지 메타 + hatchling
├── Dockerfile       # 4-stage (base/builder/tester/runtime)
├── Makefile         # 표준 타깃 (test/coverage/lint/format/build/image/clean)
├── docs/            # 모듈 단위 요구사항/설계서/테스트결과서
├── src/_template/   # Greeter, TemplateSettings
└── tests/           # T-01 ~ T-06
```

## 빠른 사용

```bash
# 환경 동기화 (한 번)
cd <repo-root>
uv sync

# 표준 타깃 검증
cd libs/_template
make lint           # ruff + ruff format --check + mypy
make coverage       # pytest --cov-fail-under=95
make image          # docker build runtime stage
make image-test     # docker build tester stage (CI 게이트)
```

## 새 모듈 만들 때

```bash
cp -r libs/_template libs/<new-module>
# pyproject.toml: name, packages 수정
# Makefile: SVC, PKG 수정
# Dockerfile: pkg 경로 수정
# docs/, src/, tests/ 채우기
# 루트 Makefile 의 MEMBERS 에 추가
```

## 환경변수 (그라운드 룰 §6/§7)

| 키 | 의미 | 기본값 |
|---|---|---|
| `TEMPLATE_GREETING_PREFIX` | 인사말 접두어 | `Hello` |

`sample.env` 에 미러링되어 있습니다.
