#!/usr/bin/env bash
# ============================================================
# up.sh — 환경변수 로드 → 시크릿 등록 → 스택 배포
# architecture_test.md §11 참조
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "${SCRIPT_DIR}")"
ENV_FILE="${INFRA_DIR}/.env"
STACK_FILE="${INFRA_DIR}/docker-stack.test.yml"
STACK_NAME="llmauto"

# .env 존재 확인
if [ ! -f "${ENV_FILE}" ]; then
    echo "ERROR: ${ENV_FILE} 가 없습니다."
    echo "  cp ${INFRA_DIR}/sample.env ${ENV_FILE}"
    echo "  실제 값(OPENAI_API_KEY 등)을 채워 넣으세요."
    exit 1
fi

echo "=== 환경변수 로드: ${ENV_FILE} ==="
set -a
# shellcheck source=/dev/null
. "${ENV_FILE}"
set +a

# Docker secret 등록 (이미 존재하면 skip)
echo "=== Docker secret 등록 ==="
if docker secret inspect openai_api_key >/dev/null 2>&1; then
    echo "  openai_api_key — 이미 존재 (skip)"
else
    printf '%s' "${OPENAI_API_KEY}" | docker secret create openai_api_key -
    echo "  openai_api_key — 등록 완료"
fi

# 스택 배포
echo "=== 스택 배포: ${STACK_NAME} ==="
docker stack deploy -c "${STACK_FILE}" "${STACK_NAME}"

echo ""
echo "=== 배포 완료 ==="
echo "  Stack: ${STACK_NAME}"
echo "  확인:"
echo "    docker stack services ${STACK_NAME}"
echo "    curl http://localhost:9100/health   # leebalso-mock"
echo "    curl http://localhost:6333/healthz  # Qdrant"
echo "    open http://localhost:5555          # Flower"
echo "    open http://localhost:3000          # Gitea"
