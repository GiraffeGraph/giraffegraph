from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.ingestion.entities import Segment, SourceUnit


@dataclass(slots=True, kw_only=True)
class GraphDelta:
    delta_id: str
    run_id: str
    project_id: str
    nodes_created: int = 0
    nodes_merged: int = 0
    relations_created: int = 0
    relations_merged: int = 0
    review_count: int = 0
    rejected_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True, kw_only=True)
class CanonicalCommitBundle:
    delta: GraphDelta
    source_unit: SourceUnit
    segments: list[Segment] = field(default_factory=list)
    candidate_nodes: list[CandidateNode] = field(default_factory=list)
    candidate_relations: list[CandidateRelation] = field(default_factory=list)
