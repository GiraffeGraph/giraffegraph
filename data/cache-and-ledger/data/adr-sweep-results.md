# ADR write-once sweep — first-hand measurement

**Date:** 2026-08-03
**Tool:** `verify-adr-writeonce.py` (unmodified — no bug found; the write-once
column in an earlier intermediate pass was miscounted by a *shell* one-liner that
grabbed the "1" out of the literal text "exactly **1** commit". The Python script
itself is correct. Final numbers below are parsed directly from the script's own
labelled output, not from that shell one-liner.)

**What the script measures, per repo:** ADR files (globs `NNNN-*.md`, `adr-*.md`,
`*-adr-*.md`, `ADR-*.md`; drops `index.md`/`readme.md`/`*template*`); write-once =
files touched by exactly one commit via `git log --follow`; median commits/ADR;
count carrying a `status`/`Status`/`## Status` field; forward supersede refs
(`supersede(s|d)`/`replaces`) vs back supersede refs (`superseded by`/`superseded-by`).
Per file the fwd/back test is exclusive (a "superseded by" file counts as back, not fwd).

**Population:** 67 repositories, 765 ADR files. Clones were full-history
(`git clone --filter=blob:none`, blobs-on-demand, commit history intact).
`adr/madr` and `arachne-framework/architecture` excluded per instruction.

## Headline result

| metric | value |
|---|---|
| repos measured | 67 |
| total ADRs | 765 |
| **pooled write-once (ADR-weighted)** | **356 / 765 = 46.5%** |
| **per-repo mean write-once** | **56.6%** |
| pooled carry a status field | 523 / 765 = 68.4% |
| per-repo mean status field | 73.5% |
| median of per-repo median commits/ADR | 1 |
| **forward supersede refs (total)** | **50** |
| **back supersede refs (total)** | **22** |
| back as fraction of forward | 44% |
| forward as % of all ADRs | 6.5% |
| back as % of all ADRs | 2.9% |
| repos with >=1 forward ref | 22 / 67 |
| repos with >=1 back ref | 16 / 67 |
| repos with any supersede ref | 26 / 67 |

## The load-bearing result: forward vs back supersession

**50 forward references vs 22 back references — a ratio of ~2.3 : 1, not the
order-of-magnitude gap the "3.7%" framing implies.**

The prior claim ("forward reference written far more often than the back reference
is maintained", back-link ~3.7%) is only **weakly** supported. Back-references as a
fraction of all ADRs (2.9%) roughly match the claimed 3.7%, but forward references
are only 2.3x as common, not "far more often." Back-references are genuinely
maintained in 16 of 67 repos.

I spot-checked all `superseded by` matches: they are overwhelmingly **real** status
lines ("Superseded by [ADR-0013](0013-...)") inside genuine ADR files, e.g.
`change-metrics/monocle` 0009, `cljdoc` 0014, `home-assistant/architecture` 0002,
`ledgersmb` 0011, `weaveworks/weave-gitops` 0005, four in `TolikPylypchuk/Cineaste`.
CHANGELOG/README/index/template hits exist in the tree but are excluded from the
count by the script's glob + drop rules, so they do not inflate the 22.

## Per-repo table (sorted by ADR count)

| repo | SHA | ADRs | write-once | wo% | med commits | status | fwd | back |
|---|---|---|---|---|---|---|---|---|
| state-alchemists/zrb | b52379fb88 | 95 | 84 | 88% | 1 | 1 | 8 | 2 |
| BrighterCommand/Brighter | 0950f2864f | 92 | 5 | 5% | 3 | 92 | 8 | 0 |
| ledgersmb/LedgerSMB | 841287bc0f | 37 | 0 | 0% | 3 | 37 | 0 | 1 |
| athensresearch/athens | b463a97a0d | 26 | 13 | 50% | 2 | 24 | 1 | 0 |
| cljdoc/cljdoc | 6920643da6 | 26 | 11 | 42% | 2 | 20 | 1 | 1 |
| joshrotenberg/adrs | 3aac07df1e | 24 | 14 | 58% | 1 | 24 | 2 | 1 |
| softwaremill/tapir | 061e0b90e5 | 24 | 5 | 21% | 2 | 0 | 0 | 0 |
| BrighterCommand/Darker | 095c8bd8af | 22 | 14 | 64% | 1 | 22 | 7 | 1 |
| home-assistant/architecture | 0c4f7dbf21 | 22 | 8 | 36% | 2 | 22 | 1 | 1 |
| s3gw-tech/s3gw | 7b3760c6ad | 20 | 4 | 20% | 2 | 0 | 3 | 1 |
| elsa-workflows/elsa-core | 5b0c2d7359 | 16 | 9 | 56% | 1 | 9 | 0 | 0 |
| nicoespeon/abracadabra | e61f08cdc4 | 16 | 9 | 56% | 1 | 16 | 0 | 0 |
| phodal/coca | 5866a268e4 | 16 | 2 | 12% | 3 | 16 | 0 | 0 |
| softwaremill/ox | 11f3acd4eb | 16 | 0 | 0% | 3 | 0 | 0 | 0 |
| TolikPylypchuk/Cineaste | 129691845d | 16 | 1 | 6% | 4 | 1 | 0 | 4 |
| weaveworks/weave-gitops | 936e848c4e | 16 | 10 | 62% | 1 | 16 | 1 | 1 |
| adoble/adr-j | 6666e7a7e9 | 14 | 6 | 43% | 2 | 11 | 3 | 2 |
| hackforla/CivicTechJobs | c88e704067 | 14 | 14 | 100% | 1 | 0 | 2 | 0 |
| change-metrics/monocle | ae8ea82eac | 13 | 5 | 38% | 2 | 12 | 0 | 1 |
| wireapp/wire-android | 6e39e18bdb | 13 | 9 | 69% | 1 | 13 | 0 | 0 |
| mrwilson/adr-viewer | a25f1c71e0 | 11 | 5 | 45% | 2 | 10 | 2 | 2 |
| bob-cd/bob | b559d9dbd5 | 10 | 7 | 70% | 1 | 10 | 0 | 0 |
| openrewrite/rewrite | 8175cb3b9c | 10 | 7 | 70% | 1 | 10 | 0 | 1 |
| skupperproject/skupper | 8fcff848d2 | 10 | 6 | 60% | 1 | 10 | 1 | 1 |
| asyncapi/studio | e679cc17ff | 9 | 9 | 100% | 1 | 9 | 1 | 0 |
| aws/aws-sdk-pandas | c2d0286193 | 9 | 9 | 100% | 1 | 9 | 0 | 0 |
| npryce/adr-tools | b3279baf9b | 9 | 0 | 0% | 3 | 9 | 0 | 0 |
| openfun/marsha | 0ec56ab7a3 | 9 | 7 | 78% | 1 | 4 | 0 | 0 |
| wireapp/kalium | fa069a56ce | 9 | 5 | 56% | 1 | 9 | 1 | 0 |
| dalenguyen/pdfun | 65a9563361 | 8 | 3 | 38% | 2 | 8 | 0 | 0 |
| Kl0ven/mkdocs-material-adr | cdd609beae | 8 | 0 | 0% | 4 | 8 | 2 | 0 |
| mlibrary/lauth | 09af37e45c | 8 | 8 | 100% | 1 | 7 | 0 | 0 |
| clj-kondo/clj-kondo | 4022ff03b1 | 7 | 3 | 43% | 2 | 7 | 1 | 0 |
| mahanhz/clean-architecture-example | ba4ef58abe | 7 | 0 | 0% | 3 | 7 | 1 | 1 |
| rubyforgood/casa | eb742e8c59 | 7 | 2 | 29% | 2 | 4 | 0 | 0 |
| superluminar-io/super-eks | a79464f41e | 7 | 6 | 86% | 1 | 7 | 0 | 0 |
| test-kitchen/test-kitchen | 42fb9a4d60 | 7 | 7 | 100% | 1 | 6 | 0 | 0 |
| azavea/franklin | 73db7f9b53 | 6 | 5 | 83% | 1 | 6 | 0 | 0 |
| flyingrobots/git-mind | 18b98b632b | 6 | 4 | 67% | 1 | 1 | 1 | 0 |
| pangeo-forge/roadmap | b38fd4d67a | 5 | 0 | 0% | 3 | 5 | 0 | 0 |
| tfutils/tfenv | de6ce2e809 | 5 | 1 | 20% | 2 | 0 | 1 | 0 |
| babashka/babashka | 6bead29b4d | 4 | 2 | 50% | 5 | 1 | 1 | 1 |
| catchpoint/WebPageTest | 4e157836cd | 4 | 0 | 0% | 5 | 0 | 0 | 0 |
| inmanta/inmanta-core | 3550e9a869 | 4 | 0 | 0% | 2 | 4 | 0 | 0 |
| omissis/go-jsonschema | e6bc0fe114 | 4 | 0 | 0% | 2 | 4 | 0 | 0 |
| commercetools/commercetools-sync-java | a0fbe1f4e6 | 3 | 3 | 100% | 1 | 3 | 0 | 0 |
| DFE-Digital/dfe-reference-data | b2477d4c1c | 3 | 2 | 67% | 1 | 0 | 0 | 0 |
| fork-handles/forkhandles | 39c91e2c2f | 3 | 3 | 100% | 1 | 3 | 0 | 0 |
| OpenTOSCA/container | 73f9331b7f | 3 | 3 | 100% | 1 | 2 | 0 | 0 |
| pmckeown/dependency-track-maven-plugin | 9404b2ffe6 | 3 | 3 | 100% | 1 | 3 | 0 | 0 |
| redbadger/pride-london-app | 7e7d6db956 | 3 | 3 | 100% | 1 | 3 | 0 | 0 |
| wemake-services/kira | bd86fd89ee | 3 | 3 | 100% | 1 | 0 | 0 | 0 |
| zalando/riptide | f2e276a4d8 | 3 | 3 | 100% | 1 | 3 | 0 | 0 |
| dora-metrics/pelorus | f0010dfa8d | 2 | 2 | 100% | 1 | 2 | 0 | 0 |
| droher/boxball | e5ff087a75 | 2 | 0 | 0% | 3 | 0 | 0 | 0 |
| palantir/docker-compose-rule | 41e0e0cb6d | 2 | 2 | 100% | 1 | 2 | 0 | 0 |
| safedep/vet | 2ae1aafb98 | 2 | 2 | 100% | 1 | 1 | 0 | 0 |
| stac-utils/pystac-client | 0a9a4a95e7 | 2 | 0 | 0% | 2 | 2 | 0 | 0 |
| yetibot/core | ab1011a683 | 2 | 2 | 100% | 1 | 2 | 0 | 0 |
| antonvolkoff/kosmos | 27ac38d330 | 1 | 1 | 100% | 1 | 1 | 1 | 0 |
| digitalocean/doctl | b98e74427b | 1 | 1 | 100% | 1 | 1 | 0 | 0 |
| lensesio/lenses-jdbc | 4ea41f6687 | 1 | 1 | 100% | 1 | 1 | 0 | 0 |
| openedx/paragon | 49896f4a07 | 1 | 0 | 0% | 2 | 0 | 0 | 0 |
| phpactor/phpactor | f28b5db32f | 1 | 1 | 100% | 1 | 0 | 0 | 0 |
| rax-maas/blueflood | 6557fd4fce | 1 | 1 | 100% | 1 | 1 | 0 | 0 |
| timabell/gitopolis | de814adc18 | 1 | 0 | 0% | 2 | 1 | 0 | 0 |
| woowabros/nestjs-library-crud | b0f6621d21 | 1 | 1 | 100% | 1 | 1 | 0 | 0 |

Two repos not listed produced zero ADR files under the script's globs and were
dropped from the population: `openedx/license-manager` (SHA f44dfe9412) and
`Vizzuality/marxan-cloud` (SHA ed57372117). One clone failed as a redirect
duplicate (`forkhandles/forkhandles` -> the canonical `fork-handles/forkhandles`,
which is included).

## Distribution note (why the two weightings diverge)

Pooled (46.5%) is far below per-repo mean (56.6%) because two large repos with
opposite behavior dominate the ADR pool: `BrighterCommand/Brighter` (92 ADRs, only
5% write-once — its ADRs get a status-field edit) and `ledgersmb/LedgerSMB` (37 ADRs,
0% write-once) pull the pool down, while `state-alchemists/zrb` (95 ADRs, 88%
write-once) pulls it up. Together those three are ~29% of all ADRs. The per-repo
mean, where a 1-ADR repo counts as much as a 95-ADR repo, sits higher because the
long tail of tiny repos is almost all 100% write-once.

## Threats to validity

- **Sampling bias.** Repos were found via GitHub code search for ADR filename
  patterns (`0001-record-architecture-decisions.md`, and `filename:0001/0002`
  under `docs/decisions`, `doc/adr`, `docs/adr`). This finds repos that *adopted a
  known ADR convention* — it cannot find teams who abandoned ADRs after one file,
  nor decisions recorded outside these paths. The population skews toward projects
  that at minimum set up an ADR directory.
- **Selection toward variety, not randomness.** I hand-picked ~70 from ~180
  candidates to mix flagships (aws, home-assistant, digitalocean) with small/dead
  ones (kosmos, gitopolis, boxball, pdfun). This is a convenience sample, not a
  uniform draw from all GitHub ADR repos.
- **What the script cannot see.** (1) A rebase/squash collapses history, so a
  genuinely-edited ADR can look write-once — this *inflates* write-once. (2) A
  file rename that `--follow` fails to trace splits history and can *deflate*
  write-once. (3) A trivial one-line status edit (Accepted -> Superseded) counts
  as a second commit, so a "maintained back-reference" and a typo fix are
  indistinguishable by commit count. (4) Supersession detection is textual: a repo
  that tracks supersession only in an `index.md` table or in git, not in the ADR
  body, registers zero refs. (5) The MADR template's status enum literally contains
  "superseded by"; the script drops `*template*` files but a repo that copied the
  enum boilerplate into a real ADR without editing it would be a false back-ref —
  spot-checking showed the 22 back-refs are real, but this risk biases back-count
  *upward*, which only weakens the "back is rare" claim further.
- **Rate limits / truncation.** No rate-limit truncation hit — one authenticated
  `gh api search/code` pass (5 queries) plus 70 clones completed cleanly. The
  candidate pool (~180) was larger than what I cloned; a bigger sweep is possible
  but the marginal repos are mostly tiny (1-3 ADRs, near-certain 100% write-once),
  which would push per-repo write-once up, not down.

## Verdict on the "~52%" claim

**The population write-once rate FAILS TO REFUTE the ~52% claim: it is consistent
with it — the pooled (ADR-weighted) rate is 46.5% and the per-repo-mean rate is
56.6%, and 52% sits between them.** The claim's write-once magnitude is credible.
Its *supersession* sub-claim is the weaker part: forward references outnumber
back references only ~2.3 : 1 (50 vs 22), not the near-total asymmetry the "3.7%"
figure suggests, and back-references are actively maintained in 16 of 67 repos.
