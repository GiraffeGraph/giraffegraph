from app.application.use_cases.schema_management import SchemaVersionDetail
from app.domain.schema.entities import (
    NodeTypeDefinition,
    PropertyDefinition,
    RelationTypeDefinition,
)
from app.interfaces.api.schemas.schema import (
    NodeTypeDefinitionResponse,
    PropertyDefinitionResponse,
    RelationTypeDefinitionResponse,
    SchemaVersionResponse,
)


def to_schema_version_response(detail: SchemaVersionDetail) -> SchemaVersionResponse:
    schema_version = detail.schema_version
    return SchemaVersionResponse(
        schema_version_id=schema_version.schema_version_id,
        project_id=schema_version.project_id,
        version_no=schema_version.version_no,
        status=schema_version.status,
        notes=schema_version.notes,
        created_at=schema_version.created_at,
        activated_at=schema_version.activated_at,
        node_types=[to_node_type_response(node_type) for node_type in detail.node_types],
        relation_types=[
            to_relation_type_response(relation_type) for relation_type in detail.relation_types
        ],
    )


def to_node_type_response(node_type: NodeTypeDefinition) -> NodeTypeDefinitionResponse:
    return NodeTypeDefinitionResponse(
        node_type_id=node_type.node_type_id,
        schema_version_id=node_type.schema_version_id,
        name=node_type.name,
        display_name=node_type.display_name,
        description=node_type.description,
        is_core=node_type.is_core,
        merge_keys=node_type.merge_keys,
        confidence_threshold=node_type.confidence_threshold,
        aliases=node_type.aliases,
        extraction_hints=node_type.extraction_hints,
        properties=[to_property_response(item) for item in node_type.properties],
        is_active=node_type.is_active,
    )


def to_relation_type_response(
    relation_type: RelationTypeDefinition,
) -> RelationTypeDefinitionResponse:
    return RelationTypeDefinitionResponse(
        relation_type_id=relation_type.relation_type_id,
        schema_version_id=relation_type.schema_version_id,
        name=relation_type.name,
        from_type=relation_type.from_type,
        to_type=relation_type.to_type,
        description=relation_type.description,
        directional=relation_type.directional,
        aliases=relation_type.aliases,
        extraction_hints=relation_type.extraction_hints,
        required_properties=relation_type.required_properties,
        merge_keys=relation_type.merge_keys,
        properties=[to_property_response(item) for item in relation_type.properties],
        confidence_threshold=relation_type.confidence_threshold,
        is_active=relation_type.is_active,
    )


def to_property_response(property_definition: PropertyDefinition) -> PropertyDefinitionResponse:
    return PropertyDefinitionResponse(
        property_id=property_definition.property_id,
        owner_kind=property_definition.owner_kind,
        owner_type_name=property_definition.owner_type_name,
        name=property_definition.name,
        data_type=property_definition.data_type,
        required=property_definition.required,
        description=property_definition.description,
        default_value=property_definition.default_value,
        enum_values=property_definition.enum_values,
    )
