"""T-18: CLI main 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rag_seeder.cli import GatewayEmbeddingAdapter, _build_embedder, main


class TestGatewayEmbeddingAdapter:
    def test_embed_texts(self) -> None:
        """어댑터가 LLMGateway.embed 를 올바르게 위임한다."""
        mock_gw = MagicMock()
        mock_gw.embed.return_value = MagicMock(vectors=[[0.1, 0.2], [0.3, 0.4]])
        adapter = GatewayEmbeddingAdapter(mock_gw)
        result = adapter.embed_texts(["text1", "text2"])
        assert result == [[0.1, 0.2], [0.3, 0.4]]
        mock_gw.embed.assert_called_once()


class TestBuildEmbedder:
    @patch("rag_seeder.cli.LLMGateway")
    def test_build_embedder(self, mock_gw_cls: MagicMock) -> None:
        """_build_embedder 가 GatewayEmbeddingAdapter 를 반환."""
        mock_gw_cls.return_value = MagicMock()
        gw_settings = MagicMock()
        embedder = _build_embedder(gw_settings)
        assert isinstance(embedder, GatewayEmbeddingAdapter)
        mock_gw_cls.assert_called_once_with(gw_settings)


class TestCli:
    @patch("rag_seeder.cli.QdrantStore")
    @patch("rag_seeder.cli._build_embedder")
    @patch("rag_seeder.cli.GatewaySettings")
    @patch("rag_seeder.cli.SeederSettings")
    def test_main_success(
        self,
        mock_settings_cls: MagicMock,
        mock_gw_settings_cls: MagicMock,
        mock_build_embedder: MagicMock,
        mock_store_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """T-18: 정상 실행 → exit code 0."""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()

        mock_settings = MagicMock()
        mock_settings.seeder_corpus_dir = str(corpus_dir)
        mock_settings.seeder_collection_name = "test"
        mock_settings.seeder_batch_size = 10
        mock_settings.seeder_repo_name = "repo"
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_timeout = 5.0
        mock_settings.embedding_dim = 8
        mock_settings_cls.return_value = mock_settings

        mock_gw_settings_cls.return_value = MagicMock()
        mock_build_embedder.return_value = MagicMock()
        mock_store_cls.return_value = MagicMock()

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    @patch("rag_seeder.cli.QdrantStore")
    @patch("rag_seeder.cli._build_embedder")
    @patch("rag_seeder.cli.GatewaySettings")
    @patch("rag_seeder.cli.SeederSettings")
    def test_main_with_errors(
        self,
        mock_settings_cls: MagicMock,
        mock_gw_settings_cls: MagicMock,
        mock_build_embedder: MagicMock,
        mock_store_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """T-18b: 에러 발생 시 → exit code 1."""
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()
        # 코퍼스 작성
        (corpus_dir / "test.comments.yaml").write_text(
            "- id: a::b\n  path: a.java\n  symbol: b\n  line_range: [1, 2]\n  comment: test\n",
            encoding="utf-8",
        )

        mock_settings = MagicMock()
        mock_settings.seeder_corpus_dir = str(corpus_dir)
        mock_settings.seeder_collection_name = "test"
        mock_settings.seeder_batch_size = 10
        mock_settings.seeder_repo_name = "repo"
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_timeout = 5.0
        mock_settings.embedding_dim = 8
        mock_settings_cls.return_value = mock_settings

        mock_gw_settings_cls.return_value = MagicMock()
        # 임베딩 실패 → errors > 0
        mock_embedder = MagicMock()
        mock_embedder.embed_texts.side_effect = RuntimeError("fail")
        mock_build_embedder.return_value = mock_embedder
        mock_store_cls.return_value = MagicMock()

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
