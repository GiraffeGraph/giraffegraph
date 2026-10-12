# Experiment analysis: llm_isnad_whole

| condition | model | effort | provider | segmentation | stopped |
|---|---|---|---|---|---|
| llm_isnad_whole | claude-sonnet-5-5 | low | anthropic | paragraphs | no |

Evaluated hadiths: 36 of 36 in the reference (the run processed 36; 0 were not processed because the run stopped).

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

## 1. Scores

| output | criterion | precision [95% CI] | recall [95% CI] | F1 [95% CI] | TP | FP | FN | exact-chain rate |
|---|---|---|---|---|---|---|---|---|
| proposed | M1 | 0.846 [0.700, 0.938] | 0.205 [0.093, 0.336] | 0.330 [0.167, 0.490] | 44 | 8 | 171 | 0.167 |
| proposed | M2 | 0.981 [0.927, 1.000] | 0.237 [0.122, 0.369] | 0.382 [0.216, 0.539] | 51 | 1 | 164 | 0.194 |
| validated | M1 | 0.975 [0.911, 1.000] | 0.181 [0.072, 0.308] | 0.306 [0.133, 0.469] | 39 | 1 | 176 | 0.139 |
| validated | M2 | 1.000 [1.000, 1.000] | 0.186 [0.075, 0.314] | 0.314 [0.139, 0.478] | 40 | 0 | 175 | 0.139 |

Intervals: percentile bootstrap over hadiths, 2000 resamples, seed 0.

## 2. Gates as error detectors

52 proposed Narrator mentions under M2: 51 correct, 1 wrong.

| gate | errors caught | false alarms | errors missed | precision | recall |
|---|---|---|---|---|---|
| node_merge_key | 1 | 11 | 0 | 0.083 | 1.000 |
| required_node_property | 1 | 11 | 0 | 0.083 | 1.000 |
| any gate | 1 | 11 | 0 | 0.083 | 1.000 |

## 3. Model confidence and correctness

AUC (correct vs wrong mentions, ties count one half): 1.000

| confidence | correct | wrong |
|---|---|---|
| 0.0-0.1 | 0 | 0 |
| 0.1-0.2 | 0 | 1 |
| 0.2-0.3 | 0 | 0 |
| 0.3-0.4 | 0 | 0 |
| 0.4-0.5 | 0 | 0 |
| 0.5-0.6 | 0 | 0 |
| 0.6-0.7 | 0 | 0 |
| 0.7-0.8 | 1 | 0 |
| 0.8-0.9 | 3 | 0 |
| 0.9-1.0 | 47 | 0 |

## 4. Review workload

| hadiths | candidates in review | mean per hadith | median per hadith | max per hadith | open review items | share of hadiths without review items |
|---|---|---|---|---|---|---|
| 36 | 0 | 0.000 | 0.000 | 0 | 30 | 0.167 |

## 5. Cost

| calls | cached | failed | refused | truncated | USD per hadith | USD per 1,000 hadiths | input tokens per hadith | output tokens per hadith | USD spent by this run |
|---|---|---|---|---|---|---|---|---|---|
| 36 | 0 | 0 | 0 | 0 | 0.014476 | 14.4760 | 3434.9 | 760.6 | 0.521136 |

Cost is priced from the tokens of every call, including calls served from the response cache.

## 6. Schema proposals and reason codes

| reason code | kind | type | property | count |
|---|---|---|---|---|
| schema_property_proposal | node | Narrator | أَبُو بَكْرِ بْنُ أَبِي شَيْبَةَ | 2 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ كَثِيرٍ | 1 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ عَبْدِ الْعَزِيزِ | 1 |
| schema_property_proposal | node | Narrator | الْحُمَيْدِيُّ | 1 |
| schema_property_proposal | node | Narrator | مُسَدَّدٌ | 1 |
| schema_property_proposal | node | Narrator | أَبُو عَاصِمٍ | 1 |
| schema_property_proposal | node | Narrator | يَحْيَى بْنُ يَحْيَى التَّمِيمِيُّ | 1 |
| schema_property_proposal | node | Narrator | يَحْيَى بْنُ يَحْيَى | 1 |
| schema_property_proposal | node | Narrator | يَحْيَى بْنُ أَيُّوبَ | 1 |
| schema_property_proposal | node | Narrator | عَمْرٌو النَّاقِدُ | 1 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ حَاتِمٍ | 1 |
| schema_property_proposal | node | Narrator | أَحْمَدُ بْنُ مُحَمَّدٍ الْمَرْوَزِيُّ | 1 |
| schema_property_proposal | node | Narrator | عَمْرُو بْنُ مَرْزُوقٍ | 1 |
| schema_property_proposal | node | Narrator | عِيسَى بْنُ حَمَّادٍ | 1 |
| schema_property_proposal | node | Narrator | الْحَسَنُ بْنُ عَلِيٍّ | 1 |
| schema_property_proposal | node | Narrator | قُتَيْبَةُ بْنُ سَعِيدٍ | 1 |
| schema_property_proposal | node | Narrator | هَنَّادٌ | 1 |
| schema_property_proposal | node | Narrator | الْعَبَّاسُ الدُّورِيُّ | 1 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ عُبَيْدٍ الْمُحَارِبِيُّ | 1 |
| schema_property_proposal | node | Narrator | ابْنُ أَبِي عُمَرَ | 1 |
| schema_property_proposal | node | Narrator | عَبْدُ بْنُ حُمَيْدٍ | 1 |
| schema_property_proposal | node | Narrator | سَعِيدُ بْنُ عَبْدِ الرَّحْمَنِ | 1 |
| schema_property_proposal | node | Narrator | هَارُونُ بْنُ عَبْدِ اللهِ | 1 |
| schema_property_proposal | node | Narrator | إِسْمَاعِيلُ بْنُ مَسْعُودٍ | 1 |
| schema_property_proposal | node | Narrator | الْفَضْلُ بْنُ سَهْلٍ | 1 |
| schema_property_proposal | node | Narrator | value | 1 |
| schema_property_proposal | node | Narrator | مُحَمَّدُ بْنُ آدَمَ | 1 |
| schema_property_proposal | node | Narrator | أَبُو عُمَيْرٍ عِيسَى بْنُ مُحَمَّدٍ النَّحَّاسُ | 1 |
| schema_property_proposal | node | Narrator | هِشَامُ بْنُ خَالِدٍ الْأَزْرَقُ أَبُو مَرْوَانَ الدِّمَشْقِيُّ | 1 |

| candidate kind | reason code | candidates |
|---|---|---|
| node | node_merge_key | 30 |
| node | required_node_property | 30 |
| relation | relation_dependency_rejected | 3 |

Every committed fact has a quote found verbatim in its source segment and an acceptance record: no; with the grounding gate's text normalisation: yes.
