# Experiment analysis: rule

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| rule | n/a | n/a | rule_based_isnad | isnad | no |

Evaluated hadiths: 36 of 36 in the reference (the run processed 36; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.691 [0.626, 0.755] | 0.623 [0.539, 0.703] | 0.655 [0.580, 0.726] | 134 | 60 | 81 | 0.083 |
| proposed | M2 | 0.979 [0.954, 1.000] | 0.884 [0.824, 0.935] | 0.929 [0.894, 0.959] | 190 | 4 | 25 | 0.556 |
| validated | M1 | 0.691 [0.626, 0.755] | 0.623 [0.539, 0.703] | 0.655 [0.580, 0.726] | 134 | 60 | 81 | 0.083 |
| validated | M2 | 0.979 [0.954, 1.000] | 0.884 [0.824, 0.935] | 0.929 [0.894, 0.959] | 190 | 4 | 25 | 0.556 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

194 proposed Narrator mentions under M2: 190 correct, 4 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| any gate | 0 | 0 | 4 | n/a | 0.000 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.500

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
| 0.8-0.9 | 0 | 0 |
| 0.9-1.0 | 190 | 4 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 36 | 0 | 0.000 | 0.000 | 0 | 0 | 1.000 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 37 | 0 | 0 | 0 | 0 | 0.000000 | 0.0000 | 0.0 | 0.0 | 0.000000 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| none |  | 0 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: yes; with the grounding gate's text normalisation: yes.
