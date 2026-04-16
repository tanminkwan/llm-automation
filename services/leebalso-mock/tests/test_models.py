"""T-01, T-02: 데이터 모델 테스트."""

from __future__ import annotations

import json

from leebalso_mock.models import ConfigResponse, FixtureMeta


class TestFixtureMeta:
    """T-02: FixtureMeta 정상 생성."""

    def test_create(self) -> None:
        meta = FixtureMeta(fixture="case-001", version="v1")
        assert meta.fixture == "case-001"
        assert meta.version == "v1"


class TestConfigResponse:
    """T-01: ConfigResponse 생성 + JSON 직렬화."""

    def test_create_and_serialize(self) -> None:
        resp = ConfigResponse(
            env="dev",
            before="before content",
            after="after content",
            meta=FixtureMeta(fixture="case-001", version="v1"),
        )
        assert resp.env == "dev"
        assert resp.before == "before content"
        assert resp.after == "after content"
        assert resp.meta.fixture == "case-001"

        data = json.loads(resp.model_dump_json())
        assert data["env"] == "dev"
        assert data["meta"]["version"] == "v1"
