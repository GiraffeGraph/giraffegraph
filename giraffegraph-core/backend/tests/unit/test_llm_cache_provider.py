import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from app.application.ports.llm_provider import (
    LLMUsage,
    StructuredGeneration,
    StructuredGenerationError,
)
from app.infrastructure.llm.cached_provider import CachedLLMProvider

PROMPT = "extract prompt"
SCHEMA_NAME = "extraction_contract"
MODEL = "claude-haiku-5-5"
USAGE = LLMUsage(input_tokens=900, output_tokens=120, stop_reason="end_turn", model=MODEL)


def _payload(*, run: str = "run-a", source: str = "source-a", segment: str = "seg-a") -> dict:
    return {
        "run": {"run_id": run, "schema_version_id": "schema-a", "pipeline_version": "v1"},
        "source_unit": {"source_unit_id": source, "external_ref": "Bukhari:1"},
        "schema": {"node_types": [{"name": "Narrator"}], "relation_types": []},
        "segments": [{"segment_id": segment, "segment_order": 3, "text": "حَدَّثَنَا سُفْيَانُ"}],
    }


class CountingProvider:
    provider_name = "anthropic"

    def __init__(self, error: Exception | None = None) -> None:
        self.calls = 0
        self.error = error

    def generate_structured(self, **arguments: Any) -> dict[str, Any]:
        return self.generate_structured_with_usage(**arguments).output

    def generate_structured_with_usage(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> StructuredGeneration:
        del prompt, schema_name, model
        self.calls += 1
        if self.error is not None:
            raise self.error
        segment_id = payload["segments"][0]["segment_id"]
        return StructuredGeneration(
            output={
                "nodes": [
                    {
                        "ref": "node-1",
                        "node_type": "Narrator",
                        "properties": {"name": "سُفْيَانُ"},
                        "confidence": 0.9,
                        "evidence_refs": [{"segment_id": segment_id, "quote": "سُفْيَانُ"}],
                    }
                ],
                "relations": [],
            },
            usage=USAGE,
        )


def _generate(provider: CachedLLMProvider, payload: dict[str, Any]) -> StructuredGeneration:
    return provider.generate_structured_with_usage(
        prompt=PROMPT,
        schema_name=SCHEMA_NAME,
        payload=payload,
        model=MODEL,
    )


def _key(provider: CachedLLMProvider, payload: dict[str, Any], **overrides: Any) -> str:
    arguments = {"prompt": PROMPT, "schema_name": SCHEMA_NAME, "model": MODEL, **overrides}
    return provider.cache_key(payload=payload, **arguments)


def test_miss_calls_the_provider_and_hit_does_not(tmp_path: Path) -> None:
    inner = CountingProvider()
    provider = CachedLLMProvider(inner=inner, cache_dir=tmp_path / "cache", effort="low")
    payload = _payload()

    assert provider.is_cached(
        prompt=PROMPT, schema_name=SCHEMA_NAME, payload=payload, model=MODEL
    ) is False
    miss = _generate(provider, payload)
    hit = _generate(provider, payload)

    assert inner.calls == 1
    assert (miss.cached, hit.cached) == (False, True)
    assert hit.output == miss.output
    assert hit.usage == USAGE
    assert provider.provider_name == "anthropic"
    assert provider.is_cached(
        prompt=PROMPT, schema_name=SCHEMA_NAME, payload=payload, model=MODEL
    ) is True
    assert provider.generate_structured(
        prompt=PROMPT, schema_name=SCHEMA_NAME, payload=payload, model=MODEL
    ) == miss.output
    assert inner.calls == 1


def test_entry_is_one_json_file_named_by_its_key(tmp_path: Path) -> None:
    provider = CachedLLMProvider(inner=CountingProvider(), cache_dir=tmp_path, effort="low")
    payload = _payload()

    _generate(provider, payload)

    (path,) = tmp_path.iterdir()
    entry = json.loads(path.read_text(encoding="utf-8"))
    assert path.name == f"{_key(provider, payload)}.json"
    assert entry["key"] == _key(provider, payload)
    assert (entry["provider"], entry["model"], entry["effort"]) == ("anthropic", MODEL, "low")
    assert entry["prompt_version"] == SCHEMA_NAME
    assert entry["usage"] == {
        "input_tokens": 900,
        "output_tokens": 120,
        "cache_read_input_tokens": None,
        "cache_creation_input_tokens": None,
        "stop_reason": "end_turn",
        "model": MODEL,
    }
    assert entry["output"]["nodes"][0]["properties"] == {"name": "سُفْيَانُ"}
    assert entry["created_at"].endswith("+00:00")


def test_key_is_a_stable_sha256_of_the_call_content(tmp_path: Path) -> None:
    provider = CachedLLMProvider(inner=CountingProvider(), cache_dir=tmp_path, effort="low")
    payload = _payload()
    reordered = {key: payload[key] for key in reversed(list(payload))}

    key = _key(provider, payload)

    assert len(key) == 64
    assert key == _key(provider, deepcopy(payload))
    assert key == _key(provider, reordered)
    assert key == _key(
        CachedLLMProvider(inner=CountingProvider(), cache_dir=tmp_path / "other", effort="low"),
        payload,
    )


def test_key_ignores_the_random_identifiers_of_a_run(tmp_path: Path) -> None:
    provider = CachedLLMProvider(inner=CountingProvider(), cache_dir=tmp_path, effort="low")

    assert _key(provider, _payload()) == _key(
        provider,
        _payload(run="run-b", source="source-b", segment="seg-b"),
    )


def test_key_changes_with_every_input_that_changes_the_answer(tmp_path: Path) -> None:
    provider = CachedLLMProvider(inner=CountingProvider(), cache_dir=tmp_path, effort="low")
    payload = _payload()
    other_text = _payload()
    other_text["segments"][0]["text"] = "حَدَّثَنَا لَيْثٌ"
    other_schema = _payload()
    other_schema["schema"]["node_types"][0]["extraction_hints"] = ["Copy the name verbatim."]
    other_effort = CachedLLMProvider(inner=CountingProvider(), cache_dir=tmp_path, effort="high")
    other_provider_inner = CountingProvider()
    other_provider_inner.provider_name = "openai"
    other_provider = CachedLLMProvider(inner=other_provider_inner, cache_dir=tmp_path, effort="low")

    keys = {
        _key(provider, payload),
        _key(provider, payload, model="claude-sonnet-5-5"),
        _key(provider, payload, prompt="another prompt"),
        _key(provider, payload, schema_name="another_contract"),
        _key(provider, other_text),
        _key(provider, other_schema),
        _key(other_effort, payload),
        _key(other_provider, payload),
    }

    assert len(keys) == 8


def test_hit_points_evidence_at_the_segments_of_the_current_run(tmp_path: Path) -> None:
    inner = CountingProvider()
    provider = CachedLLMProvider(inner=inner, cache_dir=tmp_path, effort="low")
    _generate(provider, _payload(segment="seg-a"))

    hit = _generate(provider, _payload(run="run-b", source="source-b", segment="seg-b"))

    assert inner.calls == 1
    assert hit.cached is True
    assert hit.output["nodes"][0]["evidence_refs"] == [
        {"segment_id": "seg-b", "quote": "سُفْيَانُ"}
    ]
    assert hit.output["nodes"][0]["ref"] == "node-1"


def test_failed_call_is_not_stored(tmp_path: Path) -> None:
    inner = CountingProvider(error=StructuredGenerationError("refused", kind="refusal"))
    provider = CachedLLMProvider(inner=inner, cache_dir=tmp_path / "cache", effort="low")

    for _ in range(2):
        with pytest.raises(StructuredGenerationError):
            _generate(provider, _payload())

    assert inner.calls == 2
    assert not (tmp_path / "cache").exists()
