# Witness survival under real commit histories

## Method

- Eight GitHub repositories, two per language, picked from 49 screened candidates by anchor-target count (rule, rejects, URLs, SHAs in `results.json`).
- t0 = last first-parent commit at least 24 months before HEAD (2026-10); horizons t0 + 1/3/6/12/24 months.
- Anchor = Markdown line at t0 naming an existing file (not Markdown, image or vendored); symbol = backticked identifier on that line found in the file.
- G0 path exists; G1 blob hash equal; G2 indentation-delimited block (80 lines at most) after the symbol's first occurrence equal; DOC = line still verbatim in its file.
- Deviations: bare file names count only when backticked alone, other tokens need a directory; identifiers need 3+ characters and pass a stop-list; trailing blank lines are dropped from blocks; a trial run on eight earlier candidates (zulip kept) showed outcomes before the selection rule was fixed.

## Pooled results

1,804 anchors, 367 doc files, 944 distinct targets; G2 on the 122 symbol anchors. Percent surviving; unweighted per-repository mean in parentheses.

| Months | G0 exists | G1 file | G2 symbol |
|---|---|---|---|
| 1 | 97.9 (96.8) | 54.2 (64.9) | 98.4 (92.0) |
| 3 | 96.8 (95.8) | 44.1 (54.3) | 96.7 (91.4) |
| 6 | 90.6 (92.8) | 25.6 (35.9) | 84.4 (77.7) |
| 12 | 87.6 (90.5) | 18.0 (24.3) | 77.9 (72.9) |
| 24 | 82.8 (86.1) | 10.4 (14.9) | 61.5 (54.9) |

G1 on the symbol anchors alone: 20.5 at 12 months, 15.6 at 24.

Witness changed × sentence edited, pooled counts:

| Witness, horizon | changed, edited | changed, verbatim | unchanged, edited | unchanged, verbatim | changed and verbatim, % of anchors | % of changed |
|---|---|---|---|---|---|---|
| G1, 12 | 338 | 1141 | 30 | 295 | 63.2 (57.3) | 77.1 |
| G1, 24 | 530 | 1087 | 35 | 152 | 60.3 (57.7) | 67.2 |
| G2, 12 | 6 | 21 | 8 | 87 | 17.2 (24.1) | 77.8 |
| G2, 24 | 21 | 26 | 16 | 59 | 21.3 (30.5) | 55.3 |

Tokens with a directory only (1,537 anchors, 84 symbol), 24 months: G0 84.8, G1 11.3, G2 61.9; changed and verbatim 61.5 (G1), 25.0 (G2).

## Per repository

| Repository | Anchors / symbol / docs | G0 24 | G1 12 | G1 24 | G2 24 | G1 changed and verbatim 24 |
|---|---|---|---|---|---|---|
| bevy (Rust) | 307 / 11 / 9 | 83.7 | 11.1 | 8.1 | 81.8 | 70.4 |
| wasmtime (Rust) | 91 / 7 / 41 | 83.5 | 37.4 | 30.8 | 57.1 | 40.7 |
| zulip (Python) | 561 / 46 / 91 | 92.9 | 18.9 | 13.2 | 41.3 | 61.7 |
| transformers (Python) | 510 / 20 / 129 | 69.8 | 9.8 | 0.2 | 70.0 | 58.8 |
| argo-cd (Go) | 137 / 6 / 41 | 67.2 | 15.3 | 9.5 | 66.7 | 47.4 |
| tektoncd/pipeline (Go) | 119 / 27 / 28 | 96.6 | 50.4 | 29.4 | 88.9 | 64.7 |
| desktop (TypeScript) | 38 / 2 / 14 | 100.0 | 34.2 | 18.4 | 0.0 | 81.6 |
| playwright (TypeScript) | 41 / 3 / 14 | 95.1 | 17.1 | 9.8 | 33.3 | 36.6 |

## Sanity checks

- 20 of 20 sampled anchors are genuine references to the repository file; one is borderline (a listing of imported WPT test assets) and six sit in translated transformers docs.
- Horizon 0: G0, G1, G2 and DOC are 100% unchanged, and the horizon-0 commit equals t0 everywhere.

## Threats to validity

- **Path-mention heuristics.** Directory, crate and module mentions are skipped (rust-analyzer's architecture doc yields 6 anchors). Duplicated or generated docs weigh heavily: 244 of 510 transformers anchors are translations, 292 of 307 bevy anchors come from one examples table, 48 of 137 argo-cd anchors from a bot-written Snyk index.
- **Renames count as deletions** for G0, G1 and G2; a moved doc file counts as edited.
- **Definition-block rule.** The first occurrence is often an import, comment or YAML key, and generic identifiers (`Task`, `status`) match. With 122 symbol anchors, two or three in two repositories, per-repository G2 is anecdotal.
- **Selection.** Path-dense docs of large active projects; no random sample; counts dominated by three repositories.
- **Verbatim-line test.** A reflow or typo fix counts as edited; an edit to a neighbouring line does not. "Changed and verbatim" is an upper bound on silent staleness: most file changes leave the sentence true.
