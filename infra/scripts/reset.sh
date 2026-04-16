#!/usr/bin/env bash
# ============================================================
# reset.sh — 볼륨/컬렉션 초기화 (테스트 환경 리셋)
# ============================================================
set -euo pipefail

STACK_NAME="llmauto"

echo "=== 스택 제거: ${STACK_NAME} ==="
docker stack rm "${STACK_NAME}" 2>/dev/null || true

# 서비스가 완전히 내려갈 때까지 대기
echo "  서비스 종료 대기..."
sleep 5

echo "=== 볼륨 제거 ==="
for vol in "${STACK_NAME}_redis-data" "${STACK_NAME}_qdrant-data" "${STACK_NAME}_gitea-data"; do
    if docker volume inspect "${vol}" >/dev/null 2>&1; then
        docker volume rm "${vol}"
        echo "  ${vol} — 제거 완료"
    else
        echo "  ${vol} — 없음 (skip)"
    fi
done

echo "=== Docker secret 제거 ==="
if docker secret inspect openai_api_key >/dev/null 2>&1; then
    docker secret rm openai_api_key
    echo "  openai_api_key — 제거 완료"
else
    echo "  openai_api_key — 없음 (skip)"
fi

echo ""
echo "=== 리셋 완료 ==="
echo "  다시 시작하려면: ./scripts/init-swarm.sh && ./scripts/up.sh"
