from app.domain.exploration.entities import (
    CanonicalNodeDetail,
    CanonicalNodeView,
    CanonicalRelationDetail,
    CanonicalRelationEndpointView,
    CanonicalRelationView,
    CanonicalSegmentSupport,
    CanonicalSourceUnitRef,
    ConnectedRelationView,
    GraphOverview,
    NodeTypeCount,
)
from app.interfaces.api.schemas.exploration import (
    CanonicalNodeDetailResponse,
    CanonicalNodeResponse,
    CanonicalRelationDetailResponse,
    CanonicalRelationEndpointResponse,
    CanonicalRelationResponse,
    CanonicalSegmentSupportResponse,
    CanonicalSourceUnitRefResponse,
    ConnectedRelationResponse,
    GraphOverviewResponse,
    NodeTypeCountResponse,
)


def to_graph_overview_response(overview: GraphOverview) -> GraphOverviewResponse:
    return GraphOverviewResponse(
        project_id=overview.project_id,
        node_count=overview.node_count,
        relation_count=overview.relation_count,
        node_type_counts=[
            to_node_type_count_response(item) for item in overview.node_type_counts
        ],
    )


def to_node_type_count_response(item: NodeTypeCount) -> NodeTypeCountResponse:
    return NodeTypeCountResponse(
        node_type=item.node_type,
        count=item.count,
    )


def to_canonical_node_response(node: CanonicalNodeView) -> CanonicalNodeResponse:
    return CanonicalNodeResponse(
        project_id=node.project_id,
        node_type=node.node_type,
        merge_key=node.merge_key,
        properties=node.properties,
        source_unit_id=node.source_unit_id,
        last_run_id=node.last_run_id,
        updated_at=node.updated_at,
    )


def to_canonical_relation_response(
    relation: CanonicalRelationView,
) -> CanonicalRelationResponse:
    return CanonicalRelationResponse(
        project_id=relation.project_id,
        relation_type=relation.relation_type,
        from_node_type=relation.from_node_type,
        from_merge_key=relation.from_merge_key,
        to_node_type=relation.to_node_type,
        to_merge_key=relation.to_merge_key,
        properties=relation.properties,
        source_unit_id=relation.source_unit_id,
        last_run_id=relation.last_run_id,
        updated_at=relation.updated_at,
    )


def to_canonical_source_unit_ref_response(
    item: CanonicalSourceUnitRef,
) -> CanonicalSourceUnitRefResponse:
    return CanonicalSourceUnitRefResponse(
        source_unit_id=item.source_unit_id,
        title=item.title,
        source_type=item.source_type,
        sequence_no=item.sequence_no,
    )


def to_canonical_segment_support_response(
    item: CanonicalSegmentSupport,
) -> CanonicalSegmentSupportResponse:
    return CanonicalSegmentSupportResponse(
        segment_id=item.segment_id,
        source_unit_id=item.source_unit_id,
        segment_order=item.segment_order,
        text=item.text,
    )


def to_connected_relation_response(
    item: ConnectedRelationView,
) -> ConnectedRelationResponse:
    return ConnectedRelationResponse(
        relation_type=item.relation_type,
        direction=item.direction,
        other_node_type=item.other_node_type,
        other_merge_key=item.other_merge_key,
        other_node_properties=item.other_node_properties,
        properties=item.properties,
        updated_at=item.updated_at,
    )


def to_canonical_node_detail_response(
    detail: CanonicalNodeDetail,
) -> CanonicalNodeDetailResponse:
    return CanonicalNodeDetailResponse(
        node=to_canonical_node_response(detail.node),
        source_units=[
            to_canonical_source_unit_ref_response(item) for item in detail.source_units
        ],
        supporting_segments=[
            to_canonical_segment_support_response(item)
            for item in detail.supporting_segments
        ],
        connected_relations=[
            to_connected_relation_response(item) for item in detail.connected_relations
        ],
    )


def to_canonical_relation_endpoint_response(
    endpoint: CanonicalRelationEndpointView,
) -> CanonicalRelationEndpointResponse:
    return CanonicalRelationEndpointResponse(
        node_type=endpoint.node_type,
        merge_key=endpoint.merge_key,
        properties=endpoint.properties,
    )


def to_canonical_relation_detail_response(
    detail: CanonicalRelationDetail,
) -> CanonicalRelationDetailResponse:
    return CanonicalRelationDetailResponse(
        relation=to_canonical_relation_response(detail.relation),
        from_node=to_canonical_relation_endpoint_response(detail.from_node),
        to_node=to_canonical_relation_endpoint_response(detail.to_node),
        source_units=[
            to_canonical_source_unit_ref_response(item) for item in detail.source_units
        ],
        supporting_segments=[
            to_canonical_segment_support_response(item)
            for item in detail.supporting_segments
        ],
    )
