from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from test_helpers import create_pipeline_definition


def test_graph_explorer_endpoints_return_canonical_graph_views() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Graph Explorer Lab",
            "description": "Read model verification",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Explorer schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "KNOWS",
            "from_type": "Character",
            "to_type": "Character",
            "description": "Character knows another character",
            "confidence_threshold": 0.7,
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali greets Veli.",
            "sequence_no": 1,
        },
    ).json()
    source_id = source["source_unit_id"]

    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    ali = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.99,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()
    veli = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Veli"},
            "merge_key_payload": {"name": "Veli"},
            "confidence": 0.99,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()
    client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "KNOWS",
            "from_candidate_ref": ali["candidate_node_id"],
            "to_candidate_ref": veli["candidate_node_id"],
            "properties": {"since": "episode-1"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200

    overview_response = client.get(f"/api/projects/{project_id}/graph/overview")
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["node_count"] == 2
    assert overview["relation_count"] == 1
    assert overview["node_type_counts"] == [{"node_type": "Character", "count": 2}]

    nodes_response = client.get(
        f"/api/projects/{project_id}/graph/nodes",
        params={"node_type": "Character", "limit": 10},
    )
    assert nodes_response.status_code == 200
    nodes = nodes_response.json()
    assert len(nodes) == 2
    assert sorted(node["properties"]["name"] for node in nodes) == ["Ali", "Veli"]
    ali_node = next(node for node in nodes if node["properties"]["name"] == "Ali")
    veli_node = next(node for node in nodes if node["properties"]["name"] == "Veli")

    node_detail_response = client.get(
        f"/api/projects/{project_id}/graph/nodes/Character/{ali_node['merge_key']}"
    )
    assert node_detail_response.status_code == 200
    node_detail = node_detail_response.json()
    assert node_detail["node"]["properties"]["name"] == "Ali"
    assert node_detail["source_units"] == [
        {
            "source_unit_id": source_id,
            "title": "Episode 1",
            "source_type": "episode_transcript",
            "sequence_no": 1,
        }
    ]
    assert len(node_detail["supporting_segments"]) == 1
    assert node_detail["supporting_segments"][0]["text"] == "Ali greets Veli."
    assert len(node_detail["connected_relations"]) == 1
    connected_relation = node_detail["connected_relations"][0]
    assert connected_relation["relation_type"] == "KNOWS"
    assert connected_relation["direction"] == "outgoing"
    assert connected_relation["other_node_type"] == "Character"
    assert connected_relation["other_merge_key"] == veli_node["merge_key"]
    assert connected_relation["other_node_properties"] == {"name": "Veli"}
    assert connected_relation["properties"] == {"since": "episode-1"}
    assert connected_relation["updated_at"] is not None

    relations_response = client.get(
        f"/api/projects/{project_id}/graph/relations",
        params={"relation_type": "KNOWS", "limit": 10},
    )
    assert relations_response.status_code == 200
    relations = relations_response.json()
    assert len(relations) == 1
    assert relations[0]["relation_type"] == "KNOWS"
    assert relations[0]["properties"]["since"] == "episode-1"

    relation_detail_response = client.get(
        "/api/projects/"
        f"{project_id}/graph/relations/KNOWS/Character/{ali_node['merge_key']}/"
        f"Character/{veli_node['merge_key']}"
    )
    assert relation_detail_response.status_code == 200
    relation_detail = relation_detail_response.json()
    assert relation_detail["relation"]["relation_type"] == "KNOWS"
    assert relation_detail["from_node"]["properties"]["name"] == "Ali"
    assert relation_detail["to_node"]["properties"]["name"] == "Veli"
    assert relation_detail["source_units"] == [
        {
            "source_unit_id": source_id,
            "title": "Episode 1",
            "source_type": "episode_transcript",
            "sequence_no": 1,
        }
    ]
    assert len(relation_detail["supporting_segments"]) == 1
    assert relation_detail["supporting_segments"][0]["text"] == "Ali greets Veli."
