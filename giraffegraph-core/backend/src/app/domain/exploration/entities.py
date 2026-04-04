from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class NodeTypeCount:
    node_type: str
    count: int


@dataclass(slots=True, kw_only=True)
class GraphOverview:
    project_id: str
    node_count: int = 0
    relation_count: int = 0
    node_type_counts: list[NodeTypeCount] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class CanonicalNodeView:
    project_id: str
    node_type: str
    merge_key: str
    properties: dict[str, object] = field(default_factory=dict)
    source_unit_id: str | None = None
    last_run_id: str | None = None
    updated_at: str | None = None


@dataclass(slots=True, kw_only=True)
class CanonicalRelationView:
    project_id: str
    relation_type: str
    from_node_type: str
    from_merge_key: str
    to_node_type: str
    to_merge_key: str
    properties: dict[str, object] = field(default_factory=dict)
    source_unit_id: str | None = None
    last_run_id: str | None = None
    updated_at: str | None = None


@dataclass(slots=True, kw_only=True)
class CanonicalSourceUnitRef:
    source_unit_id: str
    title: str | None = None
    source_type: str | None = None
    sequence_no: int | None = None


@dataclass(slots=True, kw_only=True)
class CanonicalSegmentSupport:
    segment_id: str
    source_unit_id: str | None = None
    segment_order: int | None = None
    text: str = ""


@dataclass(slots=True, kw_only=True)
class ConnectedRelationView:
    relation_type: str
    direction: str
    other_node_type: str
    other_merge_key: str
    other_node_properties: dict[str, object] = field(default_factory=dict)
    properties: dict[str, object] = field(default_factory=dict)
    updated_at: str | None = None


@dataclass(slots=True, kw_only=True)
class CanonicalNodeDetail:
    node: CanonicalNodeView
    source_units: list[CanonicalSourceUnitRef] = field(default_factory=list)
    supporting_segments: list[CanonicalSegmentSupport] = field(default_factory=list)
    connected_relations: list[ConnectedRelationView] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class CanonicalRelationEndpointView:
    node_type: str
    merge_key: str
    properties: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True, kw_only=True)
class CanonicalRelationDetail:
    relation: CanonicalRelationView
    from_node: CanonicalRelationEndpointView
    to_node: CanonicalRelationEndpointView
    source_units: list[CanonicalSourceUnitRef] = field(default_factory=list)
    supporting_segments: list[CanonicalSegmentSupport] = field(default_factory=list)
