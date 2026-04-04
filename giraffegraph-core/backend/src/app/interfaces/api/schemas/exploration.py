from pydantic import BaseModel, ConfigDict, Field


class NodeTypeCountResponse(BaseModel):
    node_type: str
    count: int


class GraphOverviewResponse(BaseModel):
    project_id: str
    node_count: int
    relation_count: int
    node_type_counts: list[NodeTypeCountResponse]


class CanonicalNodeResponse(BaseModel):
    project_id: str
    node_type: str
    merge_key: str
    properties: dict[str, object]
    source_unit_id: str | None
    last_run_id: str | None
    updated_at: str | None


class CanonicalRelationResponse(BaseModel):
    project_id: str
    relation_type: str
    from_node_type: str
    from_merge_key: str
    to_node_type: str
    to_merge_key: str
    properties: dict[str, object]
    source_unit_id: str | None
    last_run_id: str | None
    updated_at: str | None


class CanonicalSourceUnitRefResponse(BaseModel):
    source_unit_id: str
    title: str | None
    source_type: str | None
    sequence_no: int | None


class CanonicalSegmentSupportResponse(BaseModel):
    segment_id: str
    source_unit_id: str | None
    segment_order: int | None
    text: str


class ConnectedRelationResponse(BaseModel):
    relation_type: str
    direction: str
    other_node_type: str
    other_merge_key: str
    other_node_properties: dict[str, object]
    properties: dict[str, object]
    updated_at: str | None


class CanonicalNodeDetailResponse(BaseModel):
    node: CanonicalNodeResponse
    source_units: list[CanonicalSourceUnitRefResponse]
    supporting_segments: list[CanonicalSegmentSupportResponse]
    connected_relations: list[ConnectedRelationResponse]


class CanonicalRelationEndpointResponse(BaseModel):
    node_type: str
    merge_key: str
    properties: dict[str, object]


class CanonicalRelationDetailResponse(BaseModel):
    relation: CanonicalRelationResponse
    from_node: CanonicalRelationEndpointResponse
    to_node: CanonicalRelationEndpointResponse
    source_units: list[CanonicalSourceUnitRefResponse]
    supporting_segments: list[CanonicalSegmentSupportResponse]


class GraphListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=50, ge=1, le=200)
    node_type: str | None = Field(default=None, max_length=80)
    relation_type: str | None = Field(default=None, max_length=80)
