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
