import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.infrastructure.llm import rule_based_isnad_provider

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "run_isnad_baseline.py"
HADITHS = [
    {
        "coll": "Muslim",
        "num": "978",
        "raw": (
            "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، "
            "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
        ),
    },
    {"coll": "Bukhari", "num": "1", "raw": "حَدَّثَنَا سُفْيَانُ ، عَنِ ابْنِ شِهَابٍ ، عَنْ أَنَسٍ"},
    {"coll": "Note", "num": "7", "raw": "قَالَ رَجُلٌ لِصَاحِبِهِ"},
]


def _load_script() -> ModuleType:
    spec = spec_from_file_location("run_isnad_baseline", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _run_baseline(tmp_path: Path, hadiths: list[dict[str, str]]) -> tuple[int, Path]:
    input_path = tmp_path / "hadiths.json"
    input_path.write_text(json.dumps(hadiths, ensure_ascii=False), encoding="utf-8")
    out_dir = tmp_path / "out"
    exit_code = _load_script().main(["--input", str(input_path), "--out-dir", str(out_dir)])
    return exit_code, out_dir


def test_baseline_commits_only_facts_with_a_grounded_quote_and_an_acceptance_record(
    tmp_path: Path,
) -> None:
    exit_code, out_dir = _run_baseline(tmp_path, HADITHS)

    assert exit_code == 0
    client = TestClient(create_app())
    project_id = client.get("/api/projects").json()[0]["project_id"]
    runs = client.get(f"/api/projects/{project_id}/runs").json()
    assert [run["status"] for run in runs] == ["completed"] * 3
    committed_fact_count = 0
    for run in runs:
        run_id = run["run_id"]
        segment_texts = {
            segment["segment_id"]: segment["text"]
            for segment in client.get(
                f"/api/source-units/{run['source_unit_id']}/segments"
            ).json()
        }
        records = {
            record["candidate_ref"]: record
            for record in client.get(f"/api/runs/{run_id}/acceptance-records").json()
        }
        assert client.get(f"/api/runs/{run_id}/review-items").json() == []
        facts = [
            (node["candidate_node_id"], node)
            for node in client.get(f"/api/runs/{run_id}/candidate-nodes").json()
        ] + [
            (relation["candidate_relation_id"], relation)
            for relation in client.get(f"/api/runs/{run_id}/candidate-relations").json()
        ]
        for candidate_ref, fact in facts:
            assert fact["status"] == "validated"
            assert any(
                evidence["quote"] and evidence["quote"] in segment_texts[evidence["segment_id"]]
                for evidence in fact["evidence_refs"]
            )
            record = records[candidate_ref]
            assert record["decision"] is not None or record["policy"] == "auto_validated"
            assert record["rule_code"] in {"candidate_node_valid", "candidate_relation_valid"}
            committed_fact_count += 1

    report = json.loads((out_dir / "run_report.json").read_text(encoding="utf-8"))
    assert committed_fact_count == 8 + 5
    assert report["committed_fact_invariants"] == {
        "facts_checked": {"nodes": 8, "relations": 5},
        "acceptance_records": {"auto_validated": 13},
        "without_quote_in_source_segment": [],
        "without_acceptance_record": [],
        "holds": True,
    }
    overview = client.get(f"/api/projects/{project_id}/graph/overview").json()
    assert (overview["node_count"], overview["relation_count"]) == (7, 5)


def test_baseline_exports_mentions_in_chain_order_and_reports_counts(tmp_path: Path) -> None:
    exit_code, out_dir = _run_baseline(tmp_path, HADITHS)

    assert exit_code == 0
    expected_rows = [
        {
            "hadith_id": "Muslim:978",
            "mentions": [
                "قُتَيْبَةُ بْنُ سَعِيدٍ",
                "لَيْثٌ",
                "مُحَمَّدُ بْنُ رُمْحٍ",
                "اللَّيْثُ",
                "ابْنِ شِهَابٍ",
            ],
        },
        {"hadith_id": "Bukhari:1", "mentions": ["سُفْيَانُ", "ابْنِ شِهَابٍ", "أَنَسٍ"]},
        {"hadith_id": "Note:7", "mentions": []},
    ]
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == expected_rows
    assert _read_jsonl(out_dir / "system_validated.jsonl") == expected_rows
    report = json.loads((out_dir / "run_report.json").read_text(encoding="utf-8"))
    assert report["hadiths"] == 3
    assert report["segments"] == 4
    assert report["fallback_to_whole_text_units"] == 1
    assert report["llm_equivalent_calls"] == 4
    assert report["candidates_proposed"] == {"nodes": 8, "relations": 5}
    assert report["candidates_validated"] == {"nodes": 8, "relations": 5}
    assert report["candidates_in_review"] == {
        "nodes": 0,
        "relations": 0,
        "open_review_items_by_reason_code": {},
    }
    assert report["runs"] == {
        "committed": 3,
        "committed_without_any_fact": 1,
        "blocked": 0,
        "blocked_by_reason": {},
        "blocked_hadith_ids": [],
    }
    assert report["canonical_graph"]["node_writes"] == {"created": 7, "merged": 1}
    assert report["narrator_identity"] == {
        "committed_mentions": 8,
        "canonical_narrator_nodes": 7,
        "distinct_committed_mentions_ignoring_diacritics": 7,
    }
    assert report["wall_time_seconds"] >= 0


def test_baseline_leaves_runs_with_open_review_items_uncommitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rule_based_isnad_provider, "RULE_CONFIDENCE", 0.1)

    exit_code, out_dir = _run_baseline(tmp_path, HADITHS[:2])

    assert exit_code == 0
    report = json.loads((out_dir / "run_report.json").read_text(encoding="utf-8"))
    assert report["candidates_validated"] == {"nodes": 0, "relations": 0}
    assert report["candidates_in_review"] == {
        "nodes": 8,
        "relations": 5,
        "open_review_items_by_reason_code": {
            "node_confidence_threshold": 8,
            "relation_dependency_review": 5,
        },
    }
    assert report["runs"] == {
        "committed": 0,
        "committed_without_any_fact": 0,
        "blocked": 2,
        "blocked_by_reason": {"Run has open review items and cannot be committed.": 2},
        "blocked_hadith_ids": ["Muslim:978", "Bukhari:1"],
    }
    assert report["canonical_graph"]["nodes"] == 0
    assert report["committed_fact_invariants"]["facts_checked"] == {"nodes": 0, "relations": 0}
    assert [len(row["mentions"]) for row in _read_jsonl(out_dir / "system_proposed.jsonl")] == [
        5,
        3,
    ]
    assert [row["mentions"] for row in _read_jsonl(out_dir / "system_validated.jsonl")] == [[], []]
