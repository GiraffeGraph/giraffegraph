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
