# Experiment analysis: llm_isnad_chain

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_isnad_chain | claude-haiku-5-5 | low | anthropic | isnad | no |

Evaluated hadiths: 300 of 300 in the reference (the run processed 300; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.944 [0.932, 0.957] | 0.854 [0.831, 0.875] | 0.897 [0.881, 0.912] | 1518 | 90 | 260 | 0.480 |
| proposed | M2 | 0.998 [0.996, 1.000] | 0.903 [0.882, 0.922] | 0.948 [0.936, 0.959] | 1605 | 3 | 173 | 0.650 |
| validated | M1 | 0.944 [0.932, 0.957] | 0.854 [0.831, 0.875] | 0.897 [0.881, 0.912] | 1518 | 90 | 260 | 0.480 |
| validated | M2 | 0.998 [0.996, 1.000] | 0.903 [0.882, 0.922] | 0.948 [0.936, 0.959] | 1605 | 3 | 173 | 0.650 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

1608 proposed Narrator mentions under M2: 1605 correct, 3 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| any gate | 0 | 0 | 3 | n/a | 0.000 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.754

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 1 | 0 |
| 0.6-0.7 | 2 | 0 |
| 0.7-0.8 | 11 | 0 |
| 0.8-0.9 | 216 | 2 |
| 0.9-1.0 | 1375 | 1 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 300 | 6 | 0.020 | 0.000 | 3 | 6 | 0.987 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 310 | 202 | 1 | 0 | 0 | 0.002214 | 2.2139 | 3266.6 | 3774.5 | 0.240360 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| relation | potential_duplicate_relation | 3 |
| relation | relation_confidence_threshold | 3 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
