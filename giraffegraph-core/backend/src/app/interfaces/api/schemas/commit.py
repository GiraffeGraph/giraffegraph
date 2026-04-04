from datetime import datetime

from pydantic import BaseModel


class GraphDeltaResponse(BaseModel):
    delta_id: str
    run_id: str
    project_id: str
    nodes_created: int
    nodes_merged: int
    relations_created: int
    relations_merged: int
    review_count: int
    rejected_count: int
    created_at: datetime
