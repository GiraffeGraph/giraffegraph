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
