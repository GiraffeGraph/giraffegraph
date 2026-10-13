# 04a — GiraffeGraph Core: kod gerçekte ne yapıyor

Repo: `github.com/GiraffeGraph/giraffegraph-core` (public, LICENSE yok, 206 tracked dosya, 2 commit). Kod bundle'ı: `14`. Repo dokümanları ve ADR'ler: `04b`. İnceleme tarihi 2026-09-30, Claude Code.

## Teknoloji
- Backend: Python ≥3.12, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic (Postgres 16), `neo4j` driver 6 (Neo4j 5 + APOC). Clean Architecture/DDD, modüler monolit (ADR-001).
- Worker: Postgres tabanlı job kuyruğu (`extract_candidates → validate_run → commit_run` zinciri, pipeline definition ile).
- Dashboard: Next.js 15 + React 19 iç panel (proje, şema, kaynak, run, review kuyruğu, graf gezgini). Grafik kütüphanesi yok.
- LLM: `noop` ve `openai` provider. OpenAI Chat Completions, `response_format: json_object`, `temperature: 0`. `OPENAI_BASE_URL` ayarlanabilir, yani OpenAI-uyumlu herhangi bir uç (vLLM, Ollama, OpenRouter) kullanılabilir. Anthropic/yerel provider yok.
- Testler: 48 test (memory backend). **47 geçti, 1 kaldı** (`test_prompt_catalog`: prompt metninde eski "Return structured JSON" ifadesini arıyor). 2026-09-30'da çalıştırıldı. `backend/uv.lock`, `pyproject.toml` ile senkron değil (`alembic` lock'ta yok).
- Tek şablon: `blank` ve `story` (Series/Season/Episode/Scene/Character/Event/Location/Organization). **Hadis şablonu yok.**

## Veri modeli (Postgres, 17 tablo)
`projects, schema_versions, node_types, relation_types, property_definitions, source_units, segments, processing_runs, pipeline_definitions, structured_prompts, extraction_executions, processing_jobs, candidate_nodes, candidate_relations, validation_results, review_items, graph_deltas`

- **Schema-as-data** (ADR-003). `NodeTypeDefinition` alanları: name, display_name, description, merge_keys, confidence_threshold (vars. 0.5), aliases, extraction_hints, properties. `RelationTypeDefinition` alanları: from_type, to_type, directional, aliases, required_properties, confidence_threshold (vars. 0.7). `PropertyDefinition` alanları: data_type, required, enum_values.
- `CandidateNode` alanları: node_type, properties, merge_key_payload, confidence, evidence_refs[segment_id, quote, start/end_offset], status ∈ {pending, validated, rejected, review, committed}.
- `CandidateRelation`: relation_type, from/to candidate ref, properties, confidence, evidence_refs.
- `ReviewItem` alanları: item_type, item_ref, reason_code, payload_json, status ∈ {open, accepted, rejected, edited}, reviewer_note, created_at. **reviewer kimliği ve karar zamanı yok.**
- `GraphDelta`: nodes/relations created/merged, rejected_count, review_count (her zaman 0 yazılıyor).

## Neo4j modeli
- Düğüm: `(:CanonicalNode:<Type> {project_id, node_type, merge_key})`. `merge_key` = normalize edilmiş merge_key_payload'ın SHA-256'sı. Özellikler `SET n += $properties` ile yazılıyor, yani **son yazan kazanır**.
- İlişki: `MERGE (a)-[r:<TYPE> {project_id, relation_type}]->(b)`. **Aynı çift arasında aynı tipten tek kenar olur.** Özellikler `SET r +=` ile üzerine yazılıyor.
- Provenance: `(n)-[:DERIVED_FROM {run_id, candidate_ref}]->(:SourceUnit)`, `(n)-[:SUPPORTED_BY {run_id, candidate_ref,…}]->(:Segment)`, `(:SourceUnit)-[:HAS_SEGMENT]->(:Segment)`.
- Label/tip adları `^[A-Za-z_][A-Za-z0-9_]*$` regex'inden geçmek zorunda. Uymayanlar commit anında `ValueError` fırlatıyor.

## Pipeline (gerçek davranış)

```
SourceUnit (raw_content)
  └─ generate_segments: yalnızca "paragraphs" stratejisi (boş satıra göre, yoksa satıra göre böl)
ProcessingRun (schema_version, pipeline_version, llm_provider, llm_model)
  └─ extract_candidates
       prompt = candidate_graph_extraction_v1 (sistem promptu) + JSON payload {schema(node/relation tipleri, hint'ler, property'ler), segments}
       LLM → {nodes[ref,node_type,properties,merge_key_payload,confidence,evidence_refs], relations[...]}
       _normalize_output — TÜM ÇIKTI İÇİN FAIL-CLOSED:
         • JSON kontratı uymazsa → tüm çıkarım hata
         • tanımsız node/relation tipi (alias dahil çözülür) → tüm çıkarım hata
         • relation from/to tipi şemayla uyuşmazsa → tüm çıkarım hata
         • evidence segment_id bu kaynağa ait değilse → tüm çıkarım hata
         • quote'un segment metninde geçip geçmediği KONTROL EDİLMEZ
       → CandidateNode/Relation kayıtları (status=pending)
  └─ validate_run (deterministik):
       Node: tip var mı · required property'ler · merge key'ler → eksikse REJECTED
             confidence < node_type.threshold → REVIEW, değilse VALIDATED
       Relation: tip var mı · uç düğümler var mı · from/to tip uyumu · required property'ler → eksikse REJECTED
             uç düğüm REJECTED → REJECTED · uç düğüm REVIEW veya confidence < threshold → REVIEW, değilse VALIDATED
       Duplicate: aynı normalize merge key (NFKC + trim + boşluk sıkıştırma + casefold) → ikincisi REVIEW
       Canonical eşleşme: mevcut Neo4j düğümüyle aynı merge key → bilgi notu
       Uygulanmayan: data_type, enum_values, directional, kardinalite, alan kuralları, grounding, zaman/tarih kontrolleri
       → ValidationResult kayıtları + REVIEW olanlar için ReviewItem
  └─ (insan) decide_review_item: accept | reject | edit (node_type/properties/merge_key/refs/confidence)
       Edit sonrası aynı deterministik kurallar yeniden koşar. Bağımlı relation review'ları otomatik güncellenir/kapanır
  └─ commit_run:
       Açık review varsa veya pending aday varsa commit reddedilir
       Sadece VALIDATED adaylar yazılır; REJECTED olanlar sayılır ama yazılmaz
       Her düğüm/ilişki AYRI Neo4j transaction'ında (execute_write) yazılır → toplu işlem atomik değil
       Neo4j yazımı bitince GraphDelta Postgres'e yazılır (iki store arasında 2PC/outbox yok)
       Aynı run için ikinci commit ConflictError verir. Geri alma (revert) yok
```

## Çıkarım promptu (birebir özet, `14`)
"You are extracting candidate graph suggestions from segmented source material. Use only the provided schema node and relation types, including aliases." Ardından JSON şablonu geliyor, kurallar: ref benzersiz olacak, tip adları şemayla birebir eşleşecek, merge key değeri properties içine konacak, yalnızca verilen segment_id'ler kullanılacak, ekstra alan olmayacak. **Few-shot yok, alan-özgü talimat yok, "emin değilsen üretme" talimatı yok.**

## Güçlü yanlar (korunmalı)
- LLM'in DB'ye doğrudan yazma yetkisi yok. Aday → doğrulama → canonical ayrımı var (ADR-005).
- Schema-as-data, versiyonlanmış şema, pipeline definition.
- Segment düzeyinde provenance kenarları.
- Fail-closed çıktı kontratı, alias çözümleme.
- Temiz, test edilmiş, katmanlı kod. Genişletme noktaları belli (validation kuralları, provider, prompt katalog).
- Run, execution, job, delta kayıtları sayesinde denetim izi için iyi bir başlangıç var.
