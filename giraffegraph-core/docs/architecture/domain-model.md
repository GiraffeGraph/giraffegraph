# Domain Model Baseline

## Core Product Entities

### Project

Bir calisma alani. Kendi schema'lari, source unit'leri ve run'lari vardir.

### DomainTemplate

Hazir baslangic paketi.

Ornek:

- Blank
- Story / Series / Film

### SchemaVersion

Bir proje icin aktif veya pasif halde bulunabilen ontology surumu.

### NodeTypeDefinition

Bir node tipinin tanimi.

Alan ornekleri:

- name
- description
- merge_keys
- extraction_hints
- is_core

### RelationTypeDefinition

Bir relation tipinin tanimi.

Alan ornekleri:

- name
- from_type
- to_type
- directional
- confidence_threshold

### PropertyDefinition

Node veya relation uzerindeki alan tanimi.

### SourceUnit

Sisteme verilen ham veri birimi.

Story template'te bu bir `Episode` olabilir, ama generic cekirdekte `SourceUnit` olarak kalir.

### Segment

SourceUnit'in islenebilir alt parcasi.

### ProcessingRun

Belirli bir source unit ve schema version uzerinde calisan pipeline kaydi.

`pipeline_version`, ilgili schema version icinde tanimli bir `PipelineDefinition`'a karsilik gelmelidir.
`schema_version_id`, bagli oldugu `SourceUnit.schema_version_id` ile ayni olmalidir.

### ProcessingJob

Queue'ya alinan ve worker/executor tarafindan islenen pipeline isi.

Ornek tipler:

- `extract_candidates`
- `validate_run`
- `commit_run`

### PipelineDefinition

Schema version seviyesinde tutulan processing orchestration tanimi.

Her step bir `job_type` ve `chain_on_success` listesi tasir.
Her yeni schema version generic varsayilan `v1` definition ile baslar.
Bu tanim varsa processing job enqueue sirasinda varsayilan zincir buradan cozulur.

### CandidateNode / CandidateRelation

Extraction sonucunda uretilen ama henuz canonical olmayan graph adaylari.

### ValidationResult

Candidate kaydinin hangi kurallardan gecip gecmedigini tutar.

### GraphDelta

Bir run'in canonical graph'ta yarattigi degisiklik ozetidir.

### ReviewItem

Insan karari gerektiren kayit.

## Domain Kurallari

- Canonical graph'a yalnizca validated candidate'lar yazilir.
- Her processing run bir schema version'a baglanir.
- Schema degisimi otomatik olarak canonical graph degisimi anlamina gelmez.
- Provenance, canonical graph icin zorunlu bir capability olarak dusunulur.

## Story Template v1 Cekirdek Tipleri

Ilk template icin minimum node tipleri:

- Series
- Season
- Episode
- Scene
- Character
- Event
- Location
- Organization

Ilk template icin minimum relation tipleri:

- HAS_SEASON
- HAS_EPISODE
- HAS_SCENE
- APPEARS_IN
- OCCURS_IN
- INVOLVED_IN
- PART_OF
- RELATED_TO

Daha detayli tablo:

- [`../templates/story-template-v1.md`](../templates/story-template-v1.md)
