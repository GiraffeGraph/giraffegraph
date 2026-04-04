from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.use_cases.exploration_management import GraphExplorationService
from app.interfaces.api.dependencies import get_graph_exploration_service
from app.interfaces.api.mappers.exploration import (
    to_canonical_node_detail_response,
    to_canonical_node_response,
    to_canonical_relation_detail_response,
    to_canonical_relation_response,
    to_graph_overview_response,
)
from app.interfaces.api.schemas.exploration import (
    CanonicalNodeDetailResponse,
    CanonicalNodeResponse,
    CanonicalRelationDetailResponse,
    CanonicalRelationResponse,
    GraphOverviewResponse,
)

router = APIRouter(tags=["exploration"])
GraphExplorationServiceDep = Annotated[
    GraphExplorationService,
    Depends(get_graph_exploration_service),
]


@router.get(
    "/api/projects/{project_id}/graph/overview",
    response_model=GraphOverviewResponse,
)
def get_project_graph_overview(
    project_id: str,
    service: GraphExplorationServiceDep,
) -> GraphOverviewResponse:
    return to_graph_overview_response(service.get_project_overview(project_id))


@router.get(
    "/api/projects/{project_id}/graph/nodes",
    response_model=list[CanonicalNodeResponse],
)
def list_project_graph_nodes(
    project_id: str,
    service: GraphExplorationServiceDep,
    node_type: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CanonicalNodeResponse]:
    return [
        to_canonical_node_response(item)
        for item in service.list_nodes(project_id, node_type=node_type, limit=limit)
    ]


@router.get(
    "/api/projects/{project_id}/graph/nodes/{node_type}/{merge_key}",
    response_model=CanonicalNodeDetailResponse,
)
def get_project_graph_node_detail(
    project_id: str,
    node_type: str,
    merge_key: str,
    service: GraphExplorationServiceDep,
) -> CanonicalNodeDetailResponse:
    return to_canonical_node_detail_response(
        service.get_node_detail(
            project_id,
            node_type=node_type,
            merge_key=merge_key,
        )
    )


@router.get(
    "/api/projects/{project_id}/graph/relations",
    response_model=list[CanonicalRelationResponse],
)
def list_project_graph_relations(
    project_id: str,
    service: GraphExplorationServiceDep,
    relation_type: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CanonicalRelationResponse]:
    return [
        to_canonical_relation_response(item)
        for item in service.list_relations(
            project_id,
            relation_type=relation_type,
            limit=limit,
        )
    ]


@router.get(
    "/api/projects/{project_id}/graph/relations/{relation_type}/{from_node_type}/{from_merge_key}/{to_node_type}/{to_merge_key}",
    response_model=CanonicalRelationDetailResponse,
)
def get_project_graph_relation_detail(
    project_id: str,
    relation_type: str,
    from_node_type: str,
    from_merge_key: str,
    to_node_type: str,
    to_merge_key: str,
    service: GraphExplorationServiceDep,
) -> CanonicalRelationDetailResponse:
    return to_canonical_relation_detail_response(
        service.get_relation_detail(
            project_id,
            relation_type=relation_type,
            from_node_type=from_node_type,
            from_merge_key=from_merge_key,
            to_node_type=to_node_type,
            to_merge_key=to_merge_key,
        )
    )
