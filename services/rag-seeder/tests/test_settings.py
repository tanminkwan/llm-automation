"""T-16~T-17: SeederSettings 테스트."""

from __future__ import annotations

import pytest

from rag_seeder.settings import SeederSettings


class TestSeederSettings:
    def test_full_env(self, seeder_env: dict[str, str]) -> None:
        """T-16: 모든 키 env 주입 시 정상 로딩."""
        settings = SeederSettings()  # type: ignore[call-arg]
        assert settings.seeder_corpus_dir == seeder_env["SEEDER_CORPUS_DIR"]
        assert settings.seeder_collection_name == seeder_env["SEEDER_COLLECTION_NAME"]
        assert settings.seeder_batch_size == int(seeder_env["SEEDER_BATCH_SIZE"])
        assert settings.seeder_repo_name == seeder_env["SEEDER_REPO_NAME"]
        assert settings.qdrant_url == seeder_env["QDRANT_URL"]
        assert settings.qdrant_timeout == float(seeder_env["QDRANT_TIMEOUT"])
        assert settings.embedding_dim == int(seeder_env["EMBEDDING_DIM"])

    def test_defaults_except_required(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """T-17: EMBEDDING_DIM 만 주입, 나머지 기본값."""
        monkeypatch.setenv("EMBEDDING_DIM", "1024")
        settings = SeederSettings()  # type: ignore[call-arg]
        assert settings.seeder_corpus_dir == "corpus"
        assert settings.seeder_collection_name == "code_comments"
        assert settings.seeder_batch_size == 32
        assert settings.seeder_repo_name == "seed-repo"
        assert settings.qdrant_url == "http://localhost:6333"  # noqa: S104
        assert settings.embedding_dim == 1024
