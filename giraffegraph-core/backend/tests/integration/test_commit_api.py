from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.domain.shared.enums import CandidateStatus, ReviewStatus
from test_helpers import create_pipeline_definition


def test_commit_flow_creates_graph_delta_and_updates_statuses() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project_response = client.post(
        "/api/projects",
        json={
            "name": "Commit Lab",
            "description": "Graph delta baseline",
            "template_id": "story",
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["project_id"]

    schema_response = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Commit schema"},
    )
    assert schema_response.status_code == 201
    schema_id = schema_response.json()["schema_version_id"]

    client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Character",
            "display_name": "Character",
            "description": "Narrative actor",
            "merge_keys": ["name"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Event",
            "display_name": "Event",
            "description": "Narrative event",
            "merge_keys": ["title"],
            "properties": [{"name": "title", "data_type": "string", "required": True}],
        },
    )
    client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "INVOLVED_IN",
            "from_type": "Character",
            "to_type": "Event",
            "description": "Character is involved in event",
            "confidence_threshold": 0.7,
            "required_properties": ["role"],
            "properties": [{"name": "role", "data_type": "string", "required": True}],
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali walks in.\n\nA fight starts.",
            "sequence_no": 1,
        },
    )
    source_id = source_response.json()["source_unit_id"]

    run_response = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    )
    run_id = run_response.json()["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    character_candidate = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()

    event_candidate = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": "Fight"},
            "merge_key_payload": {"title": "Fight"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[1]["segment_id"]}],
        },
    ).json()

    client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": character_candidate["candidate_node_id"],
            "to_candidate_ref": event_candidate["candidate_node_id"],
            "properties": {"role": "participant"},
            "confidence": 0.95,
        },
    )

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200
    validation = validation_response.json()
    assert validation["node_validated"] == 2
    assert validation["relation_validated"] == 1

    review_items_response = client.get(f"/api/runs/{run_id}/review-items")
    assert review_items_response.status_code == 200
    assert review_items_response.json() == []

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    graph_delta = commit_response.json()
    assert graph_delta["project_id"] == project_id
    assert graph_delta["nodes_created"] == 2
    assert graph_delta["relations_created"] == 1
    assert graph_delta["review_count"] == 0
    assert graph_delta["rejected_count"] == 0

    get_graph_delta_response = client.get(f"/api/runs/{run_id}/graph-delta")
    assert get_graph_delta_response.status_code == 200
    assert get_graph_delta_response.json()["delta_id"] == graph_delta["delta_id"]

    run_detail_response = client.get(f"/api/runs/{run_id}")
    assert run_detail_response.status_code == 200
    assert run_detail_response.json()["status"] == "completed"

    source_detail_response = client.get(f"/api/source-units/{source_id}")
    assert source_detail_response.status_code == 200
    assert source_detail_response.json()["status"] == "processed"

    completed_run_mutation_response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Later edit"},
            "merge_key_payload": {"name": "Later edit"},
            "confidence": 0.9,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )
    assert completed_run_mutation_response.status_code == 422

    overview_response = client.get(f"/api/projects/{project_id}/graph/overview")
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["node_count"] == 2
    assert overview["relation_count"] == 1
    assert overview["node_type_counts"] == [
        {"node_type": "Character", "count": 1},
        {"node_type": "Event", "count": 1},
    ]


def _create_relation_project(
    client: TestClient,
    *,
    relation_merge_keys: list[str],
) -> tuple[str, str]:
    project_id = client.post(
        "/api/projects",
        json={"name": "Relation Identity Lab", "template_id": "blank"},
    ).json()["project_id"]
    schema_id = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1},
    ).json()["schema_version_id"]
    node_type_response = client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Person",
            "display_name": "Person",
            "description": "A person",
            "merge_keys": ["name"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    assert node_type_response.status_code == 201
    relation_type_response = client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "TOLD",
            "from_type": "Person",
            "to_type": "Person",
            "description": "One person told another",
            "merge_keys": relation_merge_keys,
            "properties": [
                {"name": "report_id", "data_type": "string"},
                {"name": "wording", "data_type": "string"},
            ],
        },
    )
    assert relation_type_response.status_code == 201
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    return project_id, schema_id


def _start_run_with_pair(
    client: TestClient,
    *,
    project_id: str,
    schema_id: str,
    title: str,
) -> tuple[str, str, str]:
    source_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "report",
            "title": title,
            "raw_content": "Ali told Veli.",
        },
    ).json()["source_unit_id"]
    run_id = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()["run_id"]
    node_ids = [
        client.post(
            f"/api/runs/{run_id}/candidate-nodes",
            json={"node_type": "Person", "properties": {"name": name}, "confidence": 0.95},
        ).json()["candidate_node_id"]
        for name in ("Ali", "Veli")
    ]
    return run_id, node_ids[0], node_ids[1]


def _add_relation(
    client: TestClient,
    *,
    run_id: str,
    from_id: str,
    to_id: str,
    properties: dict[str, object],
) -> str:
    response = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "TOLD",
            "from_candidate_ref": from_id,
            "to_candidate_ref": to_id,
            "properties": properties,
            "confidence": 0.95,
        },
    )
    assert response.status_code == 201
    return str(response.json()["candidate_relation_id"])


def _force_relations_validated(run_id: str) -> None:
    service = get_container().commit_management_service
    for relation in service.candidate_relation_repository.list_by_run(run_id):
        relation.status = CandidateStatus.VALIDATED
        service.candidate_relation_repository.save(relation)
    for review_item in service.review_item_repository.list_by_run(run_id):
        review_item.status = ReviewStatus.ACCEPTED
        service.review_item_repository.save(review_item)


def test_commit_keeps_relations_with_different_merge_key_values_as_distinct_edges() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_relation_project(client, relation_merge_keys=["report_id"])
    run_id, from_id, to_id = _start_run_with_pair(
        client, project_id=project_id, schema_id=schema_id, title="Reports"
    )
    first_properties = {"report_id": "r-1", "wording": "told us"}
    second_properties = {"report_id": "r-2", "wording": "informed us"}
    for properties in (first_properties, second_properties):
        _add_relation(
            client, run_id=run_id, from_id=from_id, to_id=to_id, properties=properties
        )

    validation = client.post(f"/api/runs/{run_id}/validate").json()
    assert validation["relation_validated"] == 2
    assert client.get(f"/api/runs/{run_id}/review-items").json() == []

    graph_delta = client.post(f"/api/runs/{run_id}/commit").json()
    assert graph_delta["relations_created"] == 2
    assert graph_delta["relations_merged"] == 0

    relations = client.get(f"/api/projects/{project_id}/graph/relations").json()
    assert len(relations) == 2
    assert sorted(
        (relation["properties"] for relation in relations),
        key=lambda properties: properties["report_id"],
    ) == [first_properties, second_properties]
    overview = client.get(f"/api/projects/{project_id}/graph/overview").json()
    assert overview["relation_count"] == 2


def test_commit_merges_relations_with_same_merge_key_values_into_one_edge() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_relation_project(client, relation_merge_keys=["report_id"])

    deltas = []
    for title in ("First pass", "Second pass"):
        run_id, from_id, to_id = _start_run_with_pair(
            client, project_id=project_id, schema_id=schema_id, title=title
        )
        _add_relation(
            client,
            run_id=run_id,
            from_id=from_id,
            to_id=to_id,
            properties={"report_id": "r-1", "wording": "told us"},
        )
        assert client.post(f"/api/runs/{run_id}/validate").status_code == 200
        commit_response = client.post(f"/api/runs/{run_id}/commit")
        assert commit_response.status_code == 200
        deltas.append(commit_response.json())

    assert (deltas[0]["relations_created"], deltas[0]["relations_merged"]) == (1, 0)
    assert (deltas[1]["relations_created"], deltas[1]["relations_merged"]) == (0, 1)
    relations = client.get(f"/api/projects/{project_id}/graph/relations").json()
    assert len(relations) == 1
    assert relations[0]["properties"] == {"report_id": "r-1", "wording": "told us"}


def test_validation_reports_canonical_match_only_for_same_relation_identity() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_relation_project(client, relation_merge_keys=["report_id"])
    first_run_id, from_id, to_id = _start_run_with_pair(
        client, project_id=project_id, schema_id=schema_id, title="First pass"
    )
    _add_relation(
        client,
        run_id=first_run_id,
        from_id=from_id,
        to_id=to_id,
        properties={"report_id": "r-1"},
    )
    client.post(f"/api/runs/{first_run_id}/validate")
    assert client.post(f"/api/runs/{first_run_id}/commit").status_code == 200

    second_run_id, from_id, to_id = _start_run_with_pair(
        client, project_id=project_id, schema_id=schema_id, title="Second pass"
    )
    same_identity_id = _add_relation(
        client,
        run_id=second_run_id,
        from_id=from_id,
        to_id=to_id,
        properties={"report_id": "r-1"},
    )
    other_identity_id = _add_relation(
        client,
        run_id=second_run_id,
        from_id=from_id,
        to_id=to_id,
        properties={"report_id": "r-2"},
    )

    validation = client.post(f"/api/runs/{second_run_id}/validate").json()
    matched_refs = {
        result["candidate_ref"]
        for result in validation["validation_results"]
        if result["rule_code"] == "canonical_relation_match"
    }
    assert same_identity_id in matched_refs
    assert other_identity_id not in matched_refs


def test_commit_rejects_validated_relation_without_merge_key_value() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_relation_project(client, relation_merge_keys=["report_id"])
    run_id, from_id, to_id = _start_run_with_pair(
        client, project_id=project_id, schema_id=schema_id, title="Reports"
    )
    relation_id = _add_relation(
        client, run_id=run_id, from_id=from_id, to_id=to_id, properties={"wording": "told us"}
    )
    client.post(f"/api/runs/{run_id}/validate")
    _force_relations_validated(run_id)

    commit_response = client.post(f"/api/runs/{run_id}/commit")

    assert commit_response.status_code == 422
    assert relation_id in commit_response.json()["detail"]
    assert "report_id" in commit_response.json()["detail"]
    assert client.get(f"/api/projects/{project_id}/graph/relations").json() == []


def test_commit_rejects_validated_relations_that_would_overwrite_each_other() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_relation_project(client, relation_merge_keys=[])
    run_id, from_id, to_id = _start_run_with_pair(
        client, project_id=project_id, schema_id=schema_id, title="Reports"
    )
    relation_ids = [
        _add_relation(
            client, run_id=run_id, from_id=from_id, to_id=to_id, properties=properties
        )
        for properties in ({"report_id": "r-1"}, {"report_id": "r-2"})
    ]
    client.post(f"/api/runs/{run_id}/validate")
    _force_relations_validated(run_id)

    commit_response = client.post(f"/api/runs/{run_id}/commit")

    assert commit_response.status_code == 422
    for relation_id in relation_ids:
        assert relation_id in commit_response.json()["detail"]
    assert client.get(f"/api/projects/{project_id}/graph/relations").json() == []


def test_commit_after_reviewer_rejects_one_conflicting_duplicate_writes_only_the_other() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_relation_project(client, relation_merge_keys=[])
    run_id, from_id, to_id = _start_run_with_pair(
        client, project_id=project_id, schema_id=schema_id, title="Reports"
    )
    properties_by_relation_id = {
        _add_relation(
            client, run_id=run_id, from_id=from_id, to_id=to_id, properties=properties
        ): properties
        for properties in ({"report_id": "r-1"}, {"report_id": "r-2"})
    }
    validation = client.post(f"/api/runs/{run_id}/validate").json()
    assert validation["relation_validated"] == 1
    assert validation["relation_review"] == 1
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [item["reason_code"] for item in review_items] == ["potential_duplicate_relation"]
    rejected_id = review_items[0]["item_ref"]
    kept_id = next(
        relation_id for relation_id in properties_by_relation_id if relation_id != rejected_id
    )

    decision_response = client.post(
        f"/api/review-items/{review_items[0]['review_item_id']}/decision",
        json={"action": "reject", "reviewer_id": "ayse"},
    )
    assert decision_response.status_code == 200
    assert {
        relation["candidate_relation_id"]: relation["status"]
        for relation in client.get(f"/api/runs/{run_id}/candidate-relations").json()
    } == {kept_id: "validated", rejected_id: "rejected"}

    commit_response = client.post(f"/api/runs/{run_id}/commit")

    assert commit_response.status_code == 200
    graph_delta = commit_response.json()
    assert (graph_delta["relations_created"], graph_delta["relations_merged"]) == (1, 0)
    assert graph_delta["rejected_count"] == 1
    relations = client.get(f"/api/projects/{project_id}/graph/relations").json()
    assert [relation["properties"] for relation in relations] == [
        properties_by_relation_id[kept_id]
    ]
    assert [
        item["status"] for item in client.get(f"/api/runs/{run_id}/review-items").json()
    ] == ["rejected"]
