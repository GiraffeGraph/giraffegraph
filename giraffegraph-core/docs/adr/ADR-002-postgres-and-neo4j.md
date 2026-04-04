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
