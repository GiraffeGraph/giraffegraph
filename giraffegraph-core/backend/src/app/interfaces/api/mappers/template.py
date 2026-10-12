from app.application.dto.contracts import TemplateSchema
from app.domain.template.entities import DomainTemplate
from app.interfaces.api.schemas.template import (
    DomainTemplateResponse,
    TemplateSchemaBlueprintResponse,
)


def to_domain_template_response(
    template: DomainTemplate,
    template_schema: TemplateSchema | None,
) -> DomainTemplateResponse:
    return DomainTemplateResponse(
        template_id=template.template_id,
        name=template.name,
        slug=template.slug,
        description=template.description,
        is_system=template.is_system,
        created_at=template.created_at,
        schema_blueprint=(
            TemplateSchemaBlueprintResponse(
                node_types=[node_type.name for node_type in template_schema.node_types],
                relation_types=[
                    relation_type.name for relation_type in template_schema.relation_types
                ],
                segmentation_strategy=template_schema.segmentation_strategy,
            )
            if template_schema is not None
            else None
        ),
    )
