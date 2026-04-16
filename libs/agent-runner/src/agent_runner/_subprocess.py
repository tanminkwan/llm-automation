"""subprocess 실행 유틸 (내부 모듈)."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from .errors import AgentTimeoutError
from .models import AgentResult


def run_cli(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float,
) -> AgentResult:
    """subprocess.run 래퍼 — 타임아웃/stdout/stderr 캡처.

    - shell=False (커맨드 인젝션 방지, 설계서 Q-03)
    - stdout/stderr 캡처 (text mode)
    - 타임아웃 초과 시 AgentTimeoutError
    """
    start = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: S603
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        raise AgentTimeoutError(
            f"Agent CLI timed out after {elapsed:.1f}s (limit={timeout_seconds}s)"
        ) from exc
    elapsed = time.monotonic() - start
    return AgentResult(
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_seconds=elapsed,
    )
