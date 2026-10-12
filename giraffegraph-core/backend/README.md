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
- Registry arkasinda `noop`, `rule_based_isnad`, `openai` ve `anthropic` provider'lari; son ikisi
  yalniz API anahtari tanimliysa kaydedilir
- Grounding kontrolu: cikarim cagrisindan gelen adayda kanit alintisi segment metninde, metin tipli
  merge key degeri de alintida aranir; gecmeyen aday review'a duser
- Review kararlari `review_decisions` tablosunda `reviewer_id`, karar zamani ve sure ile saklanir;
  kayitlar silinmez
- Alembic migration sistemi
- Processing job queue, auto-seeded metadata-backed pipeline definition'lari ve CLI worker komutu
- Project-level processing job queue read-model'i

## Hala Bilincli Olarak Eksik Olanlar

- Auth / tenant / permission; reviewer adi istekle gelir ve dogrulanmaz
- Pipeline definition editor / richer orchestration governance
- Commit edilmis run icin undo / rollback

## Gelistirme

Testler `memory` backend ile calisir; Postgres ve Neo4j gerekmez. `real_db` isaretli 12 test,
`GG_TEST_POSTGRES_DSN`, `GG_TEST_NEO4J_URI` ve `GG_TEST_NEO4J_PASSWORD` tanimli degilse atlanir
(ayrinti: [`tests/README.md`](tests/README.md)).

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

Docker Compose ile tum sistemi calistirma adimlari kok [`README.md`](../README.md) dosyasindadir.
