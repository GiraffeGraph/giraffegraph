# Ekip okuma listesi (27 makale): okuma notları

Bu dosya, Alperen Ulukaya'nın paylaştığı 27 makalelik listenin ve listedeki bir derlemenin işaret ettiği iki
sistemin (ODKE+, KARMA) okuma notlarıdır. Okuma 2026-10-15'te alt ajanlarla yapıldı: her ajan PDF'leri
sayfa sayfa okudu, her makaleyi projenin beş boşluk iddiasına (G1–G5) karşı sınadı ve kanıtı sayfa
numarasıyla verdi. PDF'ler depoda değildir (ekibin OneDrive klasörü; ODKE+ ve KARMA arXiv'den).
Notlar İngilizce bırakıldı; sentez ve kararlar `wiki/evaluation/related-work.md` içindedir.

Boşluklar:

- G1: LLM ile graf arasındaki her doğrulama adımının ayrı katkısını ölçen çalışma (kontrol ablation'ı)
- G2: çıkarılan değerin modelin kendi alıntısında geçtiğini sınayan ve bunu ayrı hata sınıfı sayan kontrol
- G3: her olgu için kimin ya da neyin kabul ettiğinin kaydı
- G4: insan kimlik kararının saklanıp yeniden kullanılması, kapsamının çelişkiden türetilmesi
- G5: incelemeye yönlendirmede kontrol tabanlı sinyalin çıkarıcı modelin güven skoruyla karşılaştırılması

Sayfa numaraları PDF sayfasıdır; aksi notta belirtilir. Künyeler `extraction_eval_precedents.bib` içindedir.


---

# Grup 1

## Group 1 — KG surveys (Hogan 2021, Ji 2021/22, Bian 2025)

Page numbers = PDF page numbers (in Hogan they equal the printed "XX:n" page numbers).

## 01 Hogan et al., Knowledge Graphs

1. **Bib (as printed):** "Knowledge Graphs." Aidan Hogan, Eva Blomqvist, Michael Cochez, Claudia d'Amato, Gerard de Melo, Claudio Gutierrez, Sabrina Kirrane, José Emilio Labra Gayo, Roberto Navigli, Sebastian Neumaier, Axel-Cyrille Ngonga Ngomo, Axel Polleres, Sabbir M. Rashid, Anisa Rula, Lukas Schmelzeisen, Juan Sequeda, Steffen Staab, Antoine Zimmermann. *ACM Comput. Surv.*, Vol. X, No. X, Article XX, March 2021, 35 pages. The printed DOI is a placeholder (https://doi.org/0000001.0000001), so this PDF is a pre-publication copy (p1–2).
2. **What:** A tutorial paper on graph data models, querying, validation (shapes), context, deductive knowledge (ontologies, rules, DLs) and inductive knowledge (analytics, embeddings, GNNs, rule/axiom mining).
3. **LLM:** None.
4. **Validation:** Shapes graphs (SHACL, ShEx), which give cardinality and type constraints and "A graph is valid with respect to a shapes graph … iff every node that each shape targets conforms" (p9–10). Ontology axioms and rules for entailment and finding inconsistencies (p12–18). Embedding plausibility scores can assign confidence to edges "(possibly extracted from an external source)" (p22). Constraint-refined embeddings (p25). Rule support/confidence (p28). Identity: sameAs/differentFrom, UNA vs. NUNA, and keys/functional properties that let one "conclude that two or more terms refer to the same entity" (p13–14). No grounding check against source text.
5. **Human in the loop:** Only "Creation often involves … direct human input" (p7). No routing, no measured effort.
6. **Provenance:** Context as "scope of truth". Provenance example: "data about EID15 were taken from … the Ñam webpage on April 11th, 2020", plus PROV-DM, reification, named graphs, RDF*, annotated RDF (p10–11). Per-fact *source*: yes (as representation). *Who/what accepted*: no.
7. **Evaluation:** None.
8. **Gaps:** G1 no. G2 no. G3 partly: per-fact source context, not acceptance ("…true with respect to – the Ñam webpage on April 11th, 2020", p10). G4 no (owl:sameAs/keys represent identity but say nothing about human decisions, reuse or scope). G5 no.
9. **Weakens / cite:** Creation, quality assessment and refinement are **not in this PDF**. "the extended version … further discusses knowledge graph creation, enrichment, quality assessment, refinement" (p2; arXiv:2003.02320, ref [57]). We cannot claim "not found in Hogan" for quality/refinement until we read the extended version. Cite it for SHACL/ShEx validation and for context/provenance representation (refs [16], [30], [103]: provenance/trust annotations, Wikidata external references).
10. **Read:** pp1–35 (references skimmed).

## 02 Ji et al., A Survey on Knowledge Graphs

1. **Bib (as printed):** "A Survey on Knowledge Graphs: Representation, Acquisition and Applications." Shaoxiong Ji, Shirui Pan, Erik Cambria, Pekka Marttinen, Philip S. Yu. *IEEE Transactions on Neural Networks and Learning Systems*, 2021 (header). arXiv:2002.00388v4 [cs.CL], 1 Apr 2021. No DOI printed. Note: the file is named 2022 but the PDF says 2021.
2. **What:** A survey of KG representation learning, knowledge acquisition (KGC, entity discovery, relation extraction), temporal KGs and applications, with dataset and library tables.
3. **LLM:** None. This is pre-LLM work. Pretrained LMs (BERT, KG-BERT, ERNIE) appear only as encoders (p7, p15–16).
4. **Validation:** Triple classification "to determine whether facts are correct" by a score threshold (p11). Logic rules and rule injection (AMIE, KALE, pLogicNet; p10–11). Uncertain KGs with confidence scores, and probability calibration of KG embeddings for "trustworthy link prediction" (p8). Entity alignment: BootEA's "editing technique for checking newly-labeled alignment" (automatic; p12). Distant-supervision noise handling (p13–14). No schema check of LLM output and no source-text grounding check.
5. **Human in the loop:** Only general statements: "Current knowledge graphs rely highly on manual construction, which is labor-intensive and expensive" (p17), and Wikidata is "maintained by human editors" (p21). No routing.
6. **Provenance:** Not discussed.
7. **Evaluation:** Survey only. Dataset statistics in Tables VII–VIII (p22).
8. **Gaps:** G1 no. G2 no. G3 no. G4 no (entity alignment is automatic). G5 no. The calibration discussion (p8) is the nearest point but does not route items to humans.
9. **Weakens / cite:** It is pre-LLM, so its silence on LLM checks is weak evidence. Cite it for confidence/calibration in KGs (Tabacof & Costabello; Safavi et al., p8) as background for G5, and for the statement "semi-automatic construction under the supervision of existing knowledge graphs" (p17).
10. **Read:** pp1–27 (appendices and references skimmed).

## 16 Bian, LLM-empowered KG construction survey

1. **Bib (as printed):** "LLM-empowered knowledge graph construction: A survey." Haonan Bian, Xidian University. "Published as a conference paper at ICAIS 2025". arXiv:2510.20345v1 [cs.AI], 23 Oct 2025.
2. **What:** A short survey of LLMs in ontology engineering, knowledge extraction (schema-based and schema-free) and knowledge fusion, plus future directions.
3. **LLM:** This is the survey's subject. LLMs act as ontology co-modelers (p3–4), extractors (p5–7) and alignment/fusion reasoners (p7–8).
4. **Validation:** Schema supervision, e.g. Kommineni's "ABox population under explicit schema supervision" (p6) and "enforced alignment between extracted triples and predefined ontological definitions" (p7). ODKE+ "coupling schema supervision with instance-level corroboration" (p8). KARMA agents for "conflict resolution, and quality evaluation" (p8). VaLiK "cross-modal verification module to filter noise" (p9). Zep TKG "to manage fact validity" (p9). Entity resolution: LLM-Align ("constrained multiple-choice"), EntGPT, COMEM cascade (p8). No quote-in-source check and no value-in-quote check.
5. **Human in the loop:** "human experts intervening only at critical checkpoints" (p4, ontology construction). No routing criterion, no measured effort.
6. **Provenance:** Not discussed.
7. **Evaluation:** None. No numbers anywhere.
8. **Gaps:** G1 no. G2 no. G3 no. G4 no. G5 no. The only HITL mention (p4) is general.
9. **Weakens / cite:** The survey is thin: single author, 9 pages of text, no evaluation tables, and one reference left unfinished ("Kommineni et al. … *Journal Name*, 2024", p11). Its silence is weak evidence for our gaps. Primary sources we must read before claiming G1–G5: **ODKE+** (arXiv:2509.04696; "instance-level corroboration" may be a grounding check), **KARMA** (arXiv:2502.06472; "quality evaluation"), **EDC** (EMNLP 2024), **Kommineni 2024**. The survey states "Pipeline fragmentation … causes cumulative error propagation" (p1). That is a motivation to cite, not a measurement.
10. **Read:** pp1–14 (full).

---

# Grup 2

## Group 2 reading report (8 papers)

Page numbers are PDF pages unless stated "journal p.". G-ratings are strict: "partly" only where the paper does an analogous thing; otherwise "no".

---

## 03 Paulheim 2017

1. **Bib (as printed):** "Knowledge graph refinement: A survey of approaches and evaluation methods". Heiko Paulheim. *Semantic Web* 8 (2017) 489–508, DOI 10.3233/SW-160218, IOS Press.
2. **What:** A survey of methods that refine a KG that already exists, split into completion and error detection and into internal and external methods, plus a review of how these methods are evaluated.
3. **Learned models:** Only in the methods it surveys (classifiers, SVM, tensor nets, outlier detection, the KV classifier). No LLM.
4. **Validation:** Surveys reasoning over ontologies: "NELL and PROSPERA perform reasoning at that point to determine whether the new axiom is plausible or not, and discard implausible ones" (p11 / journal p.499). Also outlier detection, arithmetic constraints such as birth before death, and DeFacto web-evidence checks (p12 / journal p.500).
5. **Human in the loop:** Crowdsourcing and games with a purpose. Validating all of DBpedia by crowdsourcing "would take more than 3,000 years" (p12). Clustering errors and "presenting only representative examples to the human for inspection" (p12–13).
6. **Provenance:** Only a description of Wikidata: "for each axiom, provenance metadata can be included – such as the source and date" (p4 / journal p.492).
7. **Evaluation:** Survey; no experiments. Three evaluation types (partial gold, silver standard, retrospective) with pros and cons in Table 2 (p8). "about half of the approaches ... are only evaluated on one knowledge graph" (p16).
8. **G1–G5:** All "no". It says that evaluating refinement in isolation "allows for ... a cleaner separation of effects" (p2), but that separates construction from refinement; it is not an ablation of checks.
9. **Must cite / weakens:** p13: completion approaches that "compute a confidence score ... could also be used for error detection by flagging axioms ... with a low confidence score". This is a precedent for confidence-based flagging, relevant to G5. Also cite the partial gold standard vs retrospective evaluation taxonomy, and "roughly half of the owl:sameAs links" being wrong (p6).
10. **Read:** pp. 1–20, all.

---

## 04 Zaveri et al. (file says 2016)

1. **Bib (as printed):** "Quality Assessment for Linked Data: A Survey. A Systematic Literature Review and Conceptual Framework". Amrapali Zaveri, Anisa Rula, Andrea Maurino, Ricardo Pietrobon, Jens Lehmann, Sören Auer. The header prints "Undefined 1 (2012) 1–5, IOS Press" and "© 2012". No DOI or final venue is printed, so this is a preprint template. Paulheim's ref. [111] cites a Zaveri et al. paper as *Semantic Web Journal* 7(1) (2015) 63–93, doi:10.3233/SW-150175, under a different title. Check the final citation before using it.
2. **What:** A systematic review: 118 articles narrowed to 21 core approaches (p4–5), from which it defines 18 quality dimensions in four groups, with metrics.
3. **Learned models:** None.
4. **Validation:**
   - Syntactic validity: "degree to which an RDF document conforms to the specification" (Def 6, p12).
   - Semantic accuracy: "degree to which data values correctly represent the real world facts" (Def 7, p12). Metrics SA1–SA6: outliers, functional dependency rules, and "SA4: verifying correctness ... with the help of unbiased trusted third party (humans)".
   - Consistency metrics CS1–CS8 (p13). Extensional conciseness covers duplicate objects (p14).
   - p15: "being syntactically valid does not necessarily mean that the value is semantically accurate".
5. **Human in the loop:**
   - Trustworthiness metric T7 is "explicit trust ratings to the dataset by humans" (p18).
   - 7 of the 8 tools are semi-automated (Table 9, p27). Human effort is not measured.
6. **Provenance:**
   - T1: statement trust "based on provenance information" in [−1,1], and "trust annotations made by several individuals" (p17). Security metric S2 checks authenticity through a provenance vocabulary (p10).
   - Trellis: "Decisions made by users on a particular source are stored as annotations" (p25).
7. **Evaluation:** None of its own. Conclusion: "no formal validation of the methodologies that were implemented as tools" (p27).
8. **G1–G5:**
   - G3 **partly.** Trellis stores user decisions as annotations (p25), but per source, not per accepted fact.
   - G1, G2, G4, G5: no.
9. **Must cite:** Use it as the vocabulary for accuracy vs trustworthiness. Our "value-in-quote" and "quote-in-source" checks map most closely to semantic accuracy plus provenance-based trust. Also cite p21: "a publisher with a high reputation will produce data that is also semantically accurate ... when in reality this may not be so".
10. **Read:** pp. 1–29, all. Reference list skimmed.

---

## 05 Dong et al. 2014 (Knowledge Vault)

1. **Bib (as printed):** "Knowledge Vault: A Web-Scale Approach to Probabilistic Knowledge Fusion". Xin Luna Dong, Evgeniy Gabrilovich, Geremy Heitz, Wilko Horn, Ni Lao, Kevin Murphy, Thomas Strohmann, Shaohua Sun, Wei Zhang (Google). "KDD 2014" is printed; the copyright line is a placeholder and no DOI is printed. Paulheim's ref. [21] gives pp. 601–610, doi:10.1145/2623330.2623623.
2. **What:** Builds a probabilistic KB from four web extractors. It fuses each extractor's confidence with graph-based priors learned from Freebase, and outputs a calibrated probability per triple.
3. **Learned models:**
   - Extractors: TXT, DOM, TBL, ANO; distant supervision.
   - Fusion: boosted decision stumps over sqrt(#sources) and mean score, with Platt calibration (p4).
   - Priors: PRA and an MLP (p6).
4. **Validation:**
   - The Freebase schema of 4469 predicates. Labels come from the local closed world assumption (LCWA) (p3). Fusion counts each triple once per domain (p5).
   - No evidence-quote check and no denial constraints. Mutual exclusion is not modelled (p8).
5. **Human in the loop:** No review queue. An in-house rater team labelled 1000 triples for 10 predicates; 305 were discarded as unknown (p7–8).
6. **Provenance:** Source count and domain count are used as features. No record of who accepted each fact.
7. **Evaluation:**
   - 1.6B candidate triples; 80/20 split (p2). Fused extractors AUC 0.927 (Table 2, p5). Fused priors 0.911; extractors + priors 0.947 (Fig 4, p7).
   - High-confidence (>0.9) facts rise from ~100M to ~271M (p7). Calibration: of triples predicted at 0.9, "about 90% ... are indeed true" (p4).
   - Table 5 (p8), extractors + priors: AUC 0.959 against LCWA labels vs 0.869 against human labels.
8. **G1–G5:**
   - G1 **partly** (analogous). It measures each extractor separately and priors vs extractors (Table 2, Fig 4).
   - G5 **no.** It uses confidence as the acceptance gate, with nothing compared against it and no human routing.
   - G2, G3, G4: no.
9. **Must cite / weakens:** It fuses extractor confidence with prior knowledge and calibrates the result. This is the obvious baseline that any G5 claim must name. Also cite Table 5: the gap between LCWA labels and human labels argues for our human reference.
10. **Read:** pp. 1–10, all.

---

## 17 Mudgal et al. 2018 (DeepMatcher)

1. **Bib (as printed):** "Deep Learning for Entity Matching: A Design Space Exploration". Sidharth Mudgal, Han Li, Theodoros Rekatsinas, AnHai Doan, Youngchoon Park, Ganesh Krishnan, Rohit Deep, Esteban Arcaute, Vijay Raghavendra. SIGMOD'18, Houston. https://doi.org/10.1145/3183713.3196926
2. **What:** Lays out a design space for deep-learning entity matching (attribute embedding, summarization, comparison, classifier), builds four models (SIF, RNN, Attention, Hybrid), and compares them with Magellan.
3. **Learned models:** The deep-learning matcher is the whole system. Uses fastText embeddings. No LLM.
4. **Validation:** None beyond the matcher. The setting excludes "crowdsourced EM or EM using hand-crafted rules" (p1).
5. **Human in the loop:** Labelled training data only. Human-guided entity matching is mentioned as related work (p3).
6. **Provenance:** None.
7. **Evaluation:**
   - 23 tasks (11 structured, 6 textual, 6 dirty), 450 to ~250K labels (Table 2, p9).
   - F1 vs Magellan (Table 1, p9): structured 87.9 vs 88.8; textual 88.0 vs 83.4; dirty 87.9 vs 68.5.
   - Robust to label noise up to ~30% (Fig 7). Errors (p12): domain term variants, missing informative tokens, tokens that look similar but differ in meaning.
8. **G1–G5:**
   - G1 **partly** (analogous). It ablates components of the matcher: embeddings (Table 7), summarization (Tables 8–9), comparison (Table 10, up to 40% F1), 17 variants (Table 11). These are matcher components, not validation checks.
   - G2–G5: no.
9. **Must cite:** Dirty data is where learned matchers beat rules. The error classes in p12 are close to the variation in narrator names.
10. **Read:** pp. 1–16, all.

---

## 18 Li et al. 2020 (Ditto)

1. **Bib (as printed):** "Deep Entity Matching with Pre-Trained Language Models". Yuliang Li, Jinfeng Li, Yoshihiko Suhara, AnHai Doan, Wang-Chiew Tan. PVLDB 14(1), 2021, doi:10.14778/3421424.3421431; arXiv:2004.00584v3 [cs.DB], 2 Sep 2020.
2. **What:** Treats entity matching as sequence-pair classification by fine-tuning BERT, DistilBERT, RoBERTa or XLNet on serialized entries. Adds three optimisations: domain knowledge (DK: span typing, normalization), summarization (SU, TF-IDF) and data augmentation (DA, MixDA).
3. **Learned models:** A pre-trained transformer language model as the matcher. This is pre-LLM in today's sense. Sentence-BERT is used for blocking in the case study.
4. **Validation:** No checks on outputs. DK injects span types via NER and regex. Only 66.2% of pairs have spans of the same type (p8).
5. **Human in the loop:** Labelling only. The case study used 10,000 labels per blocking method, 20,000 in total (p8). Active learning is left to future work (p9). The case study "requires 6k examples to achieve 95% F1" (p9).
6. **Provenance:** None.
7. **Evaluation:**
   - 13 ER-Magellan datasets (Table 5): e.g. Walmart-Amazon dirty 85.69 vs 53.8 for DeepMatcher+ (DM+).
   - WDC products (Table 6): all categories, xLarge 94.08 vs 90.16. Case study F1 96.53 (Fig 5, p8).
   - The abstract claims "up to 29%" F1 improvement; the contributions say up to 31%.
8. **G1–G5:**
   - G1 **partly** (analogous). Sec 4.4 (p7): "we analyze the effectiveness of each component (i.e., LM, SU, DK, and DA) by comparing Ditto with its variants". The language model alone accounts for 78.5% of the improvement on ER-Magellan and 55.3% on WDC (p7–8). These are matcher components.
   - G2–G5: no.
9. **Must cite:** The template for a per-component ablation table. Also the labelled-data cost, which supports storing human identity decisions once (G4).
10. **Read:** pp. 1–15, all.

---

## 19 Rekatsinas et al. 2017 (HoloClean)

1. **Bib (as printed):** "HoloClean: Holistic Data Repairs with Probabilistic Inference". Theodoros Rekatsinas, Xu Chu, Ihab F. Ilyas, Christopher Ré (Stanford, Waterloo). arXiv:1702.00820v1 [cs.DB], 2 Feb 2017. No venue printed.
2. **What:** Combines denial constraints, matching dependencies to external dictionaries, and co-occurrence statistics into one factor graph (DDlog/DeepDive), then infers repairs for cells that the detector marks as noisy.
3. **Learned models:** A probabilistic graphical model trained by ERM/SGD with Gibbs sampling. No LLM.
4. **Validation:** Denial constraints (Sec 3.1, p4) and matching dependencies. Error detection is treated as a black box and is out of scope (p4).
5. **Human in the loop:** Proposed only, not evaluated (p4): "we can ask users to verify repairs with low marginal probabilities and use those as labeled examples to retrain". Ground truth was built by labelling 2,000 cells for Food and 2,500 for Physicians by hand (p9).
6. **Provenance:** "if the provenance and lineage of t[a] is provided ... we use this information as additional features ... trustworthiness of different sources" (p5). This is a feature for inference, not a record of acceptance.
7. **Evaluation:**
   - Four datasets (Table 2, p8): Hospital, Flights, Food, Physicians.
   - F1 (Table 3, p9): Hospital 0.832, Flights 0.763, Food 0.783, Physicians 0.897; precision 1.0, 0.887, 0.769, 0.927.
   - Calibration (Fig 6, p11): marginals in [0.5–0.6] have error rate 0.58, [0.7–0.8] 0.24, [0.9–1.0] 0.04.
8. **G1–G5:**
   - G1 **partly** (analogous). Fig 5 compares variants of how constraints are encoded. External dictionaries add "less than 1%" F1 (p11). The 2.7×/2.81×/2.29× gains (p2) are against other systems, not ablations within HoloClean.
   - G5 **partly.** It proposes routing low-marginal repairs to users (p4). Fig 6 shows that error falls as the marginal rises, and the paper claims this removes the need for active learning (p11–12). It does not compare this with check-based routing.
   - G2, G3, G4: no.
9. **Must cite / weakens:**
   - Denial constraints as domain rules, and "minimality" repairs that are wrong (p1–2).
   - Confidence-based routing with calibrated buckets is a direct precedent for G5. Our claim must be that we compare the two signals, not that we route to humans.
10. **Read:** pp. 1–12; p13 is references.

---

## 21 Francis et al. 2018 (Cypher)

1. **Bib (as printed):** "Cypher: An Evolving Query Language for Property Graphs". Nadime Francis, Alastair Green, Paolo Guagliardo, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Stefan Plantikow, Mats Rydberg, Petra Selmer, Andrés Taylor. SIGMOD'18, Houston, pp. 1433–1445. https://doi.org/10.1145/3183713.3190657. PDF p1 is an Edinburgh repository cover.
2. **What:** The Cypher 9 language, the property graph model G = (N, R, src, tgt, ι, λ, τ), and a formal semantics (p7). Pattern matching under relationship isomorphism is NP-complete (p9).
3. **Learned models:** None.
4. **Validation:**
   - "Neo4j nowadays is schema-optional ... schema constraint language (e.g. for requiring nodes with a given label to have certain properties)" (p13).
   - MERGE uniqueness: an implementation "can use ... locking to ensure that patterns matched by MERGE are unique" (p3).
5. **Human in the loop:** None.
6. **Provenance:** None built in. Properties are key-value pairs on nodes and relationships (p2–3), so acceptance metadata can be stored on edges.
7. **Evaluation:** No empirical evaluation.
8. **G1–G5:** All no.
9. **Must cite:** The property graph model and the MERGE semantics we rely on.
10. **Read:** pp. 1–14, skimmed for the model, MERGE and schema.

---

## 26 Figuera et al. 2021 (Trav-SHACL)

1. **Bib (as printed):** "Trav-SHACL: Efficiently Validating Networks of SHACL Constraints". Mónica Figuera, Philipp D. Rohde, Maria-Esther Vidal. arXiv:2101.07136v1 [cs.DB], 18 Jan 2021. No venue printed.
2. **What:** A SHACL validation engine with:
   - inter-shape planning (seed shape, BFS/DFS over the dependency graph);
   - intra-shape optimisations (pushing filters down, partitioning queries);
   - interleaved execution that aims to invalidate entities early.
3. **Learned models:** None.
4. **Validation:** Shape constraints (SHACL), validated through SPARQL and rule saturation.
5. **Human in the loop:** None. Shape modelling is out of scope (p19).
6. **Provenance:** None.
7. **Evaluation:**
   - 27 LUBM-based datasets, 1.0M to 34.1M triples (Table 2, p12). Three shape schemas (|S| = 3, 7, 14). 11 engine configurations (Table 3). Metrics: time and dief@t.
   - Fig 1 example: 8379 ms vs 525 ms. Trav-SHACL usually beats SHACL2SPARQL (e.g. by a factor of 40.06, p16), but SHACL2SPARQL wins on SS2 SKG by 1.18× (p16–17).
   - SHACL2SPARQL "is not able to identify 41.10% of the valid entities" and classifies them as invalid (p18).
8. **G1–G5:** All no. Its ablation covers planner configurations for speed, not each constraint's contribution to quality.
9. **Must cite:** The standard for shape (schema) validation on RDF. Two points to note:
   - Validator correctness can differ (the 41.10% result).
   - "it does not perform as well in data sets with a small percentage of invalidated entities" (p20).
10. **Read:** pp. 1–22, all.

---

## Cross-paper summary

- **G1:** Only analogous ablations exist: KV (extractors vs priors), DeepMatcher and Ditto (matcher components), HoloClean (signal encodings, dictionaries). None ablates validation checks placed between an extractor and a graph. The claim holds in this set.
- **G2:** None found.
- **G3:** Partly in Zaveri: Trellis stores user decisions per source, and trust annotations exist. No paper keeps a per-fact record of who accepted it.
- **G4:** None found.
- **G5:** Confidence-based routing has a precedent in HoloClean (proposal plus calibration buckets). KV and Paulheim use confidence to gate or flag. Nobody compares confidence with check-based routing, so the claim must be phrased as that comparison.

---

# Grup 3

## Group 3 — REBEL, UIE, GoLLIE, EDC, Feng et al., Arsenyan et al.

Page convention: "p.N" = PDF page N; printed proceedings page in brackets where it differs.

---

## 06 — REBEL

1. **Bib (as printed):** "REBEL: Relation Extraction By End-to-end Language generation". Pere-Lluís Huguet Cabot, Roberto Navigli (Sapienza University of Rome; Babelscape). *Findings of the Association for Computational Linguistics: EMNLP 2021*, pages 2370–2381, November 7–11, 2021. No DOI/arXiv id printed.
2. **What:** A seq2seq model that writes relation triplets as a linearised token sequence (`<triplet>`, `<subj>`, `<obj>`) (p.3–4). Also releases a silver pre-training dataset built from Wikipedia and Wikidata (cRocoDiLe).
3. **Model:** BART-large (406M params, p.12), fine-tuned. It needs training data: pre-training on the silver set, then fine-tuning per dataset.
4. **Validation:** Nothing checks the model output at inference. Only the *training data* is filtered: an NLI model (xlm-roberta-large-xnli) keeps a triplet only if "the entailment prediction is higher than 0.75" (p.5 [2374]). Entities in the data are linked to Wikidata through hyperlinks (wikimapper, p.4). There is no schema check, no evidence check, and no canonicalisation.
5. **Human:** none.
6. **Provenance:** none per fact.
7. **Eval:** Strict micro-F1. REBEL_pre-training scores CONLL04 75.4, NYT 92.0, DocRED 47.1, ADE 82.2 (Table 2, p.7) and Re-TACRED 90.4 (Table 5, p.8). On the REBEL dataset it gets 74 micro-F1 and 51 macro-F1 (p.6). The only ablation is pre-training vs. none (e.g. CONLL04 71.2 → 75.4).
8. **G1–G5:** all **no**.
9. **Cite/weakens:** The NLI entailment filter (threshold 0.75) is an automatic check of support in the source, but it is applied when building training data, not as a gate before the graph. It weakens nothing.
10. **Read:** pp.1–12 (all).

---

## 07 — UIE

1. **Bib:** "Unified Structure Generation for Universal Information Extraction". Yaojie Lu, Qing Liu, Dai Dai, Xinyan Xiao, Hongyu Lin, Xianpei Han, Le Sun, Hua Wu. *Proceedings of the 60th Annual Meeting of the ACL (Volume 1: Long Papers)*, pages 5755–5772, May 22–27, 2022. No DOI printed.
2. **What:** One text-to-structure model for entity, relation, event and sentiment tasks. Output is a "Structured Extraction Language" (SEL), and a schema prompt (the "Structural Schema Instructor", SSI) controls it (p.3–4).
3. **Model:** T5-v1.1-base and T5-v1.1-large (p.6), pre-trained on Wikipedia–Wikidata/ConceptNet data and then fine-tuned per task. It needs labelled data.
4. **Validation:** The schema appears only as the SSI prompt. A "Rejection Mechanism" injects `(SpotName, [NULL])` noise during training, and "the [NULL]-valued span will be ignored during inference" (Table 1, p.6 [5760]). Generated strings are mapped to offsets "by finding the first matched offsets", with "<0.5% error offsets" (p.6; p.16). This is a lookup in the source used for scoring, not a filter. No check that a value occurs in evidence, no canonicalisation, no entity resolution.
5. **Human:** none.
6. **Provenance:** none.
7. **Eval:** Span-offset micro-F1 on 13 datasets. Average gain is +1.42 F1 over SOTA (p.7, Table 2), e.g. CoNLL04 Rel-S 75.00 and ACE05-Rel 66.06. Ablations cover training components only: L_Pair, L_Record, L_Text (Table 4, p.8); SSI adds +4.16 / +3.30 (p.8–9); rejection noise adds +13.16 precision on average (Table 5, p.8–9).
8. **G1–G5:** all **no**. The ablations are of training objectives, not of checks.
9. **Cite:** The rejection mechanism is a learned way to drop spans. Offset mapping is a precedent for locating generated text in the source.
10. **Read:** pp.1–9 and 13–18. pp.10–12 (references) were not viewed.

---

## 08 — GoLLIE

1. **Bib:** "GoLLIE: Annotation Guidelines improve Zero-Shot Information-Extraction". Oscar Sainz, Iker García-Ferrero, Rodrigo Agerri, Oier Lopez de Lacalle, German Rigau, Eneko Agirre (HiTZ, UPV/EHU). "Published as a conference paper at ICLR 2024." No DOI/arXiv id printed.
2. **What:** An LLM fine-tuned to follow annotation guidelines written as Python dataclass docstrings. It outputs instances of those classes (p.3–4).
3. **Model:** Code-LLaMA 7B, 13B and 34B, fine-tuned with QLoRA (p.5–6). Training data is 12 datasets; evaluation is zero-shot on unseen schemas.
4. **Validation:** The output is executed as Python. If an output is "impossible to parse … we treat the output as an empty list". If the model outputs a label "not defined among the input classes … we remove the label from the output" (Appendix C, p.22). Both are counted per dataset (Table 8, p.21) and occur in "less than 1% of the predictions". So out-of-schema output is **dropped and counted**. No check that the text occurs in the source or in evidence. CASIE arguments use partial matching (p.5).
5. **Human:** Experts write guidelines when none are published (p.5; Appendix F, p.25). There is no review of outputs.
6. **Provenance:** none.
7. **Eval:** Zero-shot average F1 is 55.3 for 7B vs. 42.3 for the baseline (+13), and 57.2 for 34B (Table 3, p.7). The ablation (Table 4, p.8) covers *training regularisers*: w/o Candidates 49.9, w/o Dropout 54.0, w/o all 42.3.
8. **G1:** no. **G2:** no (the counted error class is "hallucinated label", which is a schema error, not value-in-quote). **G3–G5:** no.
9. **Weakens:** We cannot claim novelty for counting schema failures as their own error class. GoLLIE already does it (Table 8, p.21–22).
10. **Read:** pp.1–11 and 15–25. pp.12–14 (references) were not viewed.

---

## 09 — EDC

1. **Bib:** "Extract, Define, Canonicalize: An LLM-based Framework for Knowledge Graph Construction". Bowen Zhang, Harold Soh (NUS). *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing*, pages 9820–9836, November 12–16, 2024. No DOI printed. (Feng et al. cite it as arXiv:2404.03868.)
2. **What:** A three-phase prompted pipeline: open IE → LLM-written schema definitions → canonicalisation, with an optional refinement pass (EDC+R) that uses a trained Schema Retriever (p.1–5).
3. **Model:** For open IE, GPT-4, GPT-3.5-turbo or Mistral-7b, used few-shot (6-shot, p.13). The other steps use GPT-3.5-turbo. The Schema Retriever is a fine-tuned E5-mistral-7b-instruct trained on 37,500 TEKGEN pairs (p.13).
4. **Validation:** In Target Alignment, the LLM judges each candidate mapping. If it is "deemed unreasonable … the component, and its related triplets are excluded" (p.4 [9823]), so out-of-schema triples are **dropped**. In Self Canonicalization, unmatched components are added to the schema. No check that the text occurs in the source. Entity dedup is listed as a limitation (p.9); a CESI trial gave F1 0.516→0.520 (p.17).
5. **Human:** Two student annotators judged triple precision for evaluation only. Inter-annotator agreement was 0.94 (p.8).
6. **Provenance:** none.
7. **Eval:** Partial/Strict/Exact F1 against WebNLG, REBEL (1000 samples) and Wiki-NRE (1000). EDC+R with GPT-4 reaches Partial F1 0.820 / 0.601 / 0.713, vs. REGEN 0.767 and GenIE 0.385 / 0.484 (Tables 3–5, p.14). Human precision: EDC 0.956 / 0.867 / 0.898 vs. CESI 0.724 / 0.504 / 0.753 (Table 2, p.8). Ablation of the Schema Retriever: e.g. REBEL Partial 0.559 → 0.517 without it (Table 1, p.8); last-round hints ablated in Table 7 (p.14).
8. **G1:** no (the ablation removes a retriever, not a validation check). **G2–G5:** no.
9. **Cite:** "ChatIE and CodeKGC may still output out-of-schema relation words although the entire schema is provided in the prompt" (p.17). This supports the need for a schema check. Reference sets are "non-exhaustive", which penalises correct triples (p.7, p.16). That is relevant to our silver-standard caveat.
10. **Read:** pp.1–17 (all).

---

## 10 — Feng et al.

1. **Bib:** "Ontology-grounded Automatic Knowledge Graph Construction by LLM under Wikidata schema". Xiaohan Feng, Xixin Wu, Helen Meng (CUHK). *HI-AI@KDD, Human-Interpretable AI Workshop at the KDD 2024*, 26th of August 2024, Barcelona. CEUR-WS.org/Vol-3841/Paper19.pdf. No DOI printed.
2. **What:** The LLM generates competency questions and answers, extracts properties, matches them to Wikidata properties, writes an OWL ontology, and then writes RDF triples grounded in that ontology (p.3–4).
3. **Model:** Mistral-7B-instruct and GPT-4o, prompted zero-shot with no fine-tuning (p.5, p.7). bge-small-en provides the embeddings.
4. **Validation:** The top-1 vector match is "vetted by LLM" with a yes/no answer (p.4; prompt on p.15). Unmatched properties are kept or discarded depending on the setting (p.4). Output is parsed with an RDF parser and "all valid RDF triples" are extracted (p.5), so invalid syntax is implicitly dropped. Grounding is by prompt only: "Do not make up answers", "Only use those properties in the ontology" (p.16). No string check against the source or against evidence.
5. **Human:** No review loop. The authors mapped four SciERC properties "based on our subjective opinion" (p.5). They say the KG "could be … audited for correctness" (p.2) but do not implement this.
6. **Provenance:** none.
7. **Eval:** Partial F1 on Wiki-NRE (1,000 samples), SciERC (974) and WebNLG (1,165). Results for "target-constrained / unconstrained" (Table 1, p.6): Mistral 0.66/0.60, 0.73/0.58, 0.74/0.68; GPT-4o 0.71, 0.77, 0.76. No ablation.
8. **G1–G5:** all **no**.
9. **Cite:** LLM yes/no vetting is an example of using an LLM as the validator rather than deterministic checks. The claim of an auditable KG has no mechanism behind it.
10. **Read:** pp.1–19 (all).

---

## 11 — Arsenyan et al.

1. **Bib:** "Large Language Models for Biomedical Knowledge Graph Construction: Information extraction from EMR notes". Vahan Arsenyan, Spartak Bughdaryan, Fadi Shaya, Kent Small, Davit Shahnazaryan. *Proceedings of the 23rd Workshop on Biomedical Language Processing*, pages 295–317, August 16, 2024. No DOI printed.
2. **What:** Template questions ("What treats %s") are posed over EMR notes to build a KG of treatments, factors and coexists_with terms for AMD (p.3–5). The paper benchmarks 12 models.
3. **Model:** BERT-family extractive QA models (already SQuAD-v2 fine-tuned), FLAN-T5-XXL, FLAN-UL2, Llama-2-70B, Vicuna-33B, WizardLM-70B and others (Table 1, p.4). All are used query-only ("no gradients", p.4), with zero-shot, few-shot, instruction or "guided" prompts.
4. **Validation:** Model confidence acts as the gate. A relation is kept if it is returned "more than relation_occurrence_number times and … average probability … greater than relation_probability" (p.5; Alg.3 p.14: ≥10 occurrences and ≥0.1). Predictions below 0.08 probability are dropped, and "I do not know" answers are removed (p.5; Table 6 p.23). Canonicalisation groups predictions at cosine ≥0.8 and keeps the one with the highest probability (p.6; Fig.2 p.15). Disease mentions are matched through UMLS synonyms, BioBERT NER and cosine ≥0.8 (p.3). There is no check against the source or against evidence.
5. **Human:** Two authors (a retina specialist and a clinical research coordinator) annotated 320 notes and adjudicated jointly. This reference is for evaluation only (p.6–7).
6. **Provenance:** none.
7. **Eval:** Precision and recall against 11 treatments, 8 factors and 8 coexists_with terms, so the reference is very small. FLAN-UL2 guided scores P/R 0.98/1, 0.84/0.875 and 0.98/1 (Table 2, p.6). There is no ablation of the filters.
8. **G1–G5:** all **no**. G5 is the closest: confidence decides acceptance or rejection, but it is not compared with check-based routing and it does not route anything to a human.
9. **Cite:** "some models generated correct responses, but these responses did not originate from the given context" (p.7). This is a documented motivation for the quote-in-source check that the paper itself does not implement. It is also a precedent for confidence-based filtering between the LLM and the KG.
10. **Read:** pp.1–23 (all).

---

## Group summary for G1–G5

None of the six papers addresses G1–G5, even partly.

Near-misses we must not overclaim against:
- **GoLLIE** drops out-of-schema labels and unparseable outputs and counts them as their own error classes (pp.21–22).
- **EDC** has the LLM verify schema mappings and drops triples it rejects (p.4).
- **Arsenyan et al.** gate on model probability and occurrence count (p.5, p.14).
- **REBEL** uses an NLI entailment filter, but only on training data (p.5).
- **UIE** maps generated strings back to source offsets, but only for scoring (pp.6, 16).

Every ablation in these papers removes training or retrieval components (UIE Table 4/5, GoLLIE Table 4, EDC Table 1/7), never validation checks.

---

# Grup 4

## Group 4 — LLM-to-KG construction papers (KGGen, Tree-KG, CoDe-KG, AutoSchemaKG, GraphRAG, Zep)

Page numbers are PDF page indices (1 = first page of the file).

---

## 12 — KGGen

1. **Bib:** "KGGen: Extracting Knowledge Graphs from Plain Text with Language Models." Belinda Mo, Kyssen Yu, Joshua Kazdan, Joan Cabezas, Proud Mpala, Lisa Yu, Chris Cundy, Charilaos Kanatsoulis, Sanmi Koyejo. 39th Conference on Neural Information Processing Systems (NeurIPS 2025). arXiv:2502.09956v2 [cs.CL], 6 Nov 2025.
2. **What:** A text-to-KG Python package. An LLM extracts entities, then triples. The triples are aggregated, then entities and edges are clustered and de-duplicated. The paper also releases the MINE benchmark.
3. **LLM:** Gemini 2.0 Flash through DSPy signatures does the extraction (p.4). Claude Sonnet 3.5 and GPT-4o were also tested (Table 1a, p.7). An LLM also does dedup and acts as judge in MINE.
4. **Validation:** No schema; it is open. The prompt says "Subject and object must be from entities list" (p.14), but that is an instruction, not a check. No grounding or quote check. Entity resolution: S-BERT plus k-means (clusters of 128), top-16 by fused BM25 and embeddings, then the LLM picks exact duplicates and a canonical alias (p.4). No contradiction handling and no domain rules.
5. **Human:** None in the pipeline. Humans did manual checks only for evaluation: they verified the MINE facts and compared 60 judge pairs, with 90.2% agreement and r=0.80 (p.5).
6. **Provenance:** "each relation is linked to a source text chunk" (p.6). No acceptor record and nothing temporal.
7. **Eval:**
   - MINE-1 (100 LLM-generated articles × 15 facts): KGGen 66.07%, GraphRAG 47.80%, OpenIE 29.84% (Fig. 3, p.7).
   - MINE-2 (WikiQA): 80.63% vs GraphRAG 81.20% (p.8).
   - Valid triples: 98/100 vs 0/100 vs 55/100 (Table 1b).
   - SemEval-2010: 96/100 (p.8).
   - Dedup on 1M characters: entities 4,602→3,573 (Table 2, p.9).
   - There is no formal ablation.
8. **G1–G5:** all no.
9. **Note:** In the limitations the authors admit "over or under de-duplication" (p.10). MINE-1 texts are LLM-generated (p.5).
10. **Read:** pp.1–24 (pp.18–24 are the NeurIPS checklist).

---

## 13 — Tree-KG

1. **Bib:** "Tree-KG: An Expandable Knowledge Graph Construction Framework for Knowledge-intensive Domains." Songjie Niu, Kaisen Yang, Rui Zhao, Yichao Liu, Zonglin Li, Hongning Wang, Wenguang Chen. Proceedings of the 63rd Annual Meeting of the ACL (Volume 1: Long Papers), pp. 18516–18529, July 27–Aug 1, 2025.
2. **What:** It builds an "explicit KG" from the textbook's table-of-contents structure, using regex and LLM summaries. Then it expands into a "hidden KG" with operators: conv, aggr, embed, dedup, pred, merge (pp.3–6).
3. **LLM:** DeepSeek-V3, with GLM-4-Air for the ablations (p.6). The LLM summarises, extracts, rewrites descriptions, assigns roles, decides duplicates, rates edge strength from 0–10, and does the evaluation.
4. **Validation:**
   - Schema: semi-fixed. Vertical edge types are predefined (has_subsection, has_entity, has_subordinate); horizontal edges have a general category plus an LLM-predicted relation (p.4).
   - Grounding: none checked. The entity template asks for "raw_content" and the relation prompt says descriptions must be "grounded in provided information", but both are prompt text only (p.14).
   - Dedup: FAISS 20-NN, distance below 0.55 and the same role, then an LLM decision and union-find (pp.5, 9).
   - Contradiction handling: none.
5. **Human:** TAs and experts annotated the reference KGs. Fleiss' κ is mentioned, but I saw no value printed (p.6). Humans are not in the loop.
6. **Provenance:** There is section membership, but no per-fact acceptance record and nothing temporal.
7. **Eval:**
   - Text-Annotated F1 0.81; Domain-Annotated F1 0.67 vs GraphRAG 0.53 (Table 1, p.7).
   - The ablations cover only the operators: summary (ES 0.94 vs 0.86), conv steps, the dedup threshold, and the edge weights (pp.8–9).
8. **G1–G5:** all no. The operator ablation is of generation steps, not checks. The edge gate uses an LLM strength score, but it is never compared to anything.
9. **Note:** None.
10. **Read:** pp.1–14.

---

## 14 — CoDe-KG

1. **Bib:** "Automated Knowledge Graph Construction using Large Language Models and Sentence Complexity Modelling." Sydney Anuyah, Mehedi Mahmud Kaushik, Krishna Dwarampudi, Rakesh Shiradkar, Arjan Durresi, Sunandan Chakraborty. Proceedings of EMNLP 2025, pp. 15515–15539, Nov 4–9, 2025. No DOI is printed.
2. **What:** Coreference resolution, then sentence-complexity classification, then rewriting into simple sentences, then triple extraction. It runs on 7,500 PubMed lung-cancer abstracts (pp.3–6).
3. **LLM:** Open models; the best prompt-model pair is chosen per stage. Mixtral-8x7B does coreference and relation extraction; Llama-3 does simplification (pp.6–8).
4. **Validation:** No schema; it is open. No grounding check. The relation prompt says "Validate that each triple captures meaningful semantic information" (p.23), which is prompt text. Algorithm 5 keeps only non-empty triples (p.17). There is no entity resolution beyond coreference, and no contradiction handling.
5. **Human:**
   - Four expert annotators built the coreference gold, with κ=0.74 (Table 12, p.16).
   - Two verifiers kept only the sentence labels they agreed on (p.5).
   - Annotators judged 100 relations per model (p.8).
   - These roles serve gold creation and model selection, not a runtime queue.
   - Payment is reported as 40,000 NGN per week, over 5 weeks on p.18 but 8 weeks on p.10. Effort per item is not measured.
6. **Provenance:** None per fact.
7. **Eval:**
   - Ablation on 23 articles (Table 11, p.15): full pipeline P/R/F1 92.0/92.9/92.4. Without coreference, F1 77.5. Without decomposition, 57.2. Without both, 54.8.
   - REBEL macro-F1 65.78 (Table 7, p.8).
   - Error classes: missing+spurious 73%, spurious 11%, missing 9%, relation-type 7% (p.9).
8. **G1–G5:** all no. G1 is the closest: the ablation removes preprocessing stages, not checks.
9. **Must cite:**
   - It is the nearest "ablation of pipeline components" in this group.
   - Coreference was scored by cosine similarity ≥0.9 rather than exact match. The authors say 99% of the non-exact matches were correct ("a house" vs "house") (p.6). That is a counterpoint to strict string checks like our check (c).
   - The abstract's "8-point gain" does not match the text (65.78 vs a cited 51.0).
10. **Read:** pp.1–25.

---

## 15 — AutoSchemaKG

1. **Bib:** "AutoSchemaKG: Autonomous Knowledge Graph Construction through Dynamic Schema Induction from Web-Scale Corpora." Jiaxin Bai, Wei Fan, Qi Hu, et al. (20 authors), Yangqiu Song. Proceedings of the 64th Annual Meeting of the ACL (Volume 1: Long Papers), pp. 20557–20584, July 2–7, 2026.
2. **What:** Extracts entity–entity, entity–event and event–event triples, then induces concepts. The result is ATLAS: 900M+ nodes and 5.9B edges (pp.1–3).
3. **LLM:** LLaMA-3.1-8B-Instruct does extraction and schema induction. DeepSeek-V3 is the judge (p.4).
4. **Validation:**
   - Schema: induced.
   - Output handling: "repairs any malformed JSON… If parsing encounters errors, an empty list is returned" (p.15).
   - There is no grounding check. I found no entity-resolution step.
   - Contradictions are not handled. The limitations say the KGs "may contain inconsistencies, contradictions" (p.9).
5. **Human:** None ("zero manual intervention").
6. **Provenance:** "triples with their corresponding texts and metadata are serialized" (p.3). Chunks are "tagged with a unique identifier… to maintain traceability" (p.15). Nothing temporal and no acceptor.
7. **Eval:**
   - The LLM judge gives precision 95.65–100 (Table 2, p.4). I did not find a sample size.
   - "92% semantic alignment" comes from BERTScore-based metrics (Tables 6–7).
   - Multi-hop QA with HippoRAG2: HotpotQA F1 78.3 (Table 8, p.6).
   - The ablation covers only the graph's node types: entity, event, concept (Table 12, p.20).
8. **G1–G5:** all no.
9. **Note:** "Precision" here is measured by an LLM judge, not by humans.
10. **Read:** pp.1–9 and 14–28. I skipped pp.10–13, which are references.

---

## 22 — GraphRAG

1. **Bib:** "From Local to Global: A GraphRAG Approach to Query-Focused Summarization." Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson (Microsoft). "Preprint. Under review." arXiv:2404.16130v2 [cs.CL], 19 Feb 2025.
2. **What:** An LLM extracts entities, relationships and claims from chunks. Leiden detects communities, then summaries are written and used for map-reduce answers (pp.4–6).
3. **LLM:** GPT-4-turbo (p.9).
4. **Validation:**
   - No fixed schema; entity types come from few-shot examples (p.8).
   - Self-reflection "gleanings" are a yes/no check, with a forced logit bias, on whether entities were missed (p.18).
   - Entity matching is exact string match (p.5).
   - There is no grounding check, and none for contradictions.
5. **Human:** None.
6. **Provenance:** Not stated per fact in the pages I read.
7. **Eval:**
   - 125 LLM-generated questions per corpus, judged by an LLM head-to-head.
   - Comprehensiveness win rate against vector RAG: 72–83% on podcasts and 72–80% on news (p.9).
   - The claim-based check agreed with the LLM judge in 78% of cases (p.11).
   - Conditions C0–C3, TS and SS act as a rough ablation of the retrieval context.
8. **G1–G5:** all no.
9. **Must cite:** The paper says LLM extraction "is a form of abstractive summarization… may not be explicitly stated in the text" (p.5). It accepts by design the outputs our check (c) rejects.
10. **Read:** pp.1–12 and 16–18. I did not read pp.19–26 (appendices B–G).

---

## 23 — Zep

1. **Bib:** "Zep: A Temporal Knowledge Graph Architecture for Agent Memory." Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef (Zep AI). arXiv:2501.13956v1 [cs.CL], 20 Jan 2025. No venue is printed.
2. **What:** Graphiti is a temporal KG with episode, entity and community subgraphs, used as an agent's memory.
3. **LLM:** gpt-4o-mini handles extraction, reflection, entity and fact resolution, temporal extraction, and contradiction detection (pp.3, 5).
4. **Validation:**
   - Schema: predefined Cypher queries "to ensure consistent schema formats and reduce the potential for hallucinations" (p.3).
   - Entity resolution: cosine and full-text candidates, then an LLM duplicate prompt, which generates "an updated name and summary" (p.3).
   - Facts are de-duplicated only within the same entity pair.
   - Contradictions: "employs an LLM to compare new edges against semantically related existing edges… it invalidates the affected edges by setting their t_invalid… prioritizes new information" (p.3).
   - There is no grounding check.
5. **Human:** None.
6. **Provenance:**
   - Bi-temporal: t′created and t′expired record the system's timeline; t_valid and t_invalid record when the fact held (p.3).
   - Episodes link to facts, but "not directly examined in this paper's experiments" (p.3).
   - No record of who or what accepted a fact.
7. **Eval:**
   - DMR: 94.8% vs MemGPT 93.4% (Table 1, p.6).
   - LongMemEval: 71.2% vs 60.2% with gpt-4o, and latency down by about 90% (Table 2, p.7).
   - There is no ablation, and no check of the resolution or invalidation accuracy.
8. **G1–G5:**
   - G1: no.
   - G2: no.
   - G3: partly. It records when a fact was created and which episode it came from ("t′created… monitor when facts are created", p.3), but no acceptor.
   - G4: no. Identity is merged by an LLM, not a person. Contradiction handling invalidates facts, not identity decisions.
   - G5: no.
9. **Must cite:** It is the nearest prior work for invalidation driven by contradictions with temporal scope, and for per-fact timestamps. G3 and G4 must be worded around who accepted a fact and human identity decisions.
10. **Read:** pp.1–12.

---

# Grup 5

## Group 5: close-to-contribution papers (Carriero, Tsaneva, Zhang, Sikos)

All four PDFs were read in full, references included. Page numbers are PDF page numbers. For Carriero, Tsaneva and Zhang these match the printed page numbers. For Sikos, PDF p.1 is the ECU Research Online cover sheet and the journal text starts on PDF p.2.

---

## 20 — Carriero et al.

1. **Bibliographic line.** "Human Evaluation of Procedural Knowledge Graph Extraction from Text with Large Language Models". Valentina Anita Carriero, Antonia Azzini, Ilaria Baroni, Mario Scrocca, Irene Celino (Cefriel – Politecnico di Milano). arXiv:2412.03589v1 [cs.AI], 27 Nov 2024. No venue is printed. Code: github.com/cefriel/procedural-kg-llm.
2. **What it does.** A two-prompt chain turns WikiHow procedures into an RDF procedural KG: P1 writes semi-structured steps with action, direct object, equipment and time; P2 converts that to Turtle (pp.8–10). Crowd workers then rate how good and how useful the extraction is. An A/B test checks for bias against AI.
3. **LLM.** GPT-4o is the extractor, run through LangChain. GPT-3.5 Turbo was tried and did worse (p.9). The LLM is not a validator.
4. **Validation.** There is no automatic check. The authors judged the outputs by hand, "with majority voting" (p.7), and report: "All produced KGs are valid RDF in Turtle syntax. Properties' domains and ranges are correctly used, and individuals are typed flawlessly" (p.9). The ontology reuses P-Plan, K-Hub, FRAPO and the Time Ontology (p.5). The authors deliberately moved away from verbatim extraction: letting the LLM write its own step sentences "gave better results ... as opposed to strictly report the verbatim sentence" (p.8).
5. **Human in the loop.** This is evaluation only, not a review queue.
   - Preliminary study: n=24, 8 people per procedure. They found "no significant inter-rater agreement indicator", and Krippendorff's alpha showed no agreement (p.6).
   - Main study: 180 Prolific workers in 6 campaigns of 30, covering 3 procedures × the LLM/human label, between-subject (p.11).
   - Everyone saw everything: the P1 output, not the RDF (p.10).
   - Ratings on a 1–5 Likert scale. Effort and time were not measured.
6. **Provenance.** None.
7. **Evaluation (Table 3, p.14).**
   - Quality items: Q1 3.94, Q2 4.16, Q3 3.82. Comparative quality: CQ1–CQ4 3.55–4.02. Usefulness: U1–U5 2.90–3.39.
   - Correlations among items: quality r 0.56–0.64, usefulness r 0.15–0.62 (pp.12–13).
   - Kruskal-Wallis with n=90 per group: the "LLM" label got significantly lower scores on Q2, Q3, CQ1, CQ4 and U4, with p between 0.007 and 0.04 (p.14).
   - No ablation.
8. **Gaps.** G1 no. G2 no. G3 no. G4 no. G5 no.
9. **Implications.**
   - They argue procedural extraction has no definitive ground truth and that "the LLM can be considered as 'yet another annotator'" (p.6). Humans rephrased the text even when told to extract it verbatim. This supports our point that platform labels are only silver.
   - Their move away from verbatim extraction is the opposite of our value-in-quote design. Cite it as a contrast.
   - Conclusion: human-in-the-loop "is very likely required to verify" the output (p.15).
10. **Reading depth.** pp.1–19, all pages.

---

## 24 — Tsaneva et al.

1. **Bibliographic line.** "Knowledge graph validation by integrating LLMs and human-in-the-loop". Stefani Tsaneva, Danilo Dessì, Francesco Osborne, Marta Sabou. *Information Processing and Management* 62 (2025) 104145. https://doi.org/10.1016/j.ipm.2025.104145. Data: doi 10.5281/zenodo.13730203.
2. **What it does.** The paper extends the validation stage of SCICERO, the pipeline that builds CS-KG. It defines nine workflows that combine LLM and human validators, sorted by Faggioli et al.'s collaboration levels (Table 1, p.7), and tests them on 3.6K and 600 triples.
3. **LLM.** The LLM is a validator/judge doing binary true/false classification of triples. Models: gpt-4o-2024-05-13, claude-3-5-sonnet-20241022 and Llama-3.3-70B-Instruct (Table 2, p.11). Each batch of 100 triples was sent with no context, three times, and majority vote decided (p.11). The extractor is not an LLM: it is the CSO classifier plus CoreNLP (p.5).
4. **Validation.** SCICERO already has two validators (p.5):
   - A transformer validator based on support (how many documents a triple comes from): s ≥ 5 is T_reliable, otherwise T_uncertain. It is fine-tuned on T_reliable plus corrupted T_negative triples.
   - An ontology validator that checks domain and range against the CS Ontology.
   There is no grounding check against the text.
5. **Human in the loop.**
   - Experiment A simulates the human by drawing one of the 3 senior-expert labels at random (p.12).
   - Experiment B uses 4 PhD researchers who had no part in building CS-KG. They reviewed 333 triples in Google Sheets, seeing entity types and source file ids and with access to the papers via OpenAlex/Scopus. One annotator per triple; a second if the first was unsure; a third plus discussion and majority otherwise. It took a week (p.12).
   - Routing to humans: all triples (WF1–2), low-support triples only (WF3), or triples where the LLM and SCICERO disagree (WF5–6).
   - Effort is reported as a count of human-judged triples (N_Human). Time per item and inter-annotator agreement are not reported.
6. **Provenance.** Not addressed.
7. **Evaluation.**
   - Data: CS-KG-3600, 600 triples from each of six strata. CS-KG-600 has 100 from each (p.11). Metrics are precision, recall and F1 against a 3-expert majority vote.
   - Experiment A (Table 4, p.13):

     | Workflow | P/R/F1 | Triples judged |
     |---|---|---|
     | SCICERO alone | 75/79/77 | – |
     | WF1, humans judge all | 88/87/87 | 3.6K human |
     | WF3, low support to humans | 83/77/80 | 600 human |
     | WF5, disagreement to humans | F1 81–82 | 423–444 human + 1.1K LLM |
     | WF9, LLM only | P 58–70, F1 70–71 | – |

   - Experiment B (Table 5, p.14):

     | Workflow | P/R/F1 | Triples judged |
     |---|---|---|
     | SCICERO alone | 73/77/75 | – |
     | WF3 | 77/67/72 | 100 human |
     | WF5 | F1 77–79 | 61–75 human |
     | WF7, gpt-4o | P 85 | – |

   - Workflows that add, remove or replace validators work as an ablation at the level of whole modules.
8. **Gaps.**
   - **G1 partly.** Workflow variants are compared, but the paper says "this study does not aim to evaluate the HiL or LLM validation modules in isolation" (p.10). Earlier SCICERO work reports "validation modules contribute to an over 20% increase in precision" (p.6).
   - **G2 no.**
   - **G3 no.**
   - **G4 no.**
   - **G5 partly.** "the support-level s can be interpreted as confidence of the correctness of the triple" (p.5). WF3 routes by this confidence proxy; WF5 routes by disagreement. Disagreement routing gave a higher F1 with fewer human labels in Experiment B. The paper does not measure model self-confidence or a per-item catch rate.
9. **Implications.**
   - This is the closest prior work for G1 and G5. Narrow our claims: "per-check ablation inside the gate" for G1, and "the extractor LLM's own confidence vs. deterministic checks" for G5.
   - The original SCICERO evaluation found that 34% of the triples the transformer validator discarded were in fact correct (p.8). This supports flagging instead of deleting.
   - Related work it cites: confidence-threshold routing to humans (Demartini 2013, Li 2017; p.3). We must cite these.
   - "LLMs can outperform junior experts" (p.16): reviewer expertise matters.
10. **Reading depth.** pp.1–18, all pages.

---

## 25 — Zhang et al.

1. **Bibliographic line.** "Towards Explainable Automated Knowledge Engineering with Human-in-the-loop". Bohui Zhang, Albert Meroño-Peñuela, Elena Simperl (King's College London). *Semantic Web* 0 (0) 1, IOS Press. This is a pre-issue header: no year, volume or DOI is printed. The repo is github.com/bohuizhang/XKGC.
2. **What it does.** A PRISMA review of explainable-AI (XAI) methods for KG construction, plus a semi-structured interview study with 13 knowledge engineers and researchers. It ends with a design blueprint (Fig.6, p.25).
   - Review: search Oct–Dec 2022; 4,073 records screened, 162 assessed, 84 included (p.7).
   - Interviews: Aug–Nov 2023, 35–50 minutes each, ethics approval MRSP-22/23-34456 (pp.8–9).
3. **LLM.** None is used. LLMs are discussed only as context.
4. **Validation.** Interviewees report that 12 of 13 evaluate by hand (Fig.5b) and two use SHACL shapes (p.21). The review cites extraction explanations that point to "supporting evidence from the source data (e.g., text)" (p.16).
5. **Human in the loop.**
   - Interviewees work manual 38.5%, semi-automatic 38.5% and automated only 23.1% (Table 7, p.17).
   - Interventions: 53.8% pre-processing, 46.2% in-process, 53.8% post-process (p.21).
   - Participant L on sampling: "the main difficulty is to select an actual relevant sample" (p.20).
   - Only 3 human-in-the-loop systems were found in the review: myDIG, SystemER and TuneR (p.14).
6. **Provenance.**
   - 92.3% of interviewees know their data sources and 69.2% actively track provenance. Tools named: PROV-O, RDF-star, DVC, NIF, among others. What they record: "creation time, involved personnel, operation timelines, algorithms" (p.20).
   - Participant B wants provenance "directly attached to the produced artifacts" (p.20).
   - myDIG "records extraction provenance" (p.11).
7. **Evaluation.**
   - Only 17.9% of feedback on the example explanations was positive (p.23).
   - 30.8% of interviewees asked for a confidence indicator; 11 of 13 preferred natural language (p.24).
   - In the review, 58 of 84 papers did no evaluation of their explanations (p.14).
8. **Gaps.**
   - **G1 no.**
   - **G2 no.**
   - **G3 no.** It is adjacent: practitioners log personnel and time, but there is no acceptance record.
   - **G4 partly (weak, second-hand).** "human input often involves the provision or revision of rules for ... entity resolution [183, 184]" (p.14). The reused unit is a rule; scope is not derived from contradictions.
   - **G5 no.** It is a counterpoint: the paper asserts that confidence indicators help by "highlighting uncertain instances where human intervention is necessary" (p.24), without measuring this.
9. **Implications.**
   - Supports our motivation: "the fewest of approaches look at the human-in-the-loop aspects of KG construction" (p.26).
   - Its confidence-indicator claim is something our 50/275 vs. 122/155 comparison tests.
   - Design advice we should follow: show the source context as evidence (p.25), and give explanations in natural language.
10. **Reading depth.** pp.1–36, all pages.

---

## 27 — Sikos & Philp

1. **Bibliographic line.** "Provenance-Aware Knowledge Representation: A Survey of Data Models and Contextualized Knowledge Graphs". Leslie F. Sikos, Dean Philp. *Data Science and Engineering*, https://doi.org/10.1007/s41019-020-00118-0. Published online 08 May 2020 (© The Author(s) 2020).
2. **What it does.** A survey of ways to attach provenance to RDF:
   - The approaches covered: reification, n-ary relations, aRDF, RDF+, RDF*, PaCE, singleton property, N-Quads, named graphs/GraphSource, triple coloring and nanopublications.
   - They are compared on semantics, tuple type, standards compliance, granularity and scalability (Tables 3–8).
   - It also covers the provenance vocabularies (PROV-O, PAV, Dublin Core, and others), storage, querying and tools.
3. **LLM.** None.
4. **Validation.** Not addressed. It lists ProvValidator, prov-check and prov-constraints as tools for validating PROV documents (PDF p.16).
5. **Human in the loop.** None.
6. **Provenance.**
   - Six levels of granularity, from dataset down to element (PDF pp.11–12).
   - Reification makes the statement count grow "at least four times" (PDF p.4).
   - A nanopublication carries prov:wasDerivedFrom plus prov:generatedAtTime (PDF p.7).
   - Dublin Core terms cover "who affected a change" and when, including dateAccepted (PDF p.14).
   - "Data inferred by software agents should be distinguished from data explicitly provided by data publishers" (PDF p.15).
7. **Evaluation.** GraphSource vs. singleton property on ISPNet, run in Stardog (Table 10, PDF p.19):

   | Metric | GraphSource | Singleton property |
   |---|---|---|
   | File size | 93,647 B | 734,781 B |
   | Share of provenance statements | 10% | 66% |
   | Query 5 plan length | 7 lines | 22 lines |

8. **Gaps.**
   - **G1 no.**
   - **G2 no.**
   - **G3 partly.** It supplies the representation (per-triple agent/time, dateAccepted, the software-vs-publisher distinction). It does not propose acceptance records.
   - **G4 no.** But it warns that owl:sameAs "can result in the confusion of provenance and ground truth" (PDF p.15), and it suggests element-level provenance for "contradictory" claims and for entity resolution (PDF p.12).
   - **G5 no.**
9. **Implications.**
   - Cite it to justify how we serialise acceptance records: named graphs or nanopublications are standards-compliant and scalable (Tables 5 and 8); avoid reification.
   - Keep identity decisions separate from owl:sameAs assertions.
10. **Reading depth.** PDF pp.1–25, all pages.

---

## Cross-paper verdict

| Gap | Carriero | Tsaneva | Zhang | Sikos |
|---|---|---|---|---|
| G1 | no | partly | no | no |
| G2 | no | no | no | no |
| G3 | no | no | no | partly |
| G4 | no | no | partly | no |
| G5 | no | partly | no | no |

- **G2** holds against all four papers.
- **G1 and G5** must be worded narrowly because of Tsaneva.
- **G3** should say "the acceptance record as practice", not "the representation", because of Sikos.

---

# Grup 6

## Group 6: ODKE+ and KARMA

## ODKE+

1. **Bib (p.1):** "ODKE+: Ontology-Guided Open-Domain Knowledge Extraction with LLMs". Khorshidi, Nikfarjam, Shankar, Sang, Govind, Jang, Kasgari, McClimans, Soliman, Konda, Fakhry, Qi. Apple Inc. arXiv:2509.04696v1 [cs.CL], 4 Sep 2025. No venue is printed; p.1 calls it a "system demonstration".
2. **What it does:** A production pipeline (Extraction Initiator, Evidence Retriever, pattern and LLM extractors, Grounder, Corroborator) that pulls facts from Wikipedia into Apple's KG. It covers 195 predicates in batch and streaming modes (p.1–3).
3. **LLM roles:** an extractor prompted with a per-type "ontology snippet" (p.4), and a second LLM acting as the Grounder judge (p.5, App. B p.8).
4. **Validation:** The Grounder turns each triple into an assertion and asks a second LLM whether it is "explicitly supported by the context" (Yes/No). Only Yes passes (p.5). This is LLM judgement, not a string-match test. The extractor prompt asks for "answer: Shortest surface form from passage" and keeps "normalized answer" as a separate field (p.8). Extractors "link them to their provenance spans" (p.3), but no step checks that the value occurs in a span. Schema: pattern rules are checked against KG type constraints (P19, p.4); "strict schema validation" (p.6). Entity resolution: ML entity linking, and a new entity is created when there is no match (p.5–6). Conflicts: the Corroborator normalises (Duckling), groups by subject and predicate, and scores candidates with heuristics or H2O AutoML. Its features include "Confidence or score from the extractor" (p.5).
5. **Human:** The KG Quality team "audits ≈2 000 randomly sampled triples each week". The system must stay at ≥95% precision (p.6). Weekly side-by-side annotation prefers ODKE+ "in roughly two-thirds of cases" (p.6). Nothing is routed to humans, and reviewer effort is not measured.
6. **Provenance:** exported triples carry "optional qualifiers and metadata such as provenance and confidence scores" (p.5). There is no acceptance record.
7. **Eval (Table 2, p.6):** 19M facts, 195 predicates, 4M pages, 48% coverage vs a third-party KG, 98.8% precision. The precision sample and method are not given. Also: 9M+ pages processed (p.1), 150–250K facts/day, <2h latency, +10% answerable facts, ~50 days fresher (p.6). Component effect (p.6): "Grounding reduced hallucinated extractions by 35%. Corroboration improved factual precision from 91% (raw LLM) to 98.8% post-ranking". There is no ablation table and no method for these figures.
8. **Gaps:**
   - **G1: partly.** Only the two figures quoted in item 7 (p.6). They come with no design or sample.
   - **G2: no.**
   - **G3: no.** The closest is the "metadata such as provenance and confidence scores" quote (p.5).
   - **G4: no.**
   - **G5: no.** Extractor confidence serves to rank candidates, not to route them to review.
9. **Must cite:** a deployed second-LLM grounding gate, and its separation of the surface form from the normalized answer, which is the same failure mode G2 targets. Its per-component numbers weaken any claim that "nobody measures checks" unless we specify a controlled ablation.
10. **Pages read:** 1–8 (all).

## KARMA

1. **Bib (p.1):** "KARMA: Leveraging Multi-Agent LLMs for Automated Knowledge Graph Enrichment". Yuxing Lu, Wei Wu, Xukai Zhao, Rui Peng, Jinzhuo Wang. 39th Conference on Neural Information Processing Systems (NeurIPS 2025). arXiv:2502.06472v2 [cs.CL], 11 Jan 2026.
2. **What it does:** LLM agents (Ingestion, Reader, Summarizer, Entity and Relation Extraction, Schema Alignment, Conflict Resolution, Evaluator) enrich a biomedical KG from PubMed papers (p.3–5).
3. **LLM roles:** every agent (p.4–6). DeepSeek-v3 performs "all LLM-based evaluations" (p.6).
4. **Validation:**
   - Entities pass a dictionary/ontology filter ⊙D_E (Eq.5).
   - Entity normalisation is an embedding argmin. If the distance is >ρ, the entity is "flagged as new" (Eq.6, p.5).
   - Relations need a probability ≥θ_r (Eq.7–8).
   - The Schema Alignment Agent (SAA) classifies the type and "flags v or r as candidate additions for review" (p.5).
   - The Conflict Resolution Agent (CRA) runs an LLM debate (Agree/Contradict) against an existing triple t′ (Eq.11).
   - The Evaluator integrates a triple if mean(C, Cl, R) ≥ Θ (Eq.15, p.6).
   - No check tests that the triple or value appears in the source text.
5. **Human:** "If LLM_CRA yields Contradict, t is then discarded or queued for manual expert review, depending on the system's confidence" (p.5). Two human experts give R_HE (p.7). Reviewer effort is not measured.
6. **Provenance:** only document metadata (journal, date, authors; p.4). No per-fact record.
7. **Eval:** 1,200 PubMed papers: 720 genomics, 360 proteomics, 120 metabolomics (p.6). No gold standard. Table 1 (p.7), DeepSeek-v3 on genomics: Δ_Cov 38,230, R_LC 0.831, R_CR 0.186, R_HE 0.625. Ablation in Table 2 (p.9): w/o Summarizer, w/o Conflict Resolution, w/o Evaluator. Full KARMA is best on R_HE in all three domains (0.625, 0.625, 0.580). The p.9 text labels the deltas inconsistently: "C_QA drop 4.9% (0.831→0.790)" uses values from the column headed R_CR. The Full-model values in that column also do not match Table 1's R_CR.
8. **Gaps:**
   - **G1: partly.** Table 2 (p.9) removes the validation agents and measures the effect. The metrics are judged by an LLM, and the ablated units are agents, not individual checks.
   - **G2: no.**
   - **G3: no.**
   - **G4: no.**
   - **G5: no.** Routing is "depending on the system's confidence" (p.5) and is never compared with check-based routing.
9. **Must cite:** an ablation of validation components exists, so G1 must be framed as a deterministic, per-check ablation with a human reference. KARMA also routes contradictions to experts.
10. **Pages read:** 1–9, the whole downloaded PDF. The appendix (§8–9) and the reference list are not in this PDF.
