"""OpenAI 어댑터 테스트 — 설계서 §8 의 T-14 ~ T-19."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from openai import APIConnectionError

from llm_gateway.errors import BackendCallError
from llm_gateway.models import ChatMessage
from llm_gateway.openai_backend import (
    OpenAIChatBackend,
    OpenAIEmbeddingBackend,
)


def _make_chat_completion(
    *,
    content: str = "hello!",
    model: str = "test-chat-model",
    finish_reason: str = "stop",
    prompt_tokens: int = 4,
    completion_tokens: int = 3,
) -> SimpleNamespace:
    """openai.ChatCompletion 형태의 가짜 응답."""
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content, role="assistant"),
                finish_reason=finish_reason,
                index=0,
            )
        ],
        model=model,
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


def _make_embedding_response(
    *,
    vectors: list[list[float]] | None = None,
    model: str = "test-embed-model",
) -> SimpleNamespace:
    """openai.CreateEmbeddingResponse 형태의 가짜 응답."""
    if vectors is None:
        vectors = [[0.1, 0.2, 0.3]]
    return SimpleNamespace(
        data=[SimpleNamespace(embedding=vec, index=i) for i, vec in enumerate(vectors)],
        model=model,
    )


def _make_chat_backend(
    client: Any,
    *,
    model: str = "test-chat-model",
    max_retries: int = 2,
) -> OpenAIChatBackend:
    return OpenAIChatBackend(
        base_url="https://chat.example.com/v1",
        api_key="sk-test",
        default_model=model,
        timeout_seconds=0.1,
        max_retries=max_retries,
        client=client,
    )


def _make_embed_backend(
    client: Any,
    *,
    model: str = "test-embed-model",
    dim: int = 3,
    max_retries: int = 2,
) -> OpenAIEmbeddingBackend:
    return OpenAIEmbeddingBackend(
        base_url="https://embed.example.com/v1",
        api_key="sk-test",
        default_model=model,
        dim=dim,
        timeout_seconds=0.1,
        max_retries=max_retries,
        client=client,
    )


def test_chat_returns_response_on_success() -> None:
    """T-14: 정상 응답 → ChatResponse 변환."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_chat_completion(
        content="안녕!", model="actual-model", finish_reason="stop"
    )
    backend = _make_chat_backend(mock_client)

    resp = backend.chat(
        [ChatMessage(role="user", content="hi")],
        model="actual-model",
    )

    assert resp.content == "안녕!"
    assert resp.model == "actual-model"
    assert resp.finish_reason == "stop"
    assert resp.usage.total_tokens == 7


def test_chat_forwards_call_arguments() -> None:
    """T-15: 호출 인자(model/messages/temperature/max_tokens) 위임 검증."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_chat_completion()
    backend = _make_chat_backend(mock_client)

    backend.chat(
        [ChatMessage(role="user", content="say hi")],
        model="my-model",
        temperature=0.7,
        max_tokens=128,
    )

    mock_client.chat.completions.create.assert_called_once()
    kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "my-model"
    assert kwargs["temperature"] == 0.7
    assert kwargs["max_tokens"] == 128
    assert kwargs["messages"] == [{"role": "user", "content": "say hi"}]


def test_chat_omits_optional_params_when_none() -> None:
    """temperature/max_tokens 가 None 이면 하부 호출에 전달하지 않음 (provider 기본값 사용)."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_chat_completion()
    backend = _make_chat_backend(mock_client)

    backend.chat([ChatMessage(role="user", content="hi")], model="m")

    kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert "temperature" not in kwargs
    assert "max_tokens" not in kwargs


def test_chat_retries_transient_then_succeeds() -> None:
    """T-16: transient 예외 재시도 후 성공."""
    request = httpx.Request("POST", "https://chat.example.com/v1/chat/completions")
    transient = APIConnectionError(request=request)

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [transient, _make_chat_completion()]

    backend = _make_chat_backend(mock_client, max_retries=3)

    resp = backend.chat([ChatMessage(role="user", content="hi")], model="m")

    assert resp.content == "hello!"
    assert mock_client.chat.completions.create.call_count == 2


def test_chat_raises_backend_call_error_after_all_retries() -> None:
    """T-17: 모든 재시도 실패 시 BackendCallError 로 래핑."""
    request = httpx.Request("POST", "https://chat.example.com/v1/chat/completions")
    transient = APIConnectionError(request=request)

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = transient

    backend = _make_chat_backend(mock_client, max_retries=3)

    with pytest.raises(BackendCallError) as excinfo:
        backend.chat([ChatMessage(role="user", content="hi")], model="m")

    assert isinstance(excinfo.value.__cause__, APIConnectionError)
    assert mock_client.chat.completions.create.call_count == 3


def test_chat_uses_default_model_when_not_specified() -> None:
    """default_model 폴백 — 호출자가 model 인자를 생략 가능."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _make_chat_completion()
    backend = _make_chat_backend(mock_client, model="default-from-settings")

    backend.chat([ChatMessage(role="user", content="hi")])

    assert mock_client.chat.completions.create.call_args.kwargs["model"] == "default-from-settings"


def test_embed_returns_response_on_success() -> None:
    """T-18: 정상 응답 → EmbeddingResponse (vectors/dim/model)."""
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = _make_embedding_response(
        vectors=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        model="actual-embed-model",
    )
    backend = _make_embed_backend(mock_client, dim=3)

    resp = backend.embed(["a", "b"], model="actual-embed-model")

    assert resp.vectors == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    assert resp.model == "actual-embed-model"
    assert resp.dim == 3


def test_embed_handles_empty_input() -> None:
    """T-19: 빈 입력 리스트 → 외부 호출 없이 빈 응답."""
    mock_client = MagicMock()
    backend = _make_embed_backend(mock_client, dim=3)

    resp = backend.embed([], model="m")

    assert resp.vectors == []
    assert resp.model == "m"
    assert resp.dim == 3
    mock_client.embeddings.create.assert_not_called()


def test_embed_uses_default_model_when_not_specified() -> None:
    """embedding 도 default_model 폴백."""
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = _make_embedding_response()
    backend = _make_embed_backend(mock_client, model="default-embed")

    backend.embed(["x"])

    assert mock_client.embeddings.create.call_args.kwargs["model"] == "default-embed"


def test_embed_raises_backend_call_error_after_all_retries() -> None:
    """embed 도 transient 실패 시 BackendCallError 로 래핑."""
    request = httpx.Request("POST", "https://embed.example.com/v1/embeddings")
    transient = APIConnectionError(request=request)

    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = transient

    backend = _make_embed_backend(mock_client, max_retries=2)

    with pytest.raises(BackendCallError):
        backend.embed(["x"], model="m")

    assert mock_client.embeddings.create.call_count == 2
