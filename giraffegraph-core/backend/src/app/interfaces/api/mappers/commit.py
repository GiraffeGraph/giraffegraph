from app.domain.graph_commit.entities import GraphDelta
from app.interfaces.api.schemas.commit import GraphDeltaResponse


def to_graph_delta_response(delta: GraphDelta) -> GraphDeltaResponse:
    return GraphDeltaResponse(
        delta_id=delta.delta_id,
        run_id=delta.run_id,
        project_id=delta.project_id,
        nodes_created=delta.nodes_created,
        nodes_merged=delta.nodes_merged,
        relations_created=delta.relations_created,
        relations_merged=delta.relations_merged,
        review_count=delta.review_count,
        rejected_count=delta.rejected_count,
        created_at=delta.created_at,
    )
