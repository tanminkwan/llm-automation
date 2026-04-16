"""CorpusLoader — corpus/**/*.comments.yaml 재귀 로드."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Snippet


class CorpusLoader:
    """YAML 코퍼스 파일을 Snippet 리스트로 로드한다."""

    def __init__(self, corpus_dir: Path) -> None:
        self._corpus_dir = corpus_dir

    def load(self) -> list[Snippet]:
        """corpus_dir/**/*.comments.yaml 을 재귀 탐색하여 Snippet 리스트 반환."""
        snippets: list[Snippet] = []
        for yaml_path in sorted(self._corpus_dir.rglob("*.comments.yaml")):
            snippets.extend(self._parse_file(yaml_path))
        return snippets

    def _parse_file(self, path: Path) -> list[Snippet]:
        """단일 YAML 파일을 파싱하여 Snippet 리스트 반환."""
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        return [Snippet.model_validate(item) for item in raw]
