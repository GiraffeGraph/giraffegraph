from typing import Any

from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from app.infrastructure.llm.rule_based_isnad_provider import RuleBasedIsnadProvider
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_ID

FIRST_CHAIN = "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ"
SECOND_CHAIN = "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
TAHWIL_SOURCE = f"{FIRST_CHAIN} . ح ، {SECOND_CHAIN}"
OTHER_SOURCE = "حَدَّثَنَا يَحْيَى ، أَخْبَرَنَا اللَّيْثُ ، عَنْ نَافِعٍ"
PROVIDER = "rule_based_isnad"
QITAYBA = "قُتَيْبَةُ بْنُ سَعِيدٍ"
LAYTH = "اللَّيْثُ"


class LowConfidenceFirstNarratorProvider:
    provider_name = "low-confidence-test"

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        output = RuleBasedIsnadProvider().generate_structured(
            prompt=prompt,
            schema_name=schema_name,
            payload=payload,
            model=model,
        )
        output["nodes"][0]["confidence"] = 0.3
        return output


def _client() -> TestClient:
    get_container.cache_clear()
    return TestClient(create_app())


def _isnad_project(client: TestClient) -> str:
    response = client.post(
        "/api/projects",
        json={
            "name": "Chains",
            "template_id": ISNAD_TEMPLATE_ID,
            "apply_template_schema": True,
        },
    )
    assert response.status_code == 201, response.text
    project_id: str = response.json()["project_id"]
    return project_id


def _load(client: TestClient, project_id: str, hadiths: dict[str, str]) -> dict[str, str]:
    response = client.post(
        f"/api/projects/{project_id}/source-units/bulk",
        json={
            "source_type": "hadith",
            "items": [
                {"external_ref": ref, "raw_content": raw} for ref, raw in hadiths.items()
            ],
        },
    )
    assert response.status_code == 200, response.text
    return {item["external_ref"]: item["source_unit_id"] for item in response.json()["results"]}


def _process(
    client: TestClient,
    project_id: str,
    source_unit_ids: list[str],
    *,
    provider: str = PROVIDER,
    commit: bool = True,
) -> list[dict[str, Any]]:
    response = client.post(
        f"/api/projects/{project_id}/source-units/process",
        json={"source_unit_ids": source_unit_ids, "llm_provider": provider, "commit": commit},
    )
    assert response.status_code == 200, response.text
    results: list[dict[str, Any]] = response.json()["results"]
    return results


def _chains(client: TestClient, project_id: str, hadith_ref: str) -> dict[str, Any]:
    response = client.get(
        f"/api/projects/{project_id}/chains/hadith",
        params={"hadith_ref": hadith_ref},
    )
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def test_tahwil_hadith_returns_two_chains_in_order_with_quotes_and_acceptance() -> None:
    client = _client()
    project_id = _isnad_project(client)
    units = _load(client, project_id, {"muslim:978": TAHWIL_SOURCE})
    run_id = _process(client, project_id, [units["muslim:978"]])[0]["run_id"]

    view = _chains(client, project_id, "muslim:978")

    assert view["hadith_ref"] == "muslim:978"
    assert view["committed"] is True
    assert view["source_unit"]["source_unit_id"] == units["muslim:978"]
    assert view["source_unit"]["raw_content"] == TAHWIL_SOURCE
    assert [(run["run_id"], run["llm_provider"]) for run in view["runs"]] == [(run_id, PROVIDER)]
    assert view["runs"][0]["committed_at"] is not None

    assert [chain["chain_no"] for chain in view["chains"]] == [1, 2]
    first, second = view["chains"]
    assert first["narrators"] == [QITAYBA, "لَيْثٌ"]
    assert second["narrators"] == ["مُحَمَّدُ بْنُ رُمْحٍ", LAYTH, "ابْنِ شِهَابٍ"]
    assert [
        (link["position"], link["from_narrator"], link["to_narrator"], link["sigha"])
        for link in first["links"]
    ] == [(1, QITAYBA, "لَيْثٌ", "حدثنا")]
    assert [
        (link["position"], link["from_narrator"], link["to_narrator"], link["sigha"])
        for link in second["links"]
    ] == [
        (1, "مُحَمَّدُ بْنُ رُمْحٍ", LAYTH, "اخبرنا"),
        (2, LAYTH, "ابْنِ شِهَابٍ", "عن"),
    ]

    second_start = TAHWIL_SOURCE.index(SECOND_CHAIN)
    for chain, segment_text, segment_start in (
        (first, FIRST_CHAIN, 0),
        (second, SECOND_CHAIN, second_start),
    ):
        for link in chain["links"]:
            assert link["acceptance"] == {
                "kind": "policy",
                "policy": "auto_validated",
                "rule_code": "candidate_relation_valid",
                "action": None,
                "reviewer_id": None,
                "decided_at": None,
            }
            (evidence,) = link["evidence"]
            assert evidence["segment_text"] == segment_text
            assert evidence["segment_order"] == chain["chain_no"]
            assert evidence["quote"].startswith(link["from_narrator"])
            assert evidence["quote"].endswith(link["to_narrator"])
            assert (
                segment_text[evidence["start_offset"] : evidence["end_offset"]]
                == evidence["quote"]
            )
            assert evidence["source_start_offset"] == segment_start + evidence["start_offset"]
            assert (
                TAHWIL_SOURCE[evidence["source_start_offset"] : evidence["source_end_offset"]]
                == evidence["quote"]
            )

    assert [narrator["name"] for narrator in view["narrators"]] == [
        QITAYBA,
        "لَيْثٌ",
        "مُحَمَّدُ بْنُ رُمْحٍ",
        LAYTH,
        "ابْنِ شِهَابٍ",
    ]
    for narrator in view["narrators"]:
        assert narrator["acceptance"]["kind"] == "policy"
        assert narrator["acceptance"]["rule_code"] == "candidate_node_valid"
        (mention,) = narrator["evidence"]
        assert mention["quote"] == narrator["name"]
        assert (
            TAHWIL_SOURCE[mention["source_start_offset"] : mention["source_end_offset"]]
            == narrator["name"]
        )


def test_human_decision_is_reported_with_reviewer_and_time() -> None:
    client = _client()
    get_container().extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[LowConfidenceFirstNarratorProvider()]
    )
    project_id = _isnad_project(client)
    units = _load(client, project_id, {"muslim:1": FIRST_CHAIN})
    result = _process(
        client,
        project_id,
        [units["muslim:1"]],
        provider=LowConfidenceFirstNarratorProvider.provider_name,
    )[0]
    assert result["status"] == "needs_review"
    assert result["open_review_count"] >= 1
    assert _chains(client, project_id, "muslim:1")["chains"] == []

    run_id = result["run_id"]
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    node_item = next(item for item in review_items if item["item_type"] == "candidate_node")
    decision = client.post(
        f"/api/review-items/{node_item['review_item_id']}/decision",
        json={"action": "accept", "reviewer_id": "efe"},
    )
    assert decision.status_code == 200, decision.text
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 200

    view = _chains(client, project_id, "muslim:1")

    narrators = {narrator["name"]: narrator for narrator in view["narrators"]}
    human = narrators[QITAYBA]["acceptance"]
    assert human["kind"] == "human"
    assert human["action"] == "accept"
    assert human["reviewer_id"] == "efe"
    assert human["decided_at"] is not None
    assert human["policy"] is None
    assert narrators["لَيْثٌ"]["acceptance"]["kind"] == "policy"
    (chain,) = view["chains"]
    (link,) = chain["links"]
    assert link["acceptance"]["kind"] == "policy"
    assert link["acceptance"]["policy"] == "auto_validated"


def test_hadith_with_nothing_committed_returns_an_empty_well_formed_result() -> None:
    client = _client()
    project_id = _isnad_project(client)
    units = _load(client, project_id, {"muslim:1": FIRST_CHAIN})

    loaded = _chains(client, project_id, "muslim:1")
    unknown = _chains(client, project_id, "muslim:404")

    assert loaded == {
        "project_id": project_id,
        "hadith_ref": "muslim:1",
        "committed": False,
        "source_unit": {
            "source_unit_id": units["muslim:1"],
            "title": "muslim:1",
            "raw_content": FIRST_CHAIN,
        },
        "runs": [],
        "chains": [],
        "narrators": [],
    }
    assert unknown == {
        "project_id": project_id,
        "hadith_ref": "muslim:404",
        "committed": False,
        "source_unit": None,
        "runs": [],
        "chains": [],
        "narrators": [],
    }
    assert client.get(f"/api/projects/{project_id}/chains").json() == {
        "project_id": project_id,
        "total_count": 0,
        "hadiths": [],
    }


def test_committed_hadiths_are_listed_and_searchable_by_ref() -> None:
    client = _client()
    project_id = _isnad_project(client)
    units = _load(
        client,
        project_id,
        {"bukhari:5": OTHER_SOURCE, "bukhari:6": FIRST_CHAIN, "muslim:978": TAHWIL_SOURCE},
    )
    _process(client, project_id, [units["bukhari:5"], units["muslim:978"]])

    listing = client.get(f"/api/projects/{project_id}/chains").json()
    filtered = client.get(f"/api/projects/{project_id}/chains", params={"q": "BUKH"}).json()

    assert listing["total_count"] == 2
    assert [
        (item["hadith_ref"], item["source_unit_id"], item["title"])
        for item in listing["hadiths"]
    ] == [
        ("bukhari:5", units["bukhari:5"], "bukhari:5"),
        ("muslim:978", units["muslim:978"], "muslim:978"),
    ]
    assert all(item["committed_at"] and item["run_id"] for item in listing["hadiths"])
    assert [item["hadith_ref"] for item in filtered["hadiths"]] == ["bukhari:5"]
    assert filtered["total_count"] == 1


def test_narrator_view_returns_hadith_refs_and_neighbours() -> None:
    client = _client()
    project_id = _isnad_project(client)
    units = _load(client, project_id, {"bukhari:5": OTHER_SOURCE, "muslim:978": TAHWIL_SOURCE})
    _process(client, project_id, list(units.values()))

    response = client.get(
        f"/api/projects/{project_id}/chains/narrator",
        params={"name": LAYTH},
    )

    assert response.status_code == 200, response.text
    view = response.json()
    assert view["name"] == LAYTH
    assert view["hadith_count"] == 2
    assert [(item["hadith_ref"], item["source_unit_id"]) for item in view["hadiths"]] == [
        ("bukhari:5", units["bukhari:5"]),
        ("muslim:978", units["muslim:978"]),
    ]
    assert view["narrated_from_count"] == 2
    assert [
        (item["name"], item["link_count"], item["hadith_refs"])
        for item in view["narrated_from"]
    ] == [
        ("ابْنِ شِهَابٍ", 1, ["muslim:978"]),
        ("نَافِعٍ", 1, ["bukhari:5"]),
    ]
    assert view["narrated_to_count"] == 2
    assert [
        (item["name"], item["link_count"], item["hadith_refs"]) for item in view["narrated_to"]
    ] == [
        ("مُحَمَّدُ بْنُ رُمْحٍ", 1, ["muslim:978"]),
        ("يَحْيَى", 1, ["bukhari:5"]),
    ]


def test_unknown_narrator_and_project_are_not_found() -> None:
    client = _client()
    project_id = _isnad_project(client)

    narrator = client.get(
        f"/api/projects/{project_id}/chains/narrator",
        params={"name": "مجهول"},
    )
    project = client.get("/api/projects/missing/chains/hadith", params={"hadith_ref": "x"})

    assert narrator.status_code == 404
    assert "مجهول" in narrator.json()["detail"]
    assert project.status_code == 404
