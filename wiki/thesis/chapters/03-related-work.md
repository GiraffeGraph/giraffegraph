# 3 Related work

This chapter reviews work on hadith data, on the extraction and identification of narrators, on hadith knowledge graphs, and on the evaluation of knowledge graphs built with large language models (LLMs). For each work we ask who produced the reference, at what level quality was measured, and whether annotator agreement was reported.

The works were found in October 2026 by web search and by reading primary sources. The search was not systematic. We read the full text except in three cases: the thesis of Oumer is not openly accessible, so its figures come from the author's model repository; of Gao et al. we read Sections 1 to 7.1; of Raja, Sections 6 to 8. For the 2023 SemanticHadith paper and the construction frameworks named in Section 3.5 we rely on bibliographic records and report no figures.

## 3.1 Hadith corpora and labelled resources

**Sanadset 650K** has 650,986 records and is described as covering 926 books [@mghari2022sanadset]; the file we downloaded has 956 distinct book values [@internal-data-manifest]. The text was collected by web scraping, and its components were separated and the narrators tagged "with the help of regular expressions and text matching". The data paper reports no accuracy measurement and no human check. A score against these tags measures agreement with rules. The licence is stated as cc0-1.0 on the dataset card of the Hugging Face mirror [@sanadset_hf] and as "CC BY 4.0" on the Mendeley Data record of the original deposit, both read on 12 October 2026.

**The Ifta Sunnah data family** consists of three Kaggle releases of one corpus, which its curator extracted from the Ifta' Sunnah digital library by crawling and parsing [@internal-data-manifest]. The original corpus has 33 books, 276,347 hadiths and 20,957 narrator profiles. The entities and relations release adds narrator spans and transmission relations, with a fixed split of 223,478 hadiths (156,434 training, 33,521 validation, 33,523 test). The graph release has 257,840 hadiths in which every chain step is linked to a narrator identifier. The labels are the platform's markup, restructured by a third party; the source does not say how the platform produced it and reports no annotator agreement. On 12 October 2026 the Kaggle licence field was stated as "CC BY-SA 4.0" for the original corpus, "Unknown" for the entities release and "CC BY-NC-SA 3.0 IGO" for the graph release; the documentation asks users to follow the terms of the platform.

**AR-Sanad 280K** provides 279,625 artificial chains for training and validation and a test set of 27,056 real chains from the six canonical collections, covering 6,378 narrators, each name with a narrator identifier [@mahmoud2022arsanad]. According to the paper, a group of 30 experts carried out narrator identification on the source website. The test set contains separated names and no hadith text, so it can test identity but not extraction. The repository has no licence file; the article is listed with a CC BY 4.0 licence URL, and the repository does not say whether this extends to the data [@internal-data-manifest].

## 3.2 Isnad and narrator extraction

Altammami et al. separate chain from body with n-gram models [@altammami2019text]. The authors labelled 240 hadiths, 40 from each of the six collections, and measured per hadith whether the split point was correct. The bi-gram model was correct on 222 of 240 (92.5%) and the tri-gram model on 48%. Reported error types include parallel chains.

Muther and Smith detect chain spans in long, unpunctuated classical texts [@muther2020tracing]. Their corpus has 50 texts, 907,110 tokens and 3,071 chains, annotated by experts in Islamic history who corrected model suggestions. Agreement was measured with 5 annotators on 2,000 lines: Krippendorff's alpha was 0.84 and pairwise Cohen's kappa ranged from 0.71 to 0.96. Annotators agreed exactly on the start of a chain in 70% of cases and on its end in 53%. A conditional random field model reached F1 0.254 under strict span matching and 0.835 under partial matching. Two points matter for us: the matching criterion changes the score by a large factor, and even experts disagree on where a chain ends.

Oumer fine-tunes the models CAMeLBERT-CA, AraT5 and AraBART on the Ifta entities and relations data [@oumer2025relation]. The author's model repository reports, on 33,523 test hadiths, narrator F1 0.98 and relation-pair F1 0.95 for CAMeLBERT-CA; narrator F1 0.97, pair F1 0.95 and F1 0.93 for triples that include the chain number for AraT5; and triple F1 0.48 for AraBART. Pairs and triples are scored by exact match against relations derived from the platform markup. Separation between books in the split is not stated. We found no study that measures LLM-based extraction on this data.

## 3.3 Narrator identity resolution

Mahmoud et al. treat identification as classification of each name mention into one of 18,298 narrators [@mahmoud2022arsanad]. On artificial validation chains the model reaches micro-F1 92.9 (on a scale of 0 to 100) with a chain error rate of 30.2%, the percentage of chains with at least one wrongly identified narrator. On the real test chains micro-F1 is 83.5, macro-F1 78.8 and the chain error rate 60.6%, ranging by collection from 48.7% (al-Tirmidhi) to 70.5% (al-Nasai). The correct narrator is among the top three candidates in 95.3% of cases and among the top five in 97.1%. In the validation set, 26% of 3,669 instances of common names such as Muhammad and Abdullah were identified correctly. A mention-level score thus hides failure at chain level, and a short ranked list contains the correct narrator more often than the first answer does.

Wirahman links the 185,216 narrator name variants of Sanadset to biographical databases without a labelled reference [@wirahman2026linking]. Of the variants, 94,628 (51.1%) were linked and 88,343 (47.7%) had no candidate. Accuracy was not measured and thresholds were chosen by inspection. The author leaves 1,000 to 2,000 expert-confirmed links to future work. The two highest-degree nodes of the resulting graph are "his father" (7,612) and "my father" (5,550), which shows the effect of merging unnamed narrators by their surface string.

## 3.4 Hadith knowledge graphs and LLM-based structuring

SemanticHadith is an ontology-driven knowledge graph for the hadith corpus [@kamran2023semantichadith]. Its 2026 extension, version 2.0.1, builds a graph from the 34,458 hadiths of the six collections with 303,869 entities, 6,822 persons and 47,496 similarity links [@kamran2026semantic]. Entities in the text are extracted by a named entity recogniser (micro-F1 97%, macro-F1 85%) and mapped to ontology instances through a name dictionary; unmatched entities are dropped. The ontology has classes for a narrator chain and for its segments. For the graph, three domain experts checked 100 random samples from each collection and no discrepancy was reported; no agreement statistic is given. The work uses no LLM, records no decision per fact and has no check against a source quotation. Persons who share a name are flagged for manual inspection or left out, and a framework that presents ambiguous names to an expert with a candidate list is named as future work.

Rezwan is a corpus of narrations processed with LLMs [@asgari2025rezwan]. Six domain experts scored 1,213 random narrations from 0 to 10 per dimension, without an agreement statistic. Chain and body separation received 9.30 (9.33 in the abstract). The 5.85% of narrations whose error rate exceeded 60% were excluded from the mean.

Çinici builds a biographical dataset with 21 variables for 271 scholars from one volume of a classical biographical work, using retrieval with Gemini 2.5 Flash [@cinici2026hadis]. The author compared the first 100 records with the original and states that accuracy was high, without a figure. The task is biography, not chains, and there is no graph or approval step.

## 3.5 LLM-based knowledge graph construction and its evaluation

General frameworks such as Extract, Define, Canonicalize, KGGen and iText2KG build graphs from text with LLMs [@zhang2024edc; @mo2025kggen; @lavie2024itext2kg].

Text2KGBench is a benchmark for ontology-driven extraction with three metric families: precision, recall and F1 against reference triples; conformance to the ontology; and a hallucination measure that tests whether subject and object occur in the sentence or the ontology [@mihindukulasooriya2023text2kgbench]. On its Wikidata-TekGen part, Vicuna-13B obtained precision 0.38, recall 0.34 and F1 0.35, ontology conformance 0.83 and subject hallucination 0.17.

Gao et al. estimate the accuracy of a whole graph from a sample [@gao2019efficient]. On their MOVIE graph, a random sample of 174 triples from 174 entities took 3.53 hours, while two-stage cluster sampling of 178 triples from 24 entities took 1.4 hours, with a margin of error of about 5% in both. The estimate is unbiased and comes with a confidence interval.

## 3.6 Reviews of the field

Haque and Islam assess 32 records on six dimensions: corpus realism, evaluation design, transfer, reproducibility, expert involvement and scholarly use [@haque2026hadith]. Among the 8 rows of their assessment table, expert involvement is rated full only for Rezwan. They find a benchmark culture limited to the six collections, a gap between synthetic and real data, metrics that cannot be compared, and sparse expert validation.

Mhamedi et al. review 57 studies [@mhamedi2026computational]. In their table of narrator extraction, reported F1 values range from 33% to 99.63%, test sets have 102 to 200 hadiths, and accuracy, precision and F1 are mixed.

## 3.7 Positioning

| Work | What it provides | How quality was measured | What is missing for our purpose |
|---|---|---|---|
| Sanadset 650K [@mghari2022sanadset] | 650,986 records with tagged narrators | Not measured; tags come from regular expressions | A checked reference; narrator identity |
| Ifta data family [@internal-data-manifest] | Narrator spans, relations and identifiers | No agreement figure; origin of markup not described | Licence confirmation; an LLM-based study |
| AR-Sanad 280K [@mahmoud2022arsanad] | 27,056 real chains with identifiers; classifier | Micro and macro F1, chain error rate, top-k | Hadith text, so no extraction test |
| Altammami et al. [@altammami2019text] | Chain and body segmentation | Per-hadith accuracy on 240 hadiths | Narrator-level output |
| Muther and Smith [@muther2020tracing] | Expert-annotated corpus; span detection | Strict and partial span F1; agreement of 5 annotators | Narrator names and relations |
| Oumer [@oumer2025relation] | Fine-tuned narrator and relation extraction | Exact match on 33,523 test hadiths (author's model repository) | A setting without training data; decision records |
| Wirahman [@wirahman2026linking] | Automatic linking of 185,216 name variants | Not measured | Labelled reference; human confirmation |
| SemanticHadith 2.0.1 [@kamran2026semantic] | Ontology and graph of 34,458 hadiths | Recogniser F1; expert check of samples | Decision per fact; source quotations |
| Rezwan [@asgari2025rezwan] | LLM-processed corpus | Expert scores from 0 to 10 | Count-based precision and recall |
| Çinici [@cinici2026hadis] | LLM-built biographical records | One author, 100 records, no figure | Measured error classes; approval step |
| Text2KGBench [@mihindukulasooriya2023text2kgbench] | Benchmark and three metric families | Reference triples, ontology conformance, text presence | Value-in-quotation test; human step |
| Gao et al. [@gao2019efficient] | Sampling design for graph accuracy | Unbiased estimate with confidence interval | Not applied here; a candidate for estimating accuracy beyond the labelled sample |

Much of what such a project might claim already exists. A graph of the six collections has been published, and its ontology models chain segments as classes. Narrator linking has labelled real data and a measured baseline. Fine-tuned models extract narrators and transmission relations with F1 values of 0.95 and above against platform labels, according to the author's model repository. An expert-annotated corpus with agreement figures exists for chain spans, and a test for presence in the text is an established metric. We therefore do not claim a new schema, a new representation of the transmission event, or higher extraction accuracy.

Three things we did not find in the works we reviewed: a study that measures the separate contribution of each validation step between an LLM and a graph; a check that the extracted value occurs in the model's own quotation, reported as its own error class; and a record of who or what accepted each fact. These are the subject of this thesis: the system places deterministic checks and a human review queue between the model and the graph, counts what each step catches, and stores an acceptance record for every fact. Because the search was not systematic, "not found" does not mean "does not exist".

<!-- keys: mghari2022sanadset, internal-data-manifest, sanadset_hf, mahmoud2022arsanad, altammami2019text, muther2020tracing, oumer2025relation, wirahman2026linking, kamran2023semantichadith, kamran2026semantic, asgari2025rezwan, cinici2026hadis, zhang2024edc, mo2025kggen, lavie2024itext2kg, mihindukulasooriya2023text2kgbench, gao2019efficient, haque2026hadith, mhamedi2026computational -->
