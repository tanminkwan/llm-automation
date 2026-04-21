#!/usr/bin/env bash
# ============================================================
# stack_down.sh — E2E stack 제거 (teardown). 실패 무시.
# infra/.env 로부터 E2E_STACK_NAME 을 읽어 올바른 스택을 제거한다.
# ============================================================
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E2E_DIR="$(dirname "${SCRIPT_DIR}")"
REPO_ROOT="$(cd "${E2E_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/infra/.env"

if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck source=/dev/null
    . "${ENV_FILE}"
    set +a
fi

STACK_NAME="${E2E_STACK_NAME:-llmauto}"

echo "[stack_down] removing stack=${STACK_NAME}"
docker stack rm "${STACK_NAME}" >/dev/null 2>&1 || true

echo "[stack_down] waiting for network cleanup (up to 30s)"
for _ in {1..15}; do
    if ! docker network ls --format '{{.Name}}' | grep -q "^${STACK_NAME}_"; then
        break
    fi
    sleep 2
done

echo "[stack_down] done."
exit 0
