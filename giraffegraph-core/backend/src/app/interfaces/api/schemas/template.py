from datetime import datetime

from pydantic import BaseModel


class TemplateSchemaBlueprintResponse(BaseModel):
    node_types: list[str]
    relation_types: list[str]
    segmentation_strategy: str


class DomainTemplateResponse(BaseModel):
    template_id: str
    name: str
    slug: str
    description: str
    is_system: bool
    created_at: datetime
    schema_blueprint: TemplateSchemaBlueprintResponse | None
