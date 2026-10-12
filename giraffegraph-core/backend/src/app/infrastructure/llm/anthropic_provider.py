import json
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any, Literal

import anthropic

from app.application.errors import RuleViolationError
from app.application.ports.llm_provider import (
    LLMUsage,
    StructuredGeneration,
    StructuredGenerationError,
)

AnthropicEffort = Literal["low", "medium", "high", "xhigh", "max"]

DEFAULT_MAX_TOKENS = 8000

# Structured outputs accept closed objects only, so the free-form `properties` map of the
# extraction contract travels as a list of name/value entries and is folded back on receipt.
_PROPERTY_ENTRIES_SCHEMA: dict[str, object] = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {
                "anyOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}],
            },
        },
        "required": ["name", "value"],
        "additionalProperties": False,
    },
}
_EVIDENCE_REFS_SCHEMA: dict[str, object] = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "segment_id": {"type": "string"},
            "quote": {"type": "string"},
        },
        "required": ["segment_id", "quote"],
        "additionalProperties": False,
    },
}
EXTRACTION_WIRE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ref": {"type": "string"},
                    "node_type": {"type": "string"},
                    "properties": _PROPERTY_ENTRIES_SCHEMA,
                    "confidence": {"type": "number"},
                    "evidence_refs": _EVIDENCE_REFS_SCHEMA,
                },
                "required": ["ref", "node_type", "properties", "confidence", "evidence_refs"],
                "additionalProperties": False,
            },
        },
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "relation_type": {"type": "string"},
                    "from_ref": {"type": "string"},
                    "to_ref": {"type": "string"},
                    "properties": _PROPERTY_ENTRIES_SCHEMA,
                    "confidence": {"type": "number"},
                    "evidence_refs": _EVIDENCE_REFS_SCHEMA,
                },
                "required": [
                    "relation_type",
                    "from_ref",
                    "to_ref",
                    "properties",
                    "confidence",
                    "evidence_refs",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["nodes", "relations"],
    "additionalProperties": False,
}
WIRE_FORMAT_NOTE = (
    "Response format: write every 'properties' object as a list of "
    '{"name": "<property name>", "value": <property value>} entries, one entry per property, '
    "and leave out 'merge_key_payload'."
)


@dataclass(slots=True)
class AnthropicLLMProvider:
    client: anthropic.Anthropic
    effort: AnthropicEffort = "low"
    max_tokens: int = DEFAULT_MAX_TOKENS
    provider_name: str = "anthropic"

    @classmethod
    def from_api_key(
        cls,
        api_key: str,
        *,
        timeout_seconds: float,
        effort: AnthropicEffort = "low",
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> "AnthropicLLMProvider":
        return cls(
            client=anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds),
            effort=effort,
            max_tokens=max_tokens,
        )

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        return self.generate_structured_with_usage(
            prompt=prompt,
            schema_name=schema_name,
            payload=payload,
            model=model,
        ).output

    def generate_structured_with_usage(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> StructuredGeneration:
        normalized_model = (model or "").strip()
        if normalized_model == "":
            raise RuleViolationError(
                "Anthropic extraction provider requires a configured model."
            )

        try:
            response = self.client.messages.create(
                model=normalized_model,
                max_tokens=self.max_tokens,
                system=f"{prompt}\n\n{WIRE_FORMAT_NOTE}",
                messages=[
                    {
                        "role": "user",
                        "content": json.dumps(
                            {"schema_name": schema_name, "payload": payload},
                            ensure_ascii=False,
                        ),
                    }
                ],
                output_config={
                    "effort": self.effort,
                    "format": {"type": "json_schema", "schema": EXTRACTION_WIRE_SCHEMA},
                },
            )
        except anthropic.AuthenticationError as exc:
            raise self._status_error(exc, kind="authentication") from exc
        except anthropic.PermissionDeniedError as exc:
            raise self._status_error(exc, kind="permission_denied") from exc
        except anthropic.NotFoundError as exc:
            raise self._status_error(exc, kind="not_found") from exc
        except anthropic.BadRequestError as exc:
            raise self._status_error(exc, kind="bad_request") from exc
        except anthropic.RateLimitError as exc:
            raise self._status_error(exc, kind="rate_limit") from exc
        except anthropic.APIStatusError as exc:
            raise self._status_error(exc, kind="api_status") from exc
        except anthropic.APITimeoutError as exc:
            raise StructuredGenerationError(
                "Anthropic request timed out (APITimeoutError).",
                kind="timeout",
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise StructuredGenerationError(
                f"Anthropic request failed before a response arrived "
                f"({type(exc).__name__}): {exc.message}",
                kind="connection",
            ) from exc
        except anthropic.APIError as exc:
            raise StructuredGenerationError(
                f"Anthropic request failed ({type(exc).__name__}): {exc.message}",
                kind="api_error",
            ) from exc

        usage = LLMUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cache_read_input_tokens=response.usage.cache_read_input_tokens,
            cache_creation_input_tokens=response.usage.cache_creation_input_tokens,
            stop_reason=response.stop_reason,
            model=response.model,
        )
        if response.stop_reason == "refusal":
            category = response.stop_details.category if response.stop_details else None
            raise StructuredGenerationError(
                f"Anthropic model '{normalized_model}' refused the request "
                f"(category: {category or 'unspecified'}).",
                kind="refusal",
                usage=usage,
            )
        if response.stop_reason == "max_tokens":
            raise StructuredGenerationError(
                f"Anthropic output was truncated at max_tokens={self.max_tokens}.",
                kind="max_tokens",
                usage=usage,
            )
        if response.stop_reason != "end_turn":
            raise StructuredGenerationError(
                f"Anthropic response ended with stop_reason '{response.stop_reason}'.",
                kind="unexpected_stop_reason",
                usage=usage,
            )

        # Thinking blocks may precede the answer, so the text block is picked by type.
        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise StructuredGenerationError(
                "Anthropic response did not include a text block.",
                kind="invalid_output",
                usage=usage,
            )
        try:
            output = _fold_wire_output(json.loads(text))
        except (JSONDecodeError, KeyError, TypeError) as exc:
            raise StructuredGenerationError(
                "Anthropic response did not match the structured extraction format.",
                kind="invalid_output",
                usage=usage,
            ) from exc
        return StructuredGeneration(output=output, usage=usage)

    def _status_error(
        self,
        exc: anthropic.APIStatusError,
        *,
        kind: str,
    ) -> StructuredGenerationError:
        return StructuredGenerationError(
            f"Anthropic request failed ({type(exc).__name__}, status {exc.status_code}): "
            f"{exc.message}",
            kind=kind,
        )


def _fold_wire_output(wire_output: dict[str, Any]) -> dict[str, Any]:
    return {
        "nodes": [_fold_properties(node) for node in wire_output["nodes"]],
        "relations": [_fold_properties(relation) for relation in wire_output["relations"]],
    }


def _fold_properties(item: dict[str, Any]) -> dict[str, Any]:
    return {
        **item,
        "properties": {entry["name"]: entry["value"] for entry in item["properties"]},
    }
