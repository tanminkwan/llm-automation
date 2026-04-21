#!/usr/bin/env bash
# ============================================================
# stack_up.sh — E2E docker stack 배포 + 전체 서비스 수렴 대기
# 단일 명령(make e2e) 진입점의 일부. 독립 실행도 가능.
#   1) infra/.env 로드
#   2) bind-mount 디렉터리 준비 (host=container 동일 경로)
#   3) fixture source 시드 복사
#   4) Docker Swarm + node 라벨 확인 (없으면 init)
#   5) docker stack deploy
#   6) 모든 서비스 replicas 가 1/1 로 수렴할 때까지 대기
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E2E_DIR="$(dirname "${SCRIPT_DIR}")"
REPO_ROOT="$(cd "${E2E_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/infra/.env"
COMPOSE_FILE="${COMPOSE_FILE:-${REPO_ROOT}/infra/docker-stack.test.yml}"

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "[stack_up] ERROR: ${ENV_FILE} 없음. cp infra/sample.env infra/.env 후 값 채우기." >&2
    exit 2
fi
if [[ ! -f "${COMPOSE_FILE}" ]]; then
    echo "[stack_up] ERROR: compose 파일 없음: ${COMPOSE_FILE}" >&2
    exit 2
fi

echo "[stack_up] 환경변수 로드: ${ENV_FILE}"
set -a
# shellcheck source=/dev/null
. "${ENV_FILE}"
set +a

STACK_NAME="${E2E_STACK_NAME:-llmauto}"
TIMEOUT="${E2E_STACK_STARTUP_TIMEOUT:-180}"

# ─── 1) bind-mount 디렉터리 준비 ──────────────────────────
echo "[stack_up] bind-mount 디렉터리 준비"
for d in "${FIXTURE_SOURCE_DIR}" "${FIXTURE_RESULT_DIR}" "${REPORT_OUTPUT_DIR}" "${COMMENT_WORK_DIR}"; do
    mkdir -p "${d}"
    chmod 777 "${d}" 2>/dev/null || true
done

# 이전 실행이 root 권한으로 남긴 결과물 제거 (컨테이너 내에서 삭제)
for d in "${FIXTURE_RESULT_DIR}" "${REPORT_OUTPUT_DIR}" "${COMMENT_WORK_DIR}"; do
    if [[ -n "$(ls -A "${d}" 2>/dev/null)" ]]; then
        docker run --rm -v "${d}:/x" alpine sh -c 'rm -rf /x/* /x/.[!.]* 2>/dev/null || true' >/dev/null
    fi
done

# ─── 2) fixture source 시드 ─────────────────────────────
# trigger.json 의 clone_url=fixture://scenario_A/before 를 만족하려면
# 대상 경로가 ${FIXTURE_SOURCE_DIR}/scenario_A/before/ 여야 한다.
echo "[stack_up] fixture source 시드: ${FIXTURE_SOURCE_DIR}"
rm -rf "${FIXTURE_SOURCE_DIR:?}"/*
mkdir -p "${FIXTURE_SOURCE_DIR}/scenario_A"
cp -r "${E2E_DIR}/fixtures/scenario_A/before" "${FIXTURE_SOURCE_DIR}/scenario_A/"

# ─── 3) Swarm + node 라벨 ────────────────────────────────
if ! docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null | grep -q active; then
    echo "[stack_up] Swarm 초기화"
    docker swarm init >/dev/null
fi
NODE_ID="$(docker info --format '{{.Swarm.NodeID}}')"
LABELS="$(docker node inspect "${NODE_ID}" --format '{{ json .Spec.Labels }}')"
if [[ "${LABELS}" != *'"node-role.manager":"true"'* ]]; then
    docker node update --label-add node-role.manager=true "${NODE_ID}" >/dev/null
fi
if [[ "${LABELS}" != *'"node-role.worker":"true"'* ]]; then
    docker node update --label-add node-role.worker=true "${NODE_ID}" >/dev/null
fi

# ─── 4) stack deploy ────────────────────────────────────
echo "[stack_up] stack deploy: ${STACK_NAME} (file=${COMPOSE_FILE})"
docker stack deploy --compose-file "${COMPOSE_FILE}" "${STACK_NAME}" >/dev/null

# ─── 5) 모든 서비스 replicas 수렴 대기 ────────────────────
echo "[stack_up] 서비스 수렴 대기 (timeout=${TIMEOUT}s)"
deadline=$((SECONDS + TIMEOUT))
while true; do
    # "REPLICAS" 열은 "running/desired" 형식. 전부 "1/1" 이어야 한다.
    status="$(docker stack services --format '{{.Name}} {{.Replicas}}' "${STACK_NAME}" 2>/dev/null || true)"
    if [[ -z "${status}" ]]; then
        echo "[stack_up] 서비스 목록이 비어 있음 — 재시도" >&2
    else
        # 모든 라인이 "X 1/1" 인지 확인
        not_ready="$(awk '{ if ($2 != "1/1") print $1 "=" $2 }' <<< "${status}")"
        if [[ -z "${not_ready}" ]]; then
            echo "[stack_up] 모든 서비스 1/1 수렴 완료"
            echo "${status}" | sed 's/^/  /'
            break
        fi
    fi
    if (( SECONDS > deadline )); then
        echo "[stack_up] ERROR: 서비스 수렴 timeout" >&2
        echo "[stack_up] 현재 상태:" >&2
        docker stack services "${STACK_NAME}" >&2 || true
        exit 1
    fi
    sleep 3
done

echo "[stack_up] ready."
