"""report_writer 테스트."""

import json
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

    def test_writes_json_sidecar(self) -> None:
        """E2E scenario B JSON sidecar 생성."""
        report = AnalysisReport(
            work_id="demo/config-repo:case-001",
            case="case-001",
            summary="Three anomalies detected",
            details="detailed text",
            anomalies=["missing X", "invalid Y"],
        )
        with tempfile.TemporaryDirectory() as td:
            md_path = write_report(report, Path(td))
            json_path = md_path.with_suffix(".json")
            assert json_path.is_file()
            data = json.loads(json_path.read_text(encoding="utf-8"))
            assert data["work_id"] == "demo/config-repo:case-001"
            assert data["case"] == "case-001"
            assert data["summary"] == "Three anomalies detected"
            assert data["details"] == {"text": "detailed text"}
            assert data["anomalies"] == [
                {"message": "missing X"},
                {"message": "invalid Y"},
            ]
            assert isinstance(data["generated_at"], str) and data["generated_at"]

    def test_sanitizes_filename(self) -> None:
        """work_id 내 슬래시/콜론이 파일명에서 치환됨."""
        report = AnalysisReport(
            work_id="demo/repo:abc",
            case="case",
            summary="s",
            details="d",
            anomalies=[],
        )
        with tempfile.TemporaryDirectory() as td:
            path = write_report(report, Path(td))
            assert "/" not in path.name and ":" not in path.name
            assert "demo_repo_abc" in path.name
