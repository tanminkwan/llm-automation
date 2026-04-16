"""T-10~T-14: _subprocess.run_cli 테스트."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from agent_runner._subprocess import run_cli
from agent_runner.errors import AgentTimeoutError


class TestRunCli:
    """subprocess 실행 유틸 테스트."""

    def test_success(self, tmp_work_dir: Path) -> None:
        """T-10: 정상 실행 → AgentResult (exit_code=0, stdout/stderr 캡처)."""
        result = run_cli(
            [sys.executable, "-c", "print('hello')"],
            cwd=tmp_work_dir,
            env={**os.environ},
            timeout_seconds=10.0,
        )
        assert result.exit_code == 0
        assert "hello" in result.stdout
        assert result.stderr == ""
        assert result.duration_seconds > 0

    def test_nonzero_exit(self, tmp_work_dir: Path) -> None:
        """T-11: 비정상 종료 (exit_code≠0) → AgentResult 에 반영."""
        result = run_cli(
            [sys.executable, "-c", "import sys; print('err', file=sys.stderr); sys.exit(42)"],
            cwd=tmp_work_dir,
            env={**os.environ},
            timeout_seconds=10.0,
        )
        assert result.exit_code == 42
        assert "err" in result.stderr

    def test_timeout(self, tmp_work_dir: Path) -> None:
        """T-12: 타임아웃 초과 → AgentTimeoutError."""
        with pytest.raises(AgentTimeoutError, match="timed out"):
            run_cli(
                [sys.executable, "-c", "import time; time.sleep(10)"],
                cwd=tmp_work_dir,
                env={**os.environ},
                timeout_seconds=0.5,
            )

    def test_duration_measured(self, tmp_work_dir: Path) -> None:
        """T-13: duration_seconds 측정 정확도."""
        result = run_cli(
            [sys.executable, "-c", "import time; time.sleep(0.2); print('ok')"],
            cwd=tmp_work_dir,
            env={**os.environ},
            timeout_seconds=10.0,
        )
        assert result.duration_seconds >= 0.1

    def test_no_shell(self, tmp_work_dir: Path) -> None:
        """T-14: shell=False 로 실행 (보안 — subprocess.run 에 shell 인자 미전달)."""
        with patch(
            "agent_runner._subprocess.subprocess.run", wraps=__import__("subprocess").run
        ) as mock_run:
            run_cli(
                [sys.executable, "-c", "print('safe')"],
                cwd=tmp_work_dir,
                env={**os.environ},
                timeout_seconds=10.0,
            )
            call_kwargs = mock_run.call_args
            # shell 이 전달되지 않거나 False 인지 확인
            assert call_kwargs.kwargs.get("shell", False) is False
