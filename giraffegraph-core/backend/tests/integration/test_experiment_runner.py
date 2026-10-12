import json
import sys
import threading
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest

from app.infrastructure.llm.anthropic_provider import AnthropicLLMProvider
from app.infrastructure.llm.rule_based_isnad_provider import RuleBasedIsnadProvider

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "run_isnad_experiment.py"
MUSLIM = {
    "coll": "Muslim",
    "num": "978",
    "raw": (
        "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، "
        "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
    ),
}
BUKHARI = {"coll": "Bukhari", "num": "1", "raw": "حَدَّثَنَا سُفْيَانُ ، عَنِ ابْنِ شِهَابٍ ، عَنْ أَنَسٍ"}
NOTE = {"coll": "Note", "num": "7", "raw": "قَالَ رَجُلٌ لِصَاحِبِهِ"}
HADITHS = [MUSLIM, BUKHARI, NOTE]
EXPECTED_ROWS = [
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


class FakeMessages:
    """Answers like a model that reads chains the way the rule-based provider does."""

    def __init__(
        self,
        *,
        output_tokens: int = 200,
        stop_reasons: dict[str, str] | None = None,
        error: Exception | None = None,
        evidence_segment_id: str | None = None,
    ) -> None:
        self.output_tokens = output_tokens
        self.stop_reasons = stop_reasons or {}
        self.error = error
        self.evidence_segment_id = evidence_segment_id
        self.requests: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def create(self, **request: Any) -> SimpleNamespace:
        with self._lock:
            self.requests.append(request)
        if self.error is not None:
            raise self.error
        payload = json.loads(request["messages"][0]["content"])["payload"]
        text = " ".join(segment["text"] for segment in payload["segments"])
        stop_reason = next(
            (reason for marker, reason in self.stop_reasons.items() if marker in text),
            "end_turn",
        )
        output = RuleBasedIsnadProvider().generate_structured(
            prompt="",
            schema_name="",
            payload=payload,
        )
        wire_output = {
            kind: [
                {
                    **{key: value for key, value in item.items() if key != "merge_key_payload"},
                    "properties": [
                        {"name": name, "value": value}
                        for name, value in item["properties"].items()
                    ],
                    "evidence_refs": [
                        {
                            "segment_id": self.evidence_segment_id or evidence["segment_id"],
                            "quote": evidence["quote"],
                        }
                        for evidence in item["evidence_refs"]
                    ],
                }
                for item in output[kind]
            ]
            for kind in ("nodes", "relations")
        }
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text=json.dumps(wire_output, ensure_ascii=False))
            ],
            stop_reason=stop_reason,
            stop_details=None,
            model=request["model"],
            usage=SimpleNamespace(
                input_tokens=1000,
                output_tokens=self.output_tokens,
                cache_read_input_tokens=None,
                cache_creation_input_tokens=None,
            ),
        )


def _load_script() -> ModuleType:
    spec = spec_from_file_location("run_isnad_experiment", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    condition: str,
    hadiths: list[dict[str, str]] | None = None,
    messages: FakeMessages | None = None,
    out_name: str = "out",
    extra_arguments: list[str] | None = None,
) -> tuple[int, Path, dict[str, Any]]:
    module = _load_script()

    def fake_provider(effort: str) -> AnthropicLLMProvider:
        assert messages is not None, "this condition must not build an LLM provider"
        return AnthropicLLMProvider(client=SimpleNamespace(messages=messages), effort=effort)

    monkeypatch.setattr(module, "anthropic_provider_from_settings", fake_provider)
    input_path = tmp_path / "hadiths.json"
    input_path.write_text(json.dumps(hadiths or HADITHS, ensure_ascii=False), encoding="utf-8")
    out_dir = tmp_path / out_name
    exit_code = module.main(
        [
            "--input",
            str(input_path),
            "--out-dir",
            str(out_dir),
            "--condition",
            condition,
            "--cache-dir",
            str(tmp_path / "cache"),
            *(extra_arguments or []),
        ]
    )
    report = json.loads((out_dir / "run_report.json").read_text(encoding="utf-8"))
    return exit_code, out_dir, report


def test_rule_condition_runs_without_a_model_and_exports_all_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exit_code, out_dir, report = _run(tmp_path, monkeypatch, condition="rule")

    assert exit_code == 0
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == EXPECTED_ROWS
    assert _read_jsonl(out_dir / "system_validated.jsonl") == EXPECTED_ROWS
    assert (report["condition"], report["model"], report["effort"]) == ("rule", None, None)
    assert (report["provider"], report["segmentation_strategy"]) == ("rule_based_isnad", "isnad")
    assert report["calls"] == {
        "total": 4,
        "uncached": 4,
        "cached": 0,
        "failed": 0,
        "refused": 0,
        "truncated": 0,
        "failed_by_kind": {},
    }
    assert (report["cost_usd"], report["budget_stopped"]) == (0.0, False)
    assert report["candidates_proposed"] == {"nodes": 8, "relations": 5}
    assert len(_read_jsonl(out_dir / "calls.jsonl")) == 4
    assert len(_read_jsonl(out_dir / "candidates.jsonl")) == 13
    assert not (tmp_path / "cache").exists()


def test_chain_condition_makes_one_call_per_chain_and_accounts_tokens_and_cost(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages = FakeMessages()

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition="llm_isnad_chain",
        messages=messages,
    )

    assert exit_code == 0
    assert len(messages.requests) == 4
    for request in messages.requests:
        assert request["model"] == "claude-haiku-5-5"
        assert request["output_config"]["effort"] == "low"
        assert request["output_config"]["format"]["type"] == "json_schema"
        assert "temperature" not in request
        payload = json.loads(request["messages"][0]["content"])["payload"]
        assert len(payload["segments"]) == 1
        assert payload["schema"]["node_types"][0]["extraction_hints"] != []
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == EXPECTED_ROWS
    assert _read_jsonl(out_dir / "system_validated.jsonl") == EXPECTED_ROWS

    calls = _read_jsonl(out_dir / "calls.jsonl")
    assert [(call["hadith_id"], call["call_index"], call["segment_orders"]) for call in calls] == [
        ("Muslim:978", 1, [1]),
        ("Muslim:978", 2, [2]),
        ("Bukhari:1", 1, [1]),
        ("Note:7", 1, [1]),
    ]
    for call in calls:
        assert (call["model"], call["effort"], call["cached"]) == ("claude-haiku-5-5", "low", False)
        assert (call["input_tokens"], call["output_tokens"]) == (1000, 200)
        assert call["stop_reason"] == "end_turn"
        assert call["cost_usd"] == pytest.approx(0.0002)
        assert call["error"] is None
        assert call["latency_ms"] >= 0

    assert (report["condition"], report["model"], report["effort"]) == (
        "llm_isnad_chain",
        "claude-haiku-5-5",
        "low",
    )
    assert (report["provider"], report["segmentation_strategy"]) == ("anthropic", "isnad")
    assert report["calls"]["total"] == 4
    assert (report["calls"]["uncached"], report["calls"]["cached"]) == (4, 0)
    assert report["tokens"] == {
        "input": 4000,
        "output": 800,
        "cache_read_input": 0,
        "cache_creation_input": 0,
    }
    assert report["cost_usd"] == pytest.approx(0.0008)
    assert report["cost_usd_without_response_cache"] == pytest.approx(0.0008)
    assert (report["budget_stopped"], report["stop_reason"]) == (False, None)
    assert report["hadith_ids_not_processed"] == []
    assert report["schema_proposals"] == []
    assert report["candidates_by_reason_code"] == {"node": {}, "relation": {}}
    assert report["committed_fact_invariants"]["holds"] is True
    assert report["committed_fact_invariants_with_grounding_normalisation"]["holds"] is True
    assert report["runs"]["committed"] == 3
    assert [item["hadith_id"] for item in report["per_hadith"]] == [
        "Muslim:978",
        "Bukhari:1",
        "Note:7",
    ]
    assert [item["calls"] for item in report["per_hadith"]] == [2, 1, 1]
    assert [item["open_review_items"] for item in report["per_hadith"]] == [0, 0, 0]

    candidates = _read_jsonl(out_dir / "candidates.jsonl")
    narrators = {
        (row["hadith_id"], row["name"]): row
        for row in candidates
        if row["kind"] == "node" and row["type"] == "Narrator"
    }
    assert narrators[("Muslim:978", "اللَّيْثُ")]["mention_indexes"] == [3]
    assert narrators[("Muslim:978", "اللَّيْثُ")]["call_indexes"] == [2]
    assert narrators[("Muslim:978", "اللَّيْثُ")]["status"] == "validated"
    assert narrators[("Muslim:978", "اللَّيْثُ")]["confidence"] == 0.95
    assert narrators[("Muslim:978", "اللَّيْثُ")]["evidence_quotes"] == ["اللَّيْثُ"]
    relations = [row for row in candidates if row["kind"] == "relation"]
    assert len(relations) == 5
    assert ("سُفْيَانُ", "ابْنِ شِهَابٍ") in {
        (row["from_name"], row["to_name"]) for row in relations
    }
    assert all(row["type"] == "NARRATED_FROM" for row in relations)
    assert all(row["properties"]["hadith_ref"] == row["hadith_id"] for row in relations)


def test_second_run_is_served_from_the_response_cache_at_no_cost(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages = FakeMessages()
    _run(tmp_path, monkeypatch, condition="llm_isnad_chain", messages=messages)

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition="llm_isnad_chain",
        messages=messages,
        out_name="again",
        extra_arguments=["--max-cost-usd", "0"],
    )

    assert exit_code == 0
    assert len(messages.requests) == 4
    assert (report["calls"]["uncached"], report["calls"]["cached"]) == (0, 4)
    assert report["cost_usd"] == 0.0
    assert report["cost_usd_without_response_cache"] == pytest.approx(0.0008)
    assert report["tokens"]["input"] == 4000
    assert (report["budget_stopped"], report["hadith_ids_not_processed"]) == (False, [])
    assert all(call["cached"] for call in _read_jsonl(out_dir / "calls.jsonl"))
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == EXPECTED_ROWS
    assert report["runs"]["committed"] == 3


@pytest.mark.parametrize(
    ("condition", "with_hints"),
    [("llm_schema_whole", False), ("llm_isnad_whole", True)],
)
def test_whole_conditions_make_one_call_per_hadith_with_or_without_hints(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    condition: str,
    with_hints: bool,
) -> None:
    messages = FakeMessages()

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition=condition,
        messages=messages,
        extra_arguments=["--model", "claude-sonnet-5-5", "--effort", "medium", "--workers", "1"],
    )

    assert exit_code == 0
    assert len(messages.requests) == 3
    assert (report["segmentation_strategy"], report["segments"]) == ("paragraphs", 3)
    assert (report["model"], report["effort"]) == ("claude-sonnet-5-5", "medium")
    assert report["schema_hints"] is with_hints
    for request, hadith in zip(messages.requests, HADITHS, strict=True):
        assert request["model"] == "claude-sonnet-5-5"
        assert request["output_config"]["effort"] == "medium"
        payload = json.loads(request["messages"][0]["content"])["payload"]
        assert [segment["text"] for segment in payload["segments"]] == [hadith["raw"]]
        schema = payload["schema"]
        types = {item["name"]: item for item in schema["node_types"] + schema["relation_types"]}
        assert sorted(types) == ["Hadith", "NARRATED_FROM", "Narrator", "TRANSMITS"]
        assert types["Narrator"]["merge_keys"] == ["name"]
        assert types["NARRATED_FROM"]["merge_keys"] == ["hadith_ref", "chain_no", "position"]
        assert [item["name"] for item in types["NARRATED_FROM"]["properties"]] == [
            "hadith_ref",
            "chain_no",
            "position",
            "sigha",
        ]
        for type_definition in types.values():
            described = type_definition["description"] != type_definition["name"]
            assert described is with_hints
            assert all(
                (item["description"] is not None) is with_hints
                for item in type_definition["properties"]
            )
        for type_name in ("Narrator", "Hadith", "NARRATED_FROM"):
            assert (types[type_name]["extraction_hints"] != []) is with_hints
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == EXPECTED_ROWS
    # 1000 input and 200 output tokens per call at 2.00 and 10.00 USD per million.
    assert report["cost_usd"] == pytest.approx(3 * 0.004)


def test_run_stops_issuing_calls_when_the_next_one_could_exceed_the_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Each call costs 0.0041 USD; one more worst-case call does not fit into 0.006 after it.
    messages = FakeMessages(output_tokens=8000)

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition="llm_isnad_chain",
        hadiths=[BUKHARI, MUSLIM, NOTE],
        messages=messages,
        extra_arguments=["--max-cost-usd", "0.006", "--workers", "1"],
    )

    assert exit_code == 0
    assert len(messages.requests) == 1
    assert (report["budget_stopped"], report["stop_reason"]) == (True, "budget")
    assert report["cost_usd"] == pytest.approx(0.0041)
    assert report["cost_usd"] <= report["max_cost_usd"] == 0.006
    assert (report["hadiths_requested"], report["hadiths"]) == (3, 1)
    assert report["hadith_ids_not_processed"] == ["Muslim:978", "Note:7"]
    assert report["calls"]["total"] == 1
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == [EXPECTED_ROWS[1]]
    assert [call["hadith_id"] for call in _read_jsonl(out_dir / "calls.jsonl")] == ["Bukhari:1"]
    assert {row["hadith_id"] for row in _read_jsonl(out_dir / "candidates.jsonl")} == {
        "Bukhari:1"
    }
    assert report["runs"]["committed"] == 1


def test_refused_and_truncated_calls_fail_alone_and_are_counted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages = FakeMessages(stop_reasons={"رُمْحٍ": "refusal", "أَنَسٍ": "max_tokens"})

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition="llm_isnad_chain",
        messages=messages,
    )

    assert exit_code == 0
    assert len(messages.requests) == 4
    assert report["calls"] == {
        "total": 4,
        "uncached": 4,
        "cached": 0,
        "failed": 2,
        "refused": 1,
        "truncated": 1,
        "failed_by_kind": {"max_tokens": 1, "refusal": 1},
    }
    # Failed calls are billed for the tokens the API reports.
    assert report["cost_usd"] == pytest.approx(0.0008)
    assert (report["budget_stopped"], report["hadith_ids_not_processed"]) == (False, [])
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == [
        {"hadith_id": "Muslim:978", "mentions": ["قُتَيْبَةُ بْنُ سَعِيدٍ", "لَيْثٌ"]},
        {"hadith_id": "Bukhari:1", "mentions": []},
        {"hadith_id": "Note:7", "mentions": []},
    ]
    failed = {
        (call["hadith_id"], call["call_index"]): call
        for call in _read_jsonl(out_dir / "calls.jsonl")
        if call["error"] is not None
    }
    assert failed[("Muslim:978", 2)]["error_kind"] == "refusal"
    assert failed[("Muslim:978", 2)]["stop_reason"] == "refusal"
    assert failed[("Bukhari:1", 1)]["error_kind"] == "max_tokens"
    assert "max_tokens=8000" in failed[("Bukhari:1", 1)]["error"]
    assert report["runs"]["blocked_hadith_ids"] == ["Bukhari:1"]
    # Failed calls are asked again by the next run.
    assert len(list((tmp_path / "cache").iterdir())) == 2


def test_rejected_api_key_stops_the_run_after_the_first_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    messages = FakeMessages(
        error=anthropic.AuthenticationError(
            "invalid x-api-key",
            response=httpx2.Response(401, request=request),
            body=None,
        )
    )

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition="llm_isnad_chain",
        messages=messages,
        extra_arguments=["--workers", "1"],
    )

    assert exit_code == 0
    assert len(messages.requests) == 1
    assert (report["budget_stopped"], report["stop_reason"]) == (
        False,
        "provider_error:authentication",
    )
    assert report["hadith_ids_not_processed"] == ["Muslim:978", "Bukhari:1", "Note:7"]
    assert report["cost_usd"] == 0.0
    (call,) = _read_jsonl(out_dir / "calls.jsonl")
    assert call["error_kind"] == "authentication"
    assert "AuthenticationError, status 401" in call["error"]
    assert _read_jsonl(out_dir / "system_proposed.jsonl") == []


def test_output_the_engine_does_not_accept_is_recorded_on_its_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages = FakeMessages(evidence_segment_id="segment-that-does-not-exist")

    exit_code, out_dir, report = _run(
        tmp_path,
        monkeypatch,
        condition="llm_isnad_chain",
        hadiths=[BUKHARI],
        messages=messages,
    )

    assert exit_code == 0
    (call,) = _read_jsonl(out_dir / "calls.jsonl")
    assert call["error_kind"] == "engine_rejected_output"
    assert "does not belong to the run source" in call["error"]
    assert call["stop_reason"] == "end_turn"
    assert report["calls"]["failed_by_kind"] == {"engine_rejected_output": 1}
    assert report["cost_usd"] == pytest.approx(0.0002)
    assert report["runs"]["blocked_hadith_ids"] == ["Bukhari:1"]


def test_model_without_a_listed_price_is_refused(tmp_path: Path) -> None:
    module = _load_script()

    with pytest.raises(ValueError, match="no price is listed"):
        module.run_experiment(
            [("Bukhari:1", BUKHARI["raw"])],
            condition_name="llm_isnad_chain",
            model="some-other-model",
            effort="low",
            workers=1,
            max_cost_usd=1.0,
            cache_dir=tmp_path,
        )


def test_cost_follows_the_price_table_including_prompt_cache_tokens() -> None:
    module = _load_script()
    usage = module.LLMUsage(
        input_tokens=1_000_000,
        output_tokens=100_000,
        cache_read_input_tokens=1_000_000,
        cache_creation_input_tokens=1_000_000,
    )

    assert module.PRICES_AS_OF == "2026-10-06"
    assert module.PRICES_USD_PER_MTOK == {
        "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
        "claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
    }
    # 0.10 + 0.01 + 0.125 for the three kinds of input, 0.05 for the output.
    assert module.call_cost_usd("claude-haiku-5-5", usage) == pytest.approx(0.285)
    assert module.call_cost_usd("claude-sonnet-5-5", usage) == pytest.approx(5.7)
    assert module.call_cost_usd(None, usage) == 0.0
    worst_case = module.worst_case_call_cost_usd(
        "claude-haiku-5-5",
        prompt="p" * 1000,
        payload={"text": "x" * 988},
    )
    # 1000 + 1000 request bytes and 2000 overhead tokens of input, 8000 tokens of output.
    assert worst_case == pytest.approx((4000 * 0.10 + 8000 * 0.50) / 1_000_000)
