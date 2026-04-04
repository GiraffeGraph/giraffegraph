from dataclasses import dataclass, field

from app.application.ports.llm_provider import LLMProvider


@dataclass(slots=True)
class StaticLLMProviderRegistry:
    providers: dict[str, LLMProvider] = field(default_factory=dict)

    def __init__(self, providers: list[LLMProvider]) -> None:
        registry: dict[str, LLMProvider] = {}
        for provider in providers:
            normalized_name = provider.provider_name.strip().casefold()
            if normalized_name == "":
                raise ValueError("LLM provider name cannot be empty.")
            if normalized_name in registry:
                raise ValueError(
                    f"LLM provider '{provider.provider_name}' is registered more than once."
                )
            registry[normalized_name] = provider
        self.providers = registry

    def get(self, provider_name: str) -> LLMProvider | None:
        normalized_name = provider_name.strip().casefold()
        if normalized_name == "":
            return None
        return self.providers.get(normalized_name)
