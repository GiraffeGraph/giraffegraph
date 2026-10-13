# Experiment analysis: llm_isnad_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_isnad_whole | claude-haiku-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 300 of 300 in the reference (the run processed 300; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.942 [0.929, 0.954] | 0.868 [0.848, 0.888] | 0.904 [0.889, 0.918] | 1544 | 95 | 234 | 0.513 |
| proposed | M2 | 0.997 [0.994, 0.999] | 0.919 [0.901, 0.936] | 0.956 [0.946, 0.966] | 1634 | 5 | 144 | 0.690 |
| validated | M1 | 0.944 [0.931, 0.956] | 0.868 [0.848, 0.888] | 0.905 [0.889, 0.919] | 1544 | 92 | 234 | 0.513 |
| validated | M2 | 0.999 [0.997, 1.000] | 0.919 [0.901, 0.936] | 0.957 [0.947, 0.967] | 1634 | 2 | 144 | 0.690 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

1639 proposed Narrator mentions under M2: 1634 correct, 5 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| value_not_in_quote | 3 | 0 | 2 | 1.000 | 0.600 |
| any gate | 3 | 0 | 2 | 1.000 | 0.600 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.517

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 1 | 0 |
| 0.6-0.7 | 5 | 0 |
| 0.7-0.8 | 8 | 0 |
| 0.8-0.9 | 255 | 1 |
| 0.9-1.0 | 1365 | 4 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 300 | 16 | 0.053 | 0.000 | 4 | 16 | 0.980 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 300 | 0 | 0 | 0 | 0 | 0.002295 | 2.2946 | 3490.2 | 3891.2 | 0.688388 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| node | value_not_in_quote | 3 |
| relation | relation_confidence_threshold | 5 |
| relation | relation_dependency_review | 8 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
