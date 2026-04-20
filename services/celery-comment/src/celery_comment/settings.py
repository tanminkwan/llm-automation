"""CommentSettings — 환경변수 기반 설정."""

from pydantic_settings import BaseSettings


class CommentSettings(BaseSettings):
    """celery-comment 서비스 설정."""

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    comment_work_dir: str = "/tmp/celery-comment"  # noqa: S108
    rag_mcp_url: str = "http://localhost:9001"
    agent_runner_kind: str = "opencode"
    agent_timeout_seconds: int = 300
    git_commit_author: str = "AI Bot <ai-bot@local>"
    git_client: str = "subprocess"  # "subprocess" | "fixture"
    fixture_source_dir: str = "/fixtures/source"
    fixture_result_dir: str = "/fixtures/results"

    chat_llm_base_url: str = "https://api.openai.com/v1"
    chat_llm_model: str = "gpt-4o"
    chat_llm_api_key: str = ""
    chat_llm_timeout_seconds: int = 120
