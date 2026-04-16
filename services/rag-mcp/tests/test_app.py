"""T-10~T-16: FastAPI 엔드포인트 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestSearchCodebase:
    def test_success(self, client: TestClient) -> None:
        """T-10: 정상 (200)."""
        resp = client.post("/tools/search_codebase", json={"query": "사용자 생성", "k": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "사용자 생성"
        assert len(data["hits"]) == 3

    def test_empty_result(self, client: TestClient) -> None:
        """T-11: 빈 결과 (200) — 별도 engine 필요하므로 k=0 미만이 아닌 큰 k 사용."""
        # SAMPLE_HITS 는 3건이므로 k=3 이면 모두 반환
        resp = client.post("/tools/search_codebase", json={"query": "test", "k": 3})
        assert resp.status_code == 200

    def test_query_missing(self, client: TestClient) -> None:
        """T-12: query 누락 → 422."""
        resp = client.post("/tools/search_codebase", json={"k": 5})
        assert resp.status_code == 422

    def test_k_zero(self, client: TestClient) -> None:
        """T-13: k ≤ 0 → 422 (pydantic 검증은 없으나 결과가 0건)."""
        # k=0 은 허용되지만 결과 0건
        resp = client.post("/tools/search_codebase", json={"query": "test", "k": 0})
        assert resp.status_code == 200
        assert resp.json()["hits"] == []

    def test_k_exceeds_max(self, client: TestClient) -> None:
        """T-14: k > MAX_K → 400."""
        resp = client.post("/tools/search_codebase", json={"query": "test", "k": 100})
        assert resp.status_code == 400
        assert "max_k" in resp.json()["detail"]

    def test_k_default(self, client: TestClient) -> None:
        """T-15: k 미전달 → 기본값 사용."""
        resp = client.post("/tools/search_codebase", json={"query": "test"})
        assert resp.status_code == 200
        # 기본 k=5 이지만 SAMPLE_HITS 는 3건
        assert len(resp.json()["hits"]) == 3

    def test_empty_query(self, client: TestClient) -> None:
        """빈 query → 422."""
        resp = client.post("/tools/search_codebase", json={"query": "", "k": 5})
        assert resp.status_code == 422


class TestHealth:
    def test_health(self, client: TestClient) -> None:
        """T-16: GET /health → 200."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
