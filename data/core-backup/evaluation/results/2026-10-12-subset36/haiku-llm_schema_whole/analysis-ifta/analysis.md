# Experiment analysis: llm_schema_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_schema_whole | claude-haiku-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 36 of 36 in the reference (the run processed 36; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.824 [0.733, 0.900] | 0.763 [0.677, 0.835] | 0.792 [0.710, 0.863] | 164 | 35 | 51 | 0.306 |
| proposed | M2 | 0.894 [0.806, 0.968] | 0.828 [0.737, 0.903] | 0.860 [0.771, 0.931] | 178 | 21 | 37 | 0.444 |
| validated | M1 | 0.906 [0.863, 0.947] | 0.758 [0.673, 0.832] | 0.825 [0.761, 0.878] | 163 | 17 | 52 | 0.306 |
| validated | M2 | 0.983 [0.964, 1.000] | 0.823 [0.733, 0.898] | 0.896 [0.836, 0.942] | 177 | 3 | 38 | 0.444 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

199 proposed Narrator mentions under M2: 178 correct, 21 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| value_not_in_quote | 18 | 1 | 3 | 0.947 | 0.857 |
| any gate | 18 | 1 | 3 | 0.947 | 0.857 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.585

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 0 | 0 |
| 0.7-0.8 | 0 | 1 |
| 0.8-0.9 | 96 | 13 |
| 0.9-1.0 | 82 | 7 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 36 | 75 | 2.083 | 0.000 | 12 | 75 | 0.639 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 36 | 36 | 0 | 0 | 0 | 0.001907 | 1.9068 | 3111.3 | 3191.4 | 0.000000 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| node | value_not_in_quote | 19 |
| relation | missing_relation_merge_key | 32 |
| relation | relation_confidence_threshold | 1 |
| relation | relation_dependency_review | 27 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
