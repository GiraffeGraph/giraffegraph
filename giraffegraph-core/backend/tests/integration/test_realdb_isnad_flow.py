from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.bootstrap.container import get_container
from app.domain.graph_commit.entities import CanonicalCommitBundle
from app.domain.shared.enums import CandidateStatus
from app.domain.shared.resolution import build_relation_identity_key
from app.infrastructure.persistence.neo4j.database import get_neo4j_driver
from app.infrastructure.persistence.neo4j.repositories import Neo4jCanonicalGraphRepository
from app.infrastructure.persistence.postgres.database import get_postgres_engine
from app.infrastructure.persistence.postgres.repositories import PostgresProjectRepository
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_ID, ISNAD_TEMPLATE_SCHEMA
from test_helpers import create_pipeline_definition

pytestmark = pytest.mark.real_db

NARRATED_FROM_MERGE_KEYS = ["hadith_ref", "chain_no", "position"]
TAHWIL_HADITH = (
    "Muslim:978",
    "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، "
    "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ",
)
SINGLE_CHAIN_HADITH = ("Bukhari:1", "حَدَّثَنَا سُفْيَانُ ، عَنِ ابْنِ شِهَابٍ ، عَنْ أَنَسٍ")
NO_CHAIN_TEXT = ("Note:7", "قَالَ رَجُلٌ لِصَاحِبِهِ")
FIRST_SHARED_LINK_HADITH = ("Bukhari:10", "حَدَّثَنَا سُفْيَانُ ، عَنِ الزُّهْرِيِّ ، عَنْ أَنَسٍ")
SECOND_SHARED_LINK_HADITH = ("Muslim:20", "أَخْبَرَنَا سُفْيَانُ ، عَنِ الزُّهْرِيِّ ، عَنْ سَالِمٍ")


def _create_isnad_project(client: TestClient) -> tuple[str, str]:
    project_id = client.post(
        "/api/projects",
        json={"name": "Isnad on real databases", "template_id": ISNAD_TEMPLATE_ID},
    ).json()["project_id"]
    schema_id = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1},
    ).json()["schema_version_id"]
    for node_type in ISNAD_TEMPLATE_SCHEMA.node_types:
        response = client.post(
            f"/api/schema-versions/{schema_id}/node-types",
            json=node_type.model_dump(),
        )
        assert response.status_code == 201, response.text
    for relation_type in ISNAD_TEMPLATE_SCHEMA.relation_types:
        response = client.post(
            f"/api/schema-versions/{schema_id}/relation-types",
            json=relation_type.model_dump(),
        )
        assert response.status_code == 201, response.text
    create_pipeline_definition(client, schema_id=schema_id)
    response = client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    assert response.status_code == 200, response.text
    return project_id, schema_id


def _prepare_validated_run(
    client: TestClient,
    *,
    project_id: str,
    schema_id: str,
    hadith: tuple[str, str],
) -> dict[str, Any]:
    hadith_ref, raw_content = hadith
    source_unit_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "hadith",
            "title": hadith_ref,
            "raw_content": raw_content,
            "external_ref": hadith_ref,
        },
    ).json()["source_unit_id"]
    run_id = client.post(
        f"/api/source-units/{source_unit_id}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "rule_based_isnad",
        },
    ).json()["run_id"]
    segments_response = client.post(
        f"/api/source-units/{source_unit_id}/segments/generate",
        json={"strategy": ISNAD_TEMPLATE_SCHEMA.segmentation_strategy},
    )
    assert segments_response.status_code == 201, segments_response.text
    extraction = client.post(f"/api/runs/{run_id}/extract-candidates", json={})
    assert extraction.status_code == 200, extraction.text
    validation = client.post(f"/api/runs/{run_id}/validate")
    assert validation.status_code == 200, validation.text
    return {
        "hadith_ref": hadith_ref,
        "source_unit_id": source_unit_id,
        "run_id": run_id,
        "segments": segments_response.json(),
    }


def _commit_hadith(
    client: TestClient,
    *,
    project_id: str,
    schema_id: str,
    hadith: tuple[str, str],
) -> dict[str, Any]:
    run = _prepare_validated_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        hadith=hadith,
    )
    commit = client.post(f"/api/runs/{run['run_id']}/commit")
    assert commit.status_code == 200, commit.text
    return {**run, "delta": commit.json()}


def _graph_rows(query: str, **parameters: object) -> list[dict[str, Any]]:
    records, _, _ = get_neo4j_driver().execute_query(query, **parameters)
    return [record.data() for record in records]


def _graph_counts(project_id: str) -> dict[str, int]:
    return {
        "canonical_nodes": _graph_rows(
            "MATCH (n:CanonicalNode {project_id: $project_id}) RETURN count(n) AS total",
            project_id=project_id,
        )[0]["total"],
        "canonical_edges": _graph_rows(
            "MATCH (:CanonicalNode {project_id: $project_id})-[r]->(:CanonicalNode) "
            "RETURN count(r) AS total",
            project_id=project_id,
        )[0]["total"],
        "relation_evidence": _graph_rows(
            "MATCH (e:RelationEvidence {project_id: $project_id}) RETURN count(e) AS total",
            project_id=project_id,
        )[0]["total"],
        "graph_deltas": _graph_rows(
            "MATCH (d:GraphDelta {project_id: $project_id}) RETURN count(d) AS total",
            project_id=project_id,
        )[0]["total"],
        "source_units": _graph_rows(
            "MATCH (su:SourceUnit {project_id: $project_id}) RETURN count(su) AS total",
            project_id=project_id,
        )[0]["total"],
    }


def _node_by_name(client: TestClient, project_id: str, name: str) -> dict[str, Any]:
    nodes = client.get(
        f"/api/projects/{project_id}/graph/nodes",
        params={"node_type": "Narrator"},
    ).json()
    matches = [node for node in nodes if node["properties"]["name"] == name]
    assert len(matches) == 1
    return dict(matches[0])


def test_application_is_wired_to_postgres_and_neo4j(real_db_client: TestClient) -> None:
    container = get_container()

    assert real_db_client.get("/health").status_code == 200
    assert isinstance(
        container.project_management_service.project_repository,
        PostgresProjectRepository,
    )
    assert isinstance(
        container.commit_management_service.canonical_graph_repository,
        Neo4jCanonicalGraphRepository,
    )


def test_relation_merge_keys_round_trip_through_postgres(real_db_client: TestClient) -> None:
    _, schema_id = _create_isnad_project(real_db_client)

    schema = real_db_client.get(f"/api/schema-versions/{schema_id}").json()

    assert {item["name"]: item["merge_keys"] for item in schema["relation_types"]} == {
        "NARRATED_FROM": NARRATED_FROM_MERGE_KEYS,
        "TRANSMITS": [],
    }
    with get_postgres_engine().connect() as connection:
        stored = connection.execute(
            text(
                "SELECT name, merge_keys, jsonb_typeof(merge_keys) FROM relation_types "
                "WHERE schema_version_id = :schema_id ORDER BY name"
            ),
            {"schema_id": schema_id},
        ).all()
    assert [tuple(row) for row in stored] == [
        ("NARRATED_FROM", NARRATED_FROM_MERGE_KEYS, "array"),
        ("TRANSMITS", [], "array"),
    ]


def test_rule_based_baseline_commits_three_hadiths_with_acceptance_records(
    real_db_client: TestClient,
) -> None:
    client = real_db_client
    project_id, schema_id = _create_isnad_project(client)

    committed = [
        _commit_hadith(client, project_id=project_id, schema_id=schema_id, hadith=hadith)
        for hadith in (TAHWIL_HADITH, SINGLE_CHAIN_HADITH, NO_CHAIN_TEXT)
    ]

    runs = client.get(f"/api/projects/{project_id}/runs").json()
    assert sorted(run["status"] for run in runs) == ["completed"] * 3
    fact_count = 0
    for hadith in committed:
        run_id = hadith["run_id"]
        segment_texts = {segment["segment_id"]: segment["text"] for segment in hadith["segments"]}
        records = {
            record["candidate_ref"]: record
            for record in client.get(f"/api/runs/{run_id}/acceptance-records").json()
        }
        facts = [
            (node["candidate_node_id"], node)
            for node in client.get(f"/api/runs/{run_id}/candidate-nodes").json()
        ] + [
            (relation["candidate_relation_id"], relation)
            for relation in client.get(f"/api/runs/{run_id}/candidate-relations").json()
        ]
        assert client.get(f"/api/runs/{run_id}/review-items").json() == []
        for candidate_ref, fact in facts:
            assert fact["status"] == "validated"
            assert any(
                evidence["quote"] in segment_texts[evidence["segment_id"]]
                for evidence in fact["evidence_refs"]
            )
            assert records[candidate_ref]["policy"] == "auto_validated"
            assert records[candidate_ref]["decision"] is None
            fact_count += 1
        assert client.get(f"/api/runs/{run_id}/graph-delta").json() == hadith["delta"]
    assert fact_count == 8 + 5
    assert [
        (
            hadith["delta"]["nodes_created"],
            hadith["delta"]["nodes_merged"],
            hadith["delta"]["relations_created"],
        )
        for hadith in committed
    ] == [(5, 0, 3), (2, 1, 2), (0, 0, 0)]
    overview = client.get(f"/api/projects/{project_id}/graph/overview").json()
    assert (overview["node_count"], overview["relation_count"]) == (7, 5)
    assert overview["node_type_counts"] == [{"node_type": "Narrator", "count": 7}]
    assert _graph_counts(project_id) == {
        "canonical_nodes": 7,
        "canonical_edges": 5,
        "relation_evidence": 5,
        "graph_deltas": 3,
        "source_units": 3,
    }


def test_exploration_endpoints_return_the_committed_graph_with_evidence(
    real_db_client: TestClient,
) -> None:
    client = real_db_client
    project_id, schema_id = _create_isnad_project(client)
    tahwil = _commit_hadith(
        client, project_id=project_id, schema_id=schema_id, hadith=TAHWIL_HADITH
    )
    single = _commit_hadith(
        client, project_id=project_id, schema_id=schema_id, hadith=SINGLE_CHAIN_HADITH
    )

    shared_narrator = _node_by_name(client, project_id, "ابْنِ شِهَابٍ")
    node_detail = client.get(
        f"/api/projects/{project_id}/graph/nodes/Narrator/{shared_narrator['merge_key']}"
    ).json()
    assert sorted(item["source_unit_id"] for item in node_detail["source_units"]) == sorted(
        [tahwil["source_unit_id"], single["source_unit_id"]]
    )
    assert sorted(item["text"] for item in node_detail["supporting_segments"]) == sorted(
        [tahwil["segments"][1]["text"], single["segments"][0]["text"]]
    )
    assert sorted(
        (relation["direction"], relation["other_node_properties"]["name"])
        for relation in node_detail["connected_relations"]
    ) == sorted(
        [("incoming", "اللَّيْثُ"), ("incoming", "سُفْيَانُ"), ("outgoing", "أَنَسٍ")]
    )

    relations = client.get(
        f"/api/projects/{project_id}/graph/relations",
        params={"relation_type": "NARRATED_FROM"},
    ).json()
    assert sorted(
        (
            relation["properties"]["hadith_ref"],
            relation["properties"]["chain_no"],
            relation["properties"]["position"],
        )
        for relation in relations
    ) == [
        ("Bukhari:1", 1, 1),
        ("Bukhari:1", 1, 2),
        ("Muslim:978", 1, 1),
        ("Muslim:978", 2, 1),
        ("Muslim:978", 2, 2),
    ]
    last_link = next(
        relation
        for relation in relations
        if relation["properties"]["hadith_ref"] == "Bukhari:1"
        and relation["properties"]["position"] == 2
    )
    relation_detail = client.get(
        f"/api/projects/{project_id}/graph/relations/NARRATED_FROM"
        f"/Narrator/{last_link['from_merge_key']}/Narrator/{last_link['to_merge_key']}"
    ).json()
    assert relation_detail["relation"]["properties"] == last_link["properties"]
    assert relation_detail["from_node"]["properties"]["name"] == "ابْنِ شِهَابٍ"
    assert relation_detail["to_node"]["properties"]["name"] == "أَنَسٍ"
    assert [item["source_unit_id"] for item in relation_detail["source_units"]] == [
        single["source_unit_id"]
    ]
    assert [item["text"] for item in relation_detail["supporting_segments"]] == [
        single["segments"][0]["text"]
    ]


def test_same_narrator_pair_in_two_hadiths_is_two_edges_and_recommit_adds_none(
    real_db_client: TestClient,
) -> None:
    client = real_db_client
    project_id, schema_id = _create_isnad_project(client)
    hadiths = [
        _commit_hadith(client, project_id=project_id, schema_id=schema_id, hadith=hadith)
        for hadith in (FIRST_SHARED_LINK_HADITH, SECOND_SHARED_LINK_HADITH)
    ]

    shared_edges = _graph_rows(
        """
        MATCH (from_node:CanonicalNode {project_id: $project_id, name: $from_name})
              -[r:NARRATED_FROM]->
              (to_node:CanonicalNode {project_id: $project_id, name: $to_name})
        RETURN r.hadith_ref AS hadith_ref,
               r.relation_identity_key AS relation_identity_key,
               from_node.merge_key AS from_merge_key,
               to_node.merge_key AS to_merge_key
        ORDER BY hadith_ref
        """,
        project_id=project_id,
        from_name="سُفْيَانُ",
        to_name="الزُّهْرِيِّ",
    )
    assert [edge["hadith_ref"] for edge in shared_edges] == ["Bukhari:10", "Muslim:20"]
    assert [edge["relation_identity_key"] for edge in shared_edges] == [
        build_relation_identity_key(
            merge_keys=NARRATED_FROM_MERGE_KEYS,
            properties={"hadith_ref": hadith["hadith_ref"], "chain_no": 1, "position": 1},
        )
        for hadith in hadiths
    ]
    graph_repository = get_container().commit_management_service.canonical_graph_repository
    for edge, hadith in zip(shared_edges, hadiths, strict=True):
        detail = graph_repository.get_relation_detail(
            project_id,
            relation_type="NARRATED_FROM",
            from_node_type="Narrator",
            from_merge_key=edge["from_merge_key"],
            to_node_type="Narrator",
            to_merge_key=edge["to_merge_key"],
            relation_identity_key=edge["relation_identity_key"],
        )
        assert detail is not None
        assert detail.relation.properties["hadith_ref"] == hadith["hadith_ref"]
        assert [item.source_unit_id for item in detail.source_units] == [
            hadith["source_unit_id"]
        ]
        assert [item.text for item in detail.supporting_segments] == [
            hadith["segments"][0]["text"]
        ]

    counts_after_first_commit = _graph_counts(project_id)
    assert counts_after_first_commit == {
        "canonical_nodes": 4,
        "canonical_edges": 4,
        "relation_evidence": 4,
        "graph_deltas": 2,
        "source_units": 2,
    }
    assert client.post(f"/api/runs/{hadiths[0]['run_id']}/commit").status_code == 409
    service = get_container().commit_management_service
    run_id = hadiths[0]["run_id"]
    delta = service.graph_delta_repository.get_by_run(run_id)
    source_unit = service.source_unit_repository.get(hadiths[0]["source_unit_id"])
    assert delta is not None and source_unit is not None
    candidate_relations = [
        relation
        for relation in service.candidate_relation_repository.list_by_run(run_id)
        if relation.status == CandidateStatus.VALIDATED
    ]

    recommitted = graph_repository.commit_bundle(
        CanonicalCommitBundle(
            delta=delta,
            source_unit=source_unit,
            segments=service.segment_repository.list_by_source_unit(source_unit.source_unit_id),
            candidate_nodes=[
                node
                for node in service.candidate_node_repository.list_by_run(run_id)
                if node.status == CandidateStatus.VALIDATED
            ],
            candidate_relations=candidate_relations,
        ),
        relation_identity_keys={
            relation.candidate_relation_id: build_relation_identity_key(
                merge_keys=NARRATED_FROM_MERGE_KEYS,
                properties=relation.properties,
            )
            for relation in candidate_relations
        },
    )

    assert (recommitted.nodes_created, recommitted.nodes_merged) == (0, 3)
    assert (recommitted.relations_created, recommitted.relations_merged) == (0, 2)
    assert _graph_counts(project_id) == counts_after_first_commit


def test_failed_graph_write_leaves_no_partial_graph_and_the_run_can_be_committed_again(
    real_db_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = real_db_client
    project_id, schema_id = _create_isnad_project(client)
    run = _prepare_validated_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        hadith=SINGLE_CHAIN_HADITH,
    )
    relation_writes = 0
    write_relation = Neo4jCanonicalGraphRepository._merge_candidate_relation

    def fail_on_second_relation(*args: Any, **kwargs: Any) -> bool:
        nonlocal relation_writes
        relation_writes += 1
        if relation_writes == 2:
            raise RuntimeError("graph write interrupted")
        return write_relation(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(
            Neo4jCanonicalGraphRepository,
            "_merge_candidate_relation",
            fail_on_second_relation,
        )
        with pytest.raises(RuntimeError, match="graph write interrupted"):
            client.post(f"/api/runs/{run['run_id']}/commit")

    assert relation_writes == 2
    assert _graph_counts(project_id) == {
        "canonical_nodes": 0,
        "canonical_edges": 0,
        "relation_evidence": 0,
        "graph_deltas": 0,
        "source_units": 0,
    }
    assert client.get(f"/api/runs/{run['run_id']}").json()["status"] == "failed"
    assert client.get(f"/api/runs/{run['run_id']}/graph-delta").status_code == 404

    retry = client.post(f"/api/runs/{run['run_id']}/commit")

    assert retry.status_code == 200, retry.text
    assert (retry.json()["nodes_created"], retry.json()["relations_created"]) == (3, 2)
    assert client.get(f"/api/runs/{run['run_id']}").json()["status"] == "completed"
    assert _graph_counts(project_id) == {
        "canonical_nodes": 3,
        "canonical_edges": 2,
        "relation_evidence": 2,
        "graph_deltas": 1,
        "source_units": 1,
    }


def test_commit_creates_the_lookup_indexes_its_merges_rely_on(real_db_client: TestClient) -> None:
    client = real_db_client
    project_id, schema_id = _create_isnad_project(client)

    _commit_hadith(client, project_id=project_id, schema_id=schema_id, hadith=SINGLE_CHAIN_HADITH)

    get_neo4j_driver().execute_query("CALL db.awaitIndexes(60)")
    indexed = {
        (tuple(row["labelsOrTypes"]), tuple(row["properties"]))
        for row in _graph_rows(
            "SHOW INDEXES YIELD type, labelsOrTypes, properties WHERE type = 'RANGE'"
        )
    }
    assert indexed >= {
        (("CanonicalNode",), ("project_id", "node_type", "merge_key")),
        (("SourceUnit",), ("source_unit_id",)),
        (("Segment",), ("segment_id",)),
        (("RelationEvidence",), ("candidate_relation_id",)),
        (("GraphDelta",), ("delta_id",)),
    }
    plan = (
        get_neo4j_driver()
        .execute_query(
            "EXPLAIN MATCH (n:CanonicalNode {project_id: $project_id, node_type: $node_type, "
            "merge_key: $merge_key}) RETURN n",
            project_id=project_id,
            node_type="Narrator",
            merge_key="any",
        )
        .summary.plan
    )
    assert plan is not None
    assert "NodeIndexSeek" in str(plan)
