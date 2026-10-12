from collections.abc import Mapping
from dataclasses import dataclass, field

from app.application.dto.contracts import (
    NodeTypeDefinitionInput,
    PropertyDefinitionInput,
    RelationTypeDefinitionInput,
    TemplateSchema,
)
from app.application.ports.template_catalog import DomainTemplateCatalog
from app.domain.template.entities import DomainTemplate

BLANK_TEMPLATE_ID = "blank"
STORY_TEMPLATE_ID = "story"
ISNAD_TEMPLATE_ID = "isnad"

SYSTEM_DOMAIN_TEMPLATES = [
    DomainTemplate(
        template_id=BLANK_TEMPLATE_ID,
        name="Blank",
        slug=BLANK_TEMPLATE_ID,
        description="Start from an empty generic graph schema and configure everything manually.",
    ),
    DomainTemplate(
        template_id=STORY_TEMPLATE_ID,
        name="Story / Series / Film",
        slug=STORY_TEMPLATE_ID,
        description=(
            "Story-oriented starter template for transcripts, scripts, episodes, scenes, "
            "characters, events, and related narrative structures."
        ),
    ),
    DomainTemplate(
        template_id=ISNAD_TEMPLATE_ID,
        name="Hadith Isnad",
        slug=ISNAD_TEMPLATE_ID,
        description=(
            "Narrator-chain template for hadith texts: narrators, the hadith they transmit, "
            "and who narrated from whom in each chain."
        ),
    ),
]

ISNAD_TEMPLATE_SCHEMA = TemplateSchema(
    segmentation_strategy="isnad",
    node_types=(
        NodeTypeDefinitionInput(
            name="Narrator",
            display_name="Narrator",
            description="A person who transmits a hadith in a chain of narration.",
            merge_keys=["name"],
            extraction_hints=[
                "Copy the narrator name verbatim from the segment text.",
                "Do not add or remove the definite article (ال).",
                "Do not include transmission verbs such as حدثنا, أخبرنا or عن in the name.",
                "The Prophet is not a narrator node.",
            ],
            properties=[
                PropertyDefinitionInput(
                    name="name",
                    data_type="string",
                    required=True,
                    description="Narrator name exactly as written in the text.",
                ),
            ],
        ),
        NodeTypeDefinitionInput(
            name="Hadith",
            display_name="Hadith",
            description="The report that the chain of narration transmits.",
            merge_keys=["hadith_ref"],
            extraction_hints=[
                "Create exactly one Hadith node per source unit.",
                "Set hadith_ref to source_unit.external_ref.",
            ],
            properties=[
                PropertyDefinitionInput(
                    name="hadith_ref",
                    data_type="string",
                    required=True,
                    description="Reference of the hadith, taken from source_unit.external_ref.",
                ),
            ],
        ),
    ),
    relation_types=(
        RelationTypeDefinitionInput(
            name="NARRATED_FROM",
            from_type="Narrator",
            to_type="Narrator",
            description="The first narrator received the hadith from the second narrator.",
            merge_keys=["hadith_ref", "chain_no", "position"],
            extraction_hints=[
                "Create one relation for every pair of consecutive narrators in a chain.",
                "from_ref is the narrator named first in the text, to_ref the one named next.",
            ],
            properties=[
                PropertyDefinitionInput(
                    name="hadith_ref",
                    data_type="string",
                    description="Reference of the hadith, taken from source_unit.external_ref.",
                ),
                PropertyDefinitionInput(
                    name="chain_no",
                    data_type="integer",
                    description="Number of the chain: the segment_order of the quoted segment.",
                ),
                PropertyDefinitionInput(
                    name="position",
                    data_type="integer",
                    description="1-based position of the from_ref narrator in its chain.",
                ),
                PropertyDefinitionInput(
                    name="sigha",
                    data_type="string",
                    description="Transmission formula written before the to_ref narrator.",
                ),
            ],
        ),
        RelationTypeDefinitionInput(
            name="TRANSMITS",
            from_type="Narrator",
            to_type="Hadith",
            description="The narrator appears in a chain that transmits the hadith.",
        ),
    ),
)

SYSTEM_TEMPLATE_SCHEMAS: Mapping[str, TemplateSchema] = {ISNAD_TEMPLATE_ID: ISNAD_TEMPLATE_SCHEMA}


@dataclass(slots=True)
class StaticDomainTemplateCatalog(DomainTemplateCatalog):
    templates: dict[str, DomainTemplate] = field(default_factory=dict)
    default_template_id: str = BLANK_TEMPLATE_ID
    schemas: dict[str, TemplateSchema] = field(default_factory=dict)

    def __init__(
        self,
        *,
        templates: list[DomainTemplate],
        default_template_id: str = BLANK_TEMPLATE_ID,
        schemas: Mapping[str, TemplateSchema] = SYSTEM_TEMPLATE_SCHEMAS,
    ) -> None:
        normalized_templates: dict[str, DomainTemplate] = {}
        for template in templates:
            normalized_templates[self._normalize(template.template_id)] = template
        normalized_default_template_id = self._normalize(default_template_id)
        if normalized_default_template_id not in normalized_templates:
            raise ValueError(
                f"Default template '{default_template_id}' is not registered in the catalog."
            )
        self.templates = normalized_templates
        self.default_template_id = normalized_default_template_id
        self.schemas = {
            self._normalize(template_id): schema for template_id, schema in schemas.items()
        }

    def get(self, template_id: str) -> DomainTemplate | None:
        normalized_template_id = self._normalize(template_id)
        if normalized_template_id == "":
            return None
        return self.templates.get(normalized_template_id)

    def get_schema(self, template_id: str) -> TemplateSchema | None:
        return self.schemas.get(self._normalize(template_id))

    def list(self) -> list[DomainTemplate]:
        return sorted(
            self.templates.values(),
            key=lambda template: (template.is_system is False, template.name.casefold()),
        )

    def get_default(self) -> DomainTemplate:
        return self.templates[self.default_template_id]

    def _normalize(self, value: str) -> str:
        return value.strip().casefold()
