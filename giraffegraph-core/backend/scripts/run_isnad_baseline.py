"""Run the rule-based isnad baseline through the pipeline and export scorer inputs.

Each hadith becomes one source unit that goes through isnad segmentation, the
`rule_based_isnad` provider and validation. No review decision is made; runs the
commit service accepts are committed, the others stay uncommitted. Everything runs
on the in-memory repository backend without network access.

Usage (from backend/):
  uv run python scripts/run_isnad_baseline.py --input <hadiths.json> --out-dir <dir> [--limit N]

Input: a JSON list of objects with `coll`, `num` and `raw`.
Output: system_proposed.jsonl, system_validated.jsonl, run_report.json.
Exit status is 1 when a committed fact lacks a quote found in its source segment or
an acceptance record.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from app.infrastructure.template.catalog import ISNAD_TEMPLATE_SCHEMA

sys.path.insert(0, str(Path(__file__).resolve().parent))

from isnad_pipeline import (  # noqa: E402
    PipelineResult,
    build_report,
    create_memory_container,
    create_project,
    extract,
    load_hadiths,
    prepare_run,
    quote_mention,
    validate_and_commit,
    write_scorer_files_and_report,
)

PROVIDER_NAME = "rule_based_isnad"


def run_baseline(hadiths: list[tuple[str, str]]) -> PipelineResult:
    container = create_memory_container()
    project_id, schema_id = create_project(
        container,
        name="Isnad rule-based baseline",
        node_types=ISNAD_TEMPLATE_SCHEMA.node_types,
        relation_types=ISNAD_TEMPLATE_SCHEMA.relation_types,
    )
    result = PipelineResult(container=container, project_id=project_id, runs=[])
    for hadith_id, raw in hadiths:
        hadith_run = prepare_run(
            container,
            project_id=project_id,
            schema_id=schema_id,
            hadith_id=hadith_id,
            raw=raw,
            provider_name=PROVIDER_NAME,
            model=None,
            strategy=ISNAD_TEMPLATE_SCHEMA.segmentation_strategy,
        )
        result.runs.append(hadith_run)
        extract(container, hadith_run)
        validate_and_commit(container, hadith_run)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the rule-based isnad baseline and export scorer inputs."
    )
    parser.add_argument("--input", required=True, type=Path, help="JSON list with coll, num, raw")
    parser.add_argument("--out-dir", required=True, type=Path, help="directory for the exports")
    parser.add_argument("--limit", type=int, help="only run the first N hadiths")
    args = parser.parse_args(argv)

    started = time.perf_counter()
    try:
        hadiths = load_hadiths(args.input, args.limit)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    result = run_baseline(hadiths)
    report = {
        "input": str(args.input),
        **build_report(
            result,
            provider_name=PROVIDER_NAME,
            strategy=ISNAD_TEMPLATE_SCHEMA.segmentation_strategy,
            mention_text=quote_mention,
        ),
    }
    report["wall_time_seconds"] = round(time.perf_counter() - started, 3)
    write_scorer_files_and_report(result, args.out_dir, report, mention_text=quote_mention)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["committed_fact_invariants"]["holds"]:
        print(
            "error: a committed fact lacks a quote in its source segment or an acceptance record",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
