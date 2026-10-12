from collections.abc import Callable
from copy import deepcopy
from typing import Any

from fastapi.testclient import TestClient

from app.application.errors import ExternalServiceError
from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_ID, ISNAD_TEMPLATE_SCHEMA
from test_helpers import create_pipeline_definition

Responder = Callable[[dict[str, Any]], dict[str, Any]]

FIRST_CHAIN = "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ"
SECOND_CHAIN = "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
TAHWIL_SOURCE = f"{FIRST_CHAIN} . ح ، {SECOND_CHAIN}"


class ScriptedLLMProvider:
    def __init__(self, respond: Responder) -> None:
        self.provider_name = "scripted-test"
        self.payloads: list[dict[str, Any]] = []
        self._respond = respond

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        del prompt, schema_name, model
        self.payloads.append(deepcopy(payload))
        return self._respond(payload)


def _create_isnad_project(client: TestClient) -> tuple[str, str]:
    project = client.post(
        "/api/projects",
        json={
            "name": "Isnad Lab",
            "description": "Narrator chains",
            "template_id": ISNAD_TEMPLATE_ID,
        },
    ).json()
    assert project["template_id"] == ISNAD_TEMPLATE_ID
    project_id = project["project_id"]
    schema_id = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Isnad template schema"},
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
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    return project_id, schema_id


def _start_run(
    client: TestClient,
    *,
    project_id: str,
    schema_id: str,
    raw_content: str,
    external_ref: str,
    strategy: str = ISNAD_TEMPLATE_SCHEMA.segmentation_strategy,
) -> tuple[str, list[dict[str, Any]]]:
    source_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "hadith",
            "title": external_ref,
            "raw_content": raw_content,
            "external_ref": external_ref,
        },
    ).json()["source_unit_id"]
    run_id = client.post(
        f"/api/source-units/{source_id}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "scripted-test",
        },
    ).json()["run_id"]
    segments_response = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": strategy},
    )
    assert segments_response.status_code == 201, segments_response.text
    segments: list[dict[str, Any]] = segments_response.json()
    return run_id, segments


def _use_provider(respond: Responder) -> ScriptedLLMProvider:
    provider = ScriptedLLMProvider(respond)
    get_container().extraction_management_service.provider_registry = (
        StaticLLMProviderRegistry(providers=[provider])
    )
    return provider


def _chain_response(
    payload: dict[str, Any],
    names_and_quotes: list[tuple[str, str]],
) -> dict[str, Any]:
    segment = payload["segments"][0]
    hadith_ref = payload["source_unit"]["external_ref"]

    def evidence(quote: str) -> list[dict[str, Any]]:
        return [{"segment_id": segment["segment_id"], "quote": quote}]

    return {
        "nodes": [
            {
                "ref": f"node-{index}",
                "node_type": "Narrator",
                "properties": {"name": name},
                "confidence": 0.95,
                "evidence_refs": evidence(quote),
            }
            for index, (name, quote) in enumerate(names_and_quotes, start=1)
        ],
        "relations": [
            {
                "relation_type": "NARRATED_FROM",
                "from_ref": f"node-{position}",
                "to_ref": f"node-{position + 1}",
                "properties": {
                    "hadith_ref": hadith_ref,
                    "chain_no": segment["segment_order"],
                    "position": position,
                    "sigha": "عن",
                },
                "confidence": 0.95,
                "evidence_refs": evidence(segment["text"]),
            }
            for position in range(1, len(names_and_quotes))
        ],
    }


def _tahwil_response(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["segments"][0]["text"] == FIRST_CHAIN:
        return _chain_response(
            payload,
            [("قتيبة بن سعيد", "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ"), ("ليث", "حَدَّثَنَا لَيْثٌ")],
        )
    return _chain_response(
        payload,
        [
            ("محمد بن رمح", "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ"),
            ("الليث", "أَخْبَرَنَا اللَّيْثُ"),
            ("ابن شهاب", "عَنِ ابْنِ شِهَابٍ"),
        ],
    )


def test_isnad_strategy_creates_one_segment_per_chain_from_source_substrings() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)

    _, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content=TAHWIL_SOURCE,
        external_ref="muslim-978",
    )

    second_start = TAHWIL_SOURCE.index(SECOND_CHAIN)
    assert [segment["text"] for segment in segments] == [FIRST_CHAIN, SECOND_CHAIN]
    assert [segment["segment_order"] for segment in segments] == [1, 2]
    assert [segment["metadata_json"] for segment in segments] == [
        {
            "strategy": "isnad",
            "chain_no": "1",
            "start_offset": "0",
            "end_offset": str(len(FIRST_CHAIN)),
        },
        {
            "strategy": "isnad",
            "chain_no": "2",
            "start_offset": str(second_start),
            "end_offset": str(second_start + len(SECOND_CHAIN)),
        },
    ]
    for segment in segments:
        start = int(segment["metadata_json"]["start_offset"])
        end = int(segment["metadata_json"]["end_offset"])
        assert TAHWIL_SOURCE[start:end] == segment["text"]


def test_isnad_strategy_sends_no_text_after_matn_boundary() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    source = (
        "حَدَّثَنَا لَيْثٌ ، عَنْ نَافِعٍ ، عَنِ النَّبِيِّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ قَالَ الْحَرُّ . "
        "حَدَّثَنِي حَرْمَلَةُ ، أَخْبَرَنَا ابْنُ وَهْبٍ"
    )

    _, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content=source,
        external_ref="muslim-1",
    )

    assert [segment["text"] for segment in segments] == ["حَدَّثَنَا لَيْثٌ ، عَنْ نَافِعٍ"]


def test_isnad_strategy_falls_back_to_whole_text_when_no_chain_is_found() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)

    _, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content="قَالَ رَجُلٌ لِصَاحِبِهِ",
        external_ref="note-1",
    )

    assert [(segment["text"], segment["metadata_json"]) for segment in segments] == [
        ("قَالَ رَجُلٌ لِصَاحِبِهِ", {"strategy": "isnad", "fallback": "whole_text"})
    ]


def test_unknown_segmentation_strategy_is_rejected_with_supported_names() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    source_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "hadith",
            "title": "Unknown strategy",
            "raw_content": TAHWIL_SOURCE,
        },
    ).json()["source_unit_id"]

    response = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "sentences"},
    )

    assert response.status_code == 422
    assert "isnad, paragraphs" in response.json()["detail"]


def test_isnad_extraction_issues_one_call_per_chain_with_unique_refs() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    run_id, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content=TAHWIL_SOURCE,
        external_ref="muslim-978",
    )
    provider = _use_provider(_tahwil_response)

    response = client.post(f"/api/runs/{run_id}/extract-candidates", json={})

    assert response.status_code == 200, response.text
    report = response.json()
    assert [
        [segment["segment_id"] for segment in payload["segments"]]
        for payload in provider.payloads
    ] == [[segments[0]["segment_id"]], [segments[1]["segment_id"]]]
    assert report["call_count"] == 2
    assert report["failed_calls"] == []
    refs = [node["ref"] for node in report["suggested_nodes"]]
    assert len(refs) == len(set(refs)) == 5
    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    names_by_id = {
        node["candidate_node_id"]: node["properties"]["name"] for node in candidate_nodes
    }
    candidate_relations = client.get(f"/api/runs/{run_id}/candidate-relations").json()
    assert sorted(
        (
            names_by_id[relation["from_candidate_ref"]],
            names_by_id[relation["to_candidate_ref"]],
            relation["properties"]["chain_no"],
        )
        for relation in candidate_relations
    ) == sorted(
        [
            ("قتيبة بن سعيد", "ليث", 1),
            ("محمد بن رمح", "الليث", 2),
            ("الليث", "ابن شهاب", 2),
        ]
    )
    validation = client.post(f"/api/runs/{run_id}/validate").json()
    assert validation["node_validated"] == 5
    assert validation["relation_validated"] == 3


def test_failed_segment_call_keeps_candidates_from_other_calls_and_is_recorded() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    run_id, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content=TAHWIL_SOURCE,
        external_ref="muslim-978",
    )

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        if payload["segments"][0]["text"] == SECOND_CHAIN:
            raise ExternalServiceError("Provider output was truncated at the token limit.")
        return _tahwil_response(payload)

    provider = _use_provider(respond)

    response = client.post(f"/api/runs/{run_id}/extract-candidates", json={})

    assert response.status_code == 200, response.text
    report = response.json()
    assert len(provider.payloads) == 2
    assert report["call_count"] == 2
    assert report["failed_calls"] == [
        {
            "segment_ids": [segments[1]["segment_id"]],
            "error_message": "Provider output was truncated at the token limit.",
        }
    ]
    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    assert sorted(node["properties"]["name"] for node in candidate_nodes) == sorted(
        ["قتيبة بن سعيد", "ليث"]
    )
    assert len(client.get(f"/api/runs/{run_id}/candidate-relations").json()) == 1
    execution = client.get(f"/api/runs/{run_id}/extraction-executions").json()[0]
    assert execution["status"] == "succeeded"
    assert segments[1]["segment_id"] in execution["error_message"]
    assert "truncated at the token limit" in execution["error_message"]
    assert client.get(f"/api/runs/{run_id}").json()["status"] == "running"


def test_extraction_fails_when_every_segment_call_fails() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    run_id, _ = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content=TAHWIL_SOURCE,
        external_ref="muslim-978",
    )

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        raise ExternalServiceError("Provider is unavailable.")

    provider = _use_provider(respond)

    response = client.post(f"/api/runs/{run_id}/extract-candidates", json={})

    assert response.status_code == 502
    assert len(provider.payloads) == 2
    assert client.get(f"/api/runs/{run_id}/candidate-nodes").json() == []
    execution = client.get(f"/api/runs/{run_id}/extraction-executions").json()[0]
    assert execution["status"] == "failed"
    assert client.get(f"/api/runs/{run_id}").json()["status"] == "failed"


def test_narrator_shared_by_two_chains_becomes_one_candidate_node() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    run_id, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content="حَدَّثَنَا قُتَيْبَةُ ، عَنْ مَالِكٍ . ح ، حَدَّثَنَا يَحْيَى ، عَنْ مَالِكٍ",
        external_ref="muwatta-1",
    )
    assert len(segments) == 2

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        first_narrator = (
            ("قتيبة", "حَدَّثَنَا قُتَيْبَةُ")
            if payload["segments"][0]["segment_order"] == 1
            else ("يحيى", "حَدَّثَنَا يَحْيَى")
        )
        return _chain_response(payload, [first_narrator, ("مالك", "عَنْ مَالِكٍ")])

    _use_provider(respond)

    assert client.post(f"/api/runs/{run_id}/extract-candidates", json={}).status_code == 200
    validation = client.post(f"/api/runs/{run_id}/validate").json()

    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    assert sorted(node["properties"]["name"] for node in candidate_nodes) == sorted(
        ["قتيبة", "يحيى", "مالك"]
    )
    malik = next(node for node in candidate_nodes if node["properties"]["name"] == "مالك")
    assert [evidence["segment_id"] for evidence in malik["evidence_refs"]] == [
        segment["segment_id"] for segment in segments
    ]
    candidate_relations = client.get(f"/api/runs/{run_id}/candidate-relations").json()
    assert [relation["to_candidate_ref"] for relation in candidate_relations] == [
        malik["candidate_node_id"],
        malik["candidate_node_id"],
    ]
    assert validation["node_validated"] == 3
    assert validation["relation_validated"] == 2
    assert client.get(f"/api/runs/{run_id}/review-items").json() == []


def test_paragraph_extraction_uses_configured_segment_limit_per_call() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    run_id, segments = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content=f"{FIRST_CHAIN}\n\n{SECOND_CHAIN}",
        external_ref="muslim-978",
        strategy="paragraphs",
    )
    assert len(segments) == 2
    provider = _use_provider(lambda payload: {"nodes": [], "relations": []})

    first_response = client.post(
        f"/api/runs/{run_id}/extract-candidates",
        json={"dry_run": True},
    )
    get_container().extraction_management_service.max_segments_per_call = 1
    second_response = client.post(
        f"/api/runs/{run_id}/extract-candidates",
        json={"dry_run": True},
    )

    assert first_response.json()["call_count"] == 1
    assert second_response.json()["call_count"] == 2
    assert [len(payload["segments"]) for payload in provider.payloads] == [2, 1, 1]


def test_same_link_in_two_hadiths_commits_as_two_distinct_edges() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        segment = payload["segments"][0]
        last_narrator = (
            ("أنس", "عَنْ أَنَسٍ") if "أَنَسٍ" in segment["text"] else ("سالم", "عَنْ سَالِمٍ")
        )
        response = _chain_response(
            payload,
            [("سفيان", "سُفْيَانُ"), ("الزهري", "عَنِ الزُّهْرِيِّ"), last_narrator],
        )
        evidence = [{"segment_id": segment["segment_id"], "quote": segment["text"]}]
        response["nodes"].append(
            {
                "ref": "hadith",
                "node_type": "Hadith",
                "properties": {"hadith_ref": payload["source_unit"]["external_ref"]},
                "confidence": 0.95,
                "evidence_refs": evidence,
            }
        )
        response["relations"].append(
            {
                "relation_type": "TRANSMITS",
                "from_ref": "node-1",
                "to_ref": "hadith",
                "properties": {},
                "confidence": 0.95,
                "evidence_refs": evidence,
            }
        )
        return response

    provider = _use_provider(respond)
    hadiths = [
        ("bukhari-1", "حَدَّثَنَا سُفْيَانُ ، عَنِ الزُّهْرِيِّ ، عَنْ أَنَسٍ"),
        ("muslim-2", "أَخْبَرَنَا سُفْيَانُ ، عَنِ الزُّهْرِيِّ ، عَنْ سَالِمٍ"),
    ]
    for external_ref, raw_content in hadiths:
        run_id, segments = _start_run(
            client,
            project_id=project_id,
            schema_id=schema_id,
            raw_content=raw_content,
            external_ref=external_ref,
        )
        assert [segment["text"] for segment in segments] == [raw_content]
        assert client.post(f"/api/runs/{run_id}/extract-candidates", json={}).status_code == 200
        assert client.post(f"/api/runs/{run_id}/validate").status_code == 200

        assert client.get(f"/api/runs/{run_id}/review-items").json() == []
        commit_response = client.post(f"/api/runs/{run_id}/commit")
        assert commit_response.status_code == 200, commit_response.text

    relation_types = provider.payloads[0]["schema"]["relation_types"]
    assert {item["name"]: item["merge_keys"] for item in relation_types} == {
        "NARRATED_FROM": ["hadith_ref", "chain_no", "position"],
        "TRANSMITS": [],
    }
    relations = client.get(
        f"/api/projects/{project_id}/graph/relations",
        params={"relation_type": "NARRATED_FROM"},
    ).json()
    shared_link = [relation for relation in relations if relation["properties"]["position"] == 1]
    assert sorted(relation["properties"]["hadith_ref"] for relation in shared_link) == [
        "bukhari-1",
        "muslim-2",
    ]
    assert (
        len({(relation["from_merge_key"], relation["to_merge_key"]) for relation in shared_link})
        == 1
    )
    assert len(relations) == 4
    overview = client.get(f"/api/projects/{project_id}/graph/overview").json()
    assert {item["node_type"]: item["count"] for item in overview["node_type_counts"]} == {
        "Narrator": 4,
        "Hadith": 2,
    }


def test_hadith_ref_that_differs_from_source_unit_reference_goes_to_review() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    project_id, schema_id = _create_isnad_project(client)
    run_id, _ = _start_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        raw_content="حَدَّثَنَا سُفْيَانُ ، عَنِ الزُّهْرِيِّ",
        external_ref="bukhari-1",
    )

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        segment = payload["segments"][0]
        evidence = [{"segment_id": segment["segment_id"], "quote": segment["text"]}]
        return {
            "nodes": [
                {
                    "ref": ref,
                    "node_type": "Hadith",
                    "properties": {"hadith_ref": hadith_ref},
                    "confidence": 0.95,
                    "evidence_refs": evidence,
                }
                for ref, hadith_ref in [("own", "Bukhari 1"), ("other", "bukhari-2")]
            ],
            "relations": [],
        }

    _use_provider(respond)

    assert client.post(f"/api/runs/{run_id}/extract-candidates", json={}).status_code == 200
    assert client.post(f"/api/runs/{run_id}/validate").status_code == 200

    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    assert {node["properties"]["hadith_ref"]: node["status"] for node in candidate_nodes} == {
        "Bukhari 1": "validated",
        "bukhari-2": "review",
    }
    other = next(node for node in candidate_nodes if node["status"] == "review")
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [(item["item_ref"], item["reason_code"]) for item in review_items] == [
        (other["candidate_node_id"], "value_not_in_quote")
    ]
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 422
