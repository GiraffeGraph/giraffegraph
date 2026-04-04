import json

import pytest

from app.application.errors import ExternalServiceError, RuleViolationError
from app.bootstrap.container import get_container
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.openai_provider import OpenAILLMProvider


def test_openai_provider_builds_request_and_parses_response() -> None:
    captured_request: dict[str, object] = {}

    def transport(
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout_seconds: float,
    ) -> dict[str, object]:
        captured_request["url"] = url
        captured_request["headers"] = headers
        captured_request["payload"] = payload
        captured_request["timeout_seconds"] = timeout_seconds
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"nodes": [], "relations": []}',
                    }
                }
            ]
        }

    provider = OpenAILLMProvider(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        timeout_seconds=9.5,
        transport=transport,
    )

    result = provider.generate_structured(
        prompt="extract prompt",
        schema_name="candidate_graph_extraction_v1",
        payload={"segments": [{"segment_id": "seg-1"}]},
        model="gpt-4o-mini",
    )

    assert result == {"nodes": [], "relations": []}
    assert captured_request["url"] == "https://api.openai.com/v1/chat/completions"
    assert captured_request["headers"] == {
        "Authorization": "Bearer test-key",
        "Content-Type": "application/json",
    }
    assert captured_request["timeout_seconds"] == 9.5
    payload = captured_request["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "gpt-4o-mini"
    assert payload["response_format"] == {"type": "json_object"}
    messages = payload["messages"]
    assert isinstance(messages, list)
    assert messages[0]["content"] == "extract prompt"
    user_payload = json.loads(messages[1]["content"])
    assert user_payload == {
        "schema_name": "candidate_graph_extraction_v1",
        "payload": {"segments": [{"segment_id": "seg-1"}]},
    }


def test_openai_provider_requires_model() -> None:
    provider = OpenAILLMProvider(api_key="test-key")

    with pytest.raises(RuleViolationError):
        provider.generate_structured(
            prompt="extract prompt",
            schema_name="candidate_graph_extraction_v1",
            payload={"segments": []},
            model=None,
        )


def test_openai_provider_rejects_non_json_content() -> None:
    provider = OpenAILLMProvider(
        api_key="test-key",
        transport=lambda **_: {
            "choices": [{"message": {"content": "not-json"}}]
        },
    )

    with pytest.raises(ExternalServiceError):
        provider.generate_structured(
            prompt="extract prompt",
            schema_name="candidate_graph_extraction_v1",
            payload={"segments": []},
            model="gpt-4o-mini",
        )


def test_container_registers_openai_provider_when_key_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()
    get_container.cache_clear()

    try:
        container = get_container()
        provider = container.extraction_management_service.provider_registry.get("openai")
        assert isinstance(provider, OpenAILLMProvider)
        assert provider.api_key == "test-key"
    finally:
        get_container.cache_clear()
        get_settings.cache_clear()
