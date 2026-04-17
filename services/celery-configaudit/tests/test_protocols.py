"""Protocol 만족 테스트."""

from .conftest import FakeLLMToolCall, FakeMCP


class TestProtocols:
    def test_fake_mcp_satisfies_protocol(self) -> None:
        from celery_configaudit.protocols import ConfigAuditClient

        client: ConfigAuditClient = FakeMCP()
        assert hasattr(client, "get_config_context")

    def test_fake_llm_satisfies_protocol(self) -> None:
        llm = FakeLLMToolCall()
        assert hasattr(llm, "chat")
