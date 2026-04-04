from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class NoOpLLMProvider:
    provider_name: str = "noop"

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        del prompt, schema_name, payload, model
        return {
            "nodes": [],
            "relations": [],
        }
