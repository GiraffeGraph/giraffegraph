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
