#!/usr/bin/env bash
# stack_up.sh — E2E docker stack 배포 + 헬스 대기
set -euo pipefail

STACK_NAME="${E2E_STACK_NAME:-llmauto-e2e}"
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-stack.test.yml}"
TIMEOUT="${E2E_STACK_STARTUP_TIMEOUT:-120}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "[stack_up] compose file not found: $COMPOSE_FILE" >&2
    exit 2
fi

echo "[stack_up] deploying stack=$STACK_NAME file=$COMPOSE_FILE"
docker stack deploy --compose-file "$COMPOSE_FILE" "$STACK_NAME"

echo "[stack_up] waiting for Redis (timeout=${TIMEOUT}s)"
deadline=$((SECONDS + TIMEOUT))
until docker run --rm --network "${STACK_NAME}_default" redis:7 \
        redis-cli -h redis ping 2>/dev/null | grep -q PONG; do
    if (( SECONDS > deadline )); then
        echo "[stack_up] ERROR: Redis health check timeout" >&2
        exit 1
    fi
    sleep 2
done

echo "[stack_up] stack ready."
