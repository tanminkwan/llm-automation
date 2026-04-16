# `llm-gateway` — LLM/Embedding 추상화 게이트웨이

표준 alias (`chat-llm` / `reasoning-llm` / `embedding`) 로 LLM 백엔드를 호출하는 라이브러리.
호출측은 backend 구현체를 모르고, **환경변수만으로** OpenAI / vLLM 사이를 전환한다 (`CLAUDE.md §5`, `architecture_test.md §5·§12`).

## 핵심

```python
from llm_gateway import GatewaySettings, LLMGateway, ChatMessage

settings = GatewaySettings()                     # env 자동 로딩
gateway = LLMGateway(settings)                   # 기본 OpenAI factory

resp = gateway.chat(
    "chat-llm",
    messages=[ChatMessage(role="user", content="안녕")],
)
print(resp.content, resp.usage.total_tokens)

vec = gateway.embed("embedding", texts=["문장1", "문장2"])
print(vec.dim, len(vec.vectors))
```

## 사용 가능한 alias

| alias | 용도 | 표준 환경변수 묶음 |
|---|---|---|
| `chat-llm` | 일반 chat / 코드 주석 (Workflow A) | `CHAT_LLM_*` |
| `reasoning-llm` | 분석 · 추론 (Workflow B) | `REASONING_LLM_*` |
| `embedding` | 텍스트 임베딩 | `EMBEDDING_*` |

상수가 필요하면 `from llm_gateway import CHAT_LLM, REASONING_LLM, EMBEDDING`.

## 환경변수 (그라운드 룰 §6/§7)

자세한 키 목록은 `docs/설계서.md §6` 참조. 모든 키는 루트 `sample.env` 에 미러링되어 있다.

```bash
CHAT_LLM_BASE_URL=https://api.openai.com/v1
CHAT_LLM_MODEL=gpt-4o
CHAT_LLM_API_KEY=sk-...
# ... (REASONING_LLM_*, EMBEDDING_*, *_TIMEOUT_SECONDS, *_MAX_RETRIES)
```

## 표준 타깃

```bash
make lint           # ruff + ruff format --check + mypy strict
make coverage       # pytest --cov-fail-under=95
make image          # docker build runtime stage
make image-test     # docker build tester stage (CI 게이트)
```

## 산출물

- `docs/요구사항.md` — FR/NFR
- `docs/설계서.md` — Protocol/어댑터/Settings/에러/재시도/TDD 케이스
- `docs/테스트결과서.md` — 실행 결과 + DoD 매핑
