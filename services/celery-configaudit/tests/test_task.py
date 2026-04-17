"""process_configaudit Celery task 테스트."""

import tempfile
from typing import Any

import httpx
import pytest

from celery_configaudit.task import process_configaudit


class TestProcessConfigaudit:
    def test_happy_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """정상 실행: MCP → LLM tool_call → LLM text → 보고서 생성."""
        with tempfile.TemporaryDirectory() as td:
            monkeypatch.setenv("REPORT_OUTPUT_DIR", td)
            monkeypatch.setenv("CONFIGAUDIT_MCP_URL", "http://fake-mcp:9002")
            monkeypatch.setenv("REASONING_LLM_BASE_URL", "http://fake-llm/v1")
            monkeypatch.setenv("REASONING_LLM_MODEL", "test-model")
            monkeypatch.setenv("REASONING_LLM_API_KEY", "test-key")

            call_count = 0

            def _mock_post(
                url: str,
                *,
                json: Any = None,
                headers: Any = None,
                timeout: Any = None,
            ) -> httpx.Response:
                nonlocal call_count
                request = httpx.Request("POST", url)
                if "/config-context" in url:
                    # MCP 호출
                    return httpx.Response(
                        200,
                        json={
                            "work_id": "w1",
                            "case": "w1",
                            "configs": [],
                            "change_diffs": [],
                            "cross_env_diffs": [],
                            "anomalies": [],
                        },
                        request=request,
                    )
                # LLM 호출
                call_count += 1
                if call_count == 1:
                    # 첫 번째: tool_call
                    body: dict[str, Any] = {
                        "choices": [
                            {
                                "message": {
                                    "content": "",
                                    "tool_calls": [
                                        {
                                            "function": {
                                                "name": "get_config_context",
                                                "arguments": '{"work_id":"w1","case":"w1"}',
                                            }
                                        }
                                    ],
                                }
                            }
                        ]
                    }
                else:
                    # 두 번째: 최종 분석 텍스트
                    import json as _json

                    body = {
                        "choices": [
                            {
                                "message": {
                                    "content": _json.dumps(
                                        {
                                            "summary": "All configs aligned",
                                            "details": "No issues found",
                                            "anomalies": [],
                                        }
                                    ),
                                    "tool_calls": None,
                                }
                            }
                        ]
                    }
                return httpx.Response(200, json=body, request=request)

            monkeypatch.setattr(httpx, "post", _mock_post)

            # settings 재로드 필요 — task 모듈이 이미 import 했으므로 직접 패치
            from celery_configaudit import task as task_mod
            from celery_configaudit.settings import CeleryConfigAuditSettings

            new_settings = CeleryConfigAuditSettings()
            monkeypatch.setattr(task_mod, "settings", new_settings)

            result = process_configaudit(
                work_id="w1",
                repo_url="owner/repo",
                clone_url="http://git/owner/repo.git",
                ref="refs/heads/main",
                changed_files=["cfg/http.m"],
            )
            assert result["work_id"] == "w1"
            assert result["repo_url"] == "owner/repo"
            assert "report_path" in result
            assert "summary" in result
