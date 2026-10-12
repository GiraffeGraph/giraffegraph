# Run comparison

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

| run | condition | model | effort | hadiths | M1 F1 | M2 precision [95% CI] | M2 recall [95% CI] | M2 F1 [95% CI] | exact-chain rate | validated M2 precision | validated M2 recall | validated M2 F1 | any-gate precision | any-gate recall | confidence AUC | review candidates per hadith | share of hadiths without review items | USD per 1,000 hadiths | tokens per hadith | failed calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rule | rule | n/a | n/a | 300 | 0.633 | 0.968 [0.958, 0.978] | 0.881 [0.861, 0.901] | 0.923 [0.910, 0.935] | 0.490 | 0.968 | 0.881 | 0.923 | n/a | 0.000 | 0.500 | 0.000 | 1.000 | 0.0000 | 0.0 | 0 |
| haiku-llm_schema_whole | llm_schema_whole | claude-haiku-5-5 | low | 300 | 0.826 | 0.914 [0.888, 0.939] | 0.868 [0.842, 0.894] | 0.890 [0.865, 0.914] | 0.567 | 0.985 | 0.849 | 0.912 | 0.787 | 0.841 | 0.634 | 1.793 | 0.633 | 1.8727 | 6276.1 | 0 |
| haiku-llm_isnad_whole | llm_isnad_whole | claude-haiku-5-5 | low | 300 | 0.904 | 0.997 [0.994, 0.999] | 0.919 [0.901, 0.936] | 0.956 [0.946, 0.966] | 0.690 | 0.999 | 0.919 | 0.957 | 1.000 | 0.600 | 0.517 | 0.053 | 0.980 | 2.2946 | 7381.4 | 0 |
| haiku-llm_isnad_chain | llm_isnad_chain | claude-haiku-5-5 | low | 300 | 0.897 | 0.998 [0.996, 1.000] | 0.903 [0.882, 0.922] | 0.948 [0.936, 0.959] | 0.650 | 0.998 | 0.903 | 0.948 | n/a | 0.000 | 0.754 | 0.020 | 0.987 | 2.2139 | 7041.1 | 1 |

## Paired differences (M2, proposed output)

Difference = first run minus second run. Intervals: paired percentile bootstrap over hadiths, 2000 resamples, seed 0.

| first run | second run | hadiths | metric | first value | second value | difference | 95% CI |
|---|---|---|---|---|---|---|---|
| rule | haiku-llm_schema_whole | 300 | precision | 0.968 | 0.914 | 0.054 | [0.026, 0.083] |
| rule | haiku-llm_schema_whole | 300 | recall | 0.881 | 0.868 | 0.013 | [-0.018, 0.044] |
| rule | haiku-llm_schema_whole | 300 | f1 | 0.923 | 0.890 | 0.032 | [0.006, 0.060] |
| rule | haiku-llm_isnad_whole | 300 | precision | 0.968 | 0.997 | -0.028 | [-0.039, -0.019] |
| rule | haiku-llm_isnad_whole | 300 | recall | 0.881 | 0.919 | -0.038 | [-0.061, -0.016] |
| rule | haiku-llm_isnad_whole | 300 | f1 | 0.923 | 0.956 | -0.034 | [-0.047, -0.021] |
| rule | haiku-llm_isnad_chain | 300 | precision | 0.968 | 0.998 | -0.030 | [-0.040, -0.020] |
| rule | haiku-llm_isnad_chain | 300 | recall | 0.881 | 0.903 | -0.021 | [-0.040, -0.002] |
| rule | haiku-llm_isnad_chain | 300 | f1 | 0.923 | 0.948 | -0.025 | [-0.036, -0.013] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 300 | precision | 0.914 | 0.997 | -0.083 | [-0.108, -0.059] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 300 | recall | 0.868 | 0.919 | -0.051 | [-0.078, -0.024] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 300 | f1 | 0.890 | 0.956 | -0.066 | [-0.091, -0.041] |
| haiku-llm_schema_whole | haiku-llm_isnad_chain | 300 | precision | 0.914 | 0.998 | -0.084 | [-0.109, -0.059] |
| haiku-llm_schema_whole | haiku-llm_isnad_chain | 300 | recall | 0.868 | 0.903 | -0.035 | [-0.064, -0.007] |
| haiku-llm_schema_whole | haiku-llm_isnad_chain | 300 | f1 | 0.890 | 0.948 | -0.058 | [-0.084, -0.032] |
| haiku-llm_isnad_whole | haiku-llm_isnad_chain | 300 | precision | 0.997 | 0.998 | -0.001 | [-0.004, 0.001] |
| haiku-llm_isnad_whole | haiku-llm_isnad_chain | 300 | recall | 0.919 | 0.903 | 0.016 | [-0.003, 0.035] |
| haiku-llm_isnad_whole | haiku-llm_isnad_chain | 300 | f1 | 0.956 | 0.948 | 0.008 | [-0.002, 0.019] |
