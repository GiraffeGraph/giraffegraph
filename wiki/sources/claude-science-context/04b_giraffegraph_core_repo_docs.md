# GiraffeGraph Core — in-repo docs (verbatim, Turkish/English mix)

---
## FILE: README.md
# GiraffeGraph Core

GiraffeGraph Core, ham ve dağınık verileri adım adım işlenebilir, doğrulanabilir ve büyütülebilir bir bilgi grafiğine dönüştüren genel amaçlı bir platform.

İlk alan şablonumuz `Story / Series / Film` olacak. Ancak çekirdek sistem doğrudan dizi ya da filme bağlı değil; şema tabanlı, yapay zeka destekli ve panelden yönetilebilir bir platform olarak kurgulanıyor.

Bu repo yalnızca ürünün iç panelini ve çekirdek motorunu kapsar. SaaS landing page bu reponun dışındadır.

## Ürün Tanımı

Ürünün amacı:

- Ham veriyi normalleştirmek
- Veriyi şemaya göre varlık, ilişki ve olay adaylarına çevirmek
- Aday veriyi doğrulamak
- Doğrulanan veriyi kalıcı grafik katmanına yazmak
- Her yeni kaynak birimi ile bilgi grafiğini yinelemeli olarak büyütmek

Zihinsel model:

`Grafik(t) + KaynakBirimi(t+1) -> Grafik(t+1)`

Bu yüzden ürün tek seferlik bir içe aktarma aracı değil, zaman içinde büyüyen bir grafik oluşturma platformudur.

## Temel İlkeler

- Alana özel kavramları çekirdeğe gömme; ayrı şablon olarak tut
- Şemayı kod olarak değil, veri olarak yönet
- Yapay zeka önerir, sistem karar verir
- Aday → Doğrulama → Kesinleşme
- Güven skoru düşükse insan incelemesi zorunlu
- Temiz mimari + önce tekli modüler yapı

## Repository Layout

- [`docs/README.md`](docs/README.md): Dokuman giris noktasi
- [`docs/architecture/system-overview.md`](docs/architecture/system-overview.md): Mimari omurga
- [`docs/architecture/development-environment.md`](docs/architecture/development-environment.md): Docker ve lokal gelistirme ortami
- [`docs/glossary/domain-language.md`](docs/glossary/domain-language.md): Ortak dil
- [`docs/adr/`](docs/adr): Architecture Decision Record'lar
- [`backend/README.md`](backend/README.md): Backend klasor yapisi ve amaci
- [`frontend/README.md`](frontend/README.md): Frontend klasor yapisi ve amaci

## Documentation Order

Projede yeni bir karar alinacagi zaman once su sirayla ilerlenir:

1. Problem ve kapsam yazilir.
2. Gerekirse deep research prompt hazirlanir.
3. Sonuc dokumante edilir.
4. ADR yazilir.
5. Kod iskeleti ve kontratlar guncellenir.

## Deep Research Workflow

Kullanici talebine gore, guncel ve kolay degisebilecek teknik konularda ek dis arastirma gerektiginde once bir `deep research prompt` hazirlanir. Kullanici o prompt ile arastirma yaptirip sonucu geri yollar; mimari ve implementasyon kararlarinda bu sonuc temel alinir.

Hazir reusable prompt burada tutulur:

- [`docs/research/deep-research-prompts.md`](docs/research/deep-research-prompts.md)

## Mevcut Kapsam

Bu aşamada odak:

- Genel çekirdek mimariyi kurmak
- Şema yönetimini tasarlamak
- Veri alımı → çıkarım → doğrulama → grafik kayıt hattını netleştirmek
- Story şablonunu ayrı bir alan paketi olarak tanımlamak

Bu aşamada odak değil:

- Ajan simülasyonu
- Sorgulama ürünü
- Gelişmiş GraphRAG arayüzü
- Çok alanlı şablon marketi

Notlar:

- Tüm metadata (proje, şema, kaynak birim, çalıştırma, iş, segment, aday, doğrulama, inceleme, grafik deltası) artık Postgres üzerinde tutuluyor.
- Postgres şeması Alembic migration'ları ile yönetiliyor.
- Testler ve izole çalıştırmalar için varsayılan backend `memory` olarak kalır.
- İşlem kuyruğu (extract_candidates, validate_run, commit_run) altyapısı mevcut; worker servisi bekleyen işleri otomatik tüketir.
- Panel içinde proje bazlı iş görünürlüğü eklendi; kuyruk durumu operatör panelinden izlenebilir.
- Şema versiyonu bazında pipeline tanımları tutulur; yeni şema oluşturulduğunda varsayılan v1 pipeline otomatik oluşturulur.
- Bir çalıştırma başlatmak için seçilen pipeline versiyonunun ilgili şema versiyonunda tanımlı olması zorunlu.
- Grafik yazım adımı; delta kaydı, düğüm/ilişki birleştirme ve köken bağlantılarını içeriyor.
- İnceleme kararı akışı açık: tekrar tespit, düşük güven skorlu adaylar karar altına alınabiliyor.
- Düzenleme kararları şema kurallarına göre yeniden doğrulanıyor; geçersiz düzenleme grafik yazım adımına geçemiyor.
- Kesinleşmiş grafik için temel okuma endpoint'leri hazır: genel bakış, düğüm listesi, ilişki listesi.

## Sonraki Adım

- Pipeline tanım editörü / panel görünürlüğü
- Varlık çözümleme ve tekrar tespit katmanını ilerletmek
- Kesinleşmiş grafik okuma modelleri

## Local Development

Docker Compose tabanli hot reload gelistirme ortami icin:

1. `.env.example` dosyasini `.env` olarak kopyalayin.
2. `docker compose up --build` calistirin.

Migration komutlari:

- `docker compose exec backend alembic upgrade head`
- `docker compose exec backend alembic current`
- `docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once --job-type extract_candidates`
- `docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once --run-id <run_id>`

Servisler:

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000`
- Worker: `docker compose logs -f worker`
- Neo4j Browser: `http://localhost:7474`
- Postgres: `localhost:5432`

---

gitingest . \
  -e "*.lock" \
  -e "tests/" \
  -e "docs/" \
  -e "**/migrations/versions/" \
  -e ".gitkeep" \
  -e "alembic.ini" \
  -e "script.py.mako" \
  -e "next-env.d.ts" \
  -e ".dockerignore" \
  -e "__init__.py"
---
## FILE: docs/README.md
# Belgeler

Bu klasör, GiraffeGraph Core'un ürün, mimari ve geliştirme kararlarını toplar.

## Okuma Sırası

1. [`architecture/product-overview.md`](architecture/product-overview.md)
2. [`architecture/system-overview.md`](architecture/system-overview.md)
3. [`architecture/development-environment.md`](architecture/development-environment.md)
4. [`architecture/bounded-contexts.md`](architecture/bounded-contexts.md)
5. [`architecture/domain-model.md`](architecture/domain-model.md)
6. [`glossary/domain-language.md`](glossary/domain-language.md)
7. [`templates/story-template-v1.md`](templates/story-template-v1.md)
8. [`roadmap/initial-roadmap.md`](roadmap/initial-roadmap.md)
9. [`adr/`](adr)

## Neden Bu Sırayla?

Önce ürünün ne olduğu, sonra sistemin sınırları, ardından alan dili ve kararlar okunur. Kod iskeleti bu belgelerin üzerine kurulur.

---
## FILE: docs/architecture/product-overview.md
# Ürün Genel Bakış

## Ürün Nedir?

GiraffeGraph Core, ham ve dağınık verileri şemaya bağlı bir işleme hattından geçirip kalıcı bir bilgi grafiğine dönüştüren genel amaçlı bir platformdur.

İlk alan şablonu `Story / Series / Film`'dir. Ancak sistemin çekirdeği şu soru etrafında kurulur:

`Bir kaynak birimi, panelden tanımlanan şemaya göre nasıl grafiğe dönüştürülür?`

Bu reponun arayüz tarafı genel kullanıma açık bir site değil, yalnızca iç operasyon panelidir.

## Ürünün Vaadi

- Ham veriyi anlaşılır hâle getirir.
- İlişkileri ve değişimleri görünür kılar.
- Her yeni veri kaynağıyla grafiği yinelemeli olarak büyütür.
- Yapay zeka yardımı alır; ama kararı sistem ve kullanıcı verir.
- Panel üzerinden şema, çalıştırma, inceleme ve pipeline yönetimini mümkün kılar.

## İlk Kullanım Senaryosu

Story şablonu ile sistem şu türden verileri alabilir:

- Senaryo
- Transkript
- Bölüm özeti
- Sahne kırılımları
- Karakter notları

Ve bunlardan şu bilgi yapılarını üretir:

- Karakter grafiği
- Olay grafiği
- İlişki grafiği
- Durum değişimi ve süreklilik haritası
- Kaynak destekli hikâye grafiği

## Uzun Vadeli Yön

Platform yalnızca hikâye verisi için değil, başka alanlar için de çalışacak şekilde tasarlanır:

- Araştırma külliyatı grafiği
- Hukuki dava grafiği
- Olay zaman çizelgesi grafiği
- Kurumsal bilgi grafiği

## Kısa Tanım

Yapay zeka destekli, şema tabanlı ve panel üzerinden yönetilebilir genel amaçlı grafik üretim platformu.

---
## FILE: docs/architecture/system-overview.md
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

---
## FILE: docs/architecture/bounded-contexts.md
# Bounded Contexts

## 1. Project Management

Sorumluluk:

- Project lifecycle
- Template secimi
- Genel ayarlar

Temel kavramlar:

- Project
- Workspace settings
- DomainTemplate binding

## 2. Schema Management

Sorumluluk:

- NodeTypeDefinition
- RelationTypeDefinition
- PropertyDefinition
- SchemaVersion
- Schema activation
- Schema drift suggestions

## 3. Ingestion

Sorumluluk:

- SourceUnit olusturma
- Raw content normalization
- Segmentation
- Processing run baslatma

## 4. Extraction

Sorumluluk:

- Schema-aware candidate extraction
- Core extraction
- Custom extraction
- Evidence capture

## 5. Resolution

Sorumluluk:

- Alias resolution
- Entity matching
- Merge key hazirlama
- Duplicate detection

## 6. Validation

Sorumluluk:

- Type compatibility checks
- Required property checks
- Confidence routing
- Domain rule checks

## 7. Graph Commit

Sorumluluk:

- GraphDelta olusturma
- Neo4j upsert islemleri
- Provenance baglari
- Commit raporu

## 8. Review and Audit

Sorumluluk:

- Review queue
- Human decisions
- Run history
- Decision traceability

## 9. Retrieval and Exploration

Sorumluluk:

- Graph browsing
- Search
- Future GraphRAG retrieval
- Analytics ve graph exploration

---
## FILE: docs/architecture/domain-model.md
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

---
## FILE: docs/architecture/development-environment.md
# Development Environment

## Scope

Bu repo'da sadece dashboard ve core engine gelistirilir.

Bu repo'nun disinda kalanlar:

- Marketing site
- SaaS landing page
- Public-facing waitlist veya pricing pages

## Dev Stack

Lokal gelistirme ortami Docker Compose ile calisir.

Servisler:

- `dashboard`: Next.js tabanli internal dashboard
- `backend`: FastAPI tabanli API
- `worker`: tum pending processing job'larini tuketen queue worker'i
- `postgres`: metadata, config ve run store
- `neo4j`: canonical graph store

Repository secimi:

- Docker ortaminda backend `REPOSITORY_BACKEND=postgres` ile calisir
- Test ve yalitilmis uygulama calistirmalarinda varsayilan backend `memory` olarak kalir
- Docker/Postgres ortaminda metadata schema'si Alembic migration'lari ile yonetilir

## Neden Docker + Hot Reload?

- Herkes ayni runtime ile calisir
- Postgres ve Neo4j kurulumu elle yapilmaz
- Dashboard ve API ayni anda tek komutla acilir
- Kod degisiklikleri container restart gerektirmeden gorulur

## Hot Reload Kararlari

### Backend

- `uvicorn --reload`
- Bind mount ile kaynak kod container'a baglanir
- `WATCHFILES_FORCE_POLLING=true` ile macOS ve bind mount senaryolari daha guvenli hale gelir

### Dashboard

- `next dev`
- Bind mount ile kaynak kod container'a baglanir
- `WATCHPACK_POLLING=true` ile dosya degisiklikleri daha guvenli izlenir
- `node_modules` ve `.next` container volume'lerinde tutulur

## Calistirma

1. Root dizinde `.env.example` dosyasini `.env` olarak kopyala
2. `docker compose up --build`

Migration komutlari:

- `docker compose exec backend alembic upgrade head`
- `docker compose exec backend alembic current`
- `docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once --job-type extract_candidates`
- `docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once --run-id <run_id>`
- `docker compose up -d worker`

## Portlar

- Dashboard: `3000`
- API: `8000`
- Worker: compose service olarak calisir, port acmaz
- Neo4j Browser: `7474`
- Neo4j Bolt: `7687`
- Postgres: `5432`

## Mevcut Baseline

Su an calisan metadata omurgasi:

- Project module
- Schema management API
- SourceUnit ingestion endpoints
- ProcessingRun endpoints
- Processing job queue endpoints
- Segment generation endpoints
- Candidate node / relation endpoints
- Validation result endpoints
- Review item endpoints
- Graph delta endpoints
- Review decision endpoint'leri
- Duplicate resolution endpoint'i
- Neo4j canonical node/relation MERGE
- Temel provenance link'leri
- Commit oncesi relation -> node bagimlilik guvencesi
- Dependent relation review auto-refresh
- `extract_candidates`, `validate_run`, `commit_run` job type'lari
- Run-filter'li processing job enqueue/list/process-next akislari
- Project-level processing job queue read-model endpoint'i
- `schema-version` seviyesinde pipeline definition create/list/get endpoint'leri
- Processing job chaining icin metadata-backed pipeline default'lari
- Yeni schema create sirasinda varsayilan `v1` pipeline definition auto-seed edilir
- Processing run create sirasinda `pipeline_version` -> `pipeline definition` existence guard'i
- Processing run create sirasinda `source schema` ile `run schema` eslesme guard'i
- Queue'yu tuketen ayri `worker` service'i
- Canonical graph overview / node / relation read endpoint'leri

## Sonraki Adim

Bu baseline'dan sonra siradaki uygulama adimi:

- Entity resolution / dedup katmanini derinlestirmek
- Pipeline definition editor / dashboard visibility
- Canonical read model ve graph browser baglantisi
- Dashboard review queue ve operator akislari
- Dashboard graph explorer akisi

---
## FILE: docs/glossary/domain-language.md
# Domain Language

Bu sozluk ekipte ayni kelimeleri ayni anlamla kullanmak icin tutulur.

## Generic Core Terms

### SourceUnit

Sisteme verilen ham veri birimi.

Ornek:

- Episode transcript
- Script file
- Research paper

### Segment

SourceUnit'in islenebilir alt parcasi.

### ProcessingRun

Belirli bir pipeline ve schema ile SourceUnit uzerinde calisan tekil islem kaydi.

### Candidate

Extraction tarafinda uretilen, ama henuz canonical olmayan node veya relation adayi.

### Canonical Graph

Urunun gercek source of truth graph katmani.

### GraphDelta

Bir run'in graph uzerinde yarattigi degisiklik paketi.

### Schema

Node tipleri, relation tipleri, property alanlari, validation kurallari ve extraction hint'lerini kapsayan veri modeli.

### DomainTemplate

Belirli bir domain icin hazir schema ve pipeline paketi.

## Story Domain Terms

### Episode

Story template'te bir SourceUnit turu.

### Scene

Story template'te bir Segment veya Segment group'u.

### Character

Story graph'ta sahsiyet veya fail varlik.

### Event

Hikaye icinde graph'ta izlenen anlamli olay.

### RelationshipChange

Iki varlik arasindaki durum degisimi.

---
## FILE: docs/templates/story-template-v1.md
# Story Template v1

Bu belge, ilk domain template olan `Story / Series / Film` icin minimum baslangic setini tanimlar.

## Hedef

Ilk template fazla genis olmamali. Generic engine'i zorlamadan ilk ucgeni kurmali:

- Structure
- Character
- Event

## Minimum Node Types

### Series

Koken eser veya ana universum.

### Season

Dizi odakli ise kullanilir. Film projesinde opsiyoneldir.

### Episode

Story template'te bir SourceUnit turu.

### Scene

Episode altindaki anlamli anlatim birimi.

### Character

Merkezi varlik tipi.

### Event

Hikaye icindeki izlenebilir olay.

### Location

Mekan bilgisi.

### Organization

Aile, ekip, kurum, faction gibi grup yapilari.

## Minimum Relation Types

### HAS_SEASON

`Series -> Season`

### HAS_EPISODE

`Season -> Episode`

### HAS_SCENE

`Episode -> Scene`

### APPEARS_IN

`Character -> Episode/Scene`

### OCCURS_IN

`Event -> Episode/Scene`

### INVOLVED_IN

`Character -> Event`

### PART_OF

`Character -> Organization`

### RELATED_TO

`Character -> Character`

Not:

`RELATED_TO` ilk fazda generic relation olabilir. Daha sonra `ALLY_OF`, `ENEMY_OF`, `LOVES`, `BETRAYS` gibi tipler schema studio veya AI suggestion katmanindan gelebilir.

## Ilk Fazda Ozel Tutulmayan Alanlar

Asagidaki kavramlar ilk template'te sabitlenmez, schema studio'dan gelir:

- Secret
- Goal
- Conflict
- Debt
- Bloodline
- Alliance
- Betrayal

Bu karar, generic cekirdegi story domain'ine erken kilitlememek icin alinir.

---
## FILE: docs/roadmap/initial-roadmap.md
# Initial Roadmap

## Faz 0: Mimari Baseline

Hedef:

- Product definition'i sabitlemek
- Domain language'i yazmak
- ADR'leri acmak
- Generic cekirdek sinirlarini netlestirmek

Teslimatlar:

- README
- Docs index
- Architecture baseline
- ADR seti v1

## Faz 1: Core Metadata Backbone

Hedef:

- Project management
- Schema management
- Domain template binding
- Basic backend package layout

Teslimatlar:

- Project entity ve contracts
- SchemaVersion, NodeTypeDefinition, RelationTypeDefinition
- CRUD-ready backend iskeleti

## Faz 2: Ingestion and Candidate Pipeline

Hedef:

- SourceUnit lifecycle
- Segmentation
- ProcessingRun
- Candidate node/relation storage

Teslimatlar:

- Ingestion service contracts
- Candidate models
- Validation skeleton

## Faz 3: Canonical Graph Commit

Hedef:

- Neo4j adapter
- GraphDelta modeli
- Provenance-ready commit mantigi

Teslimatlar:

- Commit adapter interface'i
- Upsert strategy baseline
- Run report modeli

## Faz 4: Story Template v1

Hedef:

- Ilk domain pack'i sabitlemek
- Story-specific minimum ontology'yi tanimlamak

Teslimatlar:

- Story template docs
- Story schema seed tanimi
- Story pipeline defaults

## Sprint 1

- Repo iskeleti
- ADR seti
- Domain entities baseline
- Pydantic contracts baseline
- FastAPI app factory skeleton

## Sprint 2

- Schema CRUD
- SourceUnit ingestion
- Run creation
- Validation pipeline v1
- Neo4j commit adapter skeleton

---
## FILE: docs/adr/ADR-001-modular-monolith.md
# ADR-001: Start with a Modular Monolith

- Status: Accepted
- Date: 2026-03-14

## Context

Urunun bounded context'leri net, ancak erken donemde domain dili ve veri modeli hizla degisecek. Bu asamada mikroservis dagitimi operasyonel karmasa yaratir.

## Decision

Projeye moduler monolith olarak baslanacak.

Ayri bounded context'ler ayni repo ve ayni backend uygulamasi icinde moduller olarak kurgulanacak:

- project
- schema
- ingestion
- extraction
- validation
- graph_commit
- review

## Consequences

Olumlu:

- Daha hizli iterasyon
- Daha dusuk operasyonel maliyet
- Domain sinirlarini kod icinde once sabitleme imkani

Olumsuz:

- Moduller arasi sinirlar disiplinle korunmazsa gevseyebilir
- Uzun vadede yuksek trafik alan context'ler ayrismak isteyebilir

---
## FILE: docs/adr/ADR-002-postgres-and-neo4j.md
# ADR-002: Use Postgres for Metadata and Neo4j for the Canonical Graph

- Status: Accepted
- Date: 2026-03-14

## Context

Platform iki farkli veri ihtiyaci tasir:

- Yapilandirilmis metadata, schema config, run log ve review kayitlari
- Yuksek iliskisellik iceren canonical graph

## Decision

Iki store kullanilacak:

- `Postgres`: Project, schema, config, run metadata, review data, candidate metadata
- `Neo4j`: Canonical graph, provenance-ready graph structure, graph traversal odakli veri

## Consequences

Olumlu:

- Her veri turu uygun store'da tutulur
- Schema-as-data tasarimi daha kolay hale gelir
- Canonical graph tarafinda traversal ve future GraphRAG senaryolari desteklenir

Olumsuz:

- Cift store operasyonu gerekir
- Senkronizasyon ve transaction sinirlari net tasarlanmalidir

---
## FILE: docs/adr/ADR-003-schema-as-data.md
# ADR-003: Treat Schema as Data

- Status: Accepted
- Date: 2026-03-14

## Context

Urun tek bir domain'e kilitli olmayacak. Node tipleri, relation tipleri, property'ler, merge key'ler ve extraction hint'leri dashboard'dan yonetilebilir olmali.

## Decision

Schema kod icine sabitlenmeyecek. Ayri veri modeli olarak tutulacak.

Temel parcalar:

- SchemaVersion
- NodeTypeDefinition
- RelationTypeDefinition
- PropertyDefinition
- ValidationRule
- ExtractionHint

## Consequences

Olumlu:

- Generic cekirdek korunur
- Domain template mantigi desteklenir
- AI suggestion + manual override birlikte calisabilir

Olumsuz:

- Baslangicta daha fazla modelleme ister
- Schema migration ve versioning stratejisi zorunlu hale gelir

---
## FILE: docs/adr/ADR-004-optional-graphrag-adapter.md
# ADR-004: Keep GraphRAG as an Optional Adapter

- Status: Accepted
- Date: 2026-03-14

## Context

GraphRAG, retrieval ve bazi extraction senaryolari icin degerli olabilir; ancak cekirdek sistemin bagimli oldugu merkez teknoloji olmamali.

## Decision

GraphRAG cekirdege hard dependency olarak baglanmayacak. Gerekli oldugunda adapter veya plugin olarak kullanilacak.

## Consequences

Olumlu:

- Cekirdek sistem daha stabil ve degisebilir kalir
- Farkli retrieval veya extraction motorlari eklenebilir
- Experimental API'lere bagimlilik azalir

Olumsuz:

- Entegrasyon katmani biraz daha fazla kod ister
- Kisa vadede resmi paketin sundugu bazi hizli kisayollar dogrudan kullanilmaz

---
## FILE: docs/adr/ADR-005-candidate-validation-canonical.md
# ADR-005: Use a Candidate -> Validation -> Canonical Pipeline

- Status: Accepted
- Date: 2026-03-14

## Context

LLM destekli extraction ciktilari dogrudan canonical graph'a yazilirsa veri kalitesi hizla bozulur.

## Decision

Uretim hatti su sekilde kurulur:

1. Candidate extraction
2. Resolution and validation
3. Canonical graph commit

## Consequences

Olumlu:

- Daha guvenli graph write
- Audit edilebilir run gecmisi
- Human review icin dogal bir ara katman

Olumsuz:

- Ek veri modeli ve operasyonel adimlar gerekir
- Ilk implementasyon dogrudan write akisina gore daha uzun surer

---
## FILE: docs/research/deep-research-prompts.md
# Deep Research Prompts

Bu belge, guncel teknik konularda kullanilmak uzere reusable prompt'lari toplar.

## Kullanim Kurali

Asagidaki durumlarda yeni bir arastirma prompt'u acilmali:

- Neo4j veya GraphRAG tarafinda surume duyarli karar alinacaksa
- Production ve experimental ayrimi net degilse
- Performans, maliyet veya deployment karari guncel veriye bagliysa
- Resmi dokuman kontrolu olmadan riskli mimari karari alinacaksa

## Neo4j + GraphRAG Deep Research Prompt

```text
Biz generic, schema-driven, AI-assisted bir graph construction platformu tasarliyoruz.
Ilk domain template'imiz dizi/film/senaryo verisi olacak, ama cekirdek sistem domain-agnostic olacak.

Lutfen asagidaki konularda 2025-2026 itibariyla guncel, teknik, derin ve uygulanabilir bir arastirma yap.
Oncelik resmi Neo4j dokumantasyonu, resmi driver belgeleri, resmi GraphRAG package belgeleri, Neo4j blog/developer guides, GDS belgeleri, ardindan guvenilir teknik kaynaklar olsun.

Arastirma hedefi:
- Urunun generic graph production engine mimarisini en saglam sekilde kurmak
- Neo4j + Python + schema-driven extraction + validation + graph commit hattini dogru modellemek
- GraphRAG, vector search, graph traversal ve knowledge graph builder tarafinda guncel en iyi pratikleri ogrenmek
- Deneysel ozelliklerle production-grade ozellikleri ayirmak
- Baslangic MVP ile uzun vadeli platform mimarisi arasinda net kararlar cikarmak

Lutfen su basliklarda arastir:

1) Neo4j'nin guncel yetenekleri
2) Neo4j GraphRAG for Python guncel durumu
3) Knowledge graph construction best practices
4) Schema-as-data / ontology management
5) Clean Architecture ve DDD acisindan oneriler
6) Ingestion + extraction orchestration
7) Testing ve reliability
8) Ilk 90 gun icin teknik roadmap onerisi

Her baslik icin:
- net oneriler ver
- tradeoff'lari belirt
- production icin uygun olanlarla arastirma/prototip seviyesinde olanlari ayir
- mumkunse karar matrisi olustur
- resmi kaynaklari ve tarihlerini belirt
- ozellikle son degisiklikleri vurgula

Ayrica su sorulara ozellikle cevap ver:

- GraphRAG paketi cekirdek urunde zorunlu dependency mi olmali, yoksa opsiyonel adapter mi?
- Neo4j canonical store, Postgres metadata/config store ayrimi dogru mu?
- Generic engine + domain templates yaklasimi teknik olarak surdurulebilir mi?
- Story template icin minimum node/relation seti ne olmali?
- Candidate -> validation -> commit hatti icin en guvenli veri modeli ne?
- Schema drift ve schema evolution nasil ele alinmali?
- Ilk production-grade surumde hangi ozellikleri kesinlikle disarida birakmaliyiz?
- Neo4j uzerinde graph write tarafinda en guvenli merge/upsert stratejileri neler?
- Vector search + graph traversal hibrit retrieval ileride nasil tasarlanmali?

Son ciktiyi su formatta ver:
1. Executive summary
2. Mimari oneri
3. Tavsiye edilen teknoloji ve paketler
4. Production-safe kararlar
5. Experimental / dikkatli kullanilacak parcalar
6. MVP roadmap
7. Acik riskler ve karar bekleyen konular
8. Kaynakca
```

## Cevap Geri Geldiginde

Arastirma sonucu gelince su uc is yapilir:

1. `docs/architecture/` altindaki ilgili belge guncellenir.
2. Gerekirse yeni ADR acilir veya mevcut ADR revize edilir.
3. Kod kontratlari ve backlog etkisi not edilir.

---
## FILE: backend/README.md
# Backend

Backend, GiraffeGraph Core'un generic graph production engine cekirdegini tasir.

Bu klasor public site veya landing page backend'i degil, dashboard ve internal graph production workflow backend'idir.

## Hedef

Ilk asamada backend tarafinda sunlar kurulur:

- Clean Architecture sinirlari
- Domain entity baseline'i
- Pydantic contract'lari
- FastAPI app factory skeleton'i
- Neo4j ve Postgres adapter alanlari

## Package Layout

- `src/app/domain/`: Saf domain kavramlari
- `src/app/application/`: Use-case kontratlari ve port'lar
- `src/app/infrastructure/`: DB, LLM, queue ve config adapter alanlari
- `src/app/interfaces/`: API katmani
- `src/app/bootstrap/`: App assembly
- `tests/`: Unit, integration ve contract test klasorleri

## Su An Var Olan Temel Yetenekler

- Gercek Postgres metadata persistence'i
- Neo4j canonical graph write/read modeli
- Registry arkasinda `noop` ve `openai` provider'lari
- Alembic migration sistemi
- Processing job queue, auto-seeded metadata-backed pipeline definition'lari ve CLI worker komutu
- Project-level processing job queue read-model'i

## Hala Bilincli Olarak Eksik Olanlar

- Auth / tenant / permission
- Pipeline definition editor / richer orchestration governance

---
## FILE: frontend/README.md
# Frontend

Frontend tarafinda hedef, generic dashboard yapisini kurmak.

Bu klasor landing page veya marketing site icin degil, sadece urun ici dashboard icindir.

Ilk odak moduller:

- Projects
- Templates
- Schema Studio
- Ingestion
- Runs
- Review
- Graph Explorer

Bu klasor su anda yalnizca moduler yapinin yerini sabitler. Uygulama implementasyonu sonraki adimda eklenecek.
