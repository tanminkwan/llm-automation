"""Protocol 정의 — DIP 의 추상화 경계.

SearchEngine 은 이 Protocol 만족 객체에만 의존한다.
"""

from __future__ import annotations

from typing import Protocol


class EmbeddingClient(Protocol):
    """임베딩 벡터화 인터페이스."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """텍스트 리스트를 벡터 리스트로 변환."""
        ...


class VectorReader(Protocol):
    """벡터 검색 인터페이스 — Qdrant 등."""

    def search(
        self,
        collection: str,
        vector: list[float],
        limit: int,
    ) -> list[dict[str, object]]:
        """벡터 유사 검색. 각 결과는 payload + score dict."""
        ...
