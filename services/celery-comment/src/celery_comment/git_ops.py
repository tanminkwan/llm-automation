"""SubprocessGitClient — subprocess 기반 Git 클라이언트."""

from __future__ import annotations

import subprocess
from pathlib import Path


class SubprocessGitClient:
    """subprocess 로 git 명령 실행 — GitClient Protocol 구현."""

    def __init__(self, author: str = "AI Bot <ai-bot@local>") -> None:
        self._author = author

    def clone(self, url: str, dest: Path, ref: str) -> None:
        """원격 repo clone + checkout ref."""
        subprocess.run(
            ["git", "clone", "--branch", ref.split("/")[-1], "--single-branch", url, str(dest)],
            check=True,
            capture_output=True,
        )

    def add_commit_push(self, repo_dir: Path, message: str, branch: str) -> None:
        """git add -A → commit → push."""
        env_author = self._author
        name, email = _parse_author(env_author)

        def _run(cmd: list[str]) -> None:
            subprocess.run(cmd, cwd=repo_dir, check=True, capture_output=True)

        _run(["git", "add", "-A"])
        _run(
            ["git", "-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "-m", message]
        )
        _run(["git", "push", "origin", branch])


def _parse_author(author: str) -> tuple[str, str]:
    """'Name <email>' 형식에서 name, email 분리."""
    if "<" in author and ">" in author:
        name = author[: author.index("<")].strip()
        email = author[author.index("<") + 1 : author.index(">")]
        return name, email
    return author, "ai-bot@local"
