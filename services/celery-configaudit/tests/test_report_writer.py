"""report_writer 테스트."""

import tempfile
from pathlib import Path

from celery_configaudit.models import AnalysisReport
from celery_configaudit.report_writer import write_report


class TestWriteReport:
    def test_creates_file(self) -> None:
        """보고서 파일 생성."""
        report = AnalysisReport(
            work_id="test-001",
            case="case-001",
            summary="Summary here",
            details="Detailed analysis",
            anomalies=["anomaly1"],
        )
        with tempfile.TemporaryDirectory() as td:
            path = write_report(report, Path(td))
            assert path.exists()
            content = path.read_text()
            assert "test-001" in content
            assert "Summary here" in content
            assert "anomaly1" in content

    def test_no_anomalies(self) -> None:
        """이상 없는 보고서."""
        report = AnalysisReport(
            work_id="test-002",
            case="case-002",
            summary="All good",
            details="No issues found",
            anomalies=[],
        )
        with tempfile.TemporaryDirectory() as td:
            path = write_report(report, Path(td))
            content = path.read_text()
            assert "Anomalies" not in content
