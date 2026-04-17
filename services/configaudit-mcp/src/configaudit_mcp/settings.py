"""설정 — ConfigAuditSettings (pydantic-settings)."""

from pydantic_settings import BaseSettings


class ConfigAuditSettings(BaseSettings):
    """configaudit-mcp 서비스 설정."""

    configaudit_host: str = "0.0.0.0"  # noqa: S104
    configaudit_port: int = 9002
    configaudit_default_case: str = "case-001"
    leebalso_base_url: str = "http://localhost:9100"
    leebalso_timeout: float = 10.0
