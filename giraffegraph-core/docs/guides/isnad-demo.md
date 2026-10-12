# Isnad demo: API call sequence

This guide lists the API calls that turn an empty backend into a project whose hadith narrator
chains can be read in the dashboard's "Zincirleri oku" step. A seeding script only needs these calls.

The sequence was run against the in-memory backend with five hadiths from a pilot file and the
`rule_based_isnad` provider. It was not run against Postgres and Neo4j.

## Start the backend

```bash
cd backend
REPOSITORY_BACKEND=memory ALLOWED_ORIGINS=http://localhost:3000 \
  uv run uvicorn app.main:app --app-dir src --port 8000
```

The in-memory backend keeps its data only while the process runs. `ALLOWED_ORIGINS` must contain
the origin the dashboard is served from.

The examples use `API=http://localhost:8000`.

## 1. Create the project with the template schema

```bash
curl -s -X POST "$API/api/projects" -H 'Content-Type: application/json' -d '{
  "name": "Isnad demo",
  "template_id": "isnad",
  "apply_template_schema": true
}'
```

`apply_template_schema` defaults to `false`. When it is `true` and the template carries a schema
blueprint (`GET /api/templates` shows `schema_blueprint` for each template; only `isnad` has one),
the request also creates schema version 1 with the template's node and relation types, activates
it, and creates pipeline definition `v1`. For a template without a blueprint the flag has no effect.

Response (`201`):

```json
{
  "project_id": "…",
  "name": "Isnad demo",
  "template_id": "isnad",
  "status": "active",
  "template_schema": {
    "schema_version_id": "…",
    "version_no": 1,
    "status": "active",
    "pipeline_version": "v1",
    "segmentation_strategy": "isnad"
  }
}
```

`template_schema` is `null` when no schema was applied. Keep `project_id`.

## 2. Load the hadiths

```bash
curl -s -X POST "$API/api/projects/$PROJECT_ID/source-units/bulk" \
  -H 'Content-Type: application/json' -d '{
  "source_type": "hadith",
  "items": [
    {"external_ref": "Muslim:978", "title": "Muslim 978", "raw_content": "حَدَّثَنَا …"},
    {"external_ref": "Muslim:1050", "raw_content": "حَدَّثَنَا …"}
  ]
}'
```

- `items`: 1 to 1000 objects. `external_ref` and `raw_content` are required; `title` defaults to
  `external_ref`. Each item becomes one source unit.
- `source_type` defaults to `document`.
- `schema_version_id` is optional and defaults to the project's active schema. Without an active
  schema the request fails with `422`.
- The hadith reference used by the chain endpoints is `external_ref`.

A pilot file with `{coll, num, raw}` rows maps to `external_ref = "<coll>:<num>"` and
`raw_content = raw`. The dashboard's "Metin yükle" step does this mapping; the API accepts only
the `{external_ref, title, raw_content}` form.

Response (`200`):

```json
{
  "project_id": "…",
  "schema_version_id": "…",
  "created_count": 2,
  "duplicate_count": 0,
  "results": [
    {"index": 0, "external_ref": "Muslim:978", "status": "created",
     "source_unit_id": "…", "detail": null}
  ]
}
```

An item whose `external_ref` already exists in the project, or occurs earlier in the same request,
gets `"status": "duplicate"`, `"source_unit_id": null` and a `detail` message. The other items are
still created. Keep the `source_unit_id` values of the created items.

## 3. Process the source units

```bash
curl -s -X POST "$API/api/projects/$PROJECT_ID/source-units/process" \
  -H 'Content-Type: application/json' -d '{
  "source_unit_ids": ["…", "…"],
  "llm_provider": "rule_based_isnad",
  "commit": true
}'
```

For each source unit, in order: start a run, cut segments, extract candidates, validate. The request
is synchronous and takes 1 to 200 ids.

| Field | Default | Meaning |
|---|---|---|
| `llm_provider` | server default (`DEFAULT_LLM_PROVIDER`) | `rule_based_isnad` needs no key or network. An unregistered provider fails the request with `422` before any run starts. |
| `llm_model` | server default | Passed to the provider. |
| `segmentation_strategy` | the project template's strategy, else `paragraphs` | `isnad` for an isnad project. |
| `pipeline_version` | `v1` | |
| `commit` | `false` | When `true`, a run with no open review item is committed to the graph. |

Response (`200`):

```json
{
  "project_id": "…",
  "segmentation_strategy": "isnad",
  "llm_provider": "rule_based_isnad",
  "llm_model": null,
  "processed_count": 2,
  "failed_count": 0,
  "committed_count": 2,
  "results": [
    {"source_unit_id": "…", "external_ref": "Muslim:978", "status": "committed",
     "run_id": "…", "segment_count": 2,
     "candidate_node_count": 7, "candidate_relation_count": 5,
     "validated_node_count": 7, "validated_relation_count": 5,
     "open_review_count": 0, "failed_call_count": 0, "detail": null}
  ]
}
```

`status` per unit:

- `committed`: validated and written to the graph (`commit: true`, no open review item).
- `validated`: validated, no open review item, not committed (`commit: false`). Commit it with
  `POST /api/runs/{run_id}/commit`.
- `needs_review`: the run has open review items. Decide them with
  `POST /api/review-items/{review_item_id}/decision`, then call `POST /api/runs/{run_id}/commit`.
- `failed`: `detail` holds the reason. A unit that is already in a run fails with
  "Source unit is already processing."; the other units are not affected.

Only committed runs appear in the chain endpoints.

## 4. Read the chains

List the committed hadiths (`q` filters by reference or title, case-insensitive):

```bash
curl -s "$API/api/projects/$PROJECT_ID/chains?q=muslim"
```

```json
{"project_id": "…", "total_count": 1, "hadiths": [
  {"hadith_ref": "Muslim:978", "source_unit_id": "…", "title": "Muslim 978",
   "run_id": "…", "committed_at": "…"}
]}
```

Read one hadith:

```bash
curl -s -G "$API/api/projects/$PROJECT_ID/chains/hadith" --data-urlencode "hadith_ref=Muslim:978"
```

```json
{
  "project_id": "…",
  "hadith_ref": "Muslim:978",
  "committed": true,
  "source_unit": {"source_unit_id": "…", "title": "Muslim 978", "raw_content": "حَدَّثَنَا …"},
  "runs": [{"run_id": "…", "committed_at": "…", "llm_provider": "rule_based_isnad",
            "llm_model": null}],
  "chains": [
    {
      "chain_no": 1,
      "narrators": ["قُتَيْبَةُ بْنُ سَعِيدٍ", "لَيْثٌ"],
      "links": [
        {
          "position": 1,
          "from_narrator": "قُتَيْبَةُ بْنُ سَعِيدٍ",
          "to_narrator": "لَيْثٌ",
          "sigha": "حدثنا",
          "evidence": [
            {"segment_id": "…", "segment_order": 1, "segment_text": "…", "quote": "…",
             "start_offset": 11, "end_offset": 54,
             "source_start_offset": 11, "source_end_offset": 54}
          ],
          "acceptance": {"kind": "policy", "policy": "auto_validated",
                         "rule_code": "candidate_relation_valid",
                         "action": null, "reviewer_id": null, "decided_at": null}
        }
      ]
    }
  ],
  "narrators": [
    {"name": "قُتَيْبَةُ بْنُ سَعِيدٍ", "evidence": [{"…": "…"}], "acceptance": {"…": "…"}}
  ]
}
```

- `chains` is ordered by `chain_no`, `links` by `position`. `from_narrator` received the hadith from
  `to_narrator`.
- `start_offset` and `end_offset` are the stored offsets inside the segment. `source_start_offset`
  and `source_end_offset` locate the quote in `raw_content`; they are `null` when the quote cannot
  be located. Offsets count Unicode code points.
- `acceptance.kind` is `human` (with `action`, `reviewer_id`, `decided_at`) or `policy` (with
  `policy` and `rule_code`).
- `narrators` lists every committed narrator of the hadith in text order, including one that is in
  no link.
- A reference with nothing committed returns `200` with `"committed": false` and empty `runs`,
  `chains` and `narrators`. `source_unit` is `null` when no source unit has that reference.

Read one narrator:

```bash
curl -s -G "$API/api/projects/$PROJECT_ID/chains/narrator" --data-urlencode "name=اللَّيْثُ"
```

```json
{
  "project_id": "…",
  "name": "اللَّيْثُ",
  "hadith_count": 1,
  "hadiths": [{"hadith_ref": "Muslim:978", "source_unit_id": "…", "title": "Muslim 978"}],
  "narrated_from_count": 1,
  "narrated_from": [{"name": "ابْنِ شِهَابٍ", "link_count": 1, "hadith_refs": ["Muslim:978"]}],
  "narrated_to_count": 1,
  "narrated_to": [{"name": "مُحَمَّدُ بْنُ رُمْحٍ", "link_count": 1, "hadith_refs": ["Muslim:978"]}]
}
```

`narrated_from` are the narrators this one received from, `narrated_to` the narrators who received
from this one. An unknown name returns `404`.

## 5. Open the dashboard

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Open the project and go to the step "Zincirleri oku". The same sequence is available in the dashboard
itself: "Yeni proje" (step 1), "Metin yükle" (step 2) and "Zincirleri çıkar" (step 3).

## Known limits

- A narrator is identified by the exact written name. Different people with the same name share one
  node, and the same person written differently is several nodes.
- The pipeline definition does not store a segmentation strategy. The process call takes it from the
  project's template or from `segmentation_strategy` in the request.
- The chain endpoints read every source unit and run of the project on each request.
- The process call runs inside the request. With a network provider, send the units in small
  batches; the dashboard sends 10 per request.
