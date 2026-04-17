"""Celery task -- configaudit.process."""

from pathlib import Path
from typing import Any

from .agent_loop import AgentLoop
from .app import celery_app, settings
from .llm_client import OpenAILLMClient
from .mcp_client import HttpConfigAuditClient
from .report_writer import write_report


@celery_app.task(name="configaudit.process", queue="configaudit_queue")  # type: ignore[misc,untyped-decorator]
def process_configaudit(
    work_id: str,
    repo_url: str,
    clone_url: str,
    ref: str,
    changed_files: list[str],
) -> dict[str, Any]:
    """configaudit_queue 소비 -- AgentLoop 실행 -> 보고서 작성 -> 결과 반환."""
    mcp = HttpConfigAuditClient(
        base_url=settings.configaudit_mcp_url,
        timeout=float(settings.reasoning_llm_timeout_seconds),
    )
    llm = OpenAILLMClient(
        base_url=settings.reasoning_llm_base_url,
        model=settings.reasoning_llm_model,
        api_key=settings.reasoning_llm_api_key,
        timeout=float(settings.reasoning_llm_timeout_seconds),
    )
    agent = AgentLoop(
        llm=llm,
        mcp=mcp,
        max_iterations=settings.agent_max_iterations,
    )

    # case 는 work_id 기반 기본값 사용
    case = work_id
    report = agent.run(work_id=work_id, case=case)

    output_dir = Path(settings.report_output_dir)
    report_path = write_report(report, output_dir)

    return {
        "work_id": work_id,
        "repo_url": repo_url,
        "clone_url": clone_url,
        "ref": ref,
        "changed_files": changed_files,
        "report_path": str(report_path),
        "summary": report.summary,
    }
