# GiraffeGraph Core

GiraffeGraph Core is an LLM-assisted, human-in-the-loop engine for building a knowledge graph from
text. A project defines a schema (node types, relation types, properties, merge keys). Source text is
split into segments, an LLM proposes candidate nodes and relations for those segments, rule-based
validation checks each candidate against the schema, uncertain or conflicting candidates go to a
human review queue, and only validated candidates are written to the graph. The project is a
university capstone and is in development; the first case study is hadith narrator chains (isnad).

## Status

Implemented:

- Projects, versioned schemas and per-schema pipeline definitions. Type and property names must be
  ASCII identifiers; `display_name` carries the human-readable label. Creating a project can apply
  its template's schema in the same request (`apply_template_schema`, default `false`); of the
  built-in templates only `isnad` carries a schema.
- Source unit ingestion (raw text), one at a time or in bulk
  (`POST /api/projects/{id}/source-units/bulk`, up to 1000 items; an `external_ref` that already
  exists is reported as a duplicate and the other items are created), and two segmentation
  strategies: `paragraphs` and `isnad` (one segment per narrator chain, with source offsets).
- A process action (`POST /api/projects/{id}/source-units/process`, up to 200 source units, one
  synchronous request) that starts a run for each source unit, cuts segments, extracts and
  validates, and with `commit: true` commits every run that has no open review item.
- Candidate extraction through a provider (`noop`, `rule_based_isnad`, `openai` or `anthropic`;
  `rule_based_isnad` needs no network), plus manual candidate entry through the API. With `isnad`
  segmentation there is one call per chain; a failed call does not discard the others.
- Validation against the schema: type existence, required properties, merge keys, relation endpoint
  types, allowed enum values, per-type confidence thresholds, duplicate detection within a run and
  against the graph. A candidate with an unknown type is dropped on its own and the unknown type is
  recorded as a review item; undeclared property keys are removed and recorded the same way.
- Grounding checks on extracted candidates: the quotation must occur in its source segment, and a
  string merge-key value must occur in the quotation or equal the source unit's external reference.
  A candidate that fails a check goes to review; it is not auto-validated.
- Relation identity: a relation type can declare `merge_keys`, so two relations between the same two
  nodes with different key values are stored as separate edges.
- Review queue with `accept`, `reject` and `edit` decisions. Every decision is stored with the
  reviewer name, time and optional duration, and decisions are append-only. Re-validation does not
  change a candidate a reviewer has decided.
- Acceptance records per run: for each validated candidate, the human decision or the automatic
  policy that accepted it.
- Commit of a run to Neo4j with a stored graph delta and links back to source units and segments.
  A run is written in one transaction, so a failed commit leaves no part of the run in the graph.
  The repository creates five range indexes for its lookups.
- A job queue (`extract_candidates`, `validate_run`, `commit_run`) with a worker process.
- Read endpoints for the committed graph, and chain and narrator read endpoints under
  `/api/projects/{id}/chains` (committed hadiths, the chains of one hadith with evidence and
  acceptance, one narrator with the narrators before and after it).
- A dashboard in Turkish for non-developers: a home page with the projects, and per project four
  steps (load text, extract chains, review, read chains), with the schema editor, step-by-step runner,
  job list and raw graph explorer under "Gelişmiş". Screenshots are in `frontend/docs/screens/`.
  [`docs/guides/isnad-demo.md`](docs/guides/isnad-demo.md) lists the API calls from an empty backend
  to a project whose chains can be read in the dashboard.
- An evaluation kit in [`evaluation/`](evaluation/README.md): scorer, annotation sheet and
  guideline, an experiment runner with a spending limit and an on-disk response cache, and scripts
  that analyse and compare runs.

Verified:

- Real databases. The 12 tests marked `real_db` run the Alembic migrations, the isnad flow and the
  review decisions against Postgres and Neo4j. They passed on 2026-10-12 against PostgreSQL 16 and
  Neo4j 5.26 in local containers; the output of that run is not stored in the repository. See
  [Run the backend tests](#run-the-backend-tests) for how to run them.
- Real LLM runs. On 2026-10-12 the `anthropic` provider was run with Claude Haiku 5.5 at effort
  `low` on 300 hadiths in three conditions, next to the rule-based provider. The run reports, the
  analyses and the comparison tables are in [`evaluation/results/`](evaluation/README.md#results).
  The scores there are agreement with platform or rule-generated labels. No human reviewed any of
  these runs, and none of the label sets is a human gold standard.

Not implemented, and known limits:

- Undo or rollback of a committed run.
- Authentication, users and permissions. The reviewer name is typed in the dashboard and trusted.
- Narrator identity resolution. In the isnad template a narrator node is identified by its exact
  name string, so different people with the same short name share a node and the same person
  written differently does not.
- Chains that start after the text of the report (matn) are not made into segments.
- The grounding checks apply only to candidates that came from an extraction call. Candidates
  entered through the candidate API are not checked against the text.
- Acceptance records are computed when they are requested; they are not stored.
- The relation-detail endpoint addresses a relation by its type and its two end nodes. When several
  edges of one type join the same two nodes, it cannot address one of them.
- The dashboard lists a language-model method only when the server accepts that provider; it finds
  out by sending a request that cannot start a run, because the API has no endpoint that lists providers.
- The `anthropic` provider sends each `properties` object as a list of `{name, value}` entries,
  because its structured output accepts closed objects only. Claude Sonnet 5.5 at effort `low`
  misused that format on a 36-hadith run: with the isnad template schema it returned a single
  narrator node for 28 of the 36 hadiths and wrote the narrator name into the `name` field of the
  entry, which the engine records as an unknown property key, and 30 of the 36 runs could not be
  committed (`evaluation/results/2026-10-12-subset36/`). This is a failure of the wire format and
  the effort setting, not a comparison of models. Only Claude Haiku 5.5 at effort `low` has been
  run on the 300 hadiths.
- No human-annotated reference exists yet, so no score in `evaluation/results/` is an accuracy.
- No licence has been chosen.

With the default `noop` provider, extraction returns no candidates. `rule_based_isnad` needs no key.
Extraction with an LLM needs the `openai` or `anthropic` provider, its API key and a model name
(see [Environment variables](#environment-variables)).

## Architecture

- `backend/` is a FastAPI application in four layers: `domain` (entities and rules), `application`
  (use cases and ports), `infrastructure` (Postgres, Neo4j, in-memory and LLM adapters) and
  `interfaces` (HTTP API and the worker CLI). `bootstrap` wires them together.
- Postgres 16 stores metadata: projects, schemas, source units, segments, runs, jobs, candidates,
  validation results, review items, review decisions (`review_decisions`) and graph deltas. Alembic
  manages its schema.
- Neo4j 5 stores the committed graph.
- An in-memory backend implements the same repository ports. It is the default when
  `REPOSITORY_BACKEND` is not set, and the test suite uses it.
- `frontend/` is a Next.js dashboard that talks to the API.

Design documents and ADRs are in [`docs/`](docs/README.md) (in Turkish).

## Prerequisites

- Git.
- To run the stack: Docker with Docker Compose v2.
- To run the backend tests: [uv](https://docs.astral.sh/uv/). uv installs Python if needed. The
  Docker image and CI use Python 3.12.
- To build the dashboard outside Docker: Node.js 22 and npm.

## Run with Docker Compose

```bash
git clone git@github.com:GiraffeGraph/giraffegraph.git
cd giraffegraph/giraffegraph-core
cp .env.example .env
docker compose up --build
```

This starts five services: `postgres`, `neo4j`, `backend` (API), `worker` (job queue consumer) and
`dashboard`. The backend applies the Postgres migrations at startup.

| Service | Address |
|---|---|
| Dashboard | http://localhost:3000 |
| API | http://localhost:8000 (`/health`, interactive docs at `/docs`) |
| Neo4j Browser | http://localhost:7474 |
| Postgres | localhost:5432 |

Useful commands while the stack is running:

```bash
docker compose logs -f worker
docker compose exec backend alembic current
docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once
```

Stop the stack with `docker compose down`. Add `-v` to delete the database volumes as well.

## Run the backend tests

The tests use the in-memory backend. They need no Postgres, no Neo4j, no `.env` file and no network
access after the dependencies are installed.

```bash
cd backend
uv sync --extra dev
uv run pytest -q
```

285 tests are collected. Without the variables below the result is 273 passed and 12 skipped; the 12
carry the `real_db` marker.

The `real_db` tests run against real servers. Set these variables to servers that are running and
run the suite again, or select the marker:

| Variable | Value |
|---|---|
| `GG_TEST_POSTGRES_DSN` | e.g. `postgresql://user:password@127.0.0.1:55432/postgres` |
| `GG_TEST_NEO4J_URI` | e.g. `bolt://127.0.0.1:57687` |
| `GG_TEST_NEO4J_PASSWORD` | Password of the Neo4j user. |
| `GG_TEST_NEO4J_USERNAME` | Optional; defaults to `neo4j`. |

```bash
uv run pytest -q -m real_db
```

The Postgres role must be allowed to create databases: every use gets its own scratch database, so
the database named in the DSN is not written to. Neo4j has a single database; the graph written for
the test projects is deleted when the session ends.

Lint and type check:

```bash
uv run ruff check src tests
uv run mypy src
```

## Environment variables

Docker Compose reads these from `.env` in the repository root. `.env.example` lists all of them with
values that work for local development. Do not commit `.env`.

| Variable | Purpose |
|---|---|
| `APP_ENV` | Environment name. |
| `REPOSITORY_BACKEND` | Metadata and graph backend: `postgres` (with Neo4j) or `memory`. |
| `AUTO_APPLY_POSTGRES_MIGRATIONS` | Apply Alembic migrations when the backend starts. |
| `ALLOWED_ORIGINS` | Comma-separated origins allowed by CORS. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Postgres database name and credentials. |
| `POSTGRES_PORT` | Host port for Postgres. |
| `NEO4J_PASSWORD` | Password of the `neo4j` user. |
| `NEO4J_HTTP_PORT`, `NEO4J_BOLT_PORT` | Host ports for Neo4j Browser and Bolt. |
| `OPENAI_API_KEY` | API key for the `openai` provider. The provider is registered only when this is set. |
| `OPENAI_BASE_URL` | Base URL of the OpenAI-compatible API. |
| `OPENAI_TIMEOUT_SECONDS` | Request timeout for the `openai` provider. |
| `ANTHROPIC_API_KEY` | API key for the `anthropic` provider. The provider is registered only when this is set. |
| `ANTHROPIC_TIMEOUT_SECONDS` | Request timeout for the `anthropic` provider. |
| `ANTHROPIC_EFFORT` | Effort setting sent with every `anthropic` request: `low`, `medium`, `high`, `xhigh` or `max`. |
| `DEFAULT_LLM_PROVIDER` | Provider used when a run does not name one: `noop`, `rule_based_isnad`, `openai` or `anthropic`. |
| `DEFAULT_LLM_MODEL` | Model used when a run does not name one. The `openai` and `anthropic` providers fail without a model. |
| `DEFAULT_EXTRACTION_PROMPT_VERSION` | Version of the extraction prompt to use. |
| `PROCESSING_JOB_POLL_INTERVAL_SECONDS` | How often the worker polls for pending jobs. |
| `API_PORT`, `DASHBOARD_PORT` | Host ports for the API and the dashboard. |
| `NEXT_PUBLIC_API_BASE_URL` | API address used by the dashboard in the browser. |

## Repository layout

```text
backend/              FastAPI application, worker CLI, Alembic migrations, tests
  src/app/domain/           entities and rules
  src/app/application/      use cases and ports
  src/app/infrastructure/   Postgres, Neo4j, in-memory and LLM adapters
  src/app/interfaces/       HTTP API and worker CLI
  src/app/bootstrap/        application wiring
  migrations/               Alembic migrations
  tests/                    unit and integration tests
  scripts/                  isnad baseline and experiment runners for the case study
frontend/             Next.js dashboard
evaluation/           standalone scoring, analysis and annotation scripts for the case study
  results/                  outputs of the measurement runs
docs/                 architecture notes, glossary and ADRs (Turkish), guides (English)
docker-compose.yml    local stack: Postgres, Neo4j, API, worker, dashboard
.env.example          environment variables for Docker Compose
.github/workflows/    CI
```

## Case study: hadith isnad chains

A hadith is transmitted with an isnad: the chain of narrators through whom the report was passed
down, written before the text of the report. The case study uses the engine to turn Arabic hadith
text into a graph of narrators and "narrated from" links, with a human reviewer deciding on the
candidates the system is unsure about. Case-study code is in `backend/src/app/domain/hadith/`
(Arabic text normalisation, quote matching, a rule-based isnad segmenter) and `evaluation/` (a
scorer for narrator mentions and scripts for a human-annotated reference). The `isnad` segmentation
strategy and the grounding checks use these helpers, and the template catalog has an `isnad` schema
(`Narrator`, `Hadith`, `NARRATED_FROM`, `TRANSMITS`). Two sets of reference labels have been used:
the narrator tags of the Sanadset dataset, which were generated by rules, and the narrator markup
of the Ifta' Sunnah platform as restructured by a third party. Neither is a human gold standard, so
scores against them are agreement with a label set and are not reported as accuracy.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request. The backend job installs the locked
dependencies with uv and runs `ruff check src tests`, `mypy src` and `pytest`. The frontend job runs
`npm ci` and `npm run build`.

## Licence

No licence has been chosen yet.
