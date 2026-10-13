# Experiment analysis: llm_schema_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_schema_whole | claude-sonnet-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 36 of 36 in the reference (the run processed 36; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.839 [0.773, 0.899] | 0.460 [0.324, 0.597] | 0.595 [0.463, 0.708] | 99 | 19 | 116 | 0.250 |
| proposed | M2 | 0.966 [0.933, 0.992] | 0.530 [0.378, 0.670] | 0.685 [0.543, 0.793] | 114 | 4 | 101 | 0.306 |
| validated | M1 | 0.907 [0.848, 0.960] | 0.451 [0.314, 0.591] | 0.602 [0.466, 0.720] | 97 | 10 | 118 | 0.250 |
| validated | M2 | 0.991 [0.971, 1.000] | 0.493 [0.342, 0.638] | 0.658 [0.508, 0.774] | 106 | 1 | 109 | 0.306 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

118 proposed Narrator mentions under M2: 114 correct, 4 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| node_merge_key | 0 | 4 | 4 | 0.000 | 0.000 |
| required_node_property | 0 | 4 | 4 | 0.000 | 0.000 |
| value_not_in_quote | 3 | 4 | 1 | 0.429 | 0.750 |
| any gate | 3 | 8 | 1 | 0.273 | 0.750 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 0.977

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 1 | 0 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 1 | 0 |
| 0.7-0.8 | 1 | 3 |
| 0.8-0.9 | 10 | 1 |
| 0.9-1.0 | 101 | 0 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 36 | 21 | 0.583 | 0.000 | 6 | 38 | 0.389 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 36 | 0 | 0 | 0 | 0 | 0.019826 | 19.8259 | 3113.1 | 1360.0 | 0.713734 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| schema_property_proposal | node | Narrator | أَبُو بَكْرِ بْنُ أَبِي شَيْبَةَ | 2 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ كَثِيرٍ | 1 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ عَبْدِ الْعَزِيزِ | 1 |
| schema_property_proposal | node | Narrator | الْحُمَيْدِيُّ | 1 |
| schema_property_proposal | node | Narrator | مُسَدَّدٌ | 1 |
| schema_property_proposal | node | Narrator | يَحْيَى بْنُ يَحْيَى التَّمِيمِيُّ | 1 |
| schema_property_proposal | node | Narrator | عَمْرٌو النَّاقِدُ | 1 |
| schema_property_proposal | node | Narrator | أَحْمَدُ بْنُ مُحَمَّدٍ الْمَرْوَزِيُّ | 1 |
| schema_property_proposal | node | Narrator | عَمْرُو بْنُ مَرْزُوقٍ | 1 |
| schema_property_proposal | node | Narrator | عِيسَى بْنُ حَمَّادٍ | 1 |
| schema_property_proposal | node | Narrator | الْحَسَنُ بْنُ عَلِيٍّ | 1 |
| schema_property_proposal | node | Narrator | ابْنُ أَبِي عُمَرَ | 1 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ عَبْدِ الْأَعْلَى | 1 |
| schema_property_proposal | node | Narrator | هَارُونُ بْنُ عَبْدِ اللهِ | 1 |
| schema_property_proposal | node | Narrator | زَكَرِيَّا بْنُ يَحْيَى | 1 |
| schema_property_proposal | node | Narrator | أَبُو عُمَيْرٍ عِيسَى بْنُ مُحَمَّدٍ النَّحَّاسُ | 1 |

| candidate kind | reason code | candidates |
|---|---|---|
| node | node_merge_key | 17 |
| node | required_node_property | 17 |
| node | value_not_in_quote | 7 |
| relation | relation_dependency_review | 14 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
