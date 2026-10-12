# 2 Background

This chapter introduces the domain of the case study and the concepts that the rest of the thesis depends on.

## 2.1 Hadith, isnad and matn

A hadith is a report with two parts. The isnad (إسناد) is the chain of narrators through whom the report was transmitted, and the matn (متن) is the reported text itself. Some sources and dataset names say sanad for the same chain. From here on we write "chain" for isnad and "report text" for matn.

A chain is written starting from the compiler of a collection and runs back to the Prophet Muhammad or to one of his Companions, the first generation of narrators. Each narrator named in the chain received the report from the narrator named after him. For example, the chain labelled in the Sanadset corpus for hadith 693 of al-Nasai's collection has five narrators: Muhammad ibn Mansur, Sufyan, al-Zuhri, Sa'id and Abu Hurayra [@mghari2022sanadset].

Narrators are joined by transmission formulas (sigha, صيغة). Frequent ones are haddathana ("he narrated to us"), akhbarana ("he informed us"), sami'tu ("I heard") and 'an (عن, "from"). The formula encodes how the report passed from one narrator to the next, and 'an leaves this open. A graph model therefore keeps the formula as a property of the relation between two narrators.

A hadith can reach a compiler through more than one chain. When such parallel chains are written one after another, the letter ح, called tahwil (تحويل), marks the switch to a new chain; we call it the chain-switch marker. In a sample of 300 hadiths that we drew from the six canonical collections, 74 have more than one chain according to the source labels [@internal-data-manifest]. If the chains of one hadith are not kept apart, the graph gains transmission paths that no chain states.

Narrator identity is the difficult part. The same person can appear as "Sufyan ibn Uyayna", "Ibn Uyayna" or "Sufyan", and different people share the same short form. In the chain above, the text does not say which Sufyan or which Sa'id is meant. Some chains name nobody, as in "from his father, from his grandfather".

In the 27,056 real chains of the AR-Sanad test set, where every name carries a narrator identifier, 815 of 15,301 distinct name strings map to more than one identifier. The name Muhammad maps to 27 narrators and the expression "his father" to 421 [@mahmoud2022arsanad; @internal-data-manifest].

Identity matters because a chain is assessed through its narrators. The biographical literature on narrators, called rijal (رجال), records who each narrator was and how reliable scholars judged that narrator to be; works ordered by generation are one part of it [@aslan2017tabakat]. The datasets we use carry fields from this tradition, such as a generation class and reliability grades attributed to Ibn Hajar and al-Dhahabi [@internal-data-manifest]. Merging two different narrators into one node can change the verdict on a chain, while a missed merge only leaves a duplicate node. The text alone cannot settle such cases; they need an authority list of narrators and an expert.

The six canonical collections (in Turkish, Kütüb-i Sitte) are those of al-Bukhari, Muslim, Abu Dawud, al-Tirmidhi, al-Nasai and Ibn Majah. A critical review lists the narrow focus of benchmarks on these six books among the weaknesses of the field [@haque2026hadith].

## 2.2 Knowledge graphs and schema-constrained extraction

By a knowledge graph we mean a set of typed nodes connected by typed relations, where nodes and relations carry properties; surveys of the concept and of domain-specific construction are [@hogan2021knowledge; @kejriwal2019domain]. A schema fixes which node types, relation types and properties are allowed. A schema for narrator chains needs little: a narrator node, a hadith node, and a "narrated from" relation that carries the hadith reference, the chain number, the position in the chain and the transmission formula.

A graph suits this domain because the questions asked about chains are path and network questions. The narrator that two chains have in common is not written in any single passage; it has to be found by traversing both chains.

Large language models (LLMs) can build such graphs from text [@ye2022generative; @pan2024unifying]. Two strategies exist. In schema-first extraction the model receives the allowed types and an output contract, and its output is validated against the schema. In the second strategy the model extracts freely and a later step defines and canonicalises what it produced, as in the Extract, Define, Canonicalize framework [@zhang2024edc]. This needs no schema in advance. In our assessment the cost is a second pass, and canonicalisation is one more step in which errors can enter.

## 2.3 Two failure modes: unsupported facts and schema drift

The title of this project names two failure modes. Schema drift means that the output uses types or properties that the schema does not define. The same relation may be called HEARD_FROM in one batch and TOLD or narratedBy in the next. At type level the model writes an undefined node or relation type. At property level it writes an undefined property key or a value outside the allowed list.

Hallucination is the common name for generated content that the source does not support. Ji et al. survey it for natural language generation [@ji2023survey]. That survey does not treat knowledge graph extraction as a task, so its figures do not transfer to our setting. We use the plainer term "unsupported fact".

A single "hallucination rate" is too coarse for extraction, because at least three different things are counted under it:

- **Value not in the source.** The extracted value, for example a narrator name, does not occur in the source text at all.
- **Value not in the model's own quotation.** The model quotes a passage that does occur in the source, but the value it reports does not occur in that passage. This covers real errors and also silent normalisation, for example a name returned in the nominative when the text has it in the accusative. In the second case the model has made a decision that is recorded nowhere.
- **Category error.** The value occurs in the text and the type exists in the schema, but the thing is not of that type, for example the Prophet extracted as a narrator.

Different checks catch the three classes, so Section 7.6 reports them separately. Text2KGBench illustrates why presence in the text is not the same as correctness. Its hallucination measure tests whether the subject or object of a triple can be found in the sentence or the ontology. With Vicuna-13B on the Wikidata-TekGen part of the benchmark, subject hallucination was 0.17 while precision against the reference triples was 0.38 [@mihindukulasooriya2023text2kgbench].

## 2.4 Grounding and attribution

Grounding ties each output to evidence in the source. Two families of methods are relevant.

Quotation-based checks ask the model to return a verbatim quotation with every candidate fact and then apply string tests: the quotation occurs in the source segment, and the extracted value occurs in the quotation. These tests are deterministic, cost almost nothing and can run on every candidate. They can show that something is wrong; they cannot show that a candidate is right.

Claim-level methods come from the evaluation of free text. FActScore splits a long answer into atomic claims and verifies each one, and SAFE addresses long-form factuality in a similar way [@min2023factscore; @wei2024longform]. Rashkin et al. define how to measure whether generated text is attributable to identified sources [@rashkin2023measuring]. SummaC and AlignScore score the consistency of a claim with a text using entailment or alignment models [@laban2022summac; @zha2023alignscore]. RARR and Chain-of-Verification use further model calls to revise or verify an output [@gao2023rarr; @dhuliawala2024chainofverification]. These methods work at the level of sentences or claims, and the automated ones need at least one model call per item. For a short structured value such as a narrator name, string tests are the cheaper first step. They cannot judge meaning, which is why a human step follows them.

## 2.5 Human-in-the-loop review and confidence as a routing signal

In a human-in-the-loop design a person decides on candidate facts before they are written to the graph. Expert time is the scarce resource, so the system needs a routing signal that selects the candidates a person must see.

The obvious signal is the confidence score that the model reports for its own output, compared with a threshold. Whether such self-reported confidence follows correctness is studied as a calibration problem [@kadavath2022language; @xiong2024can]. The hadith domain advises caution even for a trained classifier: Mahmoud et al. report that 12.9% of the wrong predictions of their narrator identification model were made with a confidence above 0.90 [@mahmoud2022arsanad]. The essay discussed in Section 2.6 argues that a model's errors look like its correct output on the surface [@internal-cache-ledger].

Two alternatives exist. Deterministic risk flags, such as a failed test from Section 2.4, can route a candidate to review without using the model's opinion of itself. Conformal prediction offers distribution-free error guarantees when a calibration set is available [@angelopoulos2021gentle]. Whatever the signal, two routing policies are comparable only at the same coverage; Raja compares the error rates of selective serving in this way [@raja2026grading]. Section 7.7 compares the confidence signal with a check at comparable shares of mentions sent to review.

## 2.6 Derivable facts and decisions

The last concept comes from an internal essay of the project, "The Cache and the Ledger" [@internal-cache-ledger]. Its principle is: a fact that can be derived from a source of truth is a cache and should be regenerated, not stored; a fact that cannot be derived is a decision and should be stored once.

The essay's example is a documentation page. "The controller lives in this file" can be recovered from the code. "We considered another design and rejected it" cannot, because the code does not contain the option that was not taken.

The essay supports the principle with counts reproduced by its own scripts. Among 733 Python Enhancement Proposals, 27 of 42 forward "replaces" links were reciprocated by a back-link (64%), although a linter checks the header. It concludes that stored derivable values decay, while append-only decision records whose back-links are derived avoid the problem by construction. It also names limits: decisions have no built-in checksum, and an automated check can flag a problem but cannot certify that a statement is true.

Applied to extraction: a candidate fact that a parser or an LLM extracts from a text is derivable, because it can be extracted again from the same text, although an LLM does not return identical output each time. An acceptance, a rejection, a correction or a merge of two narrators made by a person is not derivable from any source and must be recorded once, with who decided and when. This is why the system keeps a decision trail for every fact.

The principle also explains the second class in Section 2.3. A value that a model silently normalised is neither a plain derivation from the text nor a recorded human decision. A named rule or a person should confirm it before it is accepted.

<!-- keys: mghari2022sanadset, internal-data-manifest, mahmoud2022arsanad, aslan2017tabakat, haque2026hadith, hogan2021knowledge, kejriwal2019domain, ye2022generative, pan2024unifying, zhang2024edc, ji2023survey, mihindukulasooriya2023text2kgbench, min2023factscore, wei2024longform, rashkin2023measuring, laban2022summac, zha2023alignscore, gao2023rarr, dhuliawala2024chainofverification, kadavath2022language, xiong2024can, internal-cache-ledger, angelopoulos2021gentle, raja2026grading -->
