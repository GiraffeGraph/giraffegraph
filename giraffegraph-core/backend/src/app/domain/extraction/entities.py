from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.enums import CandidateStatus, ExtractionExecutionStatus


@dataclass(slots=True, kw_only=True)
class EvidenceRef:
    segment_id: str
    quote: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None


@dataclass(slots=True, kw_only=True)
class CandidateNode:
    candidate_node_id: str
    run_id: str
    node_type: str
    properties: dict[str, object] = field(default_factory=dict)
    merge_key_payload: dict[str, object] = field(default_factory=dict)
    confidence: float = 0.0
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    status: CandidateStatus = CandidateStatus.PENDING


@dataclass(slots=True, kw_only=True)
class CandidateRelation:
    candidate_relation_id: str
    run_id: str
    relation_type: str
    from_candidate_ref: str
    to_candidate_ref: str
    properties: dict[str, object] = field(default_factory=dict)
    confidence: float = 0.0
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    status: CandidateStatus = CandidateStatus.PENDING


@dataclass(slots=True, kw_only=True)
class SuggestedNode:
    ref: str
    node_type: str
    properties: dict[str, object] = field(default_factory=dict)
    merge_key_payload: dict[str, object] = field(default_factory=dict)
    confidence: float = 0.0
    evidence_refs: list[EvidenceRef] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class SuggestedRelation:
    relation_type: str
    from_ref: str
    to_ref: str
    properties: dict[str, object] = field(default_factory=dict)
    confidence: float = 0.0
    evidence_refs: list[EvidenceRef] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class ExtractionExecutionReport:
    execution_id: str
    run_id: str
    dry_run: bool
    prompt_version: str
    schema_name: str
    provider_name: str
    requested_llm_provider: str | None = None
    requested_llm_model: str | None = None
    resolved_llm_model: str | None = None
    segment_count: int = 0
    suggested_nodes: list[SuggestedNode] = field(default_factory=list)
    suggested_relations: list[SuggestedRelation] = field(default_factory=list)
    created_candidate_node_ids: list[str] = field(default_factory=list)
    created_candidate_relation_ids: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True, kw_only=True)
class ExtractionExecution:
    execution_id: str
    run_id: str
    dry_run: bool
    status: ExtractionExecutionStatus
    prompt_key: str
    prompt_version: str | None = None
    schema_name: str | None = None
    provider_name: str | None = None
    requested_llm_provider: str | None = None
    requested_llm_model: str | None = None
    resolved_llm_model: str | None = None
    segment_count: int = 0
    suggested_node_count: int = 0
    suggested_relation_count: int = 0
    created_candidate_node_count: int = 0
    created_candidate_relation_count: int = 0
    error_message: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
