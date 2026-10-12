from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.contracts import (
    NodeTypeDefinitionInput,
    PropertyDefinitionInput,
    RelationTypeDefinitionInput,
    SchemaVersionCreateInput,
)
from app.application.use_cases.schema_management import SchemaManagementService
from app.interfaces.api.dependencies import get_schema_management_service
from app.interfaces.api.mappers.schema import to_schema_version_response
from app.interfaces.api.schemas.schema import (
    NodeTypeDefinitionRequest,
    RelationTypeDefinitionRequest,
    SchemaVersionCreateRequest,
    SchemaVersionResponse,
)

router = APIRouter(tags=["schema"])
SchemaManagementServiceDep = Annotated[
    SchemaManagementService,
    Depends(get_schema_management_service),
]


@router.get(
    "/api/projects/{project_id}/schema-versions",
    response_model=list[SchemaVersionResponse],
)
def list_schema_versions(
    project_id: str,
    service: SchemaManagementServiceDep,
) -> list[SchemaVersionResponse]:
    details = service.list_schema_versions(project_id)
    return [to_schema_version_response(detail) for detail in details]


@router.post(
    "/api/projects/{project_id}/schema-versions",
    response_model=SchemaVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schema_version(
    project_id: str,
    request: SchemaVersionCreateRequest,
    service: SchemaManagementServiceDep,
) -> SchemaVersionResponse:
    detail = service.create_schema_version(
        SchemaVersionCreateInput(
            project_id=project_id,
            version_no=request.version_no,
            notes=request.notes,
        )
    )
    return to_schema_version_response(detail)


@router.get("/api/projects/{project_id}/active-schema", response_model=SchemaVersionResponse)
def get_active_schema(
    project_id: str,
    service: SchemaManagementServiceDep,
) -> SchemaVersionResponse:
    return to_schema_version_response(service.get_active_schema(project_id))


@router.get("/api/schema-versions/{schema_version_id}", response_model=SchemaVersionResponse)
def get_schema_version(
    schema_version_id: str,
    service: SchemaManagementServiceDep,
) -> SchemaVersionResponse:
    return to_schema_version_response(service.get_schema_version(schema_version_id))


@router.post(
    "/api/projects/{project_id}/schema-versions/{schema_version_id}/activate",
    response_model=SchemaVersionResponse,
)
def activate_schema_version(
    project_id: str,
    schema_version_id: str,
    service: SchemaManagementServiceDep,
) -> SchemaVersionResponse:
    detail = service.activate_schema_version(project_id, schema_version_id)
    return to_schema_version_response(detail)


@router.post(
    "/api/schema-versions/{schema_version_id}/node-types",
    response_model=SchemaVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_node_type(
    schema_version_id: str,
    request: NodeTypeDefinitionRequest,
    service: SchemaManagementServiceDep,
) -> SchemaVersionResponse:
    detail = service.add_node_type(
        schema_version_id,
        NodeTypeDefinitionInput(
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            is_core=request.is_core,
            merge_keys=request.merge_keys,
            confidence_threshold=request.confidence_threshold,
            aliases=request.aliases,
            extraction_hints=request.extraction_hints,
            properties=[
                PropertyDefinitionInput(
                    name=property_request.name,
                    data_type=property_request.data_type,
                    required=property_request.required,
                    description=property_request.description,
                    default_value=property_request.default_value,
                    enum_values=property_request.enum_values,
                )
                for property_request in request.properties
            ],
        ),
    )
    return to_schema_version_response(detail)


@router.post(
    "/api/schema-versions/{schema_version_id}/relation-types",
    response_model=SchemaVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_relation_type(
    schema_version_id: str,
    request: RelationTypeDefinitionRequest,
    service: SchemaManagementServiceDep,
) -> SchemaVersionResponse:
    detail = service.add_relation_type(
        schema_version_id,
        RelationTypeDefinitionInput(
            name=request.name,
            from_type=request.from_type,
            to_type=request.to_type,
            description=request.description,
            directional=request.directional,
            aliases=request.aliases,
            extraction_hints=request.extraction_hints,
            required_properties=request.required_properties,
            merge_keys=request.merge_keys,
            confidence_threshold=request.confidence_threshold,
            properties=[
                PropertyDefinitionInput(
                    name=property_request.name,
                    data_type=property_request.data_type,
                    required=property_request.required,
                    description=property_request.description,
                    default_value=property_request.default_value,
                    enum_values=property_request.enum_values,
                )
                for property_request in request.properties
            ],
        ),
    )
    return to_schema_version_response(detail)
