"""게이트웨이 도메인 예외 — 호출측이 단일 ``GatewayError`` 로 catch 가능."""

from __future__ import annotations


class GatewayError(Exception):
    """게이트웨이 도메인의 모든 예외의 부모."""


class UnknownProfileError(GatewayError):
    """등록되지 않은 alias 가 chat/embed 메서드에 전달된 경우."""

    def __init__(self, alias: str) -> None:
        super().__init__(f"unknown profile alias: {alias!r}")
        self.alias = alias


class MissingCredentialsError(GatewayError):
    """alias 에 해당하는 ``*_API_KEY`` 환경변수가 비어 있는 경우."""

    def __init__(self, alias: str) -> None:
        super().__init__(f"missing credentials for alias: {alias!r}")
        self.alias = alias


class BackendCallError(GatewayError):
    """외부 backend 호출이 재시도를 모두 소진한 후에도 실패한 경우.

    원인 예외는 ``__cause__`` 로 보존되어 디버깅에 사용된다.
    """
