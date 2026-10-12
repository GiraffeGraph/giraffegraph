from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.enums import SchemaStatus


@dataclass(slots=True, kw_only=True)
class PropertyDefinition:
    property_id: str
    owner_kind: str
    owner_type_name: str
    name: str
    data_type: str
    required: bool = False
    description: str | None = None
    default_value: str | None = None
    enum_values: list[str] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class NodeTypeDefinition:
    node_type_id: str
    schema_version_id: str
    name: str
    display_name: str
    description: str
    is_core: bool = False
    merge_keys: list[str] = field(default_factory=list)
    confidence_threshold: float = 0.5
    aliases: list[str] = field(default_factory=list)
    extraction_hints: list[str] = field(default_factory=list)
    properties: list[PropertyDefinition] = field(default_factory=list)
    is_active: bool = True


@dataclass(slots=True, kw_only=True)
class RelationTypeDefinition:
    relation_type_id: str
    schema_version_id: str
    name: str
    from_type: str
    to_type: str
    description: str
    directional: bool = True
    aliases: list[str] = field(default_factory=list)
    extraction_hints: list[str] = field(default_factory=list)
    required_properties: list[str] = field(default_factory=list)
    merge_keys: list[str] = field(default_factory=list)
    properties: list[PropertyDefinition] = field(default_factory=list)
    confidence_threshold: float = 0.7
    is_active: bool = True


@dataclass(slots=True, kw_only=True)
class SchemaVersion:
    schema_version_id: str
    project_id: str
    version_no: int
    status: SchemaStatus = SchemaStatus.DRAFT
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    activated_at: datetime | None = None
