from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.schema.identifiers import IDENTIFIER_PATTERN
from app.domain.shared.enums import SchemaStatus


class PropertyDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120, pattern=IDENTIFIER_PATTERN.pattern)
    data_type: str = Field(min_length=1, max_length=50)
    required: bool = False
    description: str | None = Field(default=None, max_length=500)
    default_value: str | None = None
    enum_values: list[str] = Field(default_factory=list)


class SchemaVersionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_no: int = Field(ge=1)
    notes: str | None = Field(default=None, max_length=1000)


class NodeTypeDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80, pattern=IDENTIFIER_PATTERN.pattern)
    display_name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    is_core: bool = False
    merge_keys: list[str] = Field(default_factory=list)
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    aliases: list[str] = Field(default_factory=list)
    extraction_hints: list[str] = Field(default_factory=list)
    properties: list[PropertyDefinitionRequest] = Field(default_factory=list)


class RelationTypeDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80, pattern=IDENTIFIER_PATTERN.pattern)
    from_type: str = Field(min_length=1, max_length=80)
    to_type: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)
    directional: bool = True
    aliases: list[str] = Field(default_factory=list)
    extraction_hints: list[str] = Field(default_factory=list)
    required_properties: list[str] = Field(default_factory=list)
    merge_keys: list[str] = Field(default_factory=list)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    properties: list[PropertyDefinitionRequest] = Field(default_factory=list)


class PropertyDefinitionResponse(BaseModel):
    property_id: str
    owner_kind: str
    owner_type_name: str
    name: str
    data_type: str
    required: bool
    description: str | None
    default_value: str | None
    enum_values: list[str]


class NodeTypeDefinitionResponse(BaseModel):
    node_type_id: str
    schema_version_id: str
    name: str
    display_name: str
    description: str
    is_core: bool
    merge_keys: list[str]
    confidence_threshold: float
    aliases: list[str]
    extraction_hints: list[str]
    properties: list[PropertyDefinitionResponse]
    is_active: bool


class RelationTypeDefinitionResponse(BaseModel):
    relation_type_id: str
    schema_version_id: str
    name: str
    from_type: str
    to_type: str
    description: str
    directional: bool
    aliases: list[str]
    extraction_hints: list[str]
    required_properties: list[str]
    merge_keys: list[str]
    properties: list[PropertyDefinitionResponse]
    confidence_threshold: float
    is_active: bool


class SchemaVersionResponse(BaseModel):
    schema_version_id: str
    project_id: str
    version_no: int
    status: SchemaStatus
    notes: str | None
    created_at: datetime
    activated_at: datetime | None
    node_types: list[NodeTypeDefinitionResponse]
    relation_types: list[RelationTypeDefinitionResponse]
