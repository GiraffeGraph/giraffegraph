from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import CandidateStatus, ReviewStatus


class SegmentGenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy: str = Field(default="paragraphs", min_length=1, max_length=50)


class SegmentResponse(BaseModel):
    segment_id: str
    source_unit_id: str
    segment_order: int
    text: str
    metadata_json: dict[str, str]


class EvidenceRefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment_id: str
    quote: str | None = None
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)


class EvidenceRefResponse(BaseModel):
    segment_id: str
    quote: str | None
    start_offset: int | None
    end_offset: int | None


class CandidateNodeCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_type: str = Field(min_length=1, max_length=80)
    properties: dict[str, object] = Field(default_factory=dict)
    merge_key_payload: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[EvidenceRefRequest] = Field(default_factory=list)


class CandidateNodeResponse(BaseModel):
    candidate_node_id: str
    run_id: str
    node_type: str
    properties: dict[str, object]
    merge_key_payload: dict[str, object]
    confidence: float
    evidence_refs: list[EvidenceRefResponse]
    status: CandidateStatus


class CandidateRelationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation_type: str = Field(min_length=1, max_length=80)
    from_candidate_ref: str
    to_candidate_ref: str
    properties: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[EvidenceRefRequest] = Field(default_factory=list)


class CandidateRelationResponse(BaseModel):
    candidate_relation_id: str
    run_id: str
    relation_type: str
    from_candidate_ref: str
    to_candidate_ref: str
    properties: dict[str, object]
    confidence: float
    evidence_refs: list[EvidenceRefResponse]
    status: CandidateStatus


class ValidationResultResponse(BaseModel):
    validation_result_id: str
    run_id: str
    candidate_ref: str
    rule_code: str
    severity: str
    result: str
    message: str


class RunValidationResponse(BaseModel):
    run_id: str
    node_total: int
    node_validated: int
    node_review: int
    node_rejected: int
    relation_total: int
    relation_validated: int
    relation_review: int
    relation_rejected: int
    validation_results: list[ValidationResultResponse]


class ReviewItemResponse(BaseModel):
    review_item_id: str
    run_id: str
    item_type: str
    item_ref: str
    reason_code: str
    payload_json: dict[str, object]
    status: ReviewStatus
    reviewer_note: str | None
    created_at: datetime


class ReviewDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1, max_length=20)
    reviewer_note: str | None = Field(default=None, max_length=1000)
    node_type: str | None = Field(default=None, max_length=80)
    relation_type: str | None = Field(default=None, max_length=80)
    from_candidate_ref: str | None = None
    to_candidate_ref: str | None = None
    properties: dict[str, object] = Field(default_factory=dict)
    merge_key_payload: dict[str, object] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
