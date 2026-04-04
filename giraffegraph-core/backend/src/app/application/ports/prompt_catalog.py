from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StructuredPromptDefinition:
    prompt_key: str
    version: str
    schema_name: str
    prompt_text: str


class StructuredPromptCatalog(Protocol):
    def get(
        self,
        *,
        prompt_key: str,
        version: str,
    ) -> StructuredPromptDefinition | None: ...
