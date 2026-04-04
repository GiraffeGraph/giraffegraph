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
