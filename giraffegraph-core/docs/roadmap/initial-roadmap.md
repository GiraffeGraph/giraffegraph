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
