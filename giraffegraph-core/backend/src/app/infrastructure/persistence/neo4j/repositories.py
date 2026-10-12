import json
from dataclasses import dataclass, field
from typing import Any

from neo4j import Driver, ManagedTransaction

from app.application.ports.repositories import CanonicalGraphRepository
from app.domain.exploration.entities import (
    CanonicalNodeDetail,
    CanonicalNodeView,
    CanonicalRelationDetail,
    CanonicalRelationEndpointView,
    CanonicalRelationView,
    CanonicalSegmentSupport,
    CanonicalSourceUnitRef,
    ConnectedRelationView,
    GraphOverview,
    NodeTypeCount,
)
from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.graph_commit.entities import CanonicalCommitBundle, GraphDelta
from app.domain.ingestion.entities import Segment, SourceUnit
from app.domain.schema.identifiers import IDENTIFIER_PATTERN
from app.domain.shared.resolution import build_canonical_merge_key

# Every commit looks these keys up many times; without an index each lookup scans the label.
LOOKUP_INDEX_STATEMENTS = (
    "CREATE INDEX canonical_node_identity IF NOT EXISTS "
    "FOR (n:CanonicalNode) ON (n.project_id, n.node_type, n.merge_key)",
    "CREATE INDEX source_unit_id IF NOT EXISTS FOR (n:SourceUnit) ON (n.source_unit_id)",
    "CREATE INDEX segment_id IF NOT EXISTS FOR (n:Segment) ON (n.segment_id)",
    "CREATE INDEX relation_evidence_candidate_relation_id IF NOT EXISTS "
    "FOR (n:RelationEvidence) ON (n.candidate_relation_id)",
    "CREATE INDEX graph_delta_id IF NOT EXISTS FOR (n:GraphDelta) ON (n.delta_id)",
)


@dataclass(slots=True)
class Neo4jCanonicalGraphRepository(CanonicalGraphRepository):
    driver: Driver
    _lookup_indexes_ensured: bool = field(default=False, init=False, repr=False)

    def commit_bundle(
        self,
        bundle: CanonicalCommitBundle,
        *,
        relation_identity_keys: dict[str, str],
    ) -> GraphDelta:
        with self.driver.session() as session:
            if not self._lookup_indexes_ensured:
                for statement in LOOKUP_INDEX_STATEMENTS:
                    session.run(statement).consume()
                self._lookup_indexes_ensured = True
            # One transaction per run: a failed write leaves no part of the run in the graph.
            return session.execute_write(self._write_bundle, bundle, relation_identity_keys)

    def _write_bundle(
        self,
        tx: ManagedTransaction,
        bundle: CanonicalCommitBundle,
        relation_identity_keys: dict[str, str],
    ) -> GraphDelta:
        delta = bundle.delta
        segment_map = {segment.segment_id: segment for segment in bundle.segments}
        node_refs_by_candidate: dict[str, tuple[str, str]] = {}

        self._upsert_source_context(tx, bundle.source_unit, bundle.segments)

        nodes_created = 0
        nodes_merged = 0
        for candidate_node in bundle.candidate_nodes:
            merge_key = self._build_merge_key(candidate_node)
            created = self._merge_candidate_node(
                tx,
                delta,
                bundle.source_unit,
                candidate_node,
                merge_key,
            )
            node_refs_by_candidate[candidate_node.candidate_node_id] = (
                candidate_node.node_type,
                merge_key,
            )
            if created:
                nodes_created += 1
            else:
                nodes_merged += 1

            self._link_node_provenance(
                tx,
                delta,
                bundle.source_unit,
                candidate_node,
                merge_key,
                segment_map,
            )

        relations_created = 0
        relations_merged = 0
        for candidate_relation in bundle.candidate_relations:
            from_ref = node_refs_by_candidate.get(candidate_relation.from_candidate_ref)
            to_ref = node_refs_by_candidate.get(candidate_relation.to_candidate_ref)
            if from_ref is None or to_ref is None:
                raise ValueError(
                    "Canonical commit received relation candidates without canonical node refs."
                )

            relation_identity_key = relation_identity_keys[
                candidate_relation.candidate_relation_id
            ]
            created = self._merge_candidate_relation(
                tx,
                delta,
                bundle.source_unit,
                candidate_relation,
                from_ref,
                to_ref,
                relation_identity_key,
            )
            if created:
                relations_created += 1
            else:
                relations_merged += 1

            self._link_relation_provenance(
                tx,
                delta,
                bundle.source_unit,
                candidate_relation,
                from_ref,
                to_ref,
                relation_identity_key,
                segment_map,
            )

        delta.nodes_created = nodes_created
        delta.nodes_merged = nodes_merged
        delta.relations_created = relations_created
        delta.relations_merged = relations_merged
        self._upsert_graph_delta(tx, delta)
        return delta

    def get_project_overview(self, project_id: str) -> GraphOverview:
        with self.driver.session() as session:
            counts = session.execute_read(self._fetch_project_overview_counts, project_id)
            node_type_counts = session.execute_read(
                self._fetch_project_node_type_counts,
                project_id,
            )
        return GraphOverview(
            project_id=project_id,
            node_count=counts["node_count"],
            relation_count=counts["relation_count"],
            node_type_counts=node_type_counts,
        )

    def list_nodes(
        self,
        project_id: str,
        *,
        node_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalNodeView]:
        with self.driver.session() as session:
            return session.execute_read(
                self._fetch_project_nodes,
                project_id,
                node_type,
                limit,
            )

    def list_relations(
        self,
        project_id: str,
        *,
        relation_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalRelationView]:
        with self.driver.session() as session:
            return session.execute_read(
                self._fetch_project_relations,
                project_id,
                relation_type,
                limit,
            )

    def get_node_detail(
        self,
        project_id: str,
        *,
        node_type: str,
        merge_key: str,
    ) -> CanonicalNodeDetail | None:
        with self.driver.session() as session:
            node = session.execute_read(
                self._fetch_canonical_node,
                project_id,
                node_type,
                merge_key,
            )
            if node is None:
                return None

            return CanonicalNodeDetail(
                node=node,
                source_units=session.execute_read(
                    self._fetch_node_source_units,
                    project_id,
                    node_type,
                    merge_key,
                ),
                supporting_segments=session.execute_read(
                    self._fetch_node_supporting_segments,
                    project_id,
                    node_type,
                    merge_key,
                ),
                connected_relations=session.execute_read(
                    self._fetch_node_connected_relations,
                    project_id,
                    node_type,
                    merge_key,
                ),
            )

    def get_relation_detail(
        self,
        project_id: str,
        *,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
        relation_identity_key: str | None = None,
    ) -> CanonicalRelationDetail | None:
        with self.driver.session() as session:
            relation_payload = session.execute_read(
                self._fetch_canonical_relation_detail_payload,
                project_id,
                relation_type,
                from_node_type,
                from_merge_key,
                to_node_type,
                to_merge_key,
                relation_identity_key,
            )
            if relation_payload is None:
                return None

            relation, from_node, to_node, resolved_identity_key = relation_payload
            return CanonicalRelationDetail(
                relation=relation,
                from_node=from_node,
                to_node=to_node,
                source_units=session.execute_read(
                    self._fetch_relation_source_units,
                    project_id,
                    relation_type,
                    from_node_type,
                    from_merge_key,
                    to_node_type,
                    to_merge_key,
                    resolved_identity_key,
                ),
                supporting_segments=session.execute_read(
                    self._fetch_relation_supporting_segments,
                    project_id,
                    relation_type,
                    from_node_type,
                    from_merge_key,
                    to_node_type,
                    to_merge_key,
                    resolved_identity_key,
                ),
            )

    def _upsert_source_context(
        self,
        tx: ManagedTransaction,
        source_unit: SourceUnit,
        segments: list[Segment],
    ) -> None:
        source_query = """
        MERGE (su:SourceUnit {source_unit_id: $source_unit_id})
        SET su.project_id = $project_id,
            su.schema_version_id = $schema_version_id,
            su.source_type = $source_type,
            su.title = $title,
            su.status = $status,
            su.sequence_no = $sequence_no,
            su.external_ref = $external_ref,
            su.metadata_json = $metadata_json,
            su.created_at = datetime($created_at)
        """
        tx.run(
            source_query,
            source_unit_id=source_unit.source_unit_id,
            project_id=source_unit.project_id,
            schema_version_id=source_unit.schema_version_id,
            source_type=source_unit.source_type,
            title=source_unit.title,
            status=source_unit.status.value,
            sequence_no=source_unit.sequence_no,
            external_ref=source_unit.external_ref,
            metadata_json=json.dumps(source_unit.metadata_json, sort_keys=True),
            created_at=source_unit.created_at.isoformat(),
        ).consume()

        segment_query = """
        MATCH (su:SourceUnit {source_unit_id: $source_unit_id})
        UNWIND $segments AS segment
        MERGE (sg:Segment {segment_id: segment.segment_id})
        SET sg.source_unit_id = $source_unit_id,
            sg.segment_order = segment.segment_order,
            sg.text = segment.text,
            sg.metadata_json = segment.metadata_json
        MERGE (su)-[:HAS_SEGMENT]->(sg)
        """
        tx.run(
            segment_query,
            source_unit_id=source_unit.source_unit_id,
            segments=[
                {
                    "segment_id": segment.segment_id,
                    "segment_order": segment.segment_order,
                    "text": segment.text,
                    "metadata_json": json.dumps(segment.metadata_json, sort_keys=True),
                }
                for segment in segments
            ],
        ).consume()

    def _merge_candidate_node(
        self,
        tx: ManagedTransaction,
        delta: GraphDelta,
        source_unit: SourceUnit,
        candidate_node: CandidateNode,
        merge_key: str,
    ) -> bool:
        label = self._quoted_identifier(candidate_node.node_type)
        query = f"""
        MERGE (n:CanonicalNode:{label} {{
            project_id: $project_id,
            node_type: $node_type,
            merge_key: $merge_key
        }})
        ON CREATE SET n.created_at = datetime($created_at)
        SET n += $properties,
            n.source_unit_id = $source_unit_id,
            n.last_run_id = $run_id,
            n.updated_at = datetime($created_at)
        """
        result = tx.run(
            query,
            project_id=delta.project_id,
            node_type=candidate_node.node_type,
            merge_key=merge_key,
            properties=self._sanitize_property_map(candidate_node.properties),
            source_unit_id=source_unit.source_unit_id,
            run_id=delta.run_id,
            created_at=delta.created_at.isoformat(),
        )
        summary = result.consume()
        return summary.counters.nodes_created > 0

    def _link_node_provenance(
        self,
        tx: ManagedTransaction,
        delta: GraphDelta,
        source_unit: SourceUnit,
        candidate_node: CandidateNode,
        merge_key: str,
        segment_map: dict[str, Segment],
    ) -> None:
        label = self._quoted_identifier(candidate_node.node_type)
        source_query = f"""
        MATCH (n:CanonicalNode:{label} {{
            project_id: $project_id,
            node_type: $node_type,
            merge_key: $merge_key
        }})
        MATCH (su:SourceUnit {{source_unit_id: $source_unit_id}})
        MERGE (n)-[:DERIVED_FROM {{
            run_id: $run_id,
            candidate_ref: $candidate_ref
        }}]->(su)
        """
        tx.run(
            source_query,
            project_id=delta.project_id,
            node_type=candidate_node.node_type,
            merge_key=merge_key,
            source_unit_id=source_unit.source_unit_id,
            run_id=delta.run_id,
            candidate_ref=candidate_node.candidate_node_id,
        ).consume()

        for evidence_ref in candidate_node.evidence_refs:
            segment = segment_map.get(evidence_ref.segment_id)
            if segment is None:
                continue
            segment_query = f"""
            MATCH (n:CanonicalNode:{label} {{
                project_id: $project_id,
                node_type: $node_type,
                merge_key: $merge_key
            }})
            MATCH (sg:Segment {{segment_id: $segment_id}})
            MERGE (n)-[:SUPPORTED_BY {{
                run_id: $run_id,
                candidate_ref: $candidate_ref,
                segment_id: $segment_id
            }}]->(sg)
            """
            tx.run(
                segment_query,
                project_id=delta.project_id,
                node_type=candidate_node.node_type,
                merge_key=merge_key,
                segment_id=segment.segment_id,
                run_id=delta.run_id,
                candidate_ref=candidate_node.candidate_node_id,
            ).consume()

        delta_query = f"""
        MERGE (d:GraphDelta {{delta_id: $delta_id}})
        WITH d
        MATCH (n:CanonicalNode:{label} {{
            project_id: $project_id,
            node_type: $node_type,
            merge_key: $merge_key
        }})
        MERGE (d)-[:AFFECTED_NODE {{candidate_ref: $candidate_ref}}]->(n)
        """
        tx.run(
            delta_query,
            delta_id=delta.delta_id,
            project_id=delta.project_id,
            node_type=candidate_node.node_type,
            merge_key=merge_key,
            candidate_ref=candidate_node.candidate_node_id,
        ).consume()

    def _merge_candidate_relation(
        self,
        tx: ManagedTransaction,
        delta: GraphDelta,
        source_unit: SourceUnit,
        candidate_relation: CandidateRelation,
        from_ref: tuple[str, str],
        to_ref: tuple[str, str],
        relation_identity_key: str,
    ) -> bool:
        relation_type = self._quoted_identifier(candidate_relation.relation_type)
        query = f"""
        MATCH (from_node:CanonicalNode {{
            project_id: $project_id,
            node_type: $from_type,
            merge_key: $from_merge_key
        }})
        MATCH (to_node:CanonicalNode {{
            project_id: $project_id,
            node_type: $to_type,
            merge_key: $to_merge_key
        }})
        MERGE (from_node)-[r:{relation_type} {{
            project_id: $project_id,
            relation_type: $relation_type,
            relation_identity_key: $relation_identity_key
        }}]->(to_node)
        ON CREATE SET r.created_at = datetime($created_at)
        SET r += $properties,
            r.source_unit_id = $source_unit_id,
            r.last_run_id = $run_id,
            r.updated_at = datetime($created_at)
        """
        result = tx.run(
            query,
            project_id=delta.project_id,
            from_type=from_ref[0],
            from_merge_key=from_ref[1],
            to_type=to_ref[0],
            to_merge_key=to_ref[1],
            relation_type=candidate_relation.relation_type,
            relation_identity_key=relation_identity_key,
            properties=self._sanitize_property_map(candidate_relation.properties),
            source_unit_id=source_unit.source_unit_id,
            run_id=delta.run_id,
            created_at=delta.created_at.isoformat(),
        )
        summary = result.consume()
        return summary.counters.relationships_created > 0

    def _link_relation_provenance(
        self,
        tx: ManagedTransaction,
        delta: GraphDelta,
        source_unit: SourceUnit,
        candidate_relation: CandidateRelation,
        from_ref: tuple[str, str],
        to_ref: tuple[str, str],
        relation_identity_key: str,
        segment_map: dict[str, Segment],
    ) -> None:
        base_query = """
        MERGE (e:RelationEvidence {candidate_relation_id: $candidate_relation_id})
        SET e.run_id = $run_id,
            e.project_id = $project_id,
            e.relation_type = $relation_type,
            e.relation_identity_key = $relation_identity_key,
            e.created_at = datetime($created_at)
        WITH e
        MATCH (from_node:CanonicalNode {
            project_id: $project_id,
            node_type: $from_type,
            merge_key: $from_merge_key
        })
        MATCH (to_node:CanonicalNode {
            project_id: $project_id,
            node_type: $to_type,
            merge_key: $to_merge_key
        })
        MATCH (su:SourceUnit {source_unit_id: $source_unit_id})
        MERGE (e)-[:FROM_NODE]->(from_node)
        MERGE (e)-[:TO_NODE]->(to_node)
        MERGE (e)-[:DERIVED_FROM]->(su)
        """
        tx.run(
            base_query,
            candidate_relation_id=candidate_relation.candidate_relation_id,
            run_id=delta.run_id,
            project_id=delta.project_id,
            relation_type=candidate_relation.relation_type,
            relation_identity_key=relation_identity_key,
            created_at=delta.created_at.isoformat(),
            from_type=from_ref[0],
            from_merge_key=from_ref[1],
            to_type=to_ref[0],
            to_merge_key=to_ref[1],
            source_unit_id=source_unit.source_unit_id,
        ).consume()

        for evidence_ref in candidate_relation.evidence_refs:
            segment = segment_map.get(evidence_ref.segment_id)
            if segment is None:
                continue
            support_query = """
            MATCH (e:RelationEvidence {candidate_relation_id: $candidate_relation_id})
            MATCH (sg:Segment {segment_id: $segment_id})
            MERGE (e)-[:SUPPORTED_BY]->(sg)
            """
            tx.run(
                support_query,
                candidate_relation_id=candidate_relation.candidate_relation_id,
                segment_id=segment.segment_id,
            ).consume()

        delta_query = """
        MERGE (d:GraphDelta {delta_id: $delta_id})
        WITH d
        MATCH (e:RelationEvidence {candidate_relation_id: $candidate_relation_id})
        MERGE (d)-[:AFFECTED_RELATION]->(e)
        """
        tx.run(
            delta_query,
            delta_id=delta.delta_id,
            candidate_relation_id=candidate_relation.candidate_relation_id,
        ).consume()

    def _upsert_graph_delta(self, tx: ManagedTransaction, delta: GraphDelta) -> None:
        query = """
        MERGE (d:GraphDelta {delta_id: $delta_id})
        SET d.run_id = $run_id,
            d.project_id = $project_id,
            d.nodes_created = $nodes_created,
            d.nodes_merged = $nodes_merged,
            d.relations_created = $relations_created,
            d.relations_merged = $relations_merged,
            d.review_count = $review_count,
            d.rejected_count = $rejected_count,
            d.created_at = datetime($created_at)
        """
        tx.run(
            query,
            delta_id=delta.delta_id,
            run_id=delta.run_id,
            project_id=delta.project_id,
            nodes_created=delta.nodes_created,
            nodes_merged=delta.nodes_merged,
            relations_created=delta.relations_created,
            relations_merged=delta.relations_merged,
            review_count=delta.review_count,
            rejected_count=delta.rejected_count,
            created_at=delta.created_at.isoformat(),
        ).consume()

    def _fetch_project_overview_counts(
        self,
        tx: ManagedTransaction,
        project_id: str,
    ) -> dict[str, int]:
        node_count_record = tx.run(
            """
            MATCH (n:CanonicalNode {project_id: $project_id})
            RETURN count(n) AS node_count
            """,
            project_id=project_id,
        ).single()
        relation_count_record = tx.run(
            """
            MATCH (from_node:CanonicalNode {project_id: $project_id})-[r]->(
                to_node:CanonicalNode {project_id: $project_id}
            )
            WHERE r.relation_type IS NOT NULL
            RETURN count(r) AS relation_count
            """,
            project_id=project_id,
        ).single()
        return {
            "node_count": int(node_count_record["node_count"]) if node_count_record else 0,
            "relation_count": (
                int(relation_count_record["relation_count"])
                if relation_count_record
                else 0
            ),
        }

    def _fetch_project_node_type_counts(
        self,
        tx: ManagedTransaction,
        project_id: str,
    ) -> list[NodeTypeCount]:
        records = tx.run(
            """
            MATCH (n:CanonicalNode {project_id: $project_id})
            RETURN n.node_type AS node_type, count(n) AS node_count
            ORDER BY node_type ASC
            """,
            project_id=project_id,
        )
        return [
            NodeTypeCount(
                node_type=str(record["node_type"]),
                count=int(record["node_count"]),
            )
            for record in records
        ]

    def _fetch_project_nodes(
        self,
        tx: ManagedTransaction,
        project_id: str,
        node_type: str | None,
        limit: int,
    ) -> list[CanonicalNodeView]:
        records = tx.run(
            """
            MATCH (n:CanonicalNode {project_id: $project_id})
            WHERE $node_type IS NULL OR n.node_type = $node_type
            RETURN n.node_type AS node_type,
                   n.merge_key AS merge_key,
                   properties(n) AS properties,
                   n.source_unit_id AS source_unit_id,
                   n.last_run_id AS last_run_id,
                   toString(n.updated_at) AS updated_at
            ORDER BY updated_at DESC, node_type ASC, merge_key ASC
            LIMIT $limit
            """,
            project_id=project_id,
            node_type=node_type,
            limit=limit,
        )
        return [
            CanonicalNodeView(
                project_id=project_id,
                node_type=str(record["node_type"]),
                merge_key=str(record["merge_key"]),
                properties=self._strip_reserved_properties(
                    dict(record["properties"]),
                    {
                        "project_id",
                        "node_type",
                        "merge_key",
                        "source_unit_id",
                        "last_run_id",
                        "updated_at",
                        "created_at",
                    },
                ),
                source_unit_id=record["source_unit_id"],
                last_run_id=record["last_run_id"],
                updated_at=record["updated_at"],
            )
            for record in records
        ]

    def _fetch_canonical_node(
        self,
        tx: ManagedTransaction,
        project_id: str,
        node_type: str,
        merge_key: str,
    ) -> CanonicalNodeView | None:
        record = tx.run(
            """
            MATCH (n:CanonicalNode {
                project_id: $project_id,
                node_type: $node_type,
                merge_key: $merge_key
            })
            RETURN n.node_type AS node_type,
                   n.merge_key AS merge_key,
                   properties(n) AS properties,
                   n.source_unit_id AS source_unit_id,
                   n.last_run_id AS last_run_id,
                   toString(n.updated_at) AS updated_at
            """,
            project_id=project_id,
            node_type=node_type,
            merge_key=merge_key,
        ).single()
        if record is None:
            return None
        return self._build_canonical_node_view(project_id, record)

    def _fetch_node_source_units(
        self,
        tx: ManagedTransaction,
        project_id: str,
        node_type: str,
        merge_key: str,
    ) -> list[CanonicalSourceUnitRef]:
        records = tx.run(
            """
            MATCH (n:CanonicalNode {
                project_id: $project_id,
                node_type: $node_type,
                merge_key: $merge_key
            })-[:DERIVED_FROM]->(su:SourceUnit)
            RETURN DISTINCT su.source_unit_id AS source_unit_id,
                            su.title AS title,
                            su.source_type AS source_type,
                            su.sequence_no AS sequence_no
            ORDER BY sequence_no ASC, source_unit_id ASC
            """,
            project_id=project_id,
            node_type=node_type,
            merge_key=merge_key,
        )
        return [
            CanonicalSourceUnitRef(
                source_unit_id=str(record["source_unit_id"]),
                title=record["title"],
                source_type=record["source_type"],
                sequence_no=(
                    int(record["sequence_no"])
                    if record["sequence_no"] is not None
                    else None
                ),
            )
            for record in records
        ]

    def _fetch_node_supporting_segments(
        self,
        tx: ManagedTransaction,
        project_id: str,
        node_type: str,
        merge_key: str,
    ) -> list[CanonicalSegmentSupport]:
        records = tx.run(
            """
            MATCH (n:CanonicalNode {
                project_id: $project_id,
                node_type: $node_type,
                merge_key: $merge_key
            })-[:SUPPORTED_BY]->(sg:Segment)
            RETURN DISTINCT sg.segment_id AS segment_id,
                            sg.source_unit_id AS source_unit_id,
                            sg.segment_order AS segment_order,
                            sg.text AS text
            ORDER BY segment_order ASC, segment_id ASC
            """,
            project_id=project_id,
            node_type=node_type,
            merge_key=merge_key,
        )
        return [
            CanonicalSegmentSupport(
                segment_id=str(record["segment_id"]),
                source_unit_id=record["source_unit_id"],
                segment_order=(
                    int(record["segment_order"])
                    if record["segment_order"] is not None
                    else None
                ),
                text=str(record["text"]),
            )
            for record in records
        ]

    def _fetch_node_connected_relations(
        self,
        tx: ManagedTransaction,
        project_id: str,
        node_type: str,
        merge_key: str,
    ) -> list[ConnectedRelationView]:
        records = tx.run(
            """
            CALL {
                MATCH (n:CanonicalNode {
                    project_id: $project_id,
                    node_type: $node_type,
                    merge_key: $merge_key
                })-[r]->(other:CanonicalNode {project_id: $project_id})
                WHERE r.relation_type IS NOT NULL
                RETURN "outgoing" AS direction,
                       r.relation_type AS relation_type,
                       other.node_type AS other_node_type,
                       other.merge_key AS other_merge_key,
                       properties(other) AS other_node_properties,
                       properties(r) AS relation_properties,
                       toString(r.updated_at) AS updated_at
                UNION ALL
                MATCH (other:CanonicalNode {project_id: $project_id})-[r]->(n:CanonicalNode {
                    project_id: $project_id,
                    node_type: $node_type,
                    merge_key: $merge_key
                })
                WHERE r.relation_type IS NOT NULL
                RETURN "incoming" AS direction,
                       r.relation_type AS relation_type,
                       other.node_type AS other_node_type,
                       other.merge_key AS other_merge_key,
                       properties(other) AS other_node_properties,
                       properties(r) AS relation_properties,
                       toString(r.updated_at) AS updated_at
            }
            RETURN direction,
                   relation_type,
                   other_node_type,
                   other_merge_key,
                   other_node_properties,
                   relation_properties,
                   updated_at
            ORDER BY updated_at DESC, relation_type ASC, other_node_type ASC, other_merge_key ASC
            """,
            project_id=project_id,
            node_type=node_type,
            merge_key=merge_key,
        )
        return [
            ConnectedRelationView(
                relation_type=str(record["relation_type"]),
                direction=str(record["direction"]),
                other_node_type=str(record["other_node_type"]),
                other_merge_key=str(record["other_merge_key"]),
                other_node_properties=self._strip_reserved_properties(
                    dict(record["other_node_properties"]),
                    {
                        "project_id",
                        "node_type",
                        "merge_key",
                        "source_unit_id",
                        "last_run_id",
                        "updated_at",
                        "created_at",
                    },
                ),
                properties=self._strip_reserved_properties(
                    dict(record["relation_properties"]),
                    {
                        "project_id",
                        "relation_type",
                        "relation_identity_key",
                        "source_unit_id",
                        "last_run_id",
                        "updated_at",
                        "created_at",
                    },
                ),
                updated_at=record["updated_at"],
            )
            for record in records
        ]

    def _fetch_project_relations(
        self,
        tx: ManagedTransaction,
        project_id: str,
        relation_type: str | None,
        limit: int,
    ) -> list[CanonicalRelationView]:
        records = tx.run(
            """
            MATCH (from_node:CanonicalNode {project_id: $project_id})-[r]->(
                to_node:CanonicalNode {project_id: $project_id}
            )
            WHERE r.relation_type IS NOT NULL
              AND ($relation_type IS NULL OR r.relation_type = $relation_type)
            RETURN r.relation_type AS relation_type,
                   from_node.node_type AS from_node_type,
                   from_node.merge_key AS from_merge_key,
                   to_node.node_type AS to_node_type,
                   to_node.merge_key AS to_merge_key,
                   properties(r) AS properties,
                   r.source_unit_id AS source_unit_id,
                   r.last_run_id AS last_run_id,
                   toString(r.updated_at) AS updated_at
            ORDER BY updated_at DESC, relation_type ASC, from_merge_key ASC, to_merge_key ASC
            LIMIT $limit
            """,
            project_id=project_id,
            relation_type=relation_type,
            limit=limit,
        )
        return [
            CanonicalRelationView(
                project_id=project_id,
                relation_type=str(record["relation_type"]),
                from_node_type=str(record["from_node_type"]),
                from_merge_key=str(record["from_merge_key"]),
                to_node_type=str(record["to_node_type"]),
                to_merge_key=str(record["to_merge_key"]),
                properties=self._strip_reserved_properties(
                    dict(record["properties"]),
                    {
                        "project_id",
                        "relation_type",
                        "relation_identity_key",
                        "source_unit_id",
                        "last_run_id",
                        "updated_at",
                        "created_at",
                    },
                ),
                source_unit_id=record["source_unit_id"],
                last_run_id=record["last_run_id"],
                updated_at=record["updated_at"],
            )
            for record in records
        ]

    def _fetch_canonical_relation_detail_payload(
        self,
        tx: ManagedTransaction,
        project_id: str,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
        relation_identity_key: str | None,
    ) -> tuple[
        CanonicalRelationView,
        CanonicalRelationEndpointView,
        CanonicalRelationEndpointView,
        str,
    ] | None:
        record = tx.run(
            """
            MATCH (from_node:CanonicalNode {
                project_id: $project_id,
                node_type: $from_node_type,
                merge_key: $from_merge_key
            })-[r]->(to_node:CanonicalNode {
                project_id: $project_id,
                node_type: $to_node_type,
                merge_key: $to_merge_key
            })
            WHERE r.project_id = $project_id
              AND r.relation_type = $relation_type
              AND (
                $relation_identity_key IS NULL
                OR r.relation_identity_key = $relation_identity_key
              )
            RETURN r.relation_type AS relation_type,
                   r.relation_identity_key AS relation_identity_key,
                   from_node.node_type AS from_node_type,
                   from_node.merge_key AS from_merge_key,
                   to_node.node_type AS to_node_type,
                   to_node.merge_key AS to_merge_key,
                   properties(r) AS relation_properties,
                   r.source_unit_id AS source_unit_id,
                   r.last_run_id AS last_run_id,
                   toString(r.updated_at) AS updated_at,
                   properties(from_node) AS from_node_properties,
                   properties(to_node) AS to_node_properties
            ORDER BY relation_identity_key ASC
            LIMIT 1
            """,
            project_id=project_id,
            relation_type=relation_type,
            from_node_type=from_node_type,
            from_merge_key=from_merge_key,
            to_node_type=to_node_type,
            to_merge_key=to_merge_key,
            relation_identity_key=relation_identity_key,
        ).single()
        if record is None:
            return None

        relation = self._build_canonical_relation_view(project_id, record)
        from_node = CanonicalRelationEndpointView(
            node_type=str(record["from_node_type"]),
            merge_key=str(record["from_merge_key"]),
            properties=self._strip_reserved_properties(
                dict(record["from_node_properties"]),
                {
                    "project_id",
                    "node_type",
                    "merge_key",
                    "source_unit_id",
                    "last_run_id",
                    "updated_at",
                    "created_at",
                },
            ),
        )
        to_node = CanonicalRelationEndpointView(
            node_type=str(record["to_node_type"]),
            merge_key=str(record["to_merge_key"]),
            properties=self._strip_reserved_properties(
                dict(record["to_node_properties"]),
                {
                    "project_id",
                    "node_type",
                    "merge_key",
                    "source_unit_id",
                    "last_run_id",
                    "updated_at",
                    "created_at",
                },
            ),
        )
        return relation, from_node, to_node, str(record["relation_identity_key"])

    def _fetch_relation_source_units(
        self,
        tx: ManagedTransaction,
        project_id: str,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
        relation_identity_key: str,
    ) -> list[CanonicalSourceUnitRef]:
        records = tx.run(
            """
            MATCH (from_node:CanonicalNode {
                project_id: $project_id,
                node_type: $from_node_type,
                merge_key: $from_merge_key
            })
            MATCH (to_node:CanonicalNode {
                project_id: $project_id,
                node_type: $to_node_type,
                merge_key: $to_merge_key
            })
            MATCH (e:RelationEvidence {
                project_id: $project_id,
                relation_type: $relation_type,
                relation_identity_key: $relation_identity_key
            })-[:FROM_NODE]->(from_node)
            MATCH (e)-[:TO_NODE]->(to_node)
            MATCH (e)-[:DERIVED_FROM]->(su:SourceUnit)
            RETURN DISTINCT su.source_unit_id AS source_unit_id,
                            su.title AS title,
                            su.source_type AS source_type,
                            su.sequence_no AS sequence_no
            ORDER BY sequence_no ASC, source_unit_id ASC
            """,
            project_id=project_id,
            relation_type=relation_type,
            from_node_type=from_node_type,
            from_merge_key=from_merge_key,
            to_node_type=to_node_type,
            to_merge_key=to_merge_key,
            relation_identity_key=relation_identity_key,
        )
        return [
            CanonicalSourceUnitRef(
                source_unit_id=str(record["source_unit_id"]),
                title=record["title"],
                source_type=record["source_type"],
                sequence_no=(
                    int(record["sequence_no"])
                    if record["sequence_no"] is not None
                    else None
                ),
            )
            for record in records
        ]

    def _fetch_relation_supporting_segments(
        self,
        tx: ManagedTransaction,
        project_id: str,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
        relation_identity_key: str,
    ) -> list[CanonicalSegmentSupport]:
        records = tx.run(
            """
            MATCH (from_node:CanonicalNode {
                project_id: $project_id,
                node_type: $from_node_type,
                merge_key: $from_merge_key
            })
            MATCH (to_node:CanonicalNode {
                project_id: $project_id,
                node_type: $to_node_type,
                merge_key: $to_merge_key
            })
            MATCH (e:RelationEvidence {
                project_id: $project_id,
                relation_type: $relation_type,
                relation_identity_key: $relation_identity_key
            })-[:FROM_NODE]->(from_node)
            MATCH (e)-[:TO_NODE]->(to_node)
            MATCH (e)-[:SUPPORTED_BY]->(sg:Segment)
            RETURN DISTINCT sg.segment_id AS segment_id,
                            sg.source_unit_id AS source_unit_id,
                            sg.segment_order AS segment_order,
                            sg.text AS text
            ORDER BY segment_order ASC, segment_id ASC
            """,
            project_id=project_id,
            relation_type=relation_type,
            from_node_type=from_node_type,
            from_merge_key=from_merge_key,
            to_node_type=to_node_type,
            to_merge_key=to_merge_key,
            relation_identity_key=relation_identity_key,
        )
        return [
            CanonicalSegmentSupport(
                segment_id=str(record["segment_id"]),
                source_unit_id=record["source_unit_id"],
                segment_order=(
                    int(record["segment_order"])
                    if record["segment_order"] is not None
                    else None
                ),
                text=str(record["text"]),
            )
            for record in records
        ]

    def _build_merge_key(self, candidate_node: CandidateNode) -> str:
        return build_canonical_merge_key(
            merge_key_payload=candidate_node.merge_key_payload,
            fallback_payload={"candidate_node_id": candidate_node.candidate_node_id},
        )

    def _quoted_identifier(self, value: str) -> str:
        if not IDENTIFIER_PATTERN.match(value):
            raise ValueError(f"Invalid Neo4j identifier '{value}'.")
        return f"`{value}`"

    def _sanitize_property_map(self, properties: dict[str, object]) -> dict[str, object]:
        sanitized: dict[str, object] = {}
        for key, value in properties.items():
            if value is None:
                continue
            sanitized[key] = self._sanitize_property_value(value)
        return sanitized

    def _sanitize_property_value(self, value: object) -> object:
        if isinstance(value, (str, bool, int, float)):
            return value
        if isinstance(value, list):
            if all(isinstance(item, (str, bool, int, float)) for item in value):
                return value
            return json.dumps(value, sort_keys=True, default=str)
        if isinstance(value, dict):
            return json.dumps(value, sort_keys=True, default=str)
        return str(value)

    def _strip_reserved_properties(
        self,
        properties: dict[str, object],
        reserved_keys: set[str],
    ) -> dict[str, object]:
        return {
            key: value
            for key, value in properties.items()
            if key not in reserved_keys
        }

    def _build_canonical_node_view(
        self,
        project_id: str,
        record: Any,
    ) -> CanonicalNodeView:
        return CanonicalNodeView(
            project_id=project_id,
            node_type=str(record["node_type"]),
            merge_key=str(record["merge_key"]),
            properties=self._strip_reserved_properties(
                dict(record["properties"]),
                {
                    "project_id",
                    "node_type",
                    "merge_key",
                    "source_unit_id",
                    "last_run_id",
                    "updated_at",
                    "created_at",
                },
            ),
            source_unit_id=record["source_unit_id"],
            last_run_id=record["last_run_id"],
            updated_at=record["updated_at"],
        )

    def _build_canonical_relation_view(
        self,
        project_id: str,
        record: Any,
    ) -> CanonicalRelationView:
        relation_properties = (
            record["properties"]
            if "properties" in record.keys()
            else record["relation_properties"]
        )
        return CanonicalRelationView(
            project_id=project_id,
            relation_type=str(record["relation_type"]),
            from_node_type=str(record["from_node_type"]),
            from_merge_key=str(record["from_merge_key"]),
            to_node_type=str(record["to_node_type"]),
            to_merge_key=str(record["to_merge_key"]),
            properties=self._strip_reserved_properties(
                dict(relation_properties),
                {
                    "project_id",
                    "relation_type",
                    "relation_identity_key",
                    "source_unit_id",
                    "last_run_id",
                    "updated_at",
                    "created_at",
                },
            ),
            source_unit_id=record["source_unit_id"],
            last_run_id=record["last_run_id"],
            updated_at=record["updated_at"],
        )
