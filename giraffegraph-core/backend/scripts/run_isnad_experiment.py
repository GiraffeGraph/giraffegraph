"""Run one isnad extraction condition through the pipeline and export it for analysis.

Conditions:
  rule              isnad segmentation, `rule_based_isnad` provider (no LLM).
  llm_schema_whole  one call per hadith; the isnad schema reduced to its structure
                    (no type or property descriptions, no extraction hints).
  llm_isnad_whole   one call per hadith; the isnad template schema with its hints.
  llm_isnad_chain   isnad segmentation, one call per chain; the template schema with hints.

The LLM conditions call the `anthropic` provider behind the on-disk response cache.
A call is issued only while the money spent, plus a worst-case reservation for every
call in flight, stays within --max-cost-usd. A hadith that needed a call that was not
issued is left out of every export and listed in `hadith_ids_not_processed`.

Usage (from backend/):
  uv run python scripts/run_isnad_experiment.py --input <hadiths.json> --out-dir <dir>
      --condition <name> [--model claude-haiku-5-5] [--effort low] [--limit N]
      [--workers 4] [--max-cost-usd 1.00] [--cache-dir D]

Input: a JSON list of objects with `coll`, `num` and `raw`.
Output: system_proposed.jsonl, system_validated.jsonl, candidates.jsonl, calls.jsonl,
run_report.json. ANTHROPIC_API_KEY is read from the environment or the repository `.env`.
"""

import argparse
import json
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.application.dto.contracts import NodeTypeDefinitionInput, RelationTypeDefinitionInput
from app.application.errors import ApplicationError
from app.application.ports.llm_provider import (
    LLMProvider,
    LLMUsage,
    StructuredGeneration,
    StructuredGenerationError,
)
from app.domain.extraction.entities import SCHEMA_PROPOSAL_ITEM_TYPE, EvidenceRef
from app.domain.hadith.grounding import quote_in_segment
from app.domain.shared.enums import CandidateStatus, ReviewStatus
from app.infrastructure.config.settings import Settings
from app.infrastructure.llm.anthropic_provider import (
    DEFAULT_MAX_TOKENS,
    AnthropicEffort,
    AnthropicLLMProvider,
)
from app.infrastructure.llm.cached_provider import CachedLLMProvider
from app.infrastructure.llm.prompt_catalog import CANDIDATE_GRAPH_EXTRACTION_V2
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from app.infrastructure.llm.rule_based_isnad_provider import RuleBasedIsnadProvider
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_SCHEMA

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from isnad_pipeline import (  # noqa: E402
    NARRATOR_NODE_TYPE,
    HadithRun,
    PipelineResult,
    build_report,
    check_committed_facts,
    create_memory_container,
    create_project,
    extract,
    load_hadiths,
    name_mention,
    narrator_occurrences,
    prepare_run,
    validate_and_commit,
    write_jsonl,
    write_scorer_files_and_report,
)

PROMPT_VERSION = CANDIDATE_GRAPH_EXTRACTION_V2.version
RULE_PROVIDER_NAME = "rule_based_isnad"
DEFAULT_CACHE_DIR = BACKEND_DIR / "var" / "llm-cache"

# USD per million tokens. The Haiku rate applies to prompts of up to 100K tokens.
PRICES_AS_OF = "2026-10-06"
PRICES_USD_PER_MTOK = {
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
}
CACHE_READ_INPUT_MULTIPLIER = 0.1
CACHE_WRITE_INPUT_MULTIPLIER = 1.25
# Tokens the request carries besides the prompt and the payload (output format, framing).
REQUEST_OVERHEAD_TOKENS = 2000
PROGRESS_EVERY_CALLS = 25
# A request the API rejects for its key, model or shape is rejected for every hadith.
RUN_STOPPING_ERROR_KINDS = {"authentication", "permission_denied", "not_found", "bad_request"}
NOT_ISSUED_ERROR_KIND = "not_issued"


@dataclass(frozen=True, slots=True)
class Condition:
    provider_name: str
    strategy: str
    with_hints: bool


CONDITIONS = {
    "rule": Condition(RULE_PROVIDER_NAME, "isnad", with_hints=True),
    "llm_schema_whole": Condition("anthropic", "paragraphs", with_hints=False),
    "llm_isnad_whole": Condition("anthropic", "paragraphs", with_hints=True),
    "llm_isnad_chain": Condition("anthropic", "isnad", with_hints=True),
}


@dataclass(slots=True, kw_only=True)
class CallRecord:
    hadith_id: str
    call_index: int
    segment_ids: list[str]
    segment_orders: list[int]
    model: str | None
    effort: str | None
    issued: bool = True
    cached: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    stop_reason: str | None = None
    latency_ms: int = 0
    cost_usd: float = 0.0
    error: str | None = None
    error_kind: str | None = None


@dataclass(slots=True)
class SpendingGate:
    """Decides whether a paid call may start; the first refusal closes it for the run."""

    max_cost_usd: float
    spent_usd: float = 0.0
    reserved_usd: float = 0.0
    stop_reason: str | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def try_reserve(self, worst_case_usd: float) -> bool:
        with self._lock:
            if self.stop_reason is not None:
                return False
            if self.spent_usd + self.reserved_usd + worst_case_usd > self.max_cost_usd:
                self.stop_reason = "budget"
                return False
            self.reserved_usd += worst_case_usd
            return True

    def settle(self, *, reserved_usd: float, cost_usd: float) -> None:
        with self._lock:
            self.reserved_usd -= reserved_usd
            self.spent_usd += cost_usd

    def stop(self, reason: str) -> None:
        with self._lock:
            if self.stop_reason is None:
                self.stop_reason = reason


def call_cost_usd(model: str | None, usage: LLMUsage) -> float:
    prices = PRICES_USD_PER_MTOK.get(model or "")
    if prices is None:
        return 0.0
    input_tokens = (
        usage.input_tokens
        + CACHE_READ_INPUT_MULTIPLIER * (usage.cache_read_input_tokens or 0)
        + CACHE_WRITE_INPUT_MULTIPLIER * (usage.cache_creation_input_tokens or 0)
    )
    return (input_tokens * prices["input"] + usage.output_tokens * prices["output"]) / 1_000_000


def worst_case_call_cost_usd(model: str | None, *, prompt: str, payload: dict[str, Any]) -> float:
    prices = PRICES_USD_PER_MTOK.get(model or "")
    if prices is None:
        return 0.0
    # A token is at least one byte of text, so the byte count bounds the input tokens.
    request_bytes = len(prompt.encode("utf-8")) + len(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    )
    return (
        (request_bytes + REQUEST_OVERHEAD_TOKENS) * prices["input"]
        + DEFAULT_MAX_TOKENS * prices["output"]
    ) / 1_000_000


@dataclass(slots=True, kw_only=True)
class RecordingProvider:
    """Records every provider call of the run and lets paid calls through the gate.

    The caller holds `service_lock` while it is inside the service layer; the lock is
    released for the duration of the provider call, so only those calls overlap.
    """

    inner: LLMProvider
    effort: str | None
    gate: SpendingGate
    service_lock: threading.Lock
    records: list[CallRecord] = field(default_factory=list)
    completed_calls: int = 0
    provider_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.provider_name = self.inner.provider_name

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        return self.generate_structured_with_usage(
            prompt=prompt,
            schema_name=schema_name,
            payload=payload,
            model=model,
        ).output

    def generate_structured_with_usage(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> StructuredGeneration:
        hadith_id = str(payload["source_unit"]["external_ref"])
        record = CallRecord(
            hadith_id=hadith_id,
            call_index=1 + sum(item.hadith_id == hadith_id for item in self.records),
            segment_ids=[segment["segment_id"] for segment in payload["segments"]],
            segment_orders=[segment["segment_order"] for segment in payload["segments"]],
            model=model,
            effort=self.effort,
        )
        self.records.append(record)
        arguments = {
            "prompt": prompt,
            "schema_name": schema_name,
            "payload": payload,
            "model": model,
        }
        reserved_usd = 0.0
        if not (isinstance(self.inner, CachedLLMProvider) and self.inner.is_cached(**arguments)):
            reserved_usd = worst_case_call_cost_usd(model, prompt=prompt, payload=payload)
            if not self.gate.try_reserve(reserved_usd):
                record.issued = False
                record.error_kind = NOT_ISSUED_ERROR_KIND
                record.error = f"Call was not issued: run stopped ({self.gate.stop_reason})."
                raise StructuredGenerationError(record.error, kind=NOT_ISSUED_ERROR_KIND)

        usage: LLMUsage | None = None
        self.service_lock.release()
        started = time.perf_counter()
        try:
            generation = self.inner.generate_structured_with_usage(**arguments)
            usage = generation.usage
            record.cached = generation.cached
            return generation
        except StructuredGenerationError as exc:
            usage = exc.usage
            record.error, record.error_kind = str(exc), exc.kind
            if exc.kind in RUN_STOPPING_ERROR_KINDS:
                self.gate.stop(f"provider_error:{exc.kind}")
            raise
        except ApplicationError as exc:
            record.error, record.error_kind = str(exc), "provider_error"
            raise
        finally:
            record.latency_ms = round((time.perf_counter() - started) * 1000)
            self.service_lock.acquire()
            if usage is not None:
                record.input_tokens = usage.input_tokens
                record.output_tokens = usage.output_tokens
                record.cache_read_input_tokens = usage.cache_read_input_tokens
                record.cache_creation_input_tokens = usage.cache_creation_input_tokens
                record.stop_reason = usage.stop_reason
                record.cost_usd = call_cost_usd(model, usage)
            self.gate.settle(
                reserved_usd=reserved_usd,
                cost_usd=0.0 if record.cached else record.cost_usd,
            )
            self.completed_calls += 1
            if self.completed_calls % PROGRESS_EVERY_CALLS == 0:
                print(
                    f"[{self.completed_calls} calls] cost ${self.gate.spent_usd:.4f}",
                    file=sys.stderr,
                )


@dataclass(slots=True, kw_only=True)
class ExperimentResult:
    pipeline: PipelineResult
    condition_name: str
    model: str | None
    effort: str | None
    gate: SpendingGate
    calls: list[CallRecord]
    not_processed: list[HadithRun]


def structure_only_schema() -> (
    tuple[list[NodeTypeDefinitionInput], list[RelationTypeDefinitionInput]]
):
    """The isnad schema as bare structure: names, data types, keys and endpoints.

    A type description is mandatory, so it repeats the type name.
    """
    node_types = [
        node_type.model_copy(
            update={
                "description": node_type.name,
                "extraction_hints": [],
                "properties": [
                    item.model_copy(update={"description": None}) for item in node_type.properties
                ],
            }
        )
        for node_type in ISNAD_TEMPLATE_SCHEMA.node_types
    ]
    relation_types = [
        relation_type.model_copy(
            update={
                "description": relation_type.name,
                "extraction_hints": [],
                "properties": [
                    item.model_copy(update={"description": None})
                    for item in relation_type.properties
                ],
            }
        )
        for relation_type in ISNAD_TEMPLATE_SCHEMA.relation_types
    ]
    return node_types, relation_types


def anthropic_provider_from_settings(effort: AnthropicEffort) -> AnthropicLLMProvider:
    # Environment variables take precedence over the repository `.env`.
    settings = Settings(_env_file=BACKEND_DIR.parent / ".env")
    api_key = (settings.anthropic_api_key or "").strip()
    if api_key == "":
        raise ValueError("ANTHROPIC_API_KEY is not set in the environment or the repository .env")
    return AnthropicLLMProvider.from_api_key(
        api_key,
        timeout_seconds=settings.anthropic_timeout_seconds,
        effort=effort,
    )


def run_experiment(
    hadiths: list[tuple[str, str]],
    *,
    condition_name: str,
    model: str,
    effort: AnthropicEffort,
    workers: int,
    max_cost_usd: float,
    cache_dir: Path,
    llm_provider: LLMProvider | None = None,
) -> ExperimentResult:
    """Run one condition. `model`, `effort` and the cache apply to the LLM conditions only;
    `llm_provider` replaces the provider built from the settings."""
    condition = CONDITIONS[condition_name]
    provider: LLMProvider
    run_model: str | None = None
    run_effort: str | None = None
    if condition.provider_name == RULE_PROVIDER_NAME:
        provider = RuleBasedIsnadProvider()
    else:
        if model not in PRICES_USD_PER_MTOK:
            raise ValueError(f"no price is listed for model '{model}'")
        if llm_provider is None:
            llm_provider = anthropic_provider_from_settings(effort)
        provider = CachedLLMProvider(inner=llm_provider, cache_dir=cache_dir, effort=effort)
        run_model, run_effort = model, effort

    container = create_memory_container()
    service_lock = threading.Lock()
    gate = SpendingGate(max_cost_usd=max_cost_usd)
    recorder = RecordingProvider(
        inner=provider,
        effort=run_effort,
        gate=gate,
        service_lock=service_lock,
    )
    extraction_service = container.extraction_management_service
    extraction_service.provider_registry = StaticLLMProviderRegistry(providers=[recorder])
    extraction_service.default_extraction_prompt_version = PROMPT_VERSION
    extraction_service.max_segments_per_call = None

    if condition.with_hints:
        node_types = list(ISNAD_TEMPLATE_SCHEMA.node_types)
        relation_types = list(ISNAD_TEMPLATE_SCHEMA.relation_types)
    else:
        node_types, relation_types = structure_only_schema()
    project_id, schema_id = create_project(
        container,
        name=f"Isnad experiment: {condition_name}",
        node_types=node_types,
        relation_types=relation_types,
    )
    runs = [
        prepare_run(
            container,
            project_id=project_id,
            schema_id=schema_id,
            hadith_id=hadith_id,
            raw=raw,
            provider_name=recorder.provider_name,
            model=run_model,
            strategy=condition.strategy,
        )
        for hadith_id, raw in hadiths
    ]

    def extract_one(hadith_run: HadithRun) -> None:
        with service_lock:
            extract(container, hadith_run)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(extract_one, runs))

    not_issued = {record.hadith_id for record in recorder.records if not record.issued}
    processed = [hadith_run for hadith_run in runs if hadith_run.hadith_id not in not_issued]
    # Validation and commit read the graph earlier runs wrote, so they keep the input order.
    for hadith_run in processed:
        validate_and_commit(container, hadith_run)
    _attach_engine_rejections(processed, recorder.records)
    input_order = {hadith_run.hadith_id: index for index, hadith_run in enumerate(runs)}
    return ExperimentResult(
        pipeline=PipelineResult(container=container, project_id=project_id, runs=processed),
        condition_name=condition_name,
        model=run_model,
        effort=run_effort,
        gate=gate,
        # Worker threads start calls in any order; the export follows the input order.
        calls=sorted(
            (record for record in recorder.records if record.issued),
            key=lambda record: (input_order[record.hadith_id], record.call_index),
        ),
        not_processed=[hadith_run for hadith_run in runs if hadith_run.hadith_id in not_issued],
    )


def _attach_engine_rejections(runs: list[HadithRun], records: list[CallRecord]) -> None:
    """Mark calls whose output the provider returned but the engine did not accept."""
    for hadith_run in runs:
        calls = [record for record in records if record.hadith_id == hadith_run.hadith_id]
        messages = {
            tuple(failed_call.segment_ids): failed_call.error_message
            for failed_call in hadith_run.failed_calls or []
        }
        for record in calls:
            message = messages.get(tuple(record.segment_ids))
            if hadith_run.extraction_error is not None:
                # The service reports the first error only when every call of a run failed.
                message = (
                    hadith_run.extraction_error
                    if record is calls[0]
                    else "The engine rejected the structured output."
                )
            if message is not None and record.error is None:
                record.error, record.error_kind = message, "engine_rejected_output"


def candidate_rows(result: ExperimentResult) -> list[dict[str, Any]]:
    pipeline = result.pipeline.container.pipeline_management_service
    rows: list[dict[str, Any]] = []
    for hadith_run in result.pipeline.runs:
        run_id = hadith_run.run_id
        segment_orders = {
            segment.segment_id: segment.segment_order for segment in hadith_run.segments
        }
        call_indexes = {
            segment_id: record.call_index
            for record in result.calls
            if record.hadith_id == hadith_run.hadith_id
            for segment_id in record.segment_ids
        }
        reason_codes: dict[str, set[str]] = {}
        for validation_result in pipeline.list_validation_results(run_id):
            if validation_result.result != "passed":
                reason_codes.setdefault(validation_result.candidate_ref, set()).add(
                    validation_result.rule_code
                )
        mention_indexes: dict[str, list[int]] = {}
        occurrences = narrator_occurrences(result.pipeline, hadith_run, validated_only=False)
        for index, occurrence in enumerate(occurrences):
            mention_indexes.setdefault(occurrence.candidate_node_id, []).append(index)

        nodes = {node.candidate_node_id: node for node in pipeline.list_candidate_nodes(run_id)}
        for node in nodes.values():
            row = {
                "hadith_id": hadith_run.hadith_id,
                "kind": "node",
                "candidate_id": node.candidate_node_id,
                "type": node.node_type,
                "name": node.properties.get("name"),
                "properties": node.properties,
                "confidence": node.confidence,
                "status": node.status.value,
                "reason_codes": sorted(reason_codes.get(node.candidate_node_id, set())),
                **_evidence_fields(node.evidence_refs, segment_orders, call_indexes),
            }
            if node.node_type == NARRATOR_NODE_TYPE:
                row["mention_indexes"] = mention_indexes.get(node.candidate_node_id, [])
            rows.append(row)
        for relation in pipeline.list_candidate_relations(run_id):
            rows.append(
                {
                    "hadith_id": hadith_run.hadith_id,
                    "kind": "relation",
                    "candidate_id": relation.candidate_relation_id,
                    "type": relation.relation_type,
                    "from_name": nodes[relation.from_candidate_ref].properties.get("name"),
                    "to_name": nodes[relation.to_candidate_ref].properties.get("name"),
                    "properties": relation.properties,
                    "confidence": relation.confidence,
                    "status": relation.status.value,
                    "reason_codes": sorted(
                        reason_codes.get(relation.candidate_relation_id, set())
                    ),
                    **_evidence_fields(relation.evidence_refs, segment_orders, call_indexes),
                }
            )
    return rows


def _evidence_fields(
    evidence_refs: list[EvidenceRef],
    segment_orders: dict[str, int],
    call_indexes: dict[str, int],
) -> dict[str, Any]:
    segment_ids = [evidence_ref.segment_id for evidence_ref in evidence_refs]
    return {
        "evidence_quotes": [evidence_ref.quote for evidence_ref in evidence_refs],
        "segment_orders": sorted({segment_orders[item] for item in segment_ids}),
        "call_indexes": sorted(
            {call_indexes[item] for item in segment_ids if item in call_indexes}
        ),
    }


def build_experiment_report(
    result: ExperimentResult,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    condition = CONDITIONS[result.condition_name]
    pipeline = result.pipeline.container.pipeline_management_service
    calls = result.calls
    proposals: Counter[tuple[str, str, str, str | None]] = Counter()
    per_hadith: list[dict[str, Any]] = []
    for hadith_run in result.pipeline.runs:
        review_items = pipeline.list_review_items(hadith_run.run_id)
        for item in review_items:
            if item.item_type == SCHEMA_PROPOSAL_ITEM_TYPE:
                property_name = item.payload_json.get("property_name")
                key = (
                    item.reason_code,
                    str(item.payload_json["kind"]),
                    str(item.payload_json["type_name"]),
                    None if property_name is None else str(property_name),
                )
                count = item.payload_json["count"]
                proposals[key] += count if isinstance(count, int) else 1
        per_hadith.append(
            {
                "hadith_id": hadith_run.hadith_id,
                "segments": len(hadith_run.segments),
                "calls": sum(record.hadith_id == hadith_run.hadith_id for record in calls),
                "candidates_in_review": sum(
                    row["hadith_id"] == hadith_run.hadith_id
                    and row["status"] == CandidateStatus.REVIEW.value
                    for row in candidates
                ),
                "open_review_items": sum(item.status == ReviewStatus.OPEN for item in review_items),
                "committed": hadith_run.delta is not None,
                "blocking_reason": hadith_run.blocking_reason,
            }
        )
    reason_counts = {
        kind: dict(
            sorted(
                Counter(
                    reason_code
                    for row in candidates
                    if row["kind"] == kind
                    for reason_code in row["reason_codes"]
                ).items()
            )
        )
        for kind in ("node", "relation")
    }
    return {
        "condition": result.condition_name,
        "model": result.model,
        "effort": result.effort,
        "prompt_version": PROMPT_VERSION,
        "schema_hints": condition.with_hints,
        **build_report(
            result.pipeline,
            provider_name=condition.provider_name,
            strategy=condition.strategy,
            mention_text=name_mention,
        ),
        "committed_fact_invariants_with_grounding_normalisation": check_committed_facts(
            result.pipeline,
            quote_in_segment=quote_in_segment,
        ),
        "hadiths_requested": len(result.pipeline.runs) + len(result.not_processed),
        "hadith_ids_not_processed": [item.hadith_id for item in result.not_processed],
        "calls": {
            "total": len(calls),
            "uncached": sum(not record.cached for record in calls),
            "cached": sum(record.cached for record in calls),
            "failed": sum(record.error is not None for record in calls),
            "refused": sum(record.error_kind == "refusal" for record in calls),
            "truncated": sum(record.error_kind == "max_tokens" for record in calls),
            "failed_by_kind": dict(
                sorted(Counter(record.error_kind for record in calls if record.error_kind).items())
            ),
        },
        "tokens": {
            "input": sum(record.input_tokens for record in calls),
            "output": sum(record.output_tokens for record in calls),
            "cache_read_input": sum(record.cache_read_input_tokens or 0 for record in calls),
            "cache_creation_input": sum(
                record.cache_creation_input_tokens or 0 for record in calls
            ),
        },
        "cost_usd": round(result.gate.spent_usd, 6),
        "cost_usd_without_response_cache": round(sum(record.cost_usd for record in calls), 6),
        "max_cost_usd": result.gate.max_cost_usd,
        "budget_stopped": result.gate.stop_reason == "budget",
        "stop_reason": result.gate.stop_reason,
        "prices_usd_per_mtok": {"as_of": PRICES_AS_OF, **PRICES_USD_PER_MTOK},
        "schema_proposals": [
            {
                "reason_code": reason_code,
                "kind": kind,
                "type_name": type_name,
                "property_name": property_name,
                "count": count,
            }
            for (reason_code, kind, type_name, property_name), count in proposals.most_common()
        ],
        "candidates_by_reason_code": reason_counts,
        "per_hadith": per_hadith,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one isnad extraction condition and export it for analysis."
    )
    parser.add_argument("--input", required=True, type=Path, help="JSON list with coll, num, raw")
    parser.add_argument("--out-dir", required=True, type=Path, help="directory for the exports")
    parser.add_argument("--condition", required=True, choices=sorted(CONDITIONS))
    parser.add_argument("--model", default="claude-haiku-5-5", choices=sorted(PRICES_USD_PER_MTOK))
    parser.add_argument(
        "--effort",
        default="low",
        choices=["low", "medium", "high", "xhigh", "max"],
    )
    parser.add_argument("--limit", type=int, help="only run the first N hadiths")
    parser.add_argument("--workers", type=int, default=4, help="concurrent provider calls")
    parser.add_argument("--max-cost-usd", type=float, default=1.00, help="spending limit")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    args = parser.parse_args(argv)

    started = time.perf_counter()
    try:
        hadiths = load_hadiths(args.input, args.limit)
        result = run_experiment(
            hadiths,
            condition_name=args.condition,
            model=args.model,
            effort=args.effort,
            workers=max(args.workers, 1),
            max_cost_usd=args.max_cost_usd,
            cache_dir=args.cache_dir,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    candidates = candidate_rows(result)
    report = {"input": str(args.input), **build_experiment_report(result, candidates)}
    report["wall_time_seconds"] = round(time.perf_counter() - started, 3)
    write_scorer_files_and_report(result.pipeline, args.out_dir, report, mention_text=name_mention)
    write_jsonl(args.out_dir / "candidates.jsonl", candidates)
    write_jsonl(
        args.out_dir / "calls.jsonl",
        [
            {key: value for key, value in asdict(record).items() if key != "issued"}
            for record in result.calls
        ],
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(
        f"final cost ${report['cost_usd']:.4f} of ${args.max_cost_usd:.2f} "
        f"({report['calls']['uncached']} provider calls, "
        f"{report['calls']['cached']} served from the response cache)",
        file=sys.stderr,
    )
    if result.gate.stop_reason is not None:
        print(
            f"run stopped ({result.gate.stop_reason}): "
            f"{len(result.not_processed)} hadiths not processed",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
