# Appendix A Reproducing the results

All commands are run from `giraffegraph-core/`. The evaluation data is described in `data/README.md` in the project workspace and is not redistributed.

Backend tests, with no database or network:

```
cd backend
uv sync --extra dev
uv run pytest -q
```

Tests against real databases need a PostgreSQL 16 and a Neo4j 5 instance and three environment variables:

```
GG_TEST_POSTGRES_DSN=... GG_TEST_NEO4J_URI=... GG_TEST_NEO4J_PASSWORD=... uv run pytest -q -m real_db
```

One evaluation run and its analysis:

```
cd backend
uv run python scripts/run_isnad_experiment.py --input <hadiths.json> --out-dir <run-dir> \
    --condition llm_isnad_whole --model claude-haiku-5-5 --effort low --max-cost-usd 0.85
cd ..
python evaluation/analyze_experiment.py --run <run-dir> --reference <reference.jsonl> --out <run-dir>/analysis
python evaluation/compare_runs.py --runs <run-dir> <run-dir> ... --reference <reference.jsonl> --out compare.md
python evaluation/extra_tables.py --runs <run-dir> ... --reference <reference.jsonl> \
    --reference-chains <reference_chains.jsonl> --out extra-tables.json
python evaluation/classify_value_flags.py --run <run-dir> --hadiths <hadiths.json> \
    --reference <reference.jsonl> --out value-flag-classes.json
python evaluation/identity_baseline.py --reference-chains <reference_chains.jsonl> --out identity.json
```

Model responses are cached under `backend/var/llm-cache/`. With the cache present a run makes no API call and reproduces the same output.

# Appendix B Result files

| Content | Path under `giraffegraph-core/evaluation/results/` |
|---|---|
| Six-book test set, four conditions | `2026-10-12-sixbooks300/` (`compare-ifta.md`, `extra-tables-ifta.json`, one folder per run; `haiku-llm_schema_whole/value-flag-classes.json`) |
| Pilot set, four conditions | `2026-10-12-pilot50/` (`compare-sanadset.md`) |
| Second-model subset | `2026-10-12-subset36/` (`compare-ifta.md`) |
| Narrator identity baseline | `2026-10-12-identity-baseline/sixbooks300.json` |
| Rule-based baseline of the first end-to-end run | `2026-10-12-rule-based-baseline/` |

Each run folder holds the system output in the scorer's format, one line per candidate with its status and reason codes, one line per provider call with tokens and latency, a run report and the analysis.

# Appendix C Use of AI tools

AI assistants were used throughout this project: for the literature search, for the design analysis and pilot of 30 September 2026, for most of the code written on the evaluated branch, for the analysis scripts, and for drafting this report. The extraction experiments themselves use a language model as the system under test.

To limit the risks of this way of working we applied the following rules. Bibliographic records were retrieved from Crossref, arXiv, the ACL Anthology or the publisher's first page, never written from memory; three references in an earlier project document could not be found in any index and are not used here. Every measured number in this report was produced by a script and is stored in a result file; statistics of the data sets are taken from the data manifest. Code was accepted only with tests, and the tests marked for real databases were run against PostgreSQL and Neo4j. A draft of this report was checked by an independent AI reviewer against the result files, and the report was corrected where it claimed more than the files show. Statements about other work are limited to what was read in the cited source.

The authors are responsible for the content of this report.
