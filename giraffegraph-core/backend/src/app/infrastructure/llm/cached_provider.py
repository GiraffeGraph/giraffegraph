import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.application.ports.llm_provider import LLMProvider, LLMUsage, StructuredGeneration


@dataclass(slots=True)
class CachedLLMProvider:
    """Serves repeated structured-generation calls from one JSON file per call on disk.

    The engine gives runs, source units and segments random identifiers, so those are
    replaced by positional placeholders in the key and in the stored response. A call with
    the same content is a hit in any later run, and its evidence points at that run's
    segments.
    """

    inner: LLMProvider
    cache_dir: Path
    effort: str | None = None
    provider_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.provider_name = self.inner.provider_name

    def cache_key(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> str:
        key_material = {
            "provider": self.inner.provider_name,
            "model": model,
            "effort": self.effort,
            "prompt_version": schema_name,
            "prompt_text": prompt,
            "payload": _replace_strings(payload, _placeholders(payload)),
        }
        canonical = json.dumps(
            key_material,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def is_cached(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> bool:
        key = self.cache_key(prompt=prompt, schema_name=schema_name, payload=payload, model=model)
        return self._path(key).is_file()

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
        key = self.cache_key(prompt=prompt, schema_name=schema_name, payload=payload, model=model)
        path = self._path(key)
        placeholders = _placeholders(payload)
        if path.is_file():
            with path.open(encoding="utf-8") as handle:
                entry = json.load(handle)
            identifiers = {placeholder: value for value, placeholder in placeholders.items()}
            return StructuredGeneration(
                output=_replace_strings(entry["output"], identifiers),
                usage=LLMUsage(**entry["usage"]),
                cached=True,
            )

        generation = self.inner.generate_structured_with_usage(
            prompt=prompt,
            schema_name=schema_name,
            payload=payload,
            model=model,
        )
        entry = {
            "key": key,
            "created_at": datetime.now(UTC).isoformat(),
            "provider": self.inner.provider_name,
            "model": model,
            "effort": self.effort,
            "prompt_version": schema_name,
            "output": _replace_strings(generation.output, placeholders),
            "usage": asdict(generation.usage),
        }
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Concurrent writers of one key each replace the file atomically with a full entry.
        temporary_path = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(entry, handle, ensure_ascii=False, indent=2)
        os.replace(temporary_path, path)
        return generation

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"


def _placeholders(payload: dict[str, Any]) -> dict[str, str]:
    placeholders: dict[str, str] = {}
    for section, id_fields in (
        ("run", ("run_id", "schema_version_id")),
        ("source_unit", ("source_unit_id",)),
    ):
        values = payload.get(section)
        if not isinstance(values, dict):
            continue
        for id_field in id_fields:
            value = values.get(id_field)
            if isinstance(value, str):
                placeholders[value] = f"@{section}.{id_field}"
    segments = payload.get("segments")
    if isinstance(segments, list):
        for position, segment in enumerate(segments, start=1):
            if isinstance(segment, dict) and isinstance(segment.get("segment_id"), str):
                placeholders[segment["segment_id"]] = f"@segment.{position}"
    return placeholders


def _replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        return replacements.get(value, value)
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_strings(item, replacements) for key, item in value.items()}
    return value
