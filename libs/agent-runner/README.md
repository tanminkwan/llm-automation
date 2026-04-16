# agent-runner

AI Agent CLI 추상화 라이브러리 — `AgentRunner` Protocol 기반 subprocess 실행.

OpenCode, Claude Code 등 다양한 Agent CLI 를 단일 인터페이스로 호출.

## 사용법

```python
from agent_runner import build_runner, RunnerSettings, ToolSpec

settings = RunnerSettings()
runner = build_runner(settings.agent_runner_kind, settings=settings)

result = runner.run(
    work_dir=Path("/workspace/repo"),
    prompt="Add docstrings to all public methods",
    files=[Path("src/main.py")],
    tools=[ToolSpec(name="search_codebase", description="Search code", input_schema={}, server_url="http://rag-mcp:9001")],
    env={"CHAT_LLM_API_KEY": "sk-..."},
)
print(result.exit_code, result.stdout)
```

## 개발

```bash
make test       # 단위 테스트
make coverage   # 커버리지 (≥95%)
make lint       # ruff + mypy
make build      # wheel
make image      # Docker runtime image
```
