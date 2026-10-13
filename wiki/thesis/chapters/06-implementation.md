# 6 Implementation

This chapter describes the code on the `main` branch of the `giraffegraph-core` repository. Most of the code on this branch was written with AI coding assistants under the authors' direction and is verified by the automated test suite described in Section 6.7.

## 6.1 Technology stack

| Part | Technology | Declared version |
|---|---|---|
| Backend | Python, FastAPI, Uvicorn, Pydantic | Python `>=3.12` (3.12 in the Docker image and in CI), `fastapi>=0.115`, `uvicorn>=0.34`, `pydantic>=2.10` |
| Metadata store | PostgreSQL, SQLAlchemy, psycopg, Alembic | image `postgres:16-alpine`, `sqlalchemy>=2.0`, `psycopg>=3.2`, `alembic>=1.15` |
| Graph store | Neo4j and its Python driver | image `neo4j:5`, `neo4j>=6.0,<7.0` |
| Model access | `anthropic` SDK; OpenAI-compatible HTTP API through the standard library | `anthropic>=1.13,<2.0` |
| Dashboard | Next.js, React, TypeScript | `next ^15`, `react ^19`, `typescript ^5`; Node 22 in CI |
| Tooling | uv, pytest, ruff, mypy in strict mode | `pytest>=8.3`, `ruff>=0.11`, `mypy>=1.15` |

Versions are the constraints declared in `backend/pyproject.toml`, `frontend/package.json` and `docker-compose.yml`. Docker Compose starts five services: `postgres`, `neo4j`, `backend`, `worker` and `dashboard`.

## 6.2 Repository layout

```text
backend/
  src/app/domain/          entities, segmentation, hadith helpers, identity keys
  src/app/application/     use cases and ports
  src/app/infrastructure/  LLM providers, template catalog, persistence
  src/app/interfaces/      API routers and worker CLI
  src/app/bootstrap/       application wiring
  migrations/versions/     Alembic migrations 0001 to 0006
  scripts/                 baseline and experiment runners
  tests/unit, tests/integration
frontend/src/modules/projects/   dashboard components, API client, types
evaluation/                scorer, analysis, annotation kit, their tests
```

## 6.3 API surface

The 13 routers in `interfaces/api/routers/` define 53 endpoints: 33 `GET` and 20 `POST`.

| Group | Count | Representative endpoints |
|---|---|---|
| Projects, templates | 4 | `POST /api/projects`, `GET /api/templates` |
| Schema | 7 | `POST /api/schema-versions/{schema_version_id}/node-types` |
| Pipeline definitions | 3 | `GET /api/schema-versions/{schema_version_id}/pipeline-definitions` |
| Ingestion and runs | 8 | `POST /api/projects/{project_id}/source-units/bulk`, `POST /api/projects/{project_id}/source-units/process`, `POST /api/source-units/{source_unit_id}/runs` |
| Segments, candidates, validation | 10 | `POST /api/source-units/{source_unit_id}/segments/generate`, `POST /api/runs/{run_id}/validate`, `GET /api/runs/{run_id}/review-items` |
| Extraction | 2 | `POST /api/runs/{run_id}/extract-candidates` |
| Review | 4 | `GET /api/projects/{project_id}/review-queue`, `POST /api/review-items/{review_item_id}/decision`, `GET /api/runs/{run_id}/acceptance-records` |
| Commit | 2 | `POST /api/runs/{run_id}/commit`, `GET /api/runs/{run_id}/graph-delta` |
| Jobs | 4 | `POST /api/runs/{run_id}/processing-jobs`, `POST /api/processing-jobs/process-next` |
| Graph | 5 | `GET /api/projects/{project_id}/graph/nodes` |
| Chains | 3 | `GET /api/projects/{project_id}/chains/hadith`, `GET /api/projects/{project_id}/chains/narrator` |
| Health | 1 | `GET /health` |

Application errors map to the status codes 404, 409, 422 and 502 in `error_handlers.py`.

## 6.4 LLM provider abstraction

The port `LLMProvider` has two methods. `generate_structured` returns the answer as a dictionary, and `generate_structured_with_usage` returns it with an `LLMUsage` record. `StaticLLMProviderRegistry` holds the providers by name. `noop` (returns no candidates) and `rule_based_isnad` (Section 5.8) are always registered; `openai` and `anthropic` are registered only when their API key is set.

- **OpenAI-compatible** (`openai_provider.py`). It posts to `{base_url}/chat/completions` with `temperature` 0 and `response_format` set to `json_object`, and treats an answer cut at the token limit as an error. It reports no token counts.
- **Anthropic** (`anthropic_provider.py`). It calls the Messages API with an `output_config` that carries the effort setting and a JSON schema (`EXTRACTION_WIRE_SCHEMA`). Because the schema allows closed objects only, properties travel as a list of name and value entries and are folded back into a map. The effort comes from `ANTHROPIC_EFFORT` (default `low`). A refusal, a truncated answer and each class of API error become a `StructuredGenerationError` with a `kind`. Usage holds input and output tokens, cache read and cache creation tokens, the stop reason and the model.

The prompt catalog holds two versions, `candidate_graph_extraction_v1` and `candidate_graph_extraction_v2`, which differ in the rule for matching type names; `v2` is the default.

`CachedLLMProvider` wraps a provider and stores one JSON file per call. The key is the SHA-256 hash of the provider name, model, effort, prompt version, prompt text and payload, after the run, schema version, source unit and segment identifiers in the payload are replaced by positional placeholders. A later run with the same content is therefore a hit, and the stored answer is mapped back to the new run's segment ids. Failed calls are not stored.

The extraction use case calls `generate_structured` and stores no token counts. The cache and the usage records are used by `scripts/run_isnad_experiment.py`, which writes tokens, latency and cost per call and stops issuing calls at a spending limit.

## 6.5 Persistence

**Postgres.** The ORM declares 18 tables. Migration `0001` creates the 15 baseline tables; `0002` adds the node type confidence threshold, `0003` the `processing_jobs` table, `0004` the `pipeline_definitions` table, `0005` the `merge_keys` column of `relation_types`, and `0006` the `review_decisions` table with two indexes. The backend applies the migrations at startup when `AUTO_APPLY_POSTGRES_MIGRATIONS` is true. A job is claimed with `FOR UPDATE SKIP LOCKED` and an advisory lock per run, and a run with a running job gets no second one.

**Neo4j.** `commit_bundle` passes `_write_bundle` to `session.execute_write`, so all statements of a run share one transaction. It merges the source unit and its segments, then each node on (`project_id`, `node_type`, `merge_key`) with the labels `CanonicalNode` and the type name, then each relation with its identity key. Provenance is written as `DERIVED_FROM` to the source unit, `SUPPORTED_BY` to segments, one `RelationEvidence` node per committed relation candidate, and a `GraphDelta` node. Type names are checked against the identifier pattern before they enter a statement. Five indexes are created with `CREATE INDEX ... IF NOT EXISTS` on the first commit of a process: one on the node key and one each on the id property of `SourceUnit`, `Segment`, `RelationEvidence` and `GraphDelta`. No uniqueness constraint is defined. Quotations and offsets stay in the candidate rows in Postgres; the graph links to whole segments.

## 6.6 Dashboard

The dashboard is a Next.js application in Turkish, written for a reader who is not a developer. Its colours and type follow the project's public page. The home page explains the product in two sentences and lists the projects as cards with a status sentence, for example "30 hadis · hepsi grafta · bekleyen yok" (30 hadiths, all in the graph, nothing waiting). Creating a project asks only for a name; the isnad template and its schema are applied automatically.

A project is a sequence of four steps shown as a stepper with counts, and each step is one screen with one main action.

1. **Metin yükle (load text).** The user pastes text, picks a JSON file, or loads ten bundled sample hadiths with one click. The result, duplicates included, is reported in a sentence.
2. **Zincirleri çıkar (extract chains).** The user chooses a method: rules, or a language model if the server has one configured. One button processes every hadith that is waiting and ends with a summary of how many hadiths were written to the graph and how many need a decision.
3. **İncele (review).** Only suggestions that need a person appear, one at a time: the hadith text with the quotation highlighted, the suggested value, one sentence that says why it waits, and three actions (accept, reject, correct). Each review reason code has its own sentence; for the value check it reads "the suggested name does not occur in the quotation the system showed". The reviewer's name is asked once and stored in the browser, and the time between opening an item and deciding it is sent with the decision.
4. **Zincirleri oku (read chains).** The committed hadiths are listed with a search field. For the selected hadith the Arabic text is shown right to left with each narrator mention highlighted at its source offsets. Each chain reads from top to bottom: a narrator, then the link with its transmission wording, its quotation and how it was accepted, written out as "accepted automatically (passed the checks)" or "accepted by a person" with the name and date. Selecting a narrator shows the hadiths the name occurs in and the names it received from and passed to, with a note that a narrator is identified by the written name.

The schema editor, the step-by-step pipeline runner, the job list and the raw graph explorer are behind one secondary entry, "Gelişmiş" (advanced). A glossary of five terms is reachable from every page. Screenshots of each screen are in `frontend/docs/screens/`.

## 6.7 Testing and continuous integration

`uv run pytest --collect-only -q` collects 285 tests: 127 unit tests in 14 files and 158 integration tests in 21 files. Our run of `uv run pytest -q` gave 273 passed and 12 skipped. Integration tests drive the API through FastAPI's `TestClient` on the in-memory backend with scripted providers, so no test calls a network service.

The 12 skipped tests carry the `real_db` marker. `test_realdb_migrations.py` (4 tests) runs the migration chain on an empty database, compares the result with the ORM models, and checks the downgrade. `test_realdb_isnad_flow.py` (7 tests) runs the isnad flow on Postgres and Neo4j: the same narrator pair in two hadiths gives two edges, a repeated graph write adds nothing, an interrupted write leaves no partial graph, and the lookup indexes exist. `test_realdb_review_decisions.py` (1 test) checks that decisions are stored and appended. These tests run only when `GG_TEST_POSTGRES_DSN`, `GG_TEST_NEO4J_URI` and `GG_TEST_NEO4J_PASSWORD` are set; they create and drop scratch Postgres databases. On 12 October 2026 they were run against PostgreSQL 16 and Neo4j 5.26 in local containers and all 12 passed; on the same day the 214 tests that existed at that point were also run once against those databases and passed. That verification found four defects that the in-memory backend had hidden, among them a graph write that used one transaction per node and could leave a partial graph, and the absence of any Neo4j index. All four are fixed.

The evaluation kit has its own tests in `evaluation/tests/`: 72 tests in six files; 71 pass and one is skipped unless `numpy` and `scipy` are installed, because it compares the scorer with the pilot script. The dashboard has no automated tests.

The CI workflow runs two jobs on every push and pull request. The backend job runs `ruff check src tests`, `mypy src` and `pytest -q`; the frontend job runs `npm ci` and `npm run build`. CI sets no database variables, so it skips the `real_db` tests, and it does not run the evaluation kit's tests.

## 6.8 How to run it

The full stack, from the repository root:

```bash
cp .env.example .env
docker compose up --build
```

The dashboard is then at `http://localhost:3000` and the API at `http://localhost:8000`.

The backend tests and checks:

```bash
cd backend
uv sync --extra dev
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

The isnad demo without databases or an API key, following `docs/guides/isnad-demo.md`:

```bash
cd backend
REPOSITORY_BACKEND=memory ALLOWED_ORIGINS=http://localhost:3000 \
  uv run uvicorn app.main:app --app-dir src --port 8000
```

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

The guide then creates a project from the `isnad` template, loads hadiths through the bulk endpoint, processes them with the `rule_based_isnad` provider, and reads the chains.

## 6.9 Known limitations

Three capabilities are absent by decision: there is no undo of a committed run, no authentication, and no narrator identity resolution.

The code has these further limits.

- The graph delta row is written to Postgres after the Neo4j transaction. A failure between the two leaves the graph ahead of the metadata.
- Node properties are written with `SET n += $properties`, so a later run overwrites a differing value without a review item.
- Accepting a schema proposal closes the review item and does not change the schema.
- The process endpoint runs inside the request, and the chain endpoints scan all source units and runs of the project.
- The relation detail endpoint has no identity key parameter, so for parallel edges it returns one of them.
- Generating segments again replaces the stored segments with new ids, so the evidence refs of earlier runs point at segments that do not exist.
- The dashboard shows only the first reason when a suggestion has several, computes project counts in the browser from two requests per project, and has no automated tests.
- No licence has been chosen.
