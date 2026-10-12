# Run comparison

Scores are agreement with the supplied reference. Against rule-generated (silver) labels they compare systems with each other and are not accuracy.

| run | condition | model | effort | hadiths | M1 F1 | M2 precision [95% CI] | M2 recall [95% CI] | M2 F1 [95% CI] | exact-chain rate | validated M2 precision | validated M2 recall | validated M2 F1 | any-gate precision | any-gate recall | confidence AUC | review candidates per hadith | share of hadiths without review items | USD per 1,000 hadiths | tokens per hadith | failed calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rule | rule | n/a | n/a | 36 | 0.655 | 0.979 [0.954, 1.000] | 0.884 [0.824, 0.935] | 0.929 [0.894, 0.959] | 0.556 | 0.979 | 0.884 | 0.929 | n/a | 0.000 | 0.500 | 0.000 | 1.000 | 0.0000 | 0.0 | 0 |
| haiku-llm_schema_whole | llm_schema_whole | claude-haiku-5-5 | low | 36 | 0.792 | 0.894 [0.806, 0.968] | 0.828 [0.737, 0.903] | 0.860 [0.771, 0.931] | 0.444 | 0.983 | 0.823 | 0.896 | 0.947 | 0.857 | 0.585 | 2.083 | 0.639 | 1.9068 | 6302.7 | 0 |
| haiku-llm_isnad_whole | llm_isnad_whole | claude-haiku-5-5 | low | 36 | 0.901 | 0.995 [0.984, 1.000] | 0.916 [0.855, 0.966] | 0.954 [0.914, 0.983] | 0.694 | 0.995 | 0.916 | 0.954 | n/a | 0.000 | 0.437 | 0.000 | 1.000 | 2.2878 | 7326.2 | 0 |
| sonnet-llm_schema_whole | llm_schema_whole | claude-sonnet-5-5 | low | 36 | 0.595 | 0.966 [0.933, 0.992] | 0.530 [0.378, 0.670] | 0.685 [0.543, 0.793] | 0.306 | 0.991 | 0.493 | 0.658 | 0.273 | 0.750 | 0.977 | 0.583 | 0.389 | 19.8259 | 4473.1 | 0 |
| sonnet-llm_isnad_whole | llm_isnad_whole | claude-sonnet-5-5 | low | 36 | 0.330 | 0.981 [0.927, 1.000] | 0.237 [0.122, 0.369] | 0.382 [0.216, 0.539] | 0.194 | 1.000 | 0.186 | 0.314 | 0.083 | 1.000 | 1.000 | 0.000 | 0.167 | 14.4760 | 4195.6 | 0 |

## Paired differences (M2, proposed output)

Difference = first run minus second run. Intervals: paired percentile bootstrap over hadiths, 2000 resamples, seed 0.

| first run | second run | hadiths | metric | first value | second value | difference | 95% CI |
|---|---|---|---|---|---|---|---|
| rule | haiku-llm_schema_whole | 36 | precision | 0.979 | 0.894 | 0.085 | [0.007, 0.181] |
| rule | haiku-llm_schema_whole | 36 | recall | 0.884 | 0.828 | 0.056 | [-0.042, 0.155] |
| rule | haiku-llm_schema_whole | 36 | f1 | 0.929 | 0.860 | 0.069 | [-0.009, 0.158] |
| rule | haiku-llm_isnad_whole | 36 | precision | 0.979 | 0.995 | -0.016 | [-0.040, 0.000] |
| rule | haiku-llm_isnad_whole | 36 | recall | 0.884 | 0.916 | -0.033 | [-0.113, 0.044] |
| rule | haiku-llm_isnad_whole | 36 | f1 | 0.929 | 0.954 | -0.025 | [-0.070, 0.019] |
| rule | sonnet-llm_schema_whole | 36 | precision | 0.979 | 0.966 | 0.013 | [-0.025, 0.051] |
| rule | sonnet-llm_schema_whole | 36 | recall | 0.884 | 0.530 | 0.353 | [0.198, 0.515] |
| rule | sonnet-llm_schema_whole | 36 | f1 | 0.929 | 0.685 | 0.244 | [0.133, 0.389] |
| rule | sonnet-llm_isnad_whole | 36 | precision | 0.979 | 0.981 | -0.001 | [-0.041, 0.062] |
| rule | sonnet-llm_isnad_whole | 36 | recall | 0.884 | 0.237 | 0.647 | [0.518, 0.757] |
| rule | sonnet-llm_isnad_whole | 36 | f1 | 0.929 | 0.382 | 0.547 | [0.393, 0.709] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 36 | precision | 0.894 | 0.995 | -0.100 | [-0.193, -0.029] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 36 | recall | 0.828 | 0.916 | -0.088 | [-0.172, -0.023] |
| haiku-llm_schema_whole | haiku-llm_isnad_whole | 36 | f1 | 0.860 | 0.954 | -0.094 | [-0.181, -0.028] |
| haiku-llm_schema_whole | sonnet-llm_schema_whole | 36 | precision | 0.894 | 0.966 | -0.072 | [-0.167, 0.003] |
| haiku-llm_schema_whole | sonnet-llm_schema_whole | 36 | recall | 0.828 | 0.530 | 0.298 | [0.123, 0.473] |
| haiku-llm_schema_whole | sonnet-llm_schema_whole | 36 | f1 | 0.860 | 0.685 | 0.175 | [0.029, 0.334] |
| haiku-llm_schema_whole | sonnet-llm_isnad_whole | 36 | precision | 0.894 | 0.981 | -0.086 | [-0.187, 0.004] |
| haiku-llm_schema_whole | sonnet-llm_isnad_whole | 36 | recall | 0.828 | 0.237 | 0.591 | [0.445, 0.726] |
| haiku-llm_schema_whole | sonnet-llm_isnad_whole | 36 | f1 | 0.860 | 0.382 | 0.478 | [0.314, 0.653] |
| haiku-llm_isnad_whole | sonnet-llm_schema_whole | 36 | precision | 0.995 | 0.966 | 0.029 | [-0.002, 0.065] |
| haiku-llm_isnad_whole | sonnet-llm_schema_whole | 36 | recall | 0.916 | 0.530 | 0.386 | [0.233, 0.554] |
| haiku-llm_isnad_whole | sonnet-llm_schema_whole | 36 | f1 | 0.954 | 0.685 | 0.269 | [0.153, 0.415] |
| haiku-llm_isnad_whole | sonnet-llm_isnad_whole | 36 | precision | 0.995 | 0.981 | 0.014 | [-0.015, 0.070] |
| haiku-llm_isnad_whole | sonnet-llm_isnad_whole | 36 | recall | 0.916 | 0.237 | 0.679 | [0.541, 0.805] |
| haiku-llm_isnad_whole | sonnet-llm_isnad_whole | 36 | f1 | 0.954 | 0.382 | 0.572 | [0.414, 0.737] |
| sonnet-llm_schema_whole | sonnet-llm_isnad_whole | 36 | precision | 0.966 | 0.981 | -0.015 | [-0.058, 0.050] |
| sonnet-llm_schema_whole | sonnet-llm_isnad_whole | 36 | recall | 0.530 | 0.237 | 0.293 | [0.094, 0.487] |
| sonnet-llm_schema_whole | sonnet-llm_isnad_whole | 36 | f1 | 0.685 | 0.382 | 0.303 | [0.089, 0.512] |
