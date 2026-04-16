"""T-11~T-18: FastAPI 앱 엔드포인트 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestGetConfig:
    """GET /config/httpm 테스트."""

    def test_success_dev(self, client: TestClient) -> None:
        """T-11: 정상 (200) — env=dev, case=case-001."""
        resp = client.get("/config/httpm", params={"env": "dev", "case": "case-001"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["env"] == "dev"
        assert "before" in data["before"]
        assert "after" in data["after"]
        assert data["meta"]["fixture"] == "case-001"
        assert data["meta"]["version"] == "v1"

    def test_default_case(self, client: TestClient) -> None:
        """T-12: case 미전달 → case-001 기본값."""
        resp = client.get("/config/httpm", params={"env": "dev"})
        assert resp.status_code == 200
        assert resp.json()["meta"]["fixture"] == "case-001"

    def test_missing_env(self, client: TestClient) -> None:
        """T-13: env 누락 → 422."""
        resp = client.get("/config/httpm")
        assert resp.status_code == 422

    def test_unknown_case(self, client: TestClient) -> None:
        """T-14: 미지 case → 404."""
        resp = client.get("/config/httpm", params={"env": "dev", "case": "bad-case"})
        assert resp.status_code == 404

    def test_unknown_env(self, client: TestClient) -> None:
        """T-15: 미지 env → 404."""
        resp = client.get("/config/httpm", params={"env": "unknown"})
        assert resp.status_code == 404

    def test_deterministic(self, client: TestClient) -> None:
        """T-16: 결정성 — 동일 요청 3회 byte-equal."""
        params = {"env": "dev", "case": "case-001"}
        r1 = client.get("/config/httpm", params=params).content
        r2 = client.get("/config/httpm", params=params).content
        r3 = client.get("/config/httpm", params=params).content
        assert r1 == r2 == r3

    def test_stage_and_prod(self, client: TestClient) -> None:
        """T-17: env=stage, env=prod 각각 올바른 fixture."""
        for env in ("stage", "prod"):
            resp = client.get("/config/httpm", params={"env": env})
            assert resp.status_code == 200
            data = resp.json()
            assert data["env"] == env
            assert env in data["before"]


class TestHealth:
    """GET /health 테스트."""

    def test_health(self, client: TestClient) -> None:
        """T-18: 200 + {"status": "ok"}."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
