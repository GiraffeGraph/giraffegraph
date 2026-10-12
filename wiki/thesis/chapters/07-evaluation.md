# 7 Evaluation

This chapter reports what we measured, on which data, against which reference and with which matching rule. Measured numbers come from files under `giraffegraph-core/evaluation/results/` produced by the scripts described in Chapter 6; statistics of the data sets come from the data manifest [@internal-data-manifest]. All runs were made on 12 October 2026 on the in-memory backend of the engine. The PostgreSQL and Neo4j backend was verified separately by tests (Section 6.7) and was not used for these runs.

## 7.1 Questions

The evaluation answers five questions.

1. How well does each extraction condition recover the narrator mentions of a hadith?
2. What do the validation checks catch when they are placed between the model and the graph, and what do they cost in lost correct output?
3. Is the model's self-reported confidence a usable signal for deciding what a person should review?
4. How much review work and how much money does each condition generate?
5. How far does a written name identify a narrator?

Questions that we could not answer are listed in Section 7.11.

## 7.2 Data and reference labels

We use two sets of hadiths (Table 7.1). Neither has a human gold standard with two independent annotators, and no source describes its labels as one [@internal-data-manifest].

**Table 7.1** Evaluation sets.

| Set | Hadiths | Reference mentions | Source of text and labels | Role |
|---|---|---|---|---|
| Pilot | 50, five collections, no Bukhari | 327 | Sanadset 650K [@mghari2022sanadset]; labels produced with regular expressions | Development set. The rule-based segmenter was tuned on it |
| Six books | 300, 50 from each of the six canonical collections | 1,778 | Ifta Sunnah data family [@oumer2025relation; @internal-data-manifest]; labels are the markup of the Ifta platform as restructured by a third party | Test set. Drawn with a fixed seed after removing every record whose text matches a pilot hadith |

The six-book set was sampled from records between 100 and 3,000 characters with at least two labelled narrators. After normalisation every reference mention occurs in its hadith text, and in all 300 hadiths the mentions appear in text order. A hadith has between 2 and 11 mentions (median 6), and 74 of the 300 contain more than one chain.

The platform labels have known inconsistencies. Narrators inside a compiler's comment or a supporting chain are sometimes labelled and sometimes not, so a system that extracts them is counted wrong in some hadiths. We did not correct the labels.

**How good are the regular-expression labels?** For 253 of the 300 hadiths a matching record exists in Sanadset (text similarity of at least 0.9; 118 are identical after normalisation). Scoring the Sanadset labels against the Ifta labels gives precision 0.939, recall 0.979 and F1 0.959 (95% interval 0.943 to 0.972) under loose matching, and F1 0.931 under strict matching. The two label sets agree closely on these hadiths. This is agreement between two label sets, not the accuracy of either, and the 253 are the hadiths whose text matched in both corpora, not a random subset.

## 7.3 Protocol

The unit of analysis is the hadith. For each hadith the system's narrator mentions are aligned with the reference mentions by maximum-weight bipartite matching, and matched pairs count as true positives. We report two matching rules, fixed before the runs:

- **Strict:** the normalised strings are equal. Normalisation removes diacritics and punctuation and unifies letter variants.
- **Loose:** the strings are equal, or one contains the other, or their token F1 is at least 0.60.

Precision, recall and F1 are micro-averaged over hadiths. Intervals are 95% percentile bootstrap intervals from 2,000 resamples of hadiths. Differences between two conditions use the same resamples for both. A hadith for which a system returns nothing counts as zero mentions and is never dropped.

Throughout this chapter a "wrong" mention is a proposed mention that is not matched to a reference mention under the loose rule, and a "correct" mention is one that is. Both are statements about agreement with the labels' surface form. Section 7.6 shows what the unmatched mentions consist of.

Strict matching is sensitive to where a mention ends. The loose rule is the one we use for comparisons, and we give strict F1 beside it because the gap between the two is itself informative [@muther2020tracing].

## 7.4 Conditions

All conditions run through the same engine: ingestion, segmentation, a provider call, validation, and commit. No review decision is made in any run, so the results show the automatic part of the pipeline only.

**Table 7.2** Extraction conditions.

| Condition | Segmentation | Provider | Schema hints |
|---|---|---|---|
| Rule | Chain span found by the rule-based segmenter, split at the marker ح | `rule_based_isnad`, no model | not used |
| LLM, schema only | Whole hadith, one call | Claude Haiku 5.5 | Type names and JSON contract only; type and property descriptions removed |
| LLM, isnad-aware | Whole hadith, one call | Claude Haiku 5.5 | Descriptions and template hints: copy names verbatim, exclude transmission verbs, the Prophet is not a narrator |
| LLM, isnad-aware, chain span | Chain span from the segmenter, one call per segment | Claude Haiku 5.5 | Same descriptions and hints |

The model runs with effort `low` and structured output. Responses are stored in a content-addressed cache, so each run can be reproduced without new calls.

## 7.5 Extraction results

**Table 7.3** Narrator mention extraction on the six-book test set (300 hadiths, 1,778 reference mentions, Ifta labels). P, R and F1 use loose matching; the interval is for loose F1.

| Condition | P | R | F1 [95% interval] | Strict F1 | Exact chains | TP / FP / FN |
|---|---|---|---|---|---|---|
| Rule | 0.968 | 0.881 | 0.923 [0.910, 0.935] | 0.633 | 0.490 | 1,567 / 51 / 211 |
| LLM, schema only | 0.914 | 0.868 | 0.890 [0.865, 0.914] | 0.826 | 0.567 | 1,543 / 145 / 235 |
| LLM, isnad-aware | 0.997 | 0.919 | 0.956 [0.946, 0.966] | 0.904 | 0.690 | 1,634 / 5 / 144 |
| LLM, isnad-aware, chain span | 0.998 | 0.903 | 0.948 [0.936, 0.959] | 0.897 | 0.650 | 1,605 / 3 / 173 |

![Figure 7.1 Loose precision, recall and F1 by condition on the six-book test set. Error bars on F1 are 95% bootstrap intervals.](figures/fig-7-1-conditions.png)

"Exact chains" is the share of hadiths in which every mention is matched, in order, with nothing extra, under loose matching.

**Under loose matching a schema alone does not make the model better than rules.** The schema-only model is below the rule-based parser by 0.032 F1 (interval 0.006 to 0.060) and by 0.054 precision (0.026 to 0.083). Recall does not differ (0.013, interval −0.018 to 0.044). Under strict matching the order is reversed: strict F1 is 0.826 for the schema-only model and 0.633 for the parser, and the model also gets more whole chains right (0.567 against 0.490). The parser finds the right names, but its spans often run past the end of a name; the model returns clean names and adds or alters some.

**Descriptions and hints account for most of the gain.** Giving the same model the type and property descriptions and the isnad hints raises precision by 0.083 (0.059 to 0.108), recall by 0.051 (0.024 to 0.078) and F1 by 0.066 (0.041 to 0.091). Unmatched proposals fall from 145 to 5. With hints the model is above the rule-based parser by 0.034 F1 (0.021 to 0.047) and well above it under strict matching. We did not run a condition without a schema, so this is the effect of the instructions given a schema, not a comparison of instructions with a schema.

**Restricting the model to the chain span did not help.** In the fourth condition the model sees only the chain span that the segmenter found. F1 is 0.948 against 0.956 for the whole hadith; the difference of 0.008 has an interval of −0.002 to 0.019. The segmenter starts a new segment only at the chain-switch marker, so only 10 of the 300 hadiths were split into two calls. The condition therefore tests the restriction of the input far more than it tests one call per chain, and the question whether per-chain calls help on long hadiths with several chains remains open. No call was truncated in either condition. The design analysis of 30 September had recommended per-chain calls after seeing truncated responses with a different model; with Claude Haiku 5.5 and hadiths of this length we do not observe truncation. In the chain-span condition one of 310 calls failed because the engine rejected a relation that referred to an unknown node.

**Table 7.4** Loose recall by structure of the hadith (six-book set).

| Condition | 1 chain (226) | 2+ chains (74) | 2–4 mentions (22) | 5–6 mentions (203) | 7–11 mentions (75) |
|---|---|---|---|---|---|
| Rule | 0.924 | 0.778 | 0.843 | 0.923 | 0.806 |
| LLM, schema only | 0.886 | 0.824 | 0.928 | 0.876 | 0.844 |
| LLM, isnad-aware | 0.940 | 0.868 | 0.976 | 0.948 | 0.854 |
| LLM, isnad-aware, chain span | 0.915 | 0.874 | 0.964 | 0.930 | 0.841 |

All conditions lose recall on hadiths with parallel chains and on long hadiths. The rule-based parser loses the most on parallel chains (0.924 to 0.778). Per collection, loose F1 for the isnad-aware model ranges from 0.936 (Bukhari) to 0.980 (Nasa'i), and for the rule-based parser from 0.862 (Abu Dawud) to 0.963 (Nasa'i).

On the pilot set, scored against the Sanadset labels, the order of the conditions is the same: rule 0.892, schema only 0.828, isnad-aware 0.945, chain span 0.919 (loose F1). The pilot numbers are optimistic for the rule-based parser, which was tuned on those 50 hadiths.

## 7.6 What the checks catch

The checks matter in the condition where the model departs from the text: schema only. Table 7.5 crosses whether a proposed mention is matched to the reference with whether a check flagged it.

**Table 7.5** The value-in-quotation check on the schema-only condition (six-book set, 1,688 proposed mentions, 145 of them not matched to the reference).

| | Not matched | Matched |
|---|---|---|
| Flagged by the check | 122 | 33 |
| Not flagged | 23 | 1,510 |

![Figure 7.2 Proposed mentions of the schema-only condition by match with the reference and by whether the value-in-quotation check flagged them.](figures/fig-7-2-gate.png)

The check flags 155 mentions (9.2% of proposals) in 70 hadiths. Of the flagged mentions 79% are unmatched, and they are 84% of all unmatched mentions. No other node-level check fired: every quotation the model gave was found in its source segment under the comparison the checks use.

What the check detects is that the model wrote a name that is not in the text it quoted. Table 7.6 classifies the 155 flagged names with fixed rules (`evaluation/classify_value_flags.py`).

**Table 7.6** Flagged names of the schema-only condition by kind of change.

| Kind of change | Example (quotation, name) | Flagged | Not matched | Matched |
|---|---|---|---|---|
| Transliterated into Latin script | `حَدَّثَنَا الْأَعْمَشُ`, "al-A'mash" | 79 | 79 | 0 |
| Grammatical case of the name changed | `عَنْ أَبِي بِشْرٍ` (genitive), `أَبُو بِشْرٍ` (nominative) | 34 | 21 | 13 |
| Kinship reference replaced by a name | `عَنْ أَبِيهِ` ("from his father"), `عُرْوَةَ` | 25 | 18 | 7 |
| Other, name found elsewhere in the text | name longer than the quotation | 7 | 3 | 4 |
| Other, name not found in the text | `حَدَّثَنَا يَحْيَى ، هُوَ ابْنُ سَعِيدٍ`, `يحيى بن سعيد` | 10 | 1 | 9 |
| All | | 155 | 122 | 33 |

Three observations qualify the headline numbers.

First, most of the "wrong" mentions are not invented narrators. Seventy-nine are the right narrator written in Latin script, all from 14 hadiths in which the model switched script. Twenty-one are the right narrator in a different grammatical case. Whether a case change counts as matched depends on the length of the name: on a two-word name the token overlap falls below the threshold of the loose rule, on a longer name it does not. The check and the scorer both compare surface forms, so part of their agreement is by construction.

Second, the kinship cases are inferences, not inventions. In the example the text reads "Hisham ibn Urwa, from his father", and the model wrote "Urwa". The name is in the text; it is not in the quotation. Of the 25 kinship names, 15 occur in the hadith text. We found one flagged name that needs knowledge from outside the text: the quotation is `قَالَ عُثْمَانُ` and the name is `عثمان بن عفان`, where the second part occurs nowhere in the hadith.

Third, the classes of Section 2.3 separate as follows. Of the 145 unmatched mentions, 102 have a name that does not occur in the normalised hadith text, and the check flags all 102. Forty-three have a name that does occur in the text; the check flags 20 of them, those whose name is outside the quotation. Ten unmatched mentions name the Prophet as a narrator, a category error; the check flags two of them, both in Latin script, and misses eight, because the name is copied correctly from the text. No implemented check covers this class.

Because a flagged candidate is not accepted until a person decides, the candidates accepted without review in this condition have precision 0.985 instead of 0.914, at recall 0.849 instead of 0.868 (Table 7.7). The graph itself receives less: a run with an open review item is not committed, and 110 of the 300 hadiths have one. Counting those hadiths as empty, the committed output has precision 0.983 and recall 0.582 until a reviewer acts.

**Table 7.7** Output of the schema-only condition at three points (six-book set, loose matching).

| Output | P | R | F1 | TP / FP / FN |
|---|---|---|---|---|
| Everything the model proposed | 0.914 | 0.868 | 0.890 | 1,543 / 145 / 235 |
| Candidates accepted without review | 0.985 | 0.849 | 0.912 | 1,510 / 23 / 268 |
| Committed to the graph without review (190 hadiths) | 0.983 | 0.582 | 0.731 | 1,034 / 18 / 744 |

In the isnad-aware condition 5 of 1,639 proposals are unmatched, and the check flags 3 of them with no matched mention flagged. The checks have little left to find when the prompt already tells the model to copy names as written. On the pilot set the pattern of the schema-only condition repeats against the Sanadset labels: 35 flagged, all 35 unmatched, 3 unmatched mentions not flagged.

## 7.7 Model confidence

For the schema-only condition, the area under the ROC curve of the model's confidence as a predictor of a matched mention is 0.634. The model used seven distinct confidence values, and 1,623 of the 1,688 mentions carry a value between 0.8 and 1.0.

![Figure 7.3 Model confidence of matched and unmatched mentions, schema-only condition.](figures/fig-7-3-confidence.png)

A confidence threshold and a check are comparable only at the same share of mentions sent to review. Table 7.8 lists the three thresholds that select a meaningful share.

**Table 7.8** Unmatched mentions sent to review by a confidence threshold and by the value-in-quotation check (schema-only condition, 145 unmatched mentions in total).

| Signal | Mentions sent to review | Unmatched among them |
|---|---|---|
| Confidence below 0.80 | 65 (3.9%) | 16 |
| Confidence below 0.85 | 275 (16.3%) | 50 |
| Confidence below 0.90 | 1,018 (60.3%) | 110 |
| Value-in-quotation check | 155 (9.2%) | 122 |

At 16% of mentions the confidence threshold finds 50 unmatched mentions; the check finds 122 at 9%. To find 110, the threshold must send 60% of all mentions to a reviewer. The check needs no model call.

## 7.8 Review workload, commits and cost

**Table 7.9** Work left for a reviewer and cost per condition (six-book set).

| Condition | Candidates sent to review | Hadiths with nothing to review | Runs committed without review | Cost per 1,000 hadiths | Median latency per call |
|---|---|---|---|---|---|
| Rule | 0 | 100% | 300 of 300 | 0 | n/a |
| LLM, schema only | 538 | 63% | 190 of 300 | USD 1.87 | 11.1 s |
| LLM, isnad-aware | 16 | 98% | 294 of 300 | USD 2.29 | 13.0 s |
| LLM, isnad-aware, chain span | 6 | 99% | 295 of 300 | USD 2.21 | 12.8 s |

In the schema-only condition the 538 review candidates are 155 nodes flagged by the value check and 383 relations. The relation findings are 192 without a value for an identity property, 208 that depend on a node under review and 9 below the confidence threshold; a relation can carry more than one. A run with an open review item cannot be committed, so 110 of the 300 hadiths wait for a person.

Costs use the price constants in the experiment script, taken from the provider's price list as of 6 October 2026 for Claude Haiku 5.5 (USD 0.10 per million input tokens, USD 0.50 per million output tokens), and the token counts returned by the API: about 3,200 to 3,500 input and 3,100 to 3,900 output tokens per hadith. Latency is the median over calls that were not served from the response cache (300, 300 and 108 calls). The whole evaluation, including the pilot runs and the subset runs in Section 7.9, cost USD 3.49, summed over the eight model runs without counting cached replays.

For every committed fact in every run we checked two properties: its quotation is found in its source segment under the comparison used by the checks, and it has an acceptance record. Both hold for all committed facts. Under byte-exact comparison the first does not hold for the model runs: the model returns Arabic text in a different Unicode composition from the source, and a few quotations differ from the source in vowel marks, which the comparison ignores.

We have no measurement of human review time. The decision record stores it, but no person reviewed these runs.

## 7.9 A second model: a configuration failure

We ran Claude Sonnet 5.5 with the same settings on a stratified subset of 36 hadiths (six per collection) to see whether the results depend on the model. The run did not produce a usable comparison, and we report why.

With effort `low`, Sonnet 5.5 returned a single narrator for 28 of the 36 hadiths in the isnad-aware condition, and in most of those it wrote the narrator's name into the field that holds a property's key. Loose recall was 0.237 (isnad-aware) and 0.530 (schema only) against 0.916 and 0.828 for Haiku 5.5 on the same 36 hadiths.

We suspect two things in our configuration, and did not test either by a further run. The provider sends properties as a list of entries with the fields `name` and `value`, and the property that holds a narrator's name is itself called `name`, which is ambiguous. Second, the effort setting is not calibrated the same way across models. Haiku 5.5 followed the format in all but one of its 910 calls on the six-book set.

The engine handled the malformed output as designed. Unknown property keys were recorded as schema proposals (29 distinct keys in one condition), nodes without their identity property were rejected, 30 of the 36 runs were blocked from commit, and precision of what was proposed stayed at 0.966 or above. Nothing malformed reached the graph. This is the property-level form of schema drift that the type-level check of the original code could not see.

We do not draw a conclusion about the two models from this run. The wire format should be changed before another model is evaluated.

## 7.10 Narrator identity

The engine identifies a narrator node by the written name. The Ifta labels attach a person identifier to each mention, which lets us measure what that choice costs without running any system. The labels list each chain separately, so a narrator shared by parallel chains is counted once per chain. Over the 300 test hadiths this gives 2,150 chain positions filled by 740 people (the 1,778 reference mentions of Table 7.1 count each written mention once).

**Table 7.10** Grouping chain positions by a string key instead of by person (six-book set, reference labels only). Pairwise precision is the share of position pairs with the same key that are the same person, and pairwise recall the share of same-person pairs that share a key. B-cubed averages, over positions, the share of positions with the same key that are the same person (precision) and the share of the person's positions that have the same key (recall).

| Key | Distinct keys | Keys that cover more than one person | Positions under such keys | People split over several keys | Pairwise P / R | B-cubed P / R |
|---|---|---|---|---|---|---|
| Name exactly as written | 964 | 24 (2.5%) | 216 (10.0%) | 191 (25.8%) | 0.737 / 0.559 | 0.941 / 0.715 |
| Normalised name | 878 | 28 (3.2%) | 262 (12.2%) | 161 (21.8%) | 0.759 / 0.703 | 0.931 / 0.792 |

One chain position in ten falls under a name shared by more than one person, and a quarter of the people appear under more than one name. The most ambiguous keys are kinship references: `أَبِيهِ` ("his father") stands for 34 different people in this sample. Normalising the name reduces splitting and increases conflation. Neither key is an identity. The same pattern is visible in the AR-Sanad test chains [@mahmoud2022arsanad], where 815 of 15,301 surface names map to more than one identifier.

This is a measurement of the problem, not of a solution. Linking mentions to an authority list is future work.

## 7.11 What we did not measure

- **Human gold standard.** No hadith in this evaluation was labelled by two independent annotators. The annotation sheet and guideline exist; the labelling has not been done.
- **Human review.** No reviewer decided any candidate, so we have no review time, no rejection rate and no measurement of the pipeline with a person in it.
- **Relations.** We scored narrator mentions and their order, not `NARRATED_FROM` links as triples.
- **Other models.** One model produced usable results. The second run failed for a configuration reason.
- **Schema drift.** The Haiku runs produced one unknown property in 910 calls and no unknown type, so the measured evidence for drift comes almost entirely from the failed second-model run.
- **Run-to-run variation.** Each condition was run once.
- **Memorisation.** We did not test whether the model recalls well-known chains instead of reading them.
- **Question answering.** The graph is not yet compared with text retrieval on any question set.
- **Text integrity.** We did not compare the corpus text with a printed edition.

## 7.12 Earlier pilot

A pilot on 30 September 2026 used the same 50 hadiths with a different model (Claude Sonnet 5) outside the engine. It reported loose F1 of 0.879 for a rule-based parser, 0.865 for a schema-only prompt and 0.935 for an isnad-aware prompt; 605 of 605 model quotations found in the source; 32 of 318 names not found in the model's own quotation; and a confidence AUC of 0.626. The engine-based runs in this chapter reproduce each of these patterns with a different model, on six times as much unseen data and against a different label source.
