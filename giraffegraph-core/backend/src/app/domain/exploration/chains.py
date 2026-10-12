from dataclasses import dataclass, field
from datetime import datetime

from app.domain.extraction.entities import EvidenceRef
from app.domain.ingestion.entities import Segment

NARRATOR_NODE_TYPE = "Narrator"
NARRATED_FROM_RELATION_TYPE = "NARRATED_FROM"
HUMAN_ACCEPTANCE = "human"
POLICY_ACCEPTANCE = "policy"


@dataclass(slots=True, kw_only=True)
class FactEvidence:
    segment_id: str
    segment_order: int | None = None
    segment_text: str | None = None
    quote: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    source_start_offset: int | None = None
    source_end_offset: int | None = None


@dataclass(slots=True, kw_only=True)
class FactAcceptance:
    kind: str
    policy: str | None = None
    rule_code: str | None = None
    action: str | None = None
    reviewer_id: str | None = None
    decided_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class ChainNarrator:
    name: str
    evidence: list[FactEvidence] = field(default_factory=list)
    acceptance: FactAcceptance | None = None


@dataclass(slots=True, kw_only=True)
class ChainLink:
    position: int
    from_narrator: str
    to_narrator: str
    sigha: str | None = None
    evidence: list[FactEvidence] = field(default_factory=list)
    acceptance: FactAcceptance | None = None


@dataclass(slots=True, kw_only=True)
class NarratorChain:
    chain_no: int
    links: list[ChainLink] = field(default_factory=list)

    @property
    def narrators(self) -> list[str]:
        names: list[str] = []
        for link in self.links:
            if not names or names[-1] != link.from_narrator:
                names.append(link.from_narrator)
            names.append(link.to_narrator)
        return names


@dataclass(slots=True, kw_only=True)
class CommittedRunRef:
    run_id: str
    committed_at: datetime | None = None
    llm_provider: str | None = None
    llm_model: str | None = None


@dataclass(slots=True, kw_only=True)
class HadithSource:
    source_unit_id: str
    title: str
    raw_content: str


@dataclass(slots=True, kw_only=True)
class HadithChainView:
    project_id: str
    hadith_ref: str
    source: HadithSource | None = None
    runs: list[CommittedRunRef] = field(default_factory=list)
    chains: list[NarratorChain] = field(default_factory=list)
    narrators: list[ChainNarrator] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class CommittedHadith:
    hadith_ref: str
    source_unit_id: str
    title: str
    run_id: str
    committed_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class NarratorHadithRef:
    hadith_ref: str
    source_unit_id: str
    title: str


@dataclass(slots=True, kw_only=True)
class NarratorNeighbour:
    name: str
    link_count: int = 0
    hadith_refs: list[str] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class NarratorView:
    project_id: str
    name: str
    hadiths: list[NarratorHadithRef] = field(default_factory=list)
    narrated_from: list[NarratorNeighbour] = field(default_factory=list)
    narrated_to: list[NarratorNeighbour] = field(default_factory=list)


def locate_evidence(
    evidence_ref: EvidenceRef,
    *,
    segment: Segment | None,
    raw_content: str,
) -> FactEvidence:
    evidence = FactEvidence(
        segment_id=evidence_ref.segment_id,
        quote=evidence_ref.quote,
        start_offset=evidence_ref.start_offset,
        end_offset=evidence_ref.end_offset,
    )
    if segment is None:
        return evidence
    evidence.segment_order = segment.segment_order
    evidence.segment_text = segment.text

    span = _span_in_segment(evidence_ref, segment.text)
    segment_start = _segment_start(segment, raw_content)
    if span is not None and segment_start is not None:
        evidence.source_start_offset = segment_start + span[0]
        evidence.source_end_offset = segment_start + span[1]
    return evidence


def _span_in_segment(evidence_ref: EvidenceRef, segment_text: str) -> tuple[int, int] | None:
    start, end, quote = evidence_ref.start_offset, evidence_ref.end_offset, evidence_ref.quote
    if start is not None and end is not None and start < end <= len(segment_text):
        if quote is None or segment_text[start:end] == quote:
            return start, end
    if quote:
        found = segment_text.find(quote)
        if found >= 0:
            return found, found + len(quote)
    return None


def _segment_start(segment: Segment, raw_content: str) -> int | None:
    stored = segment.metadata_json.get("start_offset", "")
    if stored.isdecimal() and raw_content.startswith(segment.text, int(stored)):
        return int(stored)
    found = raw_content.find(segment.text)
    return found if found >= 0 else None
