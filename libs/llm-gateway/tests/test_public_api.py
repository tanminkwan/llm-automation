"""public API import 테스트 — 설계서 §8 의 T-28."""

from __future__ import annotations


def test_top_level_imports_resolve() -> None:
    """T-28: 호출측이 ``from llm_gateway import ...`` 한 줄로 사용 가능."""
    from llm_gateway import (
        CHAT_LLM,
        EMBEDDING,
        REASONING_LLM,
        BackendCallError,
        ChatBackend,
        ChatMessage,
        ChatResponse,
        EmbeddingBackend,
        EmbeddingResponse,
        GatewayError,
        GatewaySettings,
        LLMGateway,
        MissingCredentialsError,
        TokenUsage,
        UnknownProfileError,
    )

    # 단순 사용성 검증 — 클래스/상수 식별자가 import 가능하다는 사실 자체.
    assert CHAT_LLM == "chat-llm"
    assert REASONING_LLM == "reasoning-llm"
    assert EMBEDDING == "embedding"

    # 인터페이스/모델 클래스가 노출됨
    for cls in (
        LLMGateway,
        GatewaySettings,
        ChatMessage,
        ChatResponse,
        EmbeddingResponse,
        TokenUsage,
        ChatBackend,
        EmbeddingBackend,
        GatewayError,
        UnknownProfileError,
        MissingCredentialsError,
        BackendCallError,
    ):
        assert cls is not None


def test_version_attribute_exposed() -> None:
    """배포 wheel 식별을 위한 __version__ 노출."""
    import llm_gateway

    assert isinstance(llm_gateway.__version__, str)
    assert llm_gateway.__version__  # non-empty
