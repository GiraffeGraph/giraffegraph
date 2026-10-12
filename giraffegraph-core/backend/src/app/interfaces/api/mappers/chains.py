from app.domain.exploration.chains import (
    ChainLink,
    ChainNarrator,
    CommittedHadith,
    FactAcceptance,
    FactEvidence,
    HadithChainView,
    NarratorNeighbour,
    NarratorView,
)
from app.interfaces.api.schemas.chains import (
    ChainLinkResponse,
    ChainNarratorResponse,
    CommittedHadithListResponse,
    CommittedHadithResponse,
    CommittedRunRefResponse,
    FactAcceptanceResponse,
    FactEvidenceResponse,
    HadithChainViewResponse,
    HadithSourceResponse,
    NarratorChainResponse,
    NarratorHadithRefResponse,
    NarratorNeighbourResponse,
    NarratorViewResponse,
)


def to_committed_hadith_list_response(
    project_id: str,
    hadiths: list[CommittedHadith],
) -> CommittedHadithListResponse:
    return CommittedHadithListResponse(
        project_id=project_id,
        total_count=len(hadiths),
        hadiths=[
            CommittedHadithResponse(
                hadith_ref=item.hadith_ref,
                source_unit_id=item.source_unit_id,
                title=item.title,
                run_id=item.run_id,
                committed_at=item.committed_at,
            )
            for item in hadiths
        ],
    )


def to_hadith_chain_view_response(view: HadithChainView) -> HadithChainViewResponse:
    return HadithChainViewResponse(
        project_id=view.project_id,
        hadith_ref=view.hadith_ref,
        committed=bool(view.runs),
        source_unit=(
            HadithSourceResponse(
                source_unit_id=view.source.source_unit_id,
                title=view.source.title,
                raw_content=view.source.raw_content,
            )
            if view.source is not None
            else None
        ),
        runs=[
            CommittedRunRefResponse(
                run_id=run.run_id,
                committed_at=run.committed_at,
                llm_provider=run.llm_provider,
                llm_model=run.llm_model,
            )
            for run in view.runs
        ],
        chains=[
            NarratorChainResponse(
                chain_no=chain.chain_no,
                narrators=chain.narrators,
                links=[_to_chain_link_response(link) for link in chain.links],
            )
            for chain in view.chains
        ],
        narrators=[_to_chain_narrator_response(narrator) for narrator in view.narrators],
    )


def to_narrator_view_response(view: NarratorView) -> NarratorViewResponse:
    return NarratorViewResponse(
        project_id=view.project_id,
        name=view.name,
        hadith_count=len(view.hadiths),
        hadiths=[
            NarratorHadithRefResponse(
                hadith_ref=item.hadith_ref,
                source_unit_id=item.source_unit_id,
                title=item.title,
            )
            for item in view.hadiths
        ],
        narrated_from_count=len(view.narrated_from),
        narrated_from=[_to_neighbour_response(item) for item in view.narrated_from],
        narrated_to_count=len(view.narrated_to),
        narrated_to=[_to_neighbour_response(item) for item in view.narrated_to],
    )


def _to_neighbour_response(neighbour: NarratorNeighbour) -> NarratorNeighbourResponse:
    return NarratorNeighbourResponse(
        name=neighbour.name,
        link_count=neighbour.link_count,
        hadith_refs=neighbour.hadith_refs,
    )


def _to_chain_narrator_response(narrator: ChainNarrator) -> ChainNarratorResponse:
    return ChainNarratorResponse(
        name=narrator.name,
        evidence=[_to_evidence_response(item) for item in narrator.evidence],
        acceptance=_to_acceptance_response(narrator.acceptance),
    )


def _to_chain_link_response(link: ChainLink) -> ChainLinkResponse:
    return ChainLinkResponse(
        position=link.position,
        from_narrator=link.from_narrator,
        to_narrator=link.to_narrator,
        sigha=link.sigha,
        evidence=[_to_evidence_response(item) for item in link.evidence],
        acceptance=_to_acceptance_response(link.acceptance),
    )


def _to_evidence_response(evidence: FactEvidence) -> FactEvidenceResponse:
    return FactEvidenceResponse(
        segment_id=evidence.segment_id,
        segment_order=evidence.segment_order,
        segment_text=evidence.segment_text,
        quote=evidence.quote,
        start_offset=evidence.start_offset,
        end_offset=evidence.end_offset,
        source_start_offset=evidence.source_start_offset,
        source_end_offset=evidence.source_end_offset,
    )


def _to_acceptance_response(acceptance: FactAcceptance | None) -> FactAcceptanceResponse | None:
    if acceptance is None:
        return None
    return FactAcceptanceResponse(
        kind=acceptance.kind,
        policy=acceptance.policy,
        rule_code=acceptance.rule_code,
        action=acceptance.action,
        reviewer_id=acceptance.reviewer_id,
        decided_at=acceptance.decided_at,
    )
