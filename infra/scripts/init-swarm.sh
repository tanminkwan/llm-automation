#!/usr/bin/env bash
# ============================================================
# init-swarm.sh — Docker Swarm 초기화 + 노드 라벨 부여
# architecture_test.md §2, §11 참조
# ============================================================
set -euo pipefail

echo "=== Docker Swarm 초기화 ==="

# Swarm 이미 활성화된 경우 skip
if docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null | grep -q "active"; then
    echo "Swarm 이미 활성화 — skip init"
else
    docker swarm init
    echo "Swarm 초기화 완료"
fi

# 단일 노드에 manager + worker 라벨 모두 부여
# (향후 멀티노드 확장 시 라벨만 분리하면 manifest 변경 없음)
NODE_ID=$(docker info --format '{{.Swarm.NodeID}}')
docker node update --label-add role=manager "${NODE_ID}"
docker node update --label-add role=worker "${NODE_ID}"

echo "=== 노드 라벨 부여 완료 ==="
echo "  Node: ${NODE_ID}"
echo "  Labels: role=manager, role=worker"
echo ""
echo "다음 단계: ./scripts/up.sh"
