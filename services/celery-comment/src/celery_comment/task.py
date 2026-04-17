"""comment.process Celery task."""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .models import CommentResult, TaskPayload
from .prompt import build_prompt
from .protocols import AgentExecutor, GitClient

logger = logging.getLogger(__name__)


def process_comment(
    *,
    payload: TaskPayload,
    git_client: GitClient,
    agent: AgentExecutor,
    rag_mcp_url: str,
    work_dir_base: str,
) -> CommentResult:
    """comment task 핵심 로직.

    1. clone → 2. build prompt → 3. AgentRunner.run() → 4. commit/push → 5. cleanup
    """
    safe_prefix = payload.work_id.replace("/", "_").replace(":", "_") + "_"
    work_dir = Path(tempfile.mkdtemp(prefix=safe_prefix, dir=work_dir_base))
    repo_dir = work_dir / "repo"

    try:
        # 1. clone
        branch = payload.ref.split("/")[-1]
        git_client.clone(payload.clone_url, repo_dir, payload.ref)

        # 2. build prompt
        prompt = build_prompt(payload.changed_files)

        # 3. Agent 실행
        result = agent.run(
            work_dir=repo_dir,
            prompt=prompt,
            changed_files=payload.changed_files,
            rag_mcp_url=rag_mcp_url,
        )

        if result.exit_code != 0:
            logger.error("Agent failed: exit_code=%d, stdout=%s", result.exit_code, result.stdout)
            return CommentResult(
                work_id=payload.work_id,
                status="error",
                message=f"Agent exit code: {result.exit_code}",
            )

        # 4. commit/push (변경 파일이 있을 때만)
        if not result.changed_files:
            return CommentResult(
                work_id=payload.work_id,
                status="no_changes",
                message="Agent made no changes",
            )

        git_client.add_commit_push(
            repo_dir,
            message=f"[skip ci] AI 주석 자동 삽입 ({payload.work_id})",
            branch=branch,
        )

        return CommentResult(
            work_id=payload.work_id,
            status="success",
            changed_files=result.changed_files,
        )

    except Exception as exc:
        logger.exception("process_comment failed: %s", exc)
        raise

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def create_celery_task(celery_app: Any, **deps: Any) -> None:
    """Celery app 에 task 등록. deps 에 git_client, agent 등 주입."""

    @celery_app.task(name="comment.process", queue="comment_queue")  # type: ignore[misc,untyped-decorator]
    def _task(
        work_id: str = "",
        repo_url: str = "",
        clone_url: str = "",
        ref: str = "",
        changed_files: list[str] | None = None,
    ) -> dict[str, Any]:
        payload = TaskPayload(
            work_id=work_id,
            repo_url=repo_url,
            clone_url=clone_url,
            ref=ref,
            changed_files=changed_files or [],
        )
        result = process_comment(payload=payload, **deps)
        return result.model_dump()
