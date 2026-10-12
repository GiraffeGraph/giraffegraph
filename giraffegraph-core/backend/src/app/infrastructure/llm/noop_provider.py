from dataclasses import dataclass
from typing import Any

from app.application.ports.llm_provider import LLMUsage, StructuredGeneration


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

    def generate_structured_with_usage(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> StructuredGeneration:
        return StructuredGeneration(
            output=self.generate_structured(
                prompt=prompt,
                schema_name=schema_name,
                payload=payload,
                model=model,
            ),
            usage=LLMUsage(model=model),
        )
