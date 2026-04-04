from dataclasses import dataclass, field

from app.application.ports.prompt_catalog import StructuredPromptDefinition
from app.application.ports.repositories import StructuredPromptRepository

CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY = "candidate_graph_extraction"
CANDIDATE_GRAPH_EXTRACTION_V1 = StructuredPromptDefinition(
    prompt_key=CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY,
    version="candidate_graph_extraction_v1",
    schema_name="candidate_graph_extraction_v1",
    prompt_text=(
        "You are extracting candidate graph suggestions from segmented source material.\n"
        "Use only the provided schema node and relation types, including aliases.\n\n"
        "Return a JSON object with exactly this structure:\n"
        "{\n"
        '  "nodes": [\n'
        "    {\n"
        '      "ref": "<stable unique string id for this node, e.g. node-1>",\n'
        '      "node_type": "<must match a name from schema.node_types>",\n'
        '      "properties": {"<merge_key_field>": "<value>", ...},\n'
        '      "merge_key_payload": {},\n'
        '      "confidence": 0.9,\n'
        '      "evidence_refs": [{"segment_id": "<id from segments list>", "quote": "<exact quote>"}]\n'
        "    }\n"
        "  ],\n"
        '  "relations": [\n'
        "    {\n"
        '      "relation_type": "<must match a name from schema.relation_types>",\n'
        '      "from_ref": "<ref of the source node>",\n'
        '      "to_ref": "<ref of the target node>",\n'
        '      "properties": {},\n'
        '      "confidence": 0.85,\n'
        '      "evidence_refs": [{"segment_id": "<id from segments list>", "quote": "<exact quote>"}]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- 'ref' must be a unique string (e.g. node-1, node-2); never use 'id' or 'type' as field names.\n"
        "- 'node_type' and 'relation_type' must exactly match schema names (case-sensitive).\n"
        "- 'from_ref' and 'to_ref' must match a 'ref' defined in the nodes list.\n"
        "- Put the merge key value inside 'properties' (e.g. {\"name\": \"Alice\"}).\n"
        "- Only reference segment_ids that appear in the input payload.\n"
        "- Do not add any fields outside this schema."
    ),
)
DEFAULT_STRUCTURED_PROMPTS = [CANDIDATE_GRAPH_EXTRACTION_V1]


@dataclass(slots=True)
class StaticStructuredPromptCatalog:
    prompts: dict[tuple[str, str], StructuredPromptDefinition] = field(default_factory=dict)

    def __init__(self, prompts: list[StructuredPromptDefinition]) -> None:
        registry: dict[tuple[str, str], StructuredPromptDefinition] = {}
        for prompt in prompts:
            key = (prompt.prompt_key.strip().casefold(), prompt.version.strip())
            if key in registry:
                raise ValueError(
                    f"Prompt '{prompt.prompt_key}' version '{prompt.version}' is duplicated."
                )
            registry[key] = prompt
        self.prompts = registry

    def get(
        self,
        *,
        prompt_key: str,
        version: str,
    ) -> StructuredPromptDefinition | None:
        normalized_key = prompt_key.strip().casefold()
        normalized_version = version.strip()
        if normalized_key == "" or normalized_version == "":
            return None
        return self.prompts.get((normalized_key, normalized_version))


@dataclass(slots=True)
class RepositoryStructuredPromptCatalog:
    repository: StructuredPromptRepository

    def get(
        self,
        *,
        prompt_key: str,
        version: str,
    ) -> StructuredPromptDefinition | None:
        return self.repository.get(prompt_key=prompt_key, version=version)


def seed_default_structured_prompts(repository: StructuredPromptRepository) -> None:
    for prompt in DEFAULT_STRUCTURED_PROMPTS:
        repository.upsert(prompt)
