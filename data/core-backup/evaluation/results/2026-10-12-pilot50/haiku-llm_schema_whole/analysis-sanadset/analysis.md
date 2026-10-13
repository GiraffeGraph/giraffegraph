# Experiment analysis: llm_schema_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_schema_whole | claude-haiku-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 50 of 50 in the reference (the run processed 50; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.804 [0.706, 0.896] | 0.728 [0.626, 0.834] | 0.764 [0.666, 0.862] | 238 | 58 | 89 | 0.440 |
| proposed | M2 | 0.872 [0.770, 0.958] | 0.789 [0.686, 0.894] | 0.828 [0.726, 0.921] | 258 | 38 | 69 | 0.580 |
| validated | M1 | 0.912 [0.866, 0.952] | 0.728 [0.626, 0.834] | 0.810 [0.735, 0.882] | 238 | 23 | 89 | 0.440 |
| validated | M2 | 0.989 [0.973, 1.000] | 0.789 [0.686, 0.894] | 0.878 [0.808, 0.939] | 258 | 3 | 69 | 0.580 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

296 proposed Narrator mentions under M2: 258 correct, 38 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| value_not_in_quote | 35 | 0 | 3 | 1.000 | 0.921 |
| any gate | 35 | 0 | 3 | 1.000 | 0.921 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.604

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 0 | 2 |
| 0.7-0.8 | 0 | 0 |
| 0.8-0.9 | 134 | 27 |
| 0.9-1.0 | 124 | 9 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 50 | 105 | 2.100 | 0.000 | 24 | 105 | 0.720 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 0 | 0 | 0 | 0.002042 | 2.0425 | 3187.1 | 3447.5 | 0.102123 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| node | value_not_in_quote | 35 |
| relation | missing_relation_merge_key | 30 |
| relation | relation_dependency_review | 40 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
