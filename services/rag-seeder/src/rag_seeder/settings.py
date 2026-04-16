"""SeederSettings — 환경변수 기반 설정 (pydantic-settings).

그라운드 룰 §7: 의미 있는 상수는 모두 환경변수로 주입.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SeederSettings(BaseSettings):
    """rag-seeder 설정."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    seeder_corpus_dir: str = Field(alias="SEEDER_CORPUS_DIR", default="corpus")
    seeder_collection_name: str = Field(alias="SEEDER_COLLECTION_NAME", default="code_comments")
    seeder_batch_size: int = Field(alias="SEEDER_BATCH_SIZE", default=32)
    seeder_repo_name: str = Field(alias="SEEDER_REPO_NAME", default="seed-repo")
    qdrant_url: str = Field(alias="QDRANT_URL", default="http://localhost:6333")
    qdrant_timeout: float = Field(alias="QDRANT_TIMEOUT", default=30.0)
    embedding_dim: int = Field(alias="EMBEDDING_DIM")
