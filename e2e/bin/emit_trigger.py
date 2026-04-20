#!/usr/bin/env python3
"""emit_trigger.py — 시나리오 trigger.json 을 Celery 큐로 발행.

사용법:
    uv run python e2e/bin/emit_trigger.py e2e/fixtures/scenario_A/trigger.json
    uv run python e2e/bin/emit_trigger.py e2e/fixtures/scenario_B/case-001/trigger.json

환경변수:
    E2E_BROKER_URL  — Celery broker (기본 redis://localhost:6379/0)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from celery import Celery  # type: ignore[import-untyped]
from trigger_core import CeleryTriggerDispatcher, MockTriggerEmitter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E2E trigger emitter")
    parser.add_argument("trigger_json", type=Path, help="trigger.json 경로")
    parser.add_argument(
        "--broker",
        default=os.getenv("E2E_BROKER_URL", "redis://localhost:6379/0"),
        help="Celery broker URL",
    )
    args = parser.parse_args(argv)

    if not args.trigger_json.is_file():
        print(f"[emit_trigger] file not found: {args.trigger_json}", file=sys.stderr)
        return 2

    celery = Celery(broker=args.broker)
    dispatcher = CeleryTriggerDispatcher(celery)
    emitter = MockTriggerEmitter(dispatcher)

    task_id = emitter.emit_from_json(args.trigger_json)
    print(f"[emit_trigger] dispatched task_id={task_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
