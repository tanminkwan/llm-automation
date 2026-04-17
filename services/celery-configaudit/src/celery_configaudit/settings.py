"""설정 -- CeleryConfigAuditSettings (pydantic-settings)."""

from pydantic_settings import BaseSettings


class CeleryConfigAuditSettings(BaseSettings):
    """celery-configaudit 서비스 설정."""

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    configaudit_mcp_url: str = "http://localhost:9002"
    reasoning_llm_base_url: str = "https://api.openai.com/v1"
    reasoning_llm_model: str = "o4-mini"
    reasoning_llm_api_key: str = ""
    reasoning_llm_timeout_seconds: int = 60
    report_output_dir: str = "/tmp/celery-configaudit/reports"  # noqa: S108
    agent_max_iterations: int = 5
