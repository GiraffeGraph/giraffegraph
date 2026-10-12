from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.contracts import (
    NodeTypeDefinitionInput,
    PropertyDefinitionInput,
    RelationTypeDefinitionInput,
    SchemaVersionCreateInput,
    TemplateSchema,
)
from app.application.errors import ConflictError, NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    PipelineDefinitionRepository,
    ProjectRepository,
    SchemaRepository,
)
from app.domain.orchestration.pipeline_definitions import (
    DEFAULT_PIPELINE_DESCRIPTION,
    DEFAULT_PIPELINE_VERSION,
    PipelineDefinition,
    build_default_pipeline_steps,
)
from app.domain.schema.entities import (
    NodeTypeDefinition,
    PropertyDefinition,
    RelationTypeDefinition,
    SchemaVersion,
)
from app.domain.shared.enums import SchemaStatus


@dataclass(slots=True)
class SchemaVersionDetail:
    schema_version: SchemaVersion
    node_types: list[NodeTypeDefinition]
    relation_types: list[RelationTypeDefinition]


@dataclass(slots=True)
class AppliedTemplateSchema:
    schema_version: SchemaVersion
    pipeline_version: str
    segmentation_strategy: str


@dataclass(slots=True)
class SchemaManagementService:
    project_repository: ProjectRepository
    schema_repository: SchemaRepository
    pipeline_definition_repository: PipelineDefinitionRepository

    def create_schema_version(
        self,
        payload: SchemaVersionCreateInput,
        *,
        pipeline_description: str = DEFAULT_PIPELINE_DESCRIPTION,
    ) -> SchemaVersionDetail:
        self._require_project(payload.project_id)

        version_numbers = {
            schema_version.version_no
            for schema_version in self.schema_repository.list_schema_versions(payload.project_id)
        }
        if payload.version_no in version_numbers:
            raise ConflictError(
                "Schema version "
                f"'{payload.version_no}' already exists for project '{payload.project_id}'."
            )

        schema_version = SchemaVersion(
            schema_version_id=str(uuid4()),
            project_id=payload.project_id,
            version_no=payload.version_no,
            notes=payload.notes,
        )
        self.schema_repository.add_schema_version(schema_version)
        self.pipeline_definition_repository.add(
            PipelineDefinition(
                pipeline_definition_id=str(uuid4()),
                schema_version_id=schema_version.schema_version_id,
                version=DEFAULT_PIPELINE_VERSION,
                description=pipeline_description,
                steps=build_default_pipeline_steps(),
            )
        )
        return self.get_schema_version(schema_version.schema_version_id)

    def apply_template_schema(
        self,
        project_id: str,
        template_schema: TemplateSchema,
    ) -> AppliedTemplateSchema:
        strategy = template_schema.segmentation_strategy
        version_numbers = [
            schema_version.version_no
            for schema_version in self.schema_repository.list_schema_versions(project_id)
        ]
        schema_version_id = self.create_schema_version(
            SchemaVersionCreateInput(
                project_id=project_id,
                version_no=max(version_numbers, default=0) + 1,
                notes="Applied from the project template.",
            ),
            pipeline_description=(
                f"Template pipeline: '{strategy}' segmentation, extraction, validation and commit."
            ),
        ).schema_version.schema_version_id
        for node_type in template_schema.node_types:
            self.add_node_type(schema_version_id, node_type)
        for relation_type in template_schema.relation_types:
            self.add_relation_type(schema_version_id, relation_type)
        return AppliedTemplateSchema(
            schema_version=self.activate_schema_version(
                project_id,
                schema_version_id,
            ).schema_version,
            pipeline_version=DEFAULT_PIPELINE_VERSION,
            segmentation_strategy=strategy,
        )

    def list_schema_versions(self, project_id: str) -> list[SchemaVersionDetail]:
        self._require_project(project_id)
        schema_versions = self.schema_repository.list_schema_versions(project_id)
        return [self._build_detail(schema_version) for schema_version in schema_versions]

    def get_schema_version(self, schema_version_id: str) -> SchemaVersionDetail:
        schema_version = self.schema_repository.get_schema_version(schema_version_id)
        if schema_version is None:
            raise NotFoundError(f"Schema version '{schema_version_id}' was not found.")
        return self._build_detail(schema_version)

    def get_active_schema(self, project_id: str) -> SchemaVersionDetail:
        self._require_project(project_id)
        schema_version = self.schema_repository.get_active_schema(project_id)
        if schema_version is None:
            raise NotFoundError(f"Project '{project_id}' does not have an active schema.")
        return self._build_detail(schema_version)

    def activate_schema_version(
        self,
        project_id: str,
        schema_version_id: str,
    ) -> SchemaVersionDetail:
        self._require_project(project_id)
        target_schema = self.schema_repository.get_schema_version(schema_version_id)
        if target_schema is None or target_schema.project_id != project_id:
            raise NotFoundError(f"Schema version '{schema_version_id}' was not found.")

        now = datetime.now(UTC)
        for schema_version in self.schema_repository.list_schema_versions(project_id):
            if schema_version.schema_version_id == schema_version_id:
                schema_version.status = SchemaStatus.ACTIVE
                schema_version.activated_at = now
                self.schema_repository.save_schema_version(schema_version)
                continue

            if schema_version.status == SchemaStatus.ACTIVE:
                schema_version.status = SchemaStatus.PUBLISHED
                self.schema_repository.save_schema_version(schema_version)

        return self.get_schema_version(schema_version_id)

    def add_node_type(
        self,
        schema_version_id: str,
        payload: NodeTypeDefinitionInput,
    ) -> SchemaVersionDetail:
        schema_version = self._require_editable_schema(schema_version_id)
        existing_names = {
            node_type.name.casefold()
            for node_type in self.schema_repository.list_node_types(schema_version_id)
        }
        if payload.name.casefold() in existing_names:
            raise ConflictError(
                f"Node type '{payload.name}' already exists in schema '{schema_version_id}'."
            )

        node_type = NodeTypeDefinition(
            node_type_id=str(uuid4()),
            schema_version_id=schema_version.schema_version_id,
            name=payload.name.strip(),
            display_name=payload.display_name.strip(),
            description=payload.description.strip(),
            is_core=payload.is_core,
            merge_keys=payload.merge_keys,
            confidence_threshold=payload.confidence_threshold,
            aliases=payload.aliases,
            extraction_hints=payload.extraction_hints,
            properties=[
                self._build_property_definition(
                    schema_version_id=schema_version.schema_version_id,
                    owner_kind="node",
                    owner_type_name=payload.name.strip(),
                    item=property_input,
                )
                for property_input in payload.properties
            ],
        )
        self.schema_repository.add_node_type(node_type)
        return self.get_schema_version(schema_version_id)

    def add_relation_type(
        self,
        schema_version_id: str,
        payload: RelationTypeDefinitionInput,
    ) -> SchemaVersionDetail:
        schema_version = self._require_editable_schema(schema_version_id)
        existing_names = {
            relation_type.name.casefold()
            for relation_type in self.schema_repository.list_relation_types(schema_version_id)
        }
        if payload.name.casefold() in existing_names:
            raise ConflictError(
                f"Relation type '{payload.name}' already exists in schema '{schema_version_id}'."
            )

        node_names = {
            node_type.name.casefold()
            for node_type in self.schema_repository.list_node_types(schema_version_id)
        }
        if (
            payload.from_type.casefold() not in node_names
            or payload.to_type.casefold() not in node_names
        ):
            raise RuleViolationError(
                "Relation types can only reference node types "
                "that already exist in the same schema version."
            )

        property_names = {property_input.name.strip() for property_input in payload.properties}
        undeclared_merge_keys = [
            merge_key for merge_key in payload.merge_keys if merge_key not in property_names
        ]
        if undeclared_merge_keys:
            raise RuleViolationError(
                f"Relation type '{payload.name}' merge keys must name properties declared "
                "on the relation type; undeclared: " + ", ".join(undeclared_merge_keys) + "."
            )

        relation_type = RelationTypeDefinition(
            relation_type_id=str(uuid4()),
            schema_version_id=schema_version.schema_version_id,
            name=payload.name.strip(),
            from_type=payload.from_type.strip(),
            to_type=payload.to_type.strip(),
            description=payload.description.strip(),
            directional=payload.directional,
            aliases=payload.aliases,
            extraction_hints=payload.extraction_hints,
            required_properties=payload.required_properties,
            merge_keys=payload.merge_keys,
            confidence_threshold=payload.confidence_threshold,
            properties=[
                self._build_property_definition(
                    schema_version_id=schema_version.schema_version_id,
                    owner_kind="relation",
                    owner_type_name=payload.name.strip(),
                    item=property_input,
                )
                for property_input in payload.properties
            ],
        )
        self.schema_repository.add_relation_type(relation_type)
        return self.get_schema_version(schema_version_id)

    def _build_detail(self, schema_version: SchemaVersion) -> SchemaVersionDetail:
        return SchemaVersionDetail(
            schema_version=schema_version,
            node_types=self.schema_repository.list_node_types(schema_version.schema_version_id),
            relation_types=self.schema_repository.list_relation_types(schema_version.schema_version_id),
        )

    def _require_project(self, project_id: str) -> None:
        if self.project_repository.get(project_id) is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")

    def _require_editable_schema(self, schema_version_id: str) -> SchemaVersion:
        schema_version = self.schema_repository.get_schema_version(schema_version_id)
        if schema_version is None:
            raise NotFoundError(f"Schema version '{schema_version_id}' was not found.")
        if schema_version.status != SchemaStatus.DRAFT:
            raise RuleViolationError("Only draft schema versions can be edited.")
        return schema_version

    def _build_property_definition(
        self,
        *,
        schema_version_id: str,
        owner_kind: str,
        owner_type_name: str,
        item: PropertyDefinitionInput,
    ) -> PropertyDefinition:
        return PropertyDefinition(
            property_id=str(uuid4()),
            owner_kind=owner_kind,
            owner_type_name=owner_type_name,
            name=item.name.strip(),
            data_type=item.data_type.strip(),
            required=item.required,
            description=item.description,
            default_value=item.default_value,
            enum_values=item.enum_values,
        )
