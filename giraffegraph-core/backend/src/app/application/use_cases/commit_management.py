from dataclasses import dataclass
from uuid import uuid4

from app.application.errors import ConflictError, NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
    CanonicalGraphRepository,
    GraphDeltaRepository,
    ProcessingRunRepository,
    ReviewItemRepository,
    SegmentRepository,
    SourceUnitRepository,
)
from app.domain.graph_commit.entities import CanonicalCommitBundle, GraphDelta
from app.domain.ingestion.lifecycle import (
    mark_run_completed,
    mark_run_failed,
    mark_run_started,
    reserve_source_for_run,
)
from app.domain.shared.enums import CandidateStatus, ReviewStatus


@dataclass(slots=True)
class CommitManagementService:
    processing_run_repository: ProcessingRunRepository
    source_unit_repository: SourceUnitRepository
    segment_repository: SegmentRepository
    candidate_node_repository: CandidateNodeRepository
    candidate_relation_repository: CandidateRelationRepository
    review_item_repository: ReviewItemRepository
    graph_delta_repository: GraphDeltaRepository
    canonical_graph_repository: CanonicalGraphRepository

    def commit_run(self, run_id: str) -> GraphDelta:
        if self.graph_delta_repository.get_by_run(run_id) is not None:
            raise ConflictError(f"Run '{run_id}' already has a graph delta.")

        run = self.processing_run_repository.get(run_id)
        if run is None:
            raise NotFoundError(f"Processing run '{run_id}' was not found.")

        candidate_nodes = self.candidate_node_repository.list_by_run(run_id)
        candidate_relations = self.candidate_relation_repository.list_by_run(run_id)
        if any(candidate.status == CandidateStatus.PENDING for candidate in candidate_nodes):
            raise RuleViolationError("All candidate nodes must be validated before commit.")
        if any(candidate.status == CandidateStatus.PENDING for candidate in candidate_relations):
            raise RuleViolationError("All candidate relations must be validated before commit.")

        open_review_items = [
            item
            for item in self.review_item_repository.list_by_run(run_id)
            if item.status == ReviewStatus.OPEN
        ]
        if open_review_items:
            raise RuleViolationError("Run has open review items and cannot be committed.")

        validated_nodes = [
            candidate
            for candidate in candidate_nodes
            if candidate.status == CandidateStatus.VALIDATED
        ]
        validated_relations = [
            candidate
            for candidate in candidate_relations
            if candidate.status == CandidateStatus.VALIDATED
        ]
        validated_node_ids = {
            candidate.candidate_node_id
            for candidate in validated_nodes
        }
        invalid_relation_dependencies = [
            candidate.candidate_relation_id
            for candidate in validated_relations
            if candidate.from_candidate_ref not in validated_node_ids
            or candidate.to_candidate_ref not in validated_node_ids
        ]
        if invalid_relation_dependencies:
            raise RuleViolationError(
                "Validated relations depend on candidate nodes that are not validated: "
                + ", ".join(sorted(invalid_relation_dependencies))
                + ". Re-run validation or resolve dependent review items first."
            )
        rejected_count = sum(
            candidate.status == CandidateStatus.REJECTED for candidate in candidate_nodes
        ) + sum(
            candidate.status == CandidateStatus.REJECTED for candidate in candidate_relations
        )

        source_unit = self.source_unit_repository.get(run.source_unit_id)
        if source_unit is None:
            raise NotFoundError(f"Source unit '{run.source_unit_id}' was not found.")

        delta = GraphDelta(
            delta_id=str(uuid4()),
            run_id=run_id,
            project_id=run.project_id,
            nodes_created=0,
            nodes_merged=0,
            relations_created=0,
            relations_merged=0,
            review_count=0,
            rejected_count=rejected_count,
        )
        reserve_source_for_run(source_unit)
        mark_run_started(run)
        self.processing_run_repository.save(run)
        self.source_unit_repository.save(source_unit)

        try:
            committed_delta = self.canonical_graph_repository.commit_bundle(
                CanonicalCommitBundle(
                    delta=delta,
                    source_unit=source_unit,
                    segments=self.segment_repository.list_by_source_unit(
                        source_unit.source_unit_id
                    ),
                    candidate_nodes=validated_nodes,
                    candidate_relations=validated_relations,
                )
            )
        except Exception:
            mark_run_failed(run, source_unit)
            self.processing_run_repository.save(run)
            self.source_unit_repository.save(source_unit)
            raise
        self.graph_delta_repository.add(committed_delta)

        mark_run_completed(run, source_unit)
        self.processing_run_repository.save(run)
        self.source_unit_repository.save(source_unit)

        return committed_delta

    def get_graph_delta(self, run_id: str) -> GraphDelta:
        delta = self.graph_delta_repository.get_by_run(run_id)
        if delta is None:
            raise NotFoundError(f"Run '{run_id}' does not have a graph delta yet.")
        return delta
