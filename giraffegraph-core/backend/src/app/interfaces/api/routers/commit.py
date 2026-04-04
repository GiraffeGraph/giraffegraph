from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.commit_management import CommitManagementService
from app.interfaces.api.dependencies import get_commit_management_service
from app.interfaces.api.mappers.commit import to_graph_delta_response
from app.interfaces.api.schemas.commit import GraphDeltaResponse

router = APIRouter(tags=["commit"])
CommitManagementServiceDep = Annotated[
    CommitManagementService,
    Depends(get_commit_management_service),
]


@router.post("/api/runs/{run_id}/commit", response_model=GraphDeltaResponse)
def commit_run(
    run_id: str,
    service: CommitManagementServiceDep,
) -> GraphDeltaResponse:
    return to_graph_delta_response(service.commit_run(run_id))


@router.get("/api/runs/{run_id}/graph-delta", response_model=GraphDeltaResponse)
def get_graph_delta(
    run_id: str,
    service: CommitManagementServiceDep,
) -> GraphDeltaResponse:
    return to_graph_delta_response(service.get_graph_delta(run_id))
