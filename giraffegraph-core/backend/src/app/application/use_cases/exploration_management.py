from dataclasses import dataclass

from app.application.errors import NotFoundError
from app.application.ports.repositories import CanonicalGraphRepository, ProjectRepository
from app.application.use_cases.ingestion_management import IngestionManagementService
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.application.use_cases.review_management import ReviewManagementService
from app.domain.exploration.chains import (
    HUMAN_ACCEPTANCE,
    NARRATED_FROM_RELATION_TYPE,
    NARRATOR_NODE_TYPE,
    POLICY_ACCEPTANCE,
    ChainLink,
    ChainNarrator,
    CommittedHadith,
    CommittedRunRef,
    FactAcceptance,
    HadithChainView,
    HadithSource,
    NarratorChain,
    NarratorHadithRef,
    NarratorNeighbour,
    NarratorView,
    locate_evidence,
)
from app.domain.exploration.entities import (
    CanonicalNodeDetail,
    CanonicalNodeView,
    CanonicalRelationDetail,
    CanonicalRelationView,
    GraphOverview,
)
from app.domain.ingestion.entities import ProcessingRun
from app.domain.review.entities import AcceptanceRecord
from app.domain.shared.enums import CandidateStatus, RunStatus
from app.domain.shared.resolution import build_canonical_merge_key, normalize_text


@dataclass(slots=True)
class GraphExplorationService:
    project_repository: ProjectRepository
    canonical_graph_repository: CanonicalGraphRepository

    def get_project_overview(self, project_id: str) -> GraphOverview:
        self._require_project(project_id)
        return self.canonical_graph_repository.get_project_overview(project_id)

    def list_nodes(
        self,
        project_id: str,
        *,
        node_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalNodeView]:
        self._require_project(project_id)
        return self.canonical_graph_repository.list_nodes(
            project_id,
            node_type=node_type.strip() if node_type else None,
            limit=limit,
        )

    def list_relations(
        self,
        project_id: str,
        *,
        relation_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalRelationView]:
        self._require_project(project_id)
        return self.canonical_graph_repository.list_relations(
            project_id,
            relation_type=relation_type.strip() if relation_type else None,
            limit=limit,
        )

    def get_node_detail(
        self,
        project_id: str,
        *,
        node_type: str,
        merge_key: str,
    ) -> CanonicalNodeDetail:
        self._require_project(project_id)
        detail = self.canonical_graph_repository.get_node_detail(
            project_id,
            node_type=node_type.strip(),
            merge_key=merge_key,
        )
        if detail is None:
            raise NotFoundError(
                "Canonical node was not found for project "
                f"'{project_id}', node_type '{node_type}', merge_key '{merge_key}'."
            )
        return detail

    def get_relation_detail(
        self,
        project_id: str,
        *,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
    ) -> CanonicalRelationDetail:
        self._require_project(project_id)
        detail = self.canonical_graph_repository.get_relation_detail(
            project_id,
            relation_type=relation_type.strip(),
            from_node_type=from_node_type.strip(),
            from_merge_key=from_merge_key,
            to_node_type=to_node_type.strip(),
            to_merge_key=to_merge_key,
        )
        if detail is None:
            raise NotFoundError(
                "Canonical relation was not found for project "
                f"'{project_id}', relation_type '{relation_type}'."
            )
        return detail

    def _require_project(self, project_id: str) -> None:
        project = self.project_repository.get(project_id)
        if project is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")


@dataclass(slots=True)
class ChainExplorationService:
    ingestion_management_service: IngestionManagementService
    pipeline_management_service: PipelineManagementService
    review_management_service: ReviewManagementService
    graph_exploration_service: GraphExplorationService

    def list_committed_hadiths(
        self,
        project_id: str,
        *,
        query: str | None = None,
    ) -> list[CommittedHadith]:
        source_units = self.ingestion_management_service.list_source_units(project_id)
        latest_run_by_source_unit: dict[str, ProcessingRun] = {}
        for run in self._committed_runs(project_id):
            latest_run_by_source_unit.setdefault(run.source_unit_id, run)
        needle = (query or "").strip().casefold()
        return [
            CommittedHadith(
                hadith_ref=source_unit.external_ref,
                source_unit_id=source_unit.source_unit_id,
                title=source_unit.title,
                run_id=committed_run.run_id,
                committed_at=committed_run.ended_at,
            )
            for source_unit in source_units
            if source_unit.external_ref is not None
            and (committed_run := latest_run_by_source_unit.get(source_unit.source_unit_id))
            is not None
            and (
                needle in source_unit.external_ref.casefold()
                or needle in source_unit.title.casefold()
            )
        ]

    def get_hadith_chains(self, project_id: str, hadith_ref: str) -> HadithChainView:
        view = HadithChainView(project_id=project_id, hadith_ref=hadith_ref)
        source_units = [
            source_unit
            for source_unit in self.ingestion_management_service.list_source_units(project_id)
            if source_unit.external_ref == hadith_ref
        ]
        if not source_units:
            return view
        committed_runs = self._committed_runs(project_id)
        committed_source_unit_ids = {run.source_unit_id for run in committed_runs}
        source_unit = next(
            (item for item in source_units if item.source_unit_id in committed_source_unit_ids),
            source_units[0],
        )
        view.source = HadithSource(
            source_unit_id=source_unit.source_unit_id,
            title=source_unit.title,
            raw_content=source_unit.raw_content,
        )
        segments = {
            segment.segment_id: segment
            for segment in self.pipeline_management_service.list_segments(
                source_unit.source_unit_id
            )
        }
        narrators: dict[str, ChainNarrator] = {}
        links: dict[tuple[int, int], ChainLink] = {}
        # Runs come newest first, so a fact committed twice is shown as its latest run wrote it.
        for run in committed_runs:
            if run.source_unit_id != source_unit.source_unit_id:
                continue
            view.runs.append(
                CommittedRunRef(
                    run_id=run.run_id,
                    committed_at=run.ended_at,
                    llm_provider=run.llm_provider,
                    llm_model=run.llm_model,
                )
            )
            acceptance = {
                record.candidate_ref: _to_fact_acceptance(record)
                for record in self.review_management_service.list_acceptance_records(
                    run.run_id,
                    validation_results=self.pipeline_management_service.list_validation_results(
                        run.run_id
                    ),
                )
            }
            names: dict[str, str] = {}
            for node in self.pipeline_management_service.list_candidate_nodes(run.run_id):
                if (
                    node.status != CandidateStatus.VALIDATED
                    or node.node_type.casefold() != NARRATOR_NODE_TYPE.casefold()
                ):
                    continue
                name = str(node.properties.get("name", node.candidate_node_id))
                names[node.candidate_node_id] = name
                narrators.setdefault(
                    normalize_text(name),
                    ChainNarrator(
                        name=name,
                        evidence=[
                            locate_evidence(
                                evidence_ref,
                                segment=segments.get(evidence_ref.segment_id),
                                raw_content=source_unit.raw_content,
                            )
                            for evidence_ref in node.evidence_refs
                        ],
                        acceptance=acceptance.get(node.candidate_node_id),
                    ),
                )
            for relation in self.pipeline_management_service.list_candidate_relations(run.run_id):
                if (
                    relation.status != CandidateStatus.VALIDATED
                    or relation.relation_type.casefold() != NARRATED_FROM_RELATION_TYPE.casefold()
                    or relation.from_candidate_ref not in names
                    or relation.to_candidate_ref not in names
                ):
                    continue
                chain_no = _as_int(relation.properties.get("chain_no"))
                position = _as_int(relation.properties.get("position"))
                sigha = relation.properties.get("sigha")
                links.setdefault(
                    (chain_no, position),
                    ChainLink(
                        position=position,
                        from_narrator=names[relation.from_candidate_ref],
                        to_narrator=names[relation.to_candidate_ref],
                        sigha=str(sigha) if sigha is not None else None,
                        evidence=[
                            locate_evidence(
                                evidence_ref,
                                segment=segments.get(evidence_ref.segment_id),
                                raw_content=source_unit.raw_content,
                            )
                            for evidence_ref in relation.evidence_refs
                        ],
                        acceptance=acceptance.get(relation.candidate_relation_id),
                    ),
                )

        chains: dict[int, NarratorChain] = {}
        for (chain_no, _), link in sorted(links.items()):
            chains.setdefault(chain_no, NarratorChain(chain_no=chain_no)).links.append(link)
        view.chains = list(chains.values())
        view.narrators = sorted(narrators.values(), key=_first_mention_offset)
        return view

    def get_narrator(self, project_id: str, name: str) -> NarratorView:
        source_units = self.ingestion_management_service.list_source_units(project_id)
        try:
            detail = self.graph_exploration_service.get_node_detail(
                project_id,
                node_type=NARRATOR_NODE_TYPE,
                merge_key=build_canonical_merge_key(
                    merge_key_payload={"name": name},
                    fallback_payload={},
                ),
            )
        except NotFoundError as exc:
            raise NotFoundError(
                f"Narrator '{name}' was not found in project '{project_id}'."
            ) from exc

        narrator_source_unit_ids = {ref.source_unit_id for ref in detail.source_units}
        view = NarratorView(
            project_id=project_id,
            name=str(detail.node.properties.get("name", name)),
            hadiths=[
                NarratorHadithRef(
                    hadith_ref=source_unit.external_ref or source_unit.title,
                    source_unit_id=source_unit.source_unit_id,
                    title=source_unit.title,
                )
                for source_unit in source_units
                if source_unit.source_unit_id in narrator_source_unit_ids
            ],
        )
        neighbours: dict[tuple[str, str], NarratorNeighbour] = {}
        for relation in detail.connected_relations:
            if (
                relation.relation_type != NARRATED_FROM_RELATION_TYPE
                or relation.other_node_type != NARRATOR_NODE_TYPE
            ):
                continue
            neighbour = neighbours.setdefault(
                (relation.direction, relation.other_merge_key),
                NarratorNeighbour(
                    name=str(
                        relation.other_node_properties.get("name", relation.other_merge_key)
                    )
                ),
            )
            neighbour.link_count += 1
            hadith_ref = relation.properties.get("hadith_ref")
            if hadith_ref is not None and str(hadith_ref) not in neighbour.hadith_refs:
                neighbour.hadith_refs.append(str(hadith_ref))
        ranked = sorted(neighbours.items(), key=lambda item: (-item[1].link_count, item[1].name))
        for (direction, _), neighbour in ranked:
            neighbour.hadith_refs.sort()
            # An outgoing NARRATED_FROM edge points at the narrator this one received from.
            if direction == "outgoing":
                view.narrated_from.append(neighbour)
            else:
                view.narrated_to.append(neighbour)
        return view

    def _committed_runs(self, project_id: str) -> list[ProcessingRun]:
        return sorted(
            (
                run
                for run in self.ingestion_management_service.list_processing_runs(project_id)
                if run.status == RunStatus.COMPLETED
            ),
            key=lambda run: run.created_at,
            reverse=True,
        )


def _to_fact_acceptance(record: AcceptanceRecord) -> FactAcceptance:
    if record.decision is not None:
        return FactAcceptance(
            kind=HUMAN_ACCEPTANCE,
            action=record.decision.action,
            reviewer_id=record.decision.reviewer_id,
            decided_at=record.decision.decided_at,
        )
    return FactAcceptance(
        kind=POLICY_ACCEPTANCE,
        policy=record.policy,
        rule_code=record.rule_code,
    )


def _as_int(value: object) -> int:
    try:
        return int(str(value))
    except ValueError:
        return 0


def _first_mention_offset(narrator: ChainNarrator) -> float:
    return min(
        (
            evidence.source_start_offset
            for evidence in narrator.evidence
            if evidence.source_start_offset is not None
        ),
        default=float("inf"),
    )
