"""Steps shared by the isnad runners: drive the service layer and build the exports.

Each hadith is one source unit with its own processing run. No review decision is
made; runs the commit service accepts are committed, the others stay uncommitted.
Everything runs on the in-memory repository backend.
"""

import json
import os
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.application.dto.contracts import (
    ExtractionExecutionInput,
    NodeTypeDefinitionInput,
    ProcessingRunStartInput,
    ProjectCreateInput,
    RelationTypeDefinitionInput,
    SchemaVersionCreateInput,
    SegmentGenerationInput,
    SourceUnitCreateInput,
)
from app.application.errors import ApplicationError, RuleViolationError
from app.application.use_cases.review_management import AUTO_VALIDATED_POLICY
from app.bootstrap.container import ApplicationContainer, get_container
from app.domain.extraction.entities import EvidenceRef, FailedExtractionCall
from app.domain.graph_commit.entities import GraphDelta
from app.domain.hadith.grounding import normalize_for_grounding
from app.domain.hadith.normalization import normalize_arabic
from app.domain.ingestion.entities import Segment
from app.domain.orchestration.pipeline_definitions import DEFAULT_PIPELINE_VERSION
from app.domain.shared.enums import CandidateStatus, ReviewStatus
from app.infrastructure.config.settings import get_settings
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_ID

NARRATOR_NODE_TYPE = "Narrator"


@dataclass(slots=True, kw_only=True)
class HadithRun:
    hadith_id: str
    run_id: str
    segments: list[Segment]
    call_count: int = 0
    failed_calls: list[FailedExtractionCall] | None = None
    extraction_error: str | None = None
    delta: GraphDelta | None = None
    blocking_reason: str | None = None

    @property
    def failed_call_count(self) -> int:
        return len(self.failed_calls or [])


@dataclass(slots=True, kw_only=True)
class PipelineResult:
    container: ApplicationContainer
    project_id: str
    runs: list[HadithRun]


@dataclass(frozen=True, slots=True, kw_only=True)
class NarratorOccurrence:
    candidate_node_id: str
    name: str
    quote: str


MentionText = Callable[[NarratorOccurrence], str]


def quote_mention(occurrence: NarratorOccurrence) -> str:
    return occurrence.quote


def name_mention(occurrence: NarratorOccurrence) -> str:
    return occurrence.name or occurrence.quote


def load_hadiths(path: Path, limit: int | None) -> list[tuple[str, str]]:
    with path.open(encoding="utf-8") as handle:
        rows = json.load(handle)
    hadiths = [(f"{row['coll']}:{row['num']}", str(row["raw"])) for row in rows[:limit]]
    hadith_ids = [hadith_id for hadith_id, _ in hadiths]
    duplicates = sorted({item for item in hadith_ids if hadith_ids.count(item) > 1})
    if duplicates:
        raise ValueError(f"duplicate hadith id: {', '.join(duplicates)}")
    return hadiths


def create_memory_container() -> ApplicationContainer:
    os.environ["REPOSITORY_BACKEND"] = "memory"
    get_settings.cache_clear()
    get_container.cache_clear()
    return get_container()


def create_project(
    container: ApplicationContainer,
    *,
    name: str,
    node_types: Sequence[NodeTypeDefinitionInput],
    relation_types: Sequence[RelationTypeDefinitionInput],
) -> tuple[str, str]:
    project_id = container.project_management_service.create_project(
        ProjectCreateInput(name=name, template_id=ISNAD_TEMPLATE_ID)
    ).project_id
    schema_id = container.schema_management_service.create_schema_version(
        SchemaVersionCreateInput(project_id=project_id, version_no=1)
    ).schema_version.schema_version_id
    for node_type in node_types:
        container.schema_management_service.add_node_type(schema_id, node_type)
    for relation_type in relation_types:
        container.schema_management_service.add_relation_type(schema_id, relation_type)
    container.schema_management_service.activate_schema_version(project_id, schema_id)
    return project_id, schema_id


def prepare_run(
    container: ApplicationContainer,
    *,
    project_id: str,
    schema_id: str,
    hadith_id: str,
    raw: str,
    provider_name: str,
    model: str | None,
    strategy: str,
) -> HadithRun:
    source_unit_id = container.ingestion_management_service.create_source_unit(
        SourceUnitCreateInput(
            project_id=project_id,
            schema_version_id=schema_id,
            source_type="hadith",
            title=hadith_id,
            raw_content=raw,
            external_ref=hadith_id,
        )
    ).source_unit_id
    run_id = container.ingestion_management_service.start_processing_run(
        ProcessingRunStartInput(
            schema_version_id=schema_id,
            source_unit_id=source_unit_id,
            pipeline_version=DEFAULT_PIPELINE_VERSION,
            llm_provider=provider_name,
            llm_model=model,
        )
    ).run_id
    return HadithRun(
        hadith_id=hadith_id,
        run_id=run_id,
        segments=container.pipeline_management_service.generate_segments(
            SegmentGenerationInput(source_unit_id=source_unit_id, strategy=strategy)
        ),
    )


def extract(container: ApplicationContainer, hadith_run: HadithRun) -> None:
    try:
        extraction = container.extraction_management_service.extract_candidates(
            hadith_run.run_id,
            ExtractionExecutionInput(),
        )
    except ApplicationError as exc:
        hadith_run.extraction_error = str(exc)
        hadith_run.blocking_reason = f"Extraction failed: {exc}"
        return
    hadith_run.call_count = extraction.call_count
    hadith_run.failed_calls = extraction.failed_calls


def validate_and_commit(container: ApplicationContainer, hadith_run: HadithRun) -> None:
    if hadith_run.extraction_error is not None:
        return
    container.pipeline_management_service.validate_run(hadith_run.run_id)
    try:
        hadith_run.delta = container.commit_management_service.commit_run(hadith_run.run_id)
    except RuleViolationError as exc:
        hadith_run.blocking_reason = str(exc)


def narrator_occurrences(
    result: PipelineResult,
    hadith_run: HadithRun,
    *,
    validated_only: bool,
) -> list[NarratorOccurrence]:
    """Narrator mentions of a run in the order they occur in the text."""
    segments = {segment.segment_id: segment for segment in hadith_run.segments}
    candidate_nodes = result.container.pipeline_management_service.list_candidate_nodes(
        hadith_run.run_id
    )
    search_from: dict[tuple[str, str], int] = {}
    keyed: list[tuple[tuple[int, int, int], NarratorOccurrence]] = []
    for node in candidate_nodes:
        if node.node_type != NARRATOR_NODE_TYPE:
            continue
        if validated_only and node.status != CandidateStatus.VALIDATED:
            continue
        name = node.properties.get("name")
        name = name if isinstance(name, str) else ""
        for evidence in node.evidence_refs:
            if not evidence.quote:
                continue
            segment = segments[evidence.segment_id]
            position = evidence.start_offset
            if position is None:
                position = _locate(segment, evidence.quote, name, search_from)
            keyed.append(
                (
                    (segment.segment_order, position, len(keyed)),
                    NarratorOccurrence(
                        candidate_node_id=node.candidate_node_id,
                        name=name,
                        quote=evidence.quote,
                    ),
                )
            )
    return [occurrence for _, occurrence in sorted(keyed, key=lambda item: item[0])]


def _locate(
    segment: Segment,
    quote: str,
    name: str,
    search_from: dict[tuple[str, str], int],
) -> int:
    # Quotes are matched the way the grounding gate matches them; positions in the
    # normalised text keep the order of the original text.
    text = normalize_for_grounding(segment.text)
    normalized_quote = normalize_for_grounding(quote)
    normalized_name = normalize_for_grounding(name)
    if normalized_quote:
        # The same quote cited again points at its next occurrence in the segment.
        key = (segment.segment_id, normalized_quote)
        start = text.find(normalized_quote, search_from.get(key, 0))
        if start < 0:
            start = text.find(normalized_quote)
        if start >= 0:
            search_from[key] = start + 1
            return start + max(normalized_quote.find(normalized_name), 0)
    name_start = text.find(normalized_name) if normalized_name else -1
    return name_start if name_start >= 0 else len(text)


def exact_quote_in_segment(quote: str, segment_text: str) -> bool:
    return quote in segment_text


def check_committed_facts(
    result: PipelineResult,
    *,
    quote_in_segment: Callable[[str, str], bool] = exact_quote_in_segment,
) -> dict[str, Any]:
    pipeline = result.container.pipeline_management_service
    facts_checked = {"nodes": 0, "relations": 0}
    acceptance: Counter[str] = Counter()
    without_quote: list[dict[str, str]] = []
    without_acceptance: list[dict[str, str]] = []
    for hadith_run in result.runs:
        if hadith_run.delta is None:
            continue
        run_id = hadith_run.run_id
        segment_texts = {segment.segment_id: segment.text for segment in hadith_run.segments}
        accepted_by = {
            record.candidate_ref: (
                "human_decision" if record.decision is not None else AUTO_VALIDATED_POLICY
            )
            for record in result.container.review_management_service.list_acceptance_records(
                run_id,
                validation_results=pipeline.list_validation_results(run_id),
            )
            if record.decision is not None or record.policy == AUTO_VALIDATED_POLICY
        }
        facts: list[tuple[str, str, list[EvidenceRef]]] = [
            ("nodes", node.candidate_node_id, node.evidence_refs)
            for node in pipeline.list_candidate_nodes(run_id)
            if node.status == CandidateStatus.VALIDATED
        ] + [
            ("relations", relation.candidate_relation_id, relation.evidence_refs)
            for relation in pipeline.list_candidate_relations(run_id)
            if relation.status == CandidateStatus.VALIDATED
        ]
        for kind, candidate_ref, evidence_refs in facts:
            facts_checked[kind] += 1
            fact = {"hadith_id": hadith_run.hadith_id, "candidate_ref": candidate_ref}
            if not any(
                evidence_ref.quote
                and quote_in_segment(
                    evidence_ref.quote,
                    segment_texts.get(evidence_ref.segment_id, ""),
                )
                for evidence_ref in evidence_refs
            ):
                without_quote.append(fact)
            if candidate_ref in accepted_by:
                acceptance[accepted_by[candidate_ref]] += 1
            else:
                without_acceptance.append(fact)
    return {
        "facts_checked": facts_checked,
        "acceptance_records": dict(sorted(acceptance.items())),
        "without_quote_in_source_segment": without_quote,
        "without_acceptance_record": without_acceptance,
        "holds": not without_quote and not without_acceptance,
    }


def build_report(
    result: PipelineResult,
    *,
    provider_name: str,
    strategy: str,
    mention_text: MentionText,
) -> dict[str, Any]:
    pipeline = result.container.pipeline_management_service
    node_statuses: Counter[str] = Counter()
    relation_statuses: Counter[str] = Counter()
    review_reasons: Counter[str] = Counter()
    for hadith_run in result.runs:
        node_statuses.update(
            node.status.value for node in pipeline.list_candidate_nodes(hadith_run.run_id)
        )
        relation_statuses.update(
            relation.status.value
            for relation in pipeline.list_candidate_relations(hadith_run.run_id)
        )
        review_reasons.update(
            item.reason_code
            for item in pipeline.list_review_items(hadith_run.run_id)
            if item.status == ReviewStatus.OPEN
        )

    def mentions(hadith_run: HadithRun, *, validated_only: bool) -> list[str]:
        return [
            mention_text(occurrence)
            for occurrence in narrator_occurrences(
                result,
                hadith_run,
                validated_only=validated_only,
            )
        ]

    committed = [hadith_run for hadith_run in result.runs if hadith_run.delta is not None]
    blocked = [hadith_run for hadith_run in result.runs if hadith_run.delta is None]
    deltas = [hadith_run.delta for hadith_run in committed if hadith_run.delta is not None]
    committed_mentions = [
        mention
        for hadith_run in committed
        for mention in mentions(hadith_run, validated_only=True)
    ]
    overview = result.container.graph_exploration_service.get_project_overview(result.project_id)
    node_type_counts = {item.node_type: item.count for item in overview.node_type_counts}
    return {
        "provider": provider_name,
        "segmentation_strategy": strategy,
        "hadiths": len(result.runs),
        "segments": sum(len(hadith_run.segments) for hadith_run in result.runs),
        "fallback_to_whole_text_units": sum(
            hadith_run.segments[0].metadata_json.get("fallback") == "whole_text"
            for hadith_run in result.runs
        ),
        "llm_equivalent_calls": sum(hadith_run.call_count for hadith_run in result.runs),
        "failed_calls": sum(hadith_run.failed_call_count for hadith_run in result.runs),
        "candidates_proposed": {
            "nodes": sum(node_statuses.values()),
            "relations": sum(relation_statuses.values()),
        },
        "candidates_validated": {
            "nodes": node_statuses[CandidateStatus.VALIDATED.value],
            "relations": relation_statuses[CandidateStatus.VALIDATED.value],
        },
        "candidates_in_review": {
            "nodes": node_statuses[CandidateStatus.REVIEW.value],
            "relations": relation_statuses[CandidateStatus.REVIEW.value],
            "open_review_items_by_reason_code": dict(sorted(review_reasons.items())),
        },
        "candidates_rejected": {
            "nodes": node_statuses[CandidateStatus.REJECTED.value],
            "relations": relation_statuses[CandidateStatus.REJECTED.value],
        },
        "narrator_mentions": {
            "proposed": sum(
                len(mentions(hadith_run, validated_only=False)) for hadith_run in result.runs
            ),
            "validated": sum(
                len(mentions(hadith_run, validated_only=True)) for hadith_run in result.runs
            ),
            "committed": len(committed_mentions),
        },
        "runs": {
            "committed": len(committed),
            "committed_without_any_fact": sum(
                delta.nodes_created + delta.nodes_merged == 0 for delta in deltas
            ),
            "blocked": len(blocked),
            "blocked_by_reason": dict(
                sorted(Counter(str(hadith_run.blocking_reason) for hadith_run in blocked).items())
            ),
            "blocked_hadith_ids": [hadith_run.hadith_id for hadith_run in blocked],
        },
        "canonical_graph": {
            "nodes": overview.node_count,
            "edges": overview.relation_count,
            "nodes_by_type": node_type_counts,
            "node_writes": {
                "created": sum(delta.nodes_created for delta in deltas),
                "merged": sum(delta.nodes_merged for delta in deltas),
            },
            "edge_writes": {
                "created": sum(delta.relations_created for delta in deltas),
                "merged": sum(delta.relations_merged for delta in deltas),
            },
        },
        "narrator_identity": {
            "committed_mentions": len(committed_mentions),
            "canonical_narrator_nodes": node_type_counts.get(NARRATOR_NODE_TYPE, 0),
            "distinct_committed_mentions_ignoring_diacritics": len(
                {normalize_arabic(mention) for mention in committed_mentions}
            ),
        },
        "committed_fact_invariants": check_committed_facts(result),
    }


def write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_scorer_files_and_report(
    result: PipelineResult,
    out_dir: Path,
    report: dict[str, Any],
    *,
    mention_text: MentionText,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for file_name, validated_only in (
        ("system_proposed.jsonl", False),
        ("system_validated.jsonl", True),
    ):
        write_jsonl(
            out_dir / file_name,
            [
                {
                    "hadith_id": hadith_run.hadith_id,
                    "mentions": [
                        mention_text(occurrence)
                        for occurrence in narrator_occurrences(
                            result,
                            hadith_run,
                            validated_only=validated_only,
                        )
                    ],
                }
                for hadith_run in result.runs
            ],
        )
    with (out_dir / "run_report.json").open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
