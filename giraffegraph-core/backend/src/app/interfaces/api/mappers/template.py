from app.domain.template.entities import DomainTemplate
from app.interfaces.api.schemas.template import DomainTemplateResponse


def to_domain_template_response(template: DomainTemplate) -> DomainTemplateResponse:
    return DomainTemplateResponse(
        template_id=template.template_id,
        name=template.name,
        slug=template.slug,
        description=template.description,
        is_system=template.is_system,
        created_at=template.created_at,
    )
