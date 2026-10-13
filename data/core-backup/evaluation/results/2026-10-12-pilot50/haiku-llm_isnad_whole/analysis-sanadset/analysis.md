# Experiment analysis: llm_isnad_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_isnad_whole | claude-haiku-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 50 of 50 in the reference (the run processed 50; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.912 [0.869, 0.949] | 0.823 [0.756, 0.887] | 0.865 [0.813, 0.913] | 269 | 26 | 58 | 0.480 |
| proposed | M2 | 0.997 [0.988, 1.000] | 0.899 [0.842, 0.948] | 0.945 [0.913, 0.971] | 294 | 1 | 33 | 0.660 |
| validated | M1 | 0.912 [0.869, 0.949] | 0.823 [0.756, 0.887] | 0.865 [0.813, 0.913] | 269 | 26 | 58 | 0.480 |
| validated | M2 | 0.997 [0.988, 1.000] | 0.899 [0.842, 0.948] | 0.945 [0.913, 0.971] | 294 | 1 | 33 | 0.660 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

295 proposed Narrator mentions under M2: 294 correct, 1 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| any gate | 0 | 0 | 1 | n/a | 0.000 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.912

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 0 | 0 |
| 0.7-0.8 | 5 | 0 |
| 0.8-0.9 | 30 | 1 |
| 0.9-1.0 | 259 | 0 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 50 | 0 | 0.000 | 0.000 | 0 | 0 | 1.000 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 0 | 0 | 0 | 0.002428 | 2.4282 | 3515.7 | 4153.3 | 0.121410 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| none |  | 0 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
