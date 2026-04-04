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
