# Experiment analysis: rule

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| rule | n/a | n/a | rule_based_isnad | isnad | no |

Evaluated hadiths: 300 of 300 in the reference (the run processed 300; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.664 [0.640, 0.687] | 0.605 [0.576, 0.632] | 0.633 [0.608, 0.658] | 1075 | 543 | 703 | 0.093 |
| proposed | M2 | 0.968 [0.958, 0.978] | 0.881 [0.861, 0.901] | 0.923 [0.910, 0.935] | 1567 | 51 | 211 | 0.490 |
| validated | M1 | 0.664 [0.640, 0.687] | 0.605 [0.576, 0.632] | 0.633 [0.608, 0.658] | 1075 | 543 | 703 | 0.093 |
| validated | M2 | 0.968 [0.958, 0.978] | 0.881 [0.861, 0.901] | 0.923 [0.910, 0.935] | 1567 | 51 | 211 | 0.490 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

1618 proposed Narrator mentions under M2: 1567 correct, 51 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| any gate | 0 | 0 | 51 | n/a | 0.000 |

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
| 0.9-1.0 | 1567 | 51 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 300 | 0 | 0.000 | 0.000 | 0 | 0 | 1.000 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 310 | 0 | 0 | 0 | 0 | 0.000000 | 0.0000 | 0.0 | 0.0 | 0.000000 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| none |  |  |  | 0 |

| candidate kind | reason code | candidates |
|---|---|---|
| none |  | 0 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: yes; with the grounding gate's text normalisation: yes.
