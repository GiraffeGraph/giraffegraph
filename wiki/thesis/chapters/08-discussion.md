# 8 Discussion

## 8.1 Where the check belongs

The project began with the claim that tying each fact to a source quotation keeps unsupported facts out of a graph. In our runs the quotation was not where the model departed from the text. Every quotation that reached the check was found in its segment. What differed was the relation between the quotation and the extracted value: the model quoted "from his father" and wrote a name, or quoted a name in Arabic and wrote it in Latin letters.

A quotation check answers "did the model point at real text". The value-in-quotation check answers "is what the model wrote in the text it pointed at". Only the second question separated matched from unmatched proposals in our data. Both checks cost a string comparison.

The check also flags values a reviewer would accept. Of the 155 flagged names, 33 match the reference (21%), and 13 of those differ from the quotation only in grammatical case. This is why the engine sends a flagged candidate to review instead of rejecting it. A rule that recognises case endings as an allowed change would accept those 13 automatically and record that it did so; it would not remove the other 20.

The check does not tell an invented narrator from a transformed one. Most flagged names are the right person in another script or case, and most kinship cases are inferences the text supports. What the check establishes is narrower and still useful: the model changed something and did not say so. For a graph whose facts must be traceable to the wording of a source, that is the event that needs a decision.

## 8.2 What the model is needed for

Under loose matching a rule-based parser with no model call reaches F1 0.923, a model with only a schema 0.890, and a model with descriptions and hints 0.956.

The comparison between parser and schema-only model depends on the matching rule. The parser finds the names but returns spans that run long, so it does well under loose matching and badly under strict matching (0.633). The schema-only model returns clean names, so it does better under strict matching (0.826) and gets more whole chains right, but it adds and alters names. Which is preferable depends on whether a later step can trim spans or must correct names.

A schema is not domain knowledge. The schema-only model knew the types and still treated the Prophet as a narrator and transliterated names. A few sentences of description and instruction in the schema template removed almost all unmatched proposals. In this task the instructions changed the result more than any check did. We did not test instructions without a schema.

The model with hints is above the parser by 0.034 F1 under loose matching, mostly through recall on hadiths with parallel chains, and by much more under strict matching. Whether that is worth a model call per hadith depends on the use. For a first pass over a large corpus the parser costs nothing. The engine supports both through the same pipeline.

When the prompt is good the checks find little. They are what protects the graph when the prompt, the model or the configuration is not good. The failed run with a second model is an example: the output was malformed in most calls, and nothing malformed was committed.

## 8.3 Confidence

With this model and prompt, the model's confidence was a poor basis for routing. At a comparable share of mentions sent to review it found fewer than half as many unmatched mentions as the check (Table 7.8). The original code sent candidates to review by a confidence threshold alone. The current code keeps the threshold and adds the checks.

## 8.4 The cost of a strict commit rule

The checks keep altered names out of the accepted output, and the commit rule keeps a whole hadith out of the graph while any of its candidates waits for review. In the schema-only condition that leaves 110 of 300 hadiths uncommitted and the graph at recall 0.582 until a person acts. With a good prompt the cost almost disappears (6 of 300). The design moves work to the reviewer; it does not remove it, and we have not measured how long that work takes.

## 8.5 Threats to validity

**Reference labels.** The Ifta labels are platform markup restructured by a third party, with inconsistencies we observed and did not repair. A system is sometimes penalised for extracting a narrator the platform did not mark. Two label sets produced in different ways agree closely on the hadiths they share (F1 0.959), which suggests the labels are adequate for comparing conditions. We do not know how independent the two sets are, and absolute values should not be read as accuracy.

**Matching rule.** Loose matching accepts a mention that contains extra words, and it treats the same change of case as a match or a mismatch depending on the length of the name. Conclusions that hold under one rule and not the other are stated with the rule.

**What "wrong" means.** An unmatched proposal is not necessarily a false statement about the hadith. More than half of the unmatched proposals of the schema-only model name the right narrator in another script.

**One domain.** That the value-in-quotation check flags most unmatched proposals (122 of 145) is a property of this task and this prompt, in which the model's main departure from the text was to rewrite the name. We repeated the check outside hadith, on 300 abstracts of the BC5CDR corpus, which carries human annotations of chemical and disease mentions [@li2016bc5cdr], with the same model and a schema-only prompt. There the check flagged 3.9% of 2,269 proposals, and these held 53 of the 303 proposals that did not match the annotations; the other 250 were verbatim copies of spans the annotators had not labelled. With the same number of items sent to review, the model's confidence found 58 unmatched proposals and the check 53. The check establishes that a value comes from the quoted text. It does not establish that the right text was selected.

**One model, one effort setting, one run.** All usable results come from Claude Haiku 5.5 at low effort, with each condition run once. The second model failed for a reason we attribute to our own wire format and effort setting without having tested that attribution.

**In-memory backend.** The experiments ran on the in-memory backend. The same pipeline is covered on PostgreSQL and Neo4j by twelve tests, not by the experiments.

**Tuning.** The rule-based segmenter was tuned on the 50 pilot hadiths. The six-book set excludes them, so the main results are not affected, but the parser's rules reflect the collections seen in the pilot, which did not include Bukhari.

**Memorisation.** The hadiths are well known and are likely to be in the model's training data. We found one flagged name that the text does not contain in any form, which is too little to say whether the model recalls chains. We did not test this with altered names.

**No human in the measured loop.** The review queue, the decision record and the commit guards are covered by tests, but the evaluation ran without a reviewer. The claim that the engine reduces errors with a person in the loop is not measured here.

**Schema drift.** The title names schema drift. With Haiku 5.5 we observed almost none, and what we observed with the second model came from a failed configuration. The engine's handling of drift is tested; its frequency in normal use is not established.

**Authorship of the code and analysis.** Most of the code on the evaluated branch, the analysis scripts and a first draft of this text were produced with AI coding assistants under the authors' direction. The measurements are reproducible from the cached model responses and the scripts. The authors remain responsible for every statement.

## 8.6 Limits of the system

A narrator node is identified by its written name. Section 7.10 shows the size of the resulting error in the reference labels: a graph keyed this way merges different people who share a short name and splits one person across spellings. Any analysis of the narrator network built on the current graph inherits this.

Chains that begin after the report text has started are not segmented, and joined co-narrators stay in one mention. Both reduce the recall of the conditions that use the segmenter.

No check covers category errors such as the Prophet named as a narrator. The checks apply to candidates that come from an extraction call, not to candidates entered by hand. Acceptance records are computed from stored decisions and validation results when requested. Undo of a committed run is not implemented.
