# GiraffeGraph

CSE 491 senior design project: a human-in-the-loop knowledge graph generation engine, with hadith
isnad chains as the case study. Everything the team works on is in this repository.

## Layout

| Folder | What it holds |
|---|---|
| `giraffegraph-core/` | The engine (FastAPI backend, Postgres and Neo4j, Next.js review panel) and the evaluation scripts |
| `wiki/` | The project context: plan, decisions, measurements, literature, thesis and paper drafts. Written in Turkish; the thesis is in English |
| `data/` | Evaluation sets, the scripts that build them, and experiment outputs. `data/raw/` is downloaded, not tracked |

The landing page (giraffegraph.com) is a separate public repository, `GiraffeGraph/landing`.

## Getting started

```
git clone git@github.com:GiraffeGraph/giraffegraph.git
```

1. Read `wiki/README.md`, then `wiki/architecture/workspace-map.md`.
2. To run the engine, follow `giraffegraph-core/README.md`.
3. To rebuild the evaluation sets, follow `data/README.md`.

## Working rules

- Work on `main`; there are no long-lived branches.
- The repository is private. `data/` contains third-party hadith text and `wiki/thesis/` contains
  unpublished drafts; neither is copied into a public repository.
- Rules for coding agents are in `CLAUDE.md`, which imports `wiki/CLAUDE.md`.
