# Experiment analysis: llm_isnad_chain

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_isnad_chain | claude-haiku-5-5 | low | anthropic | isnad | no |

Evaluated hadiths: 50 of 50 in the reference (the run processed 50; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.924 [0.883, 0.959] | 0.786 [0.719, 0.858] | 0.850 [0.800, 0.900] | 257 | 21 | 70 | 0.460 |
| proposed | M2 | 1.000 [1.000, 1.000] | 0.850 [0.785, 0.916] | 0.919 [0.880, 0.956] | 278 | 0 | 49 | 0.640 |
| validated | M1 | 0.924 [0.883, 0.959] | 0.786 [0.719, 0.858] | 0.850 [0.800, 0.900] | 257 | 21 | 70 | 0.460 |
| validated | M2 | 1.000 [1.000, 1.000] | 0.850 [0.785, 0.916] | 0.919 [0.880, 0.956] | 278 | 0 | 49 | 0.640 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

278 proposed Narrator mentions under M2: 278 correct, 0 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| any gate | 0 | 0 | 0 | n/a | n/a |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): n/a

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 0 | 0 |
| 0.7-0.8 | 0 | 0 |
| 0.8-0.9 | 29 | 0 |
| 0.9-1.0 | 249 | 0 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 50 | 1 | 0.020 | 0.000 | 1 | 1 | 0.980 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 55 | 4 | 0 | 0 | 0 | 0.002258 | 2.2580 | 3479.3 | 3820.2 | 0.105566 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| relation | potential_duplicate_relation | 1 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
