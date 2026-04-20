"""FixtureGitClient — fixture 복사 기반 GitClient 구현 테스트."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from celery_comment.fixture_git import FixtureGitClient


@pytest.fixture()
def fixture_roots(tmp_path: Path) -> tuple[Path, Path]:
    """`source_root` / `result_root` 준비."""
    src = tmp_path / "source"
    res = tmp_path / "results"
    src.mkdir()
    res.mkdir()
    return src, res


def _seed_source(src_root: Path, key: str, files: dict[str, str]) -> Path:
    target = src_root / key
    target.mkdir(parents=True)
    for rel, content in files.items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return target


class TestClone:
    """``clone(url, dest, ref)`` — fixture://<key> 해석 + 트리 복사."""

    def test_copies_tree_from_source(
        self, fixture_roots: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """fixture://scenario_A/before → dest 에 동일 트리."""
        src, res = fixture_roots
        _seed_source(
            src,
            "scenario_A/before",
            {"README.md": "hello", "src/Foo.java": "class Foo {}"},
        )
        client = FixtureGitClient(source_root=src, result_root=res)
        dest = tmp_path / "work" / "repo"

        client.clone("fixture://scenario_A/before", dest, "refs/heads/main")

        assert (dest / "README.md").read_text(encoding="utf-8") == "hello"
        assert (dest / "src" / "Foo.java").read_text(encoding="utf-8") == "class Foo {}"

    def test_dest_overwritten_if_exists(
        self, fixture_roots: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """dest 이미 존재 → 덮어쓰기."""
        src, res = fixture_roots
        _seed_source(src, "k", {"a.txt": "new"})
        client = FixtureGitClient(source_root=src, result_root=res)
        dest = tmp_path / "repo"
        dest.mkdir()
        (dest / "stale.txt").write_text("old", encoding="utf-8")

        client.clone("fixture://k", dest, "refs/heads/main")

        assert (dest / "a.txt").read_text(encoding="utf-8") == "new"
        assert not (dest / "stale.txt").exists()

    def test_missing_source_raises(self, fixture_roots: tuple[Path, Path], tmp_path: Path) -> None:
        """소스 키 없음 → FileNotFoundError."""
        src, res = fixture_roots
        client = FixtureGitClient(source_root=src, result_root=res)
        with pytest.raises(FileNotFoundError, match="fixture source not found"):
            client.clone("fixture://missing", tmp_path / "dest", "refs/heads/main")

    def test_non_fixture_url_raises(self, fixture_roots: tuple[Path, Path], tmp_path: Path) -> None:
        """fixture:// 스킴이 아니면 ValueError."""
        src, res = fixture_roots
        client = FixtureGitClient(source_root=src, result_root=res)
        with pytest.raises(ValueError, match="invalid fixture url"):
            client.clone("http://gitea/foo.git", tmp_path / "dest", "refs/heads/main")


class TestAddCommitPush:
    """``add_commit_push`` — repo_dir 스냅샷 + manifest.json."""

    def test_snapshot_and_manifest(self, fixture_roots: tuple[Path, Path], tmp_path: Path) -> None:
        """{result_root}/<branch>/<ts>/ 아래 트리 복사 + manifest.json."""
        _src, res = fixture_roots
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        (repo_dir / "src").mkdir()
        (repo_dir / "src" / "Foo.java").write_text("/** ai */ class Foo {}", encoding="utf-8")

        client = FixtureGitClient(source_root=_src, result_root=res)
        client.add_commit_push(repo_dir, message="AI 주석 (demo/repo:abc12345)", branch="main")

        branch_dir = res / "main"
        snapshots = list(branch_dir.iterdir())
        assert len(snapshots) == 1
        snap = snapshots[0]
        assert (snap / "src" / "Foo.java").read_text(encoding="utf-8") == "/** ai */ class Foo {}"

        manifest = json.loads((snap / FixtureGitClient.MANIFEST_NAME).read_text(encoding="utf-8"))
        assert manifest["message"] == "AI 주석 (demo/repo:abc12345)"
        assert manifest["branch"] == "main"
        assert manifest["source_repo_dir"] == str(repo_dir)
        assert manifest["timestamp"] == snap.name

    def test_missing_repo_dir_raises(
        self, fixture_roots: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """repo_dir 존재 안 하면 FileNotFoundError."""
        _src, res = fixture_roots
        client = FixtureGitClient(source_root=_src, result_root=res)
        with pytest.raises(FileNotFoundError, match="repo_dir not found"):
            client.add_commit_push(tmp_path / "nope", "msg", "main")
