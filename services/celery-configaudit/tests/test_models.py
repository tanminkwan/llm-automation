"""모델 테스트."""

from celery_configaudit.models import AnalysisReport, TaskPayload, ToolCallRequest


class TestModels:
    def test_task_payload(self) -> None:
        p = TaskPayload(work_id="w", repo_url="r", ref="refs/heads/main", changed_files=["a.m"])
        assert p.work_id == "w"

    def test_tool_call_request(self) -> None:
        t = ToolCallRequest(name="get_config_context", arguments={"work_id": "w"})
        assert t.name == "get_config_context"

    def test_analysis_report(self) -> None:
        r = AnalysisReport(work_id="w", case="c", summary="s", details="d", anomalies=["a"])
        assert r.work_id == "w"
        assert r.generated_at is not None
