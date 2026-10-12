# Tests

Bu klasor, asagidaki seviyelerde test tasarimi icin ayrildi:

- `unit/`
- `integration/`
- `contract/`

`unit/` ve `integration/` test dosyalari icerir; `contract/` bostur. `uv run pytest -q` 285 test toplar:
`memory` backend ile 273'u gecer, `real_db` isaretli 12'si atlanir.

`real_db` testleri (`integration/test_realdb_*.py`) gercek Postgres ve Neo4j'e karsi kosar. Calismalari
icin `GG_TEST_POSTGRES_DSN`, `GG_TEST_NEO4J_URI` ve `GG_TEST_NEO4J_PASSWORD` (istege bagli
`GG_TEST_NEO4J_USERNAME`) tanimlanir; fixture'lar ve ornek degerler `conftest.py` icindedir.
