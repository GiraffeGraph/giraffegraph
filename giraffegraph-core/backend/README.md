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
