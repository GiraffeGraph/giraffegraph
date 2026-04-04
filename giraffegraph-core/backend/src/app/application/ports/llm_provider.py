from typing import Any, Protocol


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


class LLMProviderRegistry(Protocol):
    def get(self, provider_name: str) -> LLMProvider | None: ...


class EmbeddingProvider(Protocol):
    def embed_texts(self, *, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Return embeddings for one or many texts."""
