"""T-04~T-07: CorpusLoader 테스트."""

from __future__ import annotations

from pathlib import Path

from rag_seeder.corpus_loader import CorpusLoader


def _write_yaml(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestCorpusLoader:
    def test_load_single_file(self, tmp_path: Path) -> None:
        """T-04: 단일 YAML 파일 파싱."""
        _write_yaml(
            tmp_path / "pkg" / "svc.comments.yaml",
            """\
- id: svc::method1
  path: pkg/svc.java
  symbol: method1
  line_range: [10, 20]
  comment: "첫 번째 주석"
- id: svc::method2
  path: pkg/svc.java
  symbol: method2
  line_range: [30, 40]
  comment: "두 번째 주석"
""",
        )
        loader = CorpusLoader(tmp_path)
        snippets = loader.load()
        assert len(snippets) == 2
        assert snippets[0].id == "svc::method1"
        assert snippets[1].symbol == "method2"

    def test_load_multiple_files(self, tmp_path: Path) -> None:
        """T-05: 다중 YAML 파일 재귀 로드."""
        _write_yaml(
            tmp_path / "a" / "a.comments.yaml",
            """\
- id: a::m1
  path: a/a.java
  symbol: m1
  line_range: [1, 5]
  comment: "a comment"
""",
        )
        _write_yaml(
            tmp_path / "b" / "b.comments.yaml",
            """\
- id: b::m1
  path: b/b.java
  symbol: m1
  line_range: [1, 5]
  comment: "b comment"
""",
        )
        loader = CorpusLoader(tmp_path)
        snippets = loader.load()
        assert len(snippets) == 2
        ids = {s.id for s in snippets}
        assert ids == {"a::m1", "b::m1"}

    def test_load_empty_dir(self, tmp_path: Path) -> None:
        """T-06: 빈 디렉터리 → 빈 리스트."""
        loader = CorpusLoader(tmp_path)
        assert loader.load() == []

    def test_non_list_yaml(self, tmp_path: Path) -> None:
        """T-07b: YAML 내용이 리스트가 아니면 무시."""
        _write_yaml(tmp_path / "bad.comments.yaml", "key: value\n")
        loader = CorpusLoader(tmp_path)
        assert loader.load() == []

    def test_ignores_non_yaml(self, tmp_path: Path) -> None:
        """T-07: .comments.yaml 외 파일 무시."""
        (tmp_path / "readme.txt").write_text("ignored", encoding="utf-8")
        (tmp_path / "data.json").write_text("{}", encoding="utf-8")
        _write_yaml(
            tmp_path / "svc.comments.yaml",
            """\
- id: svc::m
  path: svc.java
  symbol: m
  line_range: [1, 2]
  comment: "ok"
""",
        )
        loader = CorpusLoader(tmp_path)
        snippets = loader.load()
        assert len(snippets) == 1
        assert snippets[0].id == "svc::m"
