from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.use_cases.exploration_management import (
    ChainExplorationService,
    GraphExplorationService,
)
from app.application.use_cases.ingestion_management import IngestionManagementService
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.application.use_cases.review_management import ReviewManagementService
from app.interfaces.api.dependencies import (
    get_graph_exploration_service,
    get_ingestion_management_service,
    get_pipeline_management_service,
    get_review_management_service,
)
from app.interfaces.api.mappers.chains import (
    to_committed_hadith_list_response,
    to_hadith_chain_view_response,
    to_narrator_view_response,
)
from app.interfaces.api.schemas.chains import (
    CommittedHadithListResponse,
    HadithChainViewResponse,
    NarratorViewResponse,
)

router = APIRouter(prefix="/api/projects/{project_id}/chains", tags=["chains"])


def get_chain_exploration_service(
    ingestion_management_service: Annotated[
        IngestionManagementService,
        Depends(get_ingestion_management_service),
    ],
    pipeline_management_service: Annotated[
        PipelineManagementService,
        Depends(get_pipeline_management_service),
    ],
    review_management_service: Annotated[
        ReviewManagementService,
        Depends(get_review_management_service),
    ],
    graph_exploration_service: Annotated[
        GraphExplorationService,
        Depends(get_graph_exploration_service),
    ],
) -> ChainExplorationService:
    return ChainExplorationService(
        ingestion_management_service=ingestion_management_service,
        pipeline_management_service=pipeline_management_service,
        review_management_service=review_management_service,
        graph_exploration_service=graph_exploration_service,
    )


ChainExplorationServiceDep = Annotated[
    ChainExplorationService,
    Depends(get_chain_exploration_service),
]


@router.get("", response_model=CommittedHadithListResponse)
def list_committed_hadiths(
    project_id: str,
    service: ChainExplorationServiceDep,
    q: str | None = Query(default=None, max_length=200),
) -> CommittedHadithListResponse:
    return to_committed_hadith_list_response(
        project_id,
        service.list_committed_hadiths(project_id, query=q),
    )


@router.get("/hadith", response_model=HadithChainViewResponse)
def get_hadith_chains(
    project_id: str,
    service: ChainExplorationServiceDep,
    hadith_ref: str = Query(min_length=1, max_length=200),
) -> HadithChainViewResponse:
    return to_hadith_chain_view_response(service.get_hadith_chains(project_id, hadith_ref))


@router.get("/narrator", response_model=NarratorViewResponse)
def get_narrator(
    project_id: str,
    service: ChainExplorationServiceDep,
    name: str = Query(min_length=1, max_length=500),
) -> NarratorViewResponse:
    return to_narrator_view_response(service.get_narrator(project_id, name))
