# System Overview

## Mimari Ozet

Sistem iki ana duzlemde calisir:

- `Design-time`: Schema / ontology / pipeline tanimlama
- `Run-time`: Source ingest etme, candidate graph cikarimi, validation ve canonical commit

## Katmanlar

### 0. Katman: Schema / Ontology Design

Bu katman su soruya cevap verir:

`Bu proje icin hangi node tipleri, relation tipleri, property'ler ve validation kurallari gerekli?`

Kaynaklar:

- Core system types
- Domain template defaults
- AI schema suggestions
- Dashboard manual edits

Cikti:

- Active schema version
- Validation rule set
- Merge strategy definitions
- Extraction hints

### 1. Katman: Source Ingestion

Bu katman source unit'i sisteme alir.

Ornek source unit tipleri:

- Episode
- Script file
- Transcript
- Document
- Note batch

Temel adimlar:

- Upload
- Metadata attach
- Normalize
- Segment

### 2. Katman: Candidate Extraction

LLM ve deterministic parser'lar birlikte calisir.

Uretilen yapilar:

- CandidateNode
- CandidateRelation
- CandidateEvent
- Evidence reference

Bu katman canonical graph'a dogrudan yazmaz.

### 3. Katman: Resolution and Validation

Bu katman sistem kalitesini korur.

Kontroller:

- Allowed relation
- Required property
- Merge key uygunlugu
- Duplicate / alias / entity resolution
- Confidence-based review routing
- Continuity or domain rule validation

### 4. Katman: Canonical Graph Commit

Validation'dan gecen adaylar Neo4j'ye delta olarak yazilir.

Model:

`Candidate -> Validation -> Canonical`

Yazim mantigi:

- MERGE / upsert
- Provenance links
- Delta report

### 5. Katman: Review and Audit

Belirsiz, cakisali veya dusuk confidence'li adaylar review queue'ya duser.

Review akisinda:

- Accept
- Reject
- Edit
- Merge override

### 6. Katman: Retrieval and Consumption

Bu repo'nun birinci faz odagi degil; ancak ileride canonical graph uzerinden:

- Graph QA
- Hybrid GraphRAG
- Analytics
- Agent memory context

uretilebilir.

## Ana Veri Aritmeti

Sistem iteratif calisir:

`Graph(t) + SourceUnit(t+1) -> Graph(t+1)`

Bu yuzden her run bir `delta package` uretir:

- Ne eklendi
- Ne merge edildi
- Ne reject edildi
- Ne review'a dustu

## Storage Strategy

- `Postgres`: Project, schema, config, run metadata, candidate metadata, review queue
- `Neo4j`: Canonical graph, provenance relations, retrieval-ready structure

## GraphRAG Konumu

GraphRAG cekirdegin yerine gecmez.

Dogru konum:

- Optional adapter
- Retrieval-time helper
- Gerektiginde extraction plugin'i

Core engine dogrudan GraphRAG package'ina bagimlanmaz.
