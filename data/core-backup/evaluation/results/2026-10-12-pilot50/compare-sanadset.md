# Run comparison

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

| run | condition | model | effort | hadiths | M1 F1 | M2 precision [95% CI] | M2 recall [95% CI] | M2 F1 [95% CI] | exact-chain rate | validated M2 precision | validated M2 recall | validated M2 F1 | any-gate precision | any-gate recall | confidence AUC | review candidates per hadith | share of hadiths without review items | USD per 1,000 hadiths | tokens per hadith | failed calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rule | rule | n/a | n/a | 50 | 0.637 | 0.958 [0.926, 0.986] | 0.835 [0.764, 0.908] | 0.892 [0.850, 0.933] | 0.440 | 0.958 | 0.835 | 0.892 | n/a | 0.000 | 0.500 | 0.000 | 1.000 | 0.0000 | 0.0 | 0 |
| haiku-llm_schema_whole | llm_schema_whole | claude-haiku-5-5 | low | 50 | 0.764 | 0.872 [0.770, 0.958] | 0.789 [0.686, 0.894] | 0.828 [0.726, 0.921] | 0.580 | 0.989 | 0.789 | 0.878 | 1.000 | 0.921 | 0.604 | 2.100 | 0.720 | 2.0425 | 6634.6 | 0 |
| haiku-llm_isnad_whole | llm_isnad_whole | claude-haiku-5-5 | low | 50 | 0.865 | 0.997 [0.988, 1.000] | 0.899 [0.842, 0.948] | 0.945 [0.913, 0.971] | 0.660 | 0.997 | 0.899 | 0.945 | n/a | 0.000 | 0.912 | 0.000 | 1.000 | 2.4282 | 7669.0 | 0 |
| haiku-llm_isnad_chain | llm_isnad_chain | claude-haiku-5-5 | low | 50 | 0.850 | 1.000 [1.000, 1.000] | 0.850 [0.785, 0.916] | 0.919 [0.880, 0.956] | 0.640 | 1.000 | 0.850 | 0.919 | n/a | n/a | n/a | 0.020 | 0.980 | 2.2580 | 7299.4 | 0 |

## Paired differences (M2, proposed output)

Difference = first run minus second run. Intervals: paired percentile bootstrap over hadiths, 2000 resamples, seed 0.

| first run | second run | hadiths | metric | first value | second value | difference | 95% CI |
|---|---|---|---|---|---|---|---|
| rule | haiku-llm_schema_whole | 50 | precision | 0.958 | 0.872 | 0.086 | [-0.011, 0.194] |
| rule | haiku-llm_schema_whole | 50 | recall | 0.835 | 0.789 | 0.046 | [-0.052, 0.139] |
| rule | haiku-llm_schema_whole | 50 | f1 | 0.892 | 0.828 | 0.064 | [-0.026, 0.160] |
| rule | haiku-llm_isnad_whole | 50 | precision | 0.958 | 0.997 | -0.039 | [-0.071, -0.011] |
| rule | haiku-llm_isnad_whole | 50 | recall | 0.835 | 0.899 | -0.064 | [-0.115, -0.007] |
| rule | haiku-llm_isnad_whole | 50 | f1 | 0.892 | 0.945 | -0.053 | [-0.085, -0.019] |
| rule | haiku-llm_isnad_chain | 50 | precision | 0.958 | 1.000 | -0.042 | [-0.074, -0.014] |
| rule | haiku-llm_isnad_chain | 50 | recall | 0.835 | 0.850 | -0.015 | [-0.057, 0.029] |
| rule | haiku-llm_isnad_chain | 50 | f1 | 0.892 | 0.919 | -0.027 | [-0.056, 0.001] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 50 | precision | 0.872 | 0.997 | -0.125 | [-0.226, -0.037] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 50 | recall | 0.789 | 0.899 | -0.110 | [-0.213, -0.015] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 50 | f1 | 0.828 | 0.945 | -0.117 | [-0.218, -0.025] |
| haiku-llm_schema_whole | haiku-llm_isnad_chain | 50 | precision | 0.872 | 1.000 | -0.128 | [-0.230, -0.042] |
| haiku-llm_schema_whole | haiku-llm_isnad_chain | 50 | recall | 0.789 | 0.850 | -0.061 | [-0.147, 0.021] |
| haiku-llm_schema_whole | haiku-llm_isnad_chain | 50 | f1 | 0.828 | 0.919 | -0.091 | [-0.182, -0.011] |
| haiku-llm_isnad_whole | haiku-llm_isnad_chain | 50 | precision | 0.997 | 1.000 | -0.003 | [-0.012, 0.000] |
| haiku-llm_isnad_whole | haiku-llm_isnad_chain | 50 | recall | 0.899 | 0.850 | 0.049 | [0.003, 0.097] |
| haiku-llm_isnad_whole | haiku-llm_isnad_chain | 50 | f1 | 0.945 | 0.919 | 0.026 | [0.000, 0.056] |
