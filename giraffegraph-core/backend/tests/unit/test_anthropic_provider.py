import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest

from app.application.errors import RuleViolationError
from app.application.ports.llm_provider import LLMUsage, StructuredGenerationError
from app.bootstrap.container import get_container
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.anthropic_provider import (
    EXTRACTION_WIRE_SCHEMA,
    AnthropicLLMProvider,
)
from app.infrastructure.llm.noop_provider import NoOpLLMProvider
from app.infrastructure.llm.rule_based_isnad_provider import RuleBasedIsnadProvider

PROMPT = "extract prompt"
SCHEMA_NAME = "extraction_contract"
PAYLOAD = {
    "source_unit": {"external_ref": "Bukhari:1"},
    "segments": [{"segment_id": "seg-1", "segment_order": 1, "text": "حَدَّثَنَا سُفْيَانُ"}],
}
WIRE_OUTPUT = {
    "nodes": [
        {
            "ref": "node-1",
            "node_type": "Narrator",
            "properties": [{"name": "name", "value": "سُفْيَانُ"}],
            "confidence": 0.9,
            "evidence_refs": [{"segment_id": "seg-1", "quote": "سُفْيَانُ"}],
        },
        {
            "ref": "node-2",
            "node_type": "Narrator",
            "properties": [{"name": "name", "value": "ابْنِ شِهَابٍ"}],
            "confidence": 0.8,
            "evidence_refs": [{"segment_id": "seg-1", "quote": "ابْنِ شِهَابٍ"}],
        },
    ],
    "relations": [
        {
            "relation_type": "NARRATED_FROM",
            "from_ref": "node-1",
            "to_ref": "node-2",
            "properties": [
                {"name": "chain_no", "value": 1},
                {"name": "sigha", "value": "عن"},
            ],
            "confidence": 0.7,
            "evidence_refs": [{"segment_id": "seg-1", "quote": "سُفْيَانُ ، عَنِ ابْنِ شِهَابٍ"}],
        }
    ],
}


def _response(
    *,
    text: str | None = None,
    stop_reason: str = "end_turn",
    stop_details: object | None = None,
    content: Any = None,
) -> SimpleNamespace:
    if content is None:
        content = [
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text=text),
        ]
    return SimpleNamespace(
        content=content,
        stop_reason=stop_reason,
        stop_details=stop_details,
        model="claude-haiku-5-5",
        usage=SimpleNamespace(
            input_tokens=1200,
            output_tokens=340,
            cache_read_input_tokens=50,
            cache_creation_input_tokens=None,
        ),
    )


class FakeMessages:
    def __init__(self, outcome: Any) -> None:
        self.outcome = outcome
        self.requests: list[dict[str, Any]] = []

    def create(self, **request: Any) -> Any:
        self.requests.append(request)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def _provider(outcome: Any, **settings: Any) -> tuple[AnthropicLLMProvider, FakeMessages]:
    messages = FakeMessages(outcome)
    return AnthropicLLMProvider(client=SimpleNamespace(messages=messages), **settings), messages


def _generate(provider: AnthropicLLMProvider, model: str | None = "claude-haiku-5-5") -> Any:
    return provider.generate_structured_with_usage(
        prompt=PROMPT,
        schema_name=SCHEMA_NAME,
        payload=PAYLOAD,
        model=model,
    )


def test_request_uses_structured_output_and_effort_without_sampling_parameters() -> None:
    provider, messages = _provider(_response(text=json.dumps(WIRE_OUTPUT)))

    _generate(provider, model="claude-sonnet-5-5")

    (request,) = messages.requests
    assert set(request) == {"model", "max_tokens", "system", "messages", "output_config"}
    assert request["model"] == "claude-sonnet-5-5"
    assert request["max_tokens"] == 8000
    assert request["output_config"] == {
        "effort": "low",
        "format": {"type": "json_schema", "schema": EXTRACTION_WIRE_SCHEMA},
    }
    assert request["system"].startswith(PROMPT)
    assert [message["role"] for message in request["messages"]] == ["user"]
    user_content = request["messages"][0]["content"]
    assert "سُفْيَانُ" in user_content
    assert json.loads(user_content) == {
        "schema_name": SCHEMA_NAME,
        "payload": PAYLOAD,
    }


def test_effort_setting_is_sent_with_the_request() -> None:
    provider, messages = _provider(_response(text=json.dumps(WIRE_OUTPUT)), effort="high")

    _generate(provider)

    assert messages.requests[0]["output_config"]["effort"] == "high"


def test_every_object_of_the_output_format_is_closed_and_fully_required() -> None:
    def objects(schema: Any) -> list[dict[str, Any]]:
        if isinstance(schema, list):
            return [found for item in schema for found in objects(item)]
        if not isinstance(schema, dict):
            return []
        found = [schema] if schema.get("type") == "object" else []
        return found + [item for value in schema.values() for item in objects(value)]

    object_schemas = objects(EXTRACTION_WIRE_SCHEMA)

    assert len(object_schemas) == 7
    for schema in object_schemas:
        assert schema["additionalProperties"] is False
        assert schema["required"] == list(schema["properties"])


def test_response_is_folded_into_the_extraction_contract_with_usage() -> None:
    provider, _ = _provider(_response(text=json.dumps(WIRE_OUTPUT, ensure_ascii=False)))

    generation = _generate(provider)

    assert generation.cached is False
    assert generation.usage == LLMUsage(
        input_tokens=1200,
        output_tokens=340,
        cache_read_input_tokens=50,
        cache_creation_input_tokens=None,
        stop_reason="end_turn",
        model="claude-haiku-5-5",
    )
    assert [node["properties"] for node in generation.output["nodes"]] == [
        {"name": "سُفْيَانُ"},
        {"name": "ابْنِ شِهَابٍ"},
    ]
    (relation,) = generation.output["relations"]
    assert relation["properties"] == {"chain_no": 1, "sigha": "عن"}
    assert relation["from_ref"] == "node-1"
    assert generation.output["nodes"][0]["evidence_refs"] == [
        {"segment_id": "seg-1", "quote": "سُفْيَانُ"}
    ]
    assert provider.generate_structured(
        prompt=PROMPT,
        schema_name=SCHEMA_NAME,
        payload=PAYLOAD,
        model="claude-haiku-5-5",
    ) == generation.output


@pytest.mark.parametrize(
    ("stop_reason", "stop_details", "kind", "message_part"),
    [
        ("refusal", SimpleNamespace(category="general_harms"), "refusal", "general_harms"),
        ("refusal", None, "refusal", "unspecified"),
        ("max_tokens", None, "max_tokens", "max_tokens=8000"),
        ("pause_turn", None, "unexpected_stop_reason", "pause_turn"),
    ],
)
def test_unfinished_response_fails_the_call_before_its_content_is_read(
    stop_reason: str,
    stop_details: object | None,
    kind: str,
    message_part: str,
) -> None:
    class UnreadableContent:
        def __iter__(self) -> Any:
            raise AssertionError("content was read before stop_reason was checked")

    provider, _ = _provider(
        _response(
            stop_reason=stop_reason,
            stop_details=stop_details,
            content=UnreadableContent(),
        )
    )

    with pytest.raises(StructuredGenerationError) as error:
        _generate(provider)

    assert error.value.kind == kind
    assert message_part in str(error.value)
    assert error.value.usage is not None
    assert error.value.usage.output_tokens == 340
    assert error.value.usage.stop_reason == stop_reason


@pytest.mark.parametrize(
    "content",
    [
        [SimpleNamespace(type="thinking", thinking="")],
        [SimpleNamespace(type="text", text="not json")],
        [SimpleNamespace(type="text", text='{"nodes": []}')],
    ],
)
def test_response_without_the_structured_format_is_an_invalid_output(content: Any) -> None:
    provider, _ = _provider(_response(content=content))

    with pytest.raises(StructuredGenerationError) as error:
        _generate(provider)

    assert error.value.kind == "invalid_output"
    assert error.value.usage is not None


def _status_error(error_type: type[anthropic.APIStatusError], status: int) -> Exception:
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return error_type(
        "the api said no",
        response=httpx2.Response(status, request=request),
        body=None,
    )


@pytest.mark.parametrize(
    ("sdk_error", "kind"),
    [
        (_status_error(anthropic.AuthenticationError, 401), "authentication"),
        (_status_error(anthropic.PermissionDeniedError, 403), "permission_denied"),
        (_status_error(anthropic.NotFoundError, 404), "not_found"),
        (_status_error(anthropic.BadRequestError, 400), "bad_request"),
        (_status_error(anthropic.RateLimitError, 429), "rate_limit"),
        (_status_error(anthropic.InternalServerError, 500), "api_status"),
        (
            anthropic.APITimeoutError(
                request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
            ),
            "timeout",
        ),
        (
            anthropic.APIConnectionError(
                request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
            ),
            "connection",
        ),
    ],
)
def test_sdk_errors_become_failed_calls_with_their_kind(sdk_error: Exception, kind: str) -> None:
    provider, _ = _provider(sdk_error)

    with pytest.raises(StructuredGenerationError) as error:
        _generate(provider)

    assert error.value.kind == kind
    assert error.value.usage is None
    assert type(sdk_error).__name__ in str(error.value)


def test_missing_model_is_rejected_without_a_request() -> None:
    provider, messages = _provider(_response(text=json.dumps(WIRE_OUTPUT)))

    with pytest.raises(RuleViolationError, match="requires a configured model"):
        _generate(provider, model="  ")

    assert messages.requests == []


def test_container_registers_anthropic_provider_when_key_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("ANTHROPIC_EFFORT", "medium")
    get_settings.cache_clear()
    get_container.cache_clear()

    try:
        registry = get_container().extraction_management_service.provider_registry
        provider = registry.get("anthropic")
        assert isinstance(provider, AnthropicLLMProvider)
        assert provider.effort == "medium"
        assert provider.client.api_key == "test-key"
        assert provider.client.timeout == 45
        assert registry.get("noop") is not None
        assert registry.get("rule_based_isnad") is not None
    finally:
        get_container.cache_clear()
        get_settings.cache_clear()


def test_container_leaves_anthropic_provider_out_without_a_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    get_settings.cache_clear()
    get_container.cache_clear()

    try:
        registry = get_container().extraction_management_service.provider_registry
        assert registry.get("anthropic") is None
    finally:
        get_container.cache_clear()
        get_settings.cache_clear()


@pytest.mark.parametrize("provider", [NoOpLLMProvider(), RuleBasedIsnadProvider()])
def test_providers_without_token_accounting_report_empty_usage(provider: Any) -> None:
    generation = provider.generate_structured_with_usage(
        prompt=PROMPT,
        schema_name=SCHEMA_NAME,
        payload=PAYLOAD,
        model=None,
    )

    assert generation.usage == LLMUsage()
    assert generation.cached is False
    assert generation.output == provider.generate_structured(
        prompt=PROMPT,
        schema_name=SCHEMA_NAME,
        payload=PAYLOAD,
    )
