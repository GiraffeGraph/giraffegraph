from datetime import datetime

from pydantic import BaseModel


class FactEvidenceResponse(BaseModel):
    segment_id: str
    segment_order: int | None
    segment_text: str | None
    quote: str | None
    start_offset: int | None
    end_offset: int | None
    source_start_offset: int | None
    source_end_offset: int | None


class FactAcceptanceResponse(BaseModel):
    kind: str
    policy: str | None
    rule_code: str | None
    action: str | None
    reviewer_id: str | None
    decided_at: datetime | None


class ChainNarratorResponse(BaseModel):
    name: str
    evidence: list[FactEvidenceResponse]
    acceptance: FactAcceptanceResponse | None


class ChainLinkResponse(BaseModel):
    position: int
    from_narrator: str
    to_narrator: str
    sigha: str | None
    evidence: list[FactEvidenceResponse]
    acceptance: FactAcceptanceResponse | None


class NarratorChainResponse(BaseModel):
    chain_no: int
    narrators: list[str]
    links: list[ChainLinkResponse]


class CommittedRunRefResponse(BaseModel):
    run_id: str
    committed_at: datetime | None
    llm_provider: str | None
    llm_model: str | None


class HadithSourceResponse(BaseModel):
    source_unit_id: str
    title: str
    raw_content: str


class HadithChainViewResponse(BaseModel):
    project_id: str
    hadith_ref: str
    committed: bool
    source_unit: HadithSourceResponse | None
    runs: list[CommittedRunRefResponse]
    chains: list[NarratorChainResponse]
    narrators: list[ChainNarratorResponse]


class CommittedHadithResponse(BaseModel):
    hadith_ref: str
    source_unit_id: str
    title: str
    run_id: str
    committed_at: datetime | None


class CommittedHadithListResponse(BaseModel):
    project_id: str
    total_count: int
    hadiths: list[CommittedHadithResponse]


class NarratorHadithRefResponse(BaseModel):
    hadith_ref: str
    source_unit_id: str
    title: str


class NarratorNeighbourResponse(BaseModel):
    name: str
    link_count: int
    hadith_refs: list[str]


class NarratorViewResponse(BaseModel):
    project_id: str
    name: str
    hadith_count: int
    hadiths: list[NarratorHadithRefResponse]
    narrated_from_count: int
    narrated_from: list[NarratorNeighbourResponse]
    narrated_to_count: int
    narrated_to: list[NarratorNeighbourResponse]
