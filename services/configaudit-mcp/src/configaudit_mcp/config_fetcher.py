"""ConfigFetcher — 리발소 API HTTP 클라이언트."""

import httpx

from .models import EnvConfig


class ConfigFetcher:
    """리발소 API HTTP 클라이언트 — ConfigClient Protocol 구현."""

    def __init__(self, base_url: str, *, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def fetch_config(self, env: str, case: str) -> EnvConfig:
        """env/case 에 해당하는 config 를 리발소 API 에서 조회."""
        resp = httpx.get(
            f"{self._base_url}/config/httpm",
            params={"env": env, "case": case},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return EnvConfig(
            env=data["env"],
            before=data["before"],
            after=data["after"],
        )
