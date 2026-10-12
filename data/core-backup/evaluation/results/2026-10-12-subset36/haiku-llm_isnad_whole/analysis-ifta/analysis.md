# Experiment analysis: llm_isnad_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_isnad_whole | claude-haiku-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 36 of 36 in the reference (the run processed 36; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.939 [0.904, 0.970] | 0.865 [0.804, 0.918] | 0.901 [0.857, 0.939] | 186 | 12 | 29 | 0.500 |
| proposed | M2 | 0.995 [0.984, 1.000] | 0.916 [0.855, 0.966] | 0.954 [0.914, 0.983] | 197 | 1 | 18 | 0.694 |
| validated | M1 | 0.939 [0.904, 0.970] | 0.865 [0.804, 0.918] | 0.901 [0.857, 0.939] | 186 | 12 | 29 | 0.500 |
| validated | M2 | 0.995 [0.984, 1.000] | 0.916 [0.855, 0.966] | 0.954 [0.914, 0.983] | 197 | 1 | 18 | 0.694 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

198 proposed Narrator mentions under M2: 197 correct, 1 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| any gate | 0 | 0 | 1 | n/a | 0.000 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.437

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 1 | 0 |
| 0.7-0.8 | 1 | 0 |
| 0.8-0.9 | 23 | 0 |
| 0.9-1.0 | 172 | 1 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 36 | 0 | 0.000 | 0.000 | 0 | 0 | 1.000 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 36 | 36 | 0 | 0 | 0 | 0.002288 | 2.2878 | 3438.1 | 3888.1 | 0.000000 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| none |  | 0 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
