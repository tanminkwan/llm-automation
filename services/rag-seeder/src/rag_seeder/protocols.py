"""Protocol 정의 — DIP 의 추상화 경계.

Seeder 는 이 Protocol 만족 객체에만 의존한다. 신규 backend 추가는
Protocol 만족 구현체만 등록 (OCP).
"""

from __future__ import annotations

from typing import Protocol


class EmbeddingClient(Protocol):
    """임베딩 벡터화 인터페이스 — LLMGateway.embed() 를 감싼다."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """텍스트 리스트를 벡터 리스트로 변환."""
        ...


class VectorStore(Protocol):
    """벡터 저장소 인터페이스 — Qdrant 등."""

    def ensure_collection(self, name: str, dim: int) -> None:
        """컬렉션이 없으면 생성."""
        ...

    def upsert(
        self,
        collection: str,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, object]],
    ) -> int:
        """벡터 + payload 를 upsert. 성공 건수 반환."""
        ...
