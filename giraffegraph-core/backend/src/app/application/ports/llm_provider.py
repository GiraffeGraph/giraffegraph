from dataclasses import dataclass
from typing import Any, Protocol

from app.application.errors import ExternalServiceError


@dataclass(frozen=True, slots=True)
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    stop_reason: str | None = None
    model: str | None = None


@dataclass(frozen=True, slots=True)
class StructuredGeneration:
    output: dict[str, Any]
    usage: LLMUsage
    cached: bool = False


class StructuredGenerationError(ExternalServiceError):
    """A structured-generation call that failed; `usage` is set when the call was billed."""

    def __init__(self, message: str, *, kind: str, usage: LLMUsage | None = None) -> None:
        super().__init__(message)
        self.kind = kind
        self.usage = usage


class LLMProvider(Protocol):
    provider_name: str

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        """Return structured output for a given schema contract."""

    def generate_structured_with_usage(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> StructuredGeneration:
        """Return the structured output together with the token usage of the call."""


class LLMProviderRegistry(Protocol):
    def get(self, provider_name: str) -> LLMProvider | None: ...


class EmbeddingProvider(Protocol):
    def embed_texts(self, *, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Return embeddings for one or many texts."""
