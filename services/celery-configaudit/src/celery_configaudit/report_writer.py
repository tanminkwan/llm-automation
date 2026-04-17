"""Markdown 보고서 작성 -- write_report."""

from pathlib import Path

from .models import AnalysisReport


def write_report(report: AnalysisReport, output_dir: Path) -> Path:
    """AnalysisReport 를 Markdown 파일로 저장.

    파일명: {work_id}_{timestamp}.md
    반환: 생성된 파일의 절대 경로.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"{report.work_id}_{timestamp}.md"
    filepath = output_dir / filename

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
    return filepath
