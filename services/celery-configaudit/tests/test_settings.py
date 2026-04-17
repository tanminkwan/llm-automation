"""Settings 테스트."""

import pytest

from celery_configaudit.settings import CeleryConfigAuditSettings


class TestSettings:
    def test_env_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CONFIGAUDIT_MCP_URL", "http://remote:9002")
        monkeypatch.setenv("REASONING_LLM_MODEL", "gpt-4o")
        monkeypatch.setenv("AGENT_MAX_ITERATIONS", "10")
        s = CeleryConfigAuditSettings()
        assert s.configaudit_mcp_url == "http://remote:9002"
        assert s.reasoning_llm_model == "gpt-4o"
        assert s.agent_max_iterations == 10

    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in [
            "CELERY_BROKER_URL",
            "CELERY_RESULT_BACKEND",
            "CONFIGAUDIT_MCP_URL",
            "REASONING_LLM_BASE_URL",
            "REASONING_LLM_MODEL",
            "REASONING_LLM_API_KEY",
            "REASONING_LLM_TIMEOUT_SECONDS",
            "REPORT_OUTPUT_DIR",
            "AGENT_MAX_ITERATIONS",
        ]:
            monkeypatch.delenv(key, raising=False)
        s = CeleryConfigAuditSettings()
        assert s.reasoning_llm_model == "o4-mini"
        assert s.agent_max_iterations == 5
