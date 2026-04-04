from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.template_management import TemplateManagementService
from app.interfaces.api.dependencies import get_template_management_service
from app.interfaces.api.mappers.template import to_domain_template_response
from app.interfaces.api.schemas.template import DomainTemplateResponse

router = APIRouter(tags=["templates"])
TemplateManagementServiceDep = Annotated[
    TemplateManagementService,
    Depends(get_template_management_service),
]


@router.get("/api/templates", response_model=list[DomainTemplateResponse])
def list_templates(
    service: TemplateManagementServiceDep,
) -> list[DomainTemplateResponse]:
    return [to_domain_template_response(template) for template in service.list_templates()]
