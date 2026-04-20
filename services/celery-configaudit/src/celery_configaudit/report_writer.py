"""Markdown 보고서 + JSON sidecar 작성 -- write_report."""

import json
from pathlib import Path

from .models import AnalysisReport


def write_report(report: AnalysisReport, output_dir: Path) -> Path:
    """AnalysisReport 를 Markdown 파일(+ JSON sidecar)로 저장.

    파일명: {safe_work_id}_{timestamp}.md (및 동명 .json)
    반환: 생성된 Markdown 파일의 절대 경로.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
    safe_work_id = report.work_id.replace("/", "_").replace(":", "_")
    base = f"{safe_work_id}_{timestamp}"
    filepath = output_dir / f"{base}.md"
    sidecar = output_dir / f"{base}.json"

    anomalies_section = ""
    if report.anomalies:
        items = "\n".join(f"- {a}" for a in report.anomalies)
        anomalies_section = f"\n## Anomalies\n\n{items}\n"

    content = (
        f"# Config Audit Report: {report.work_id}\n\n"
        f"- **Case:** {report.case}\n"
        f"- **Generated:** {report.generated_at.isoformat()}\n\n"
        f"## Summary\n\n{report.summary}\n\n"
        f"## Details\n\n{report.details}\n"
        f"{anomalies_section}"
    )

    filepath.write_text(content, encoding="utf-8")

    sidecar_payload = {
        "work_id": report.work_id,
        "case": report.case,
        "summary": report.summary,
        "anomalies": [{"message": a} for a in report.anomalies],
        "details": {"text": report.details},
        "generated_at": report.generated_at.isoformat(),
    }
    sidecar.write_text(
        json.dumps(sidecar_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return filepath
