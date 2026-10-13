---
id: 0008
title: Ship a ledger and a linter, not a compiler
date: 2026-08-03
supersedes: [0001]
---

We started (0001) intending a typed compiler: frontmatter on every doc, a build
step that regenerates the derivable parts and keeps them synced to the code, a CLI
that hands an agent a pre-assembled context bundle.

Rejected after tracing the prior art. The compiler's core job — keep the
*derivable* half of a doc in sync — is a forty-year graveyard (literate
programming, MDA round-tripping, Swimm, GraphRAG), and three independent results
say it's not just hard but wrong: lens theory (prose isn't a view of code, so it
has no inverse), determinism (early cutoff needs `f(x)==f(x)`, which LLM output
never satisfies), and Metacrap-automated (an LLM asserting metadata invents a new,
undetectable failure mode). The derivable half should not be stored at all — the
agent can re-derive it by reading the code.

What survives is the *non-derivable* half: decisions. That needs no compiler —
it needs an append-only ledger (write-once, forward-links, derived back-links)
plus a linter that flags broken anchors without ever claiming the prose is true.

Constraint that forced the call: nothing automatable can verify a semantic claim
(detection tops out near a coin flip), so the honest system is one that stores
only what a human decided and refuses to fabricate the rest.

