# 9 Conclusion and future work

We built an engine that places deterministic checks and a recorded acceptance between a language model and a knowledge graph, and we measured what that placement achieves on hadith narrator chains with one model and platform-derived labels.

The measurements support four statements within those limits. A check on the relation between the model's quotation and the value it extracted flags most proposals of a weakly instructed model that do not match the reference, with no extra model call, while a check on the quotation alone flags none. Adding descriptions and domain instructions to a schema-only prompt improves extraction more than any check does. The model's confidence finds far fewer of those proposals than the check at a comparable review budget. And a written name is not a narrator's identity: one chain position in ten is ambiguous at the level of the string.

The measurements do not show how the engine performs with a reviewer, how the results change with other models, how often schema drift occurs, or how accurate the output is against labels produced by independent human annotators.

## 9.1 Plan for Senior Design Project II

1. **Human-labelled reference.** Two annotators label the 50 pilot hadiths with the existing sheet and guideline, we measure agreement and time per hadith, revise the guideline, and then label a sample of the six-book set. The number of hadiths follows from the measured time.
2. **Reviewer in the loop.** A reviewer who did not label a hadith decides its review items in the dashboard. We report precision and recall after review, rejection rate per reason code and seconds per decision from the decision record.
3. **Narrator identity.** Link mentions to the narrator catalogue of the Ifta data, present ranked candidates to the reviewer for ambiguous names, and report wrong merges separately from missed merges.
4. **Transformation rules and a category rule.** Accept changes of grammatical case automatically and record the rule that accepted them, which would clear 13 of the 33 matched names the value check flagged. Add a rule for names that are not narrators, such as the Prophet.
5. **Models and wire format.** Rename the fields of the property list, then repeat the evaluation with at least two more models, including an open one, with repeated runs and with altered names to test memorisation.
6. **Relations and chains.** Score `NARRATED_FROM` links and whole chains, segment chains that start after the report text, and test per-chain calls on hadiths with several chains.
7. **Questions over the graph.** Build a small set of structural, path and decision questions and compare answers from the graph with answers from text retrieval.

## 9.2 Beyond hadith

The checks, the review queue, the decision record and the relation identity work on any schema, and most hadith behaviour lives in a segmentation strategy, a template and a provider. Three places in the engine still name the case study (Section 5.1). The claim that the same structure serves another domain is untested, and a second case study is the way to test it.
