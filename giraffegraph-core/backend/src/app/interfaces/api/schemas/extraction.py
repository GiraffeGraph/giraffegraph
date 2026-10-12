from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.interfaces.api.schemas.pipeline import EvidenceRefResponse


class ExtractionExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = False


class SuggestedNodeResponse(BaseModel):
    ref: str
    node_type: str
    properties: dict[str, object]
    merge_key_payload: dict[str, object]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[EvidenceRefResponse]


class SuggestedRelationResponse(BaseModel):
    relation_type: str
    from_ref: str
    to_ref: str
    properties: dict[str, object]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[EvidenceRefResponse]


class FailedExtractionCallResponse(BaseModel):
    segment_ids: list[str]
    error_message: str


class SchemaProposalResponse(BaseModel):
    reason_code: str
    kind: str
    type_name: str
    property_name: str | None
    count: int
    sample_quote: str | None
    sample_value: object | None
    dropped_relation_count: int


class ExtractionExecutionResponse(BaseModel):
    execution_id: str
    run_id: str
    dry_run: bool
    prompt_version: str
    schema_name: str
    provider_name: str
    requested_llm_provider: str | None
    requested_llm_model: str | None
    resolved_llm_model: str | None
    segment_count: int
    suggested_nodes: list[SuggestedNodeResponse]
    suggested_relations: list[SuggestedRelationResponse]
    created_candidate_node_ids: list[str]
    created_candidate_relation_ids: list[str]
    call_count: int
    failed_calls: list[FailedExtractionCallResponse]
    dropped_node_count: int
    dropped_relation_count: int
    schema_proposals: list[SchemaProposalResponse]
    started_at: datetime
    completed_at: datetime


class ExtractionExecutionAuditResponse(BaseModel):
    execution_id: str
    run_id: str
    dry_run: bool
    status: str
    prompt_key: str
    prompt_version: str | None
    schema_name: str | None
    provider_name: str | None
    requested_llm_provider: str | None
    requested_llm_model: str | None
    resolved_llm_model: str | None
    segment_count: int
    suggested_node_count: int
    suggested_relation_count: int
    created_candidate_node_count: int
    created_candidate_relation_count: int
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None
