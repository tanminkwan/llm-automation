#!/usr/bin/env bash
# stack_down.sh — E2E stack 제거 (teardown). 실패 무시.
set +e

STACK_NAME="${E2E_STACK_NAME:-llmauto-e2e}"

echo "[stack_down] removing stack=$STACK_NAME"
docker stack rm "$STACK_NAME" || true

echo "[stack_down] waiting for network cleanup (up to 30s)"
for _ in {1..15}; do
    if ! docker network ls --format '{{.Name}}' | grep -q "^${STACK_NAME}_"; then
        break
    fi
    sleep 2
done

echo "[stack_down] done."
exit 0
