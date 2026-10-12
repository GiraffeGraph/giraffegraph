# Experiment analysis: llm_schema_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_schema_whole | claude-haiku-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 300 of 300 in the reference (the run processed 300; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.848 [0.820, 0.874] | 0.805 [0.777, 0.831] | 0.826 [0.799, 0.850] | 1431 | 257 | 347 | 0.383 |
| proposed | M2 | 0.914 [0.888, 0.939] | 0.868 [0.842, 0.894] | 0.890 [0.865, 0.914] | 1543 | 145 | 235 | 0.567 |
| validated | M1 | 0.931 [0.915, 0.945] | 0.803 [0.775, 0.828] | 0.862 [0.843, 0.880] | 1427 | 106 | 351 | 0.380 |
| validated | M2 | 0.985 [0.974, 0.993] | 0.849 [0.823, 0.875] | 0.912 [0.896, 0.927] | 1510 | 23 | 268 | 0.517 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

1688 proposed Narrator mentions under M2: 1543 correct, 145 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| value_not_in_quote | 122 | 33 | 23 | 0.787 | 0.841 |
| any gate | 122 | 33 | 23 | 0.787 | 0.841 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.634

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 1 | 0 |
| 0.6-0.7 | 2 | 3 |
| 0.7-0.8 | 46 | 13 |
| 0.8-0.9 | 859 | 94 |
| 0.9-1.0 | 635 | 35 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 300 | 538 | 1.793 | 0.000 | 16 | 539 | 0.633 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 300 | 0 | 0 | 0 | 0 | 0.001873 | 1.8727 | 3163.3 | 3112.8 | 0.561821 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| schema_property_proposal | relation | TRANSMITS | hadith_ref | 1 |

| candidate kind | reason code | candidates |
|---|---|---|
| node | value_not_in_quote | 155 |
| relation | missing_relation_merge_key | 192 |
| relation | relation_confidence_threshold | 9 |
| relation | relation_dependency_review | 208 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
