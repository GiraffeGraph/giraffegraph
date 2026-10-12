# LLM Başarı Ölçüm Metrikleri — Tam Akademik Review'lar (NotebookLM, 300 kelime)

**Sorumlu:** Efe · **Konu:** LLM evaluation / success metrics
**Üretim:** Her makale ayrı NotebookLM notebook'unda, toplantı notundaki **tam** akademik review promptuyla (5 madde, max 300 kelime). Metinler NotebookLM çıktısı (kaynak PDF'ten grounded), düzenlenmeden.
**Kaynak liste + arXiv:** `efe_llm_eval_metrics_review.md` · **APA bölüm taslağı:** `efe_literature_review_section.md`

---

## A. Genel LLM Değerlendirme — Survey ve Çerçeveler

### [01] Chang et al. (2023) — A Survey on Evaluation of LLMs · arXiv:2307.03109
**Research Gap:** Chang et al. (2023) address the fragmented landscape of LLM assessment by highlighting the need for comprehensive evaluation frameworks. As LLMs become ubiquitous, evaluation must extend beyond standard task-level performance to critically assess broader societal impacts and potential risks.
**Data and Methodology:** As a comprehensive survey, the study synthesizes existing literature and benchmarks rather than generating novel empirical data. The authors conduct a systematic review organized around three key dimensions—"what," "where," and "how" to evaluate—analyzing evaluation paradigms across NLP, reasoning, medicine, ethics, education, and agent applications.
**Main Contributions:** The primary contribution is a structured, multidimensional taxonomy of LLM evaluation methods and benchmarks. It further synthesizes current model capabilities by systematically documenting explicit success and failure cases of LLMs across diverse tasks.
**Relevance to the Field:** This work provides a centralized, foundational roadmap for researchers. It advocates a critical paradigm shift, arguing that evaluation should be treated as an "essential discipline" rather than an afterthought—vital for guiding the safe and proficient development of future LLMs.
**Future Work / Limitations:** The survey explicitly sheds light on "future challenges that lie ahead" in LLM evaluation, acknowledging the critical need for evaluation methodologies to continuously adapt and evolve alongside rapidly advancing LLM capabilities.

### [02] Guo et al. (2023) — Evaluating LLMs: A Comprehensive Survey · arXiv:2310.19736
**Research Gap:** While LLMs demonstrate remarkable capabilities, they introduce critical risks such as data privacy breaches, harmful content generation, and the unchecked advancement of superintelligent systems. Guo et al. address the urgent need for rigorous, comprehensive evaluation frameworks to establish adequate safeguards.
**Data and Methodology:** As a comprehensive survey, the study relies on a systematic review of existing literature, methodologies, and benchmarks. The authors employ a categorical methodology, organizing the landscape into three primary dimensions: knowledge and capability, alignment, and safety.
**Main Contributions:** The study provides a "panoramic perspective" on LLM assessment. Beyond its tripartite classification, it compiles a compendium of evaluations across specialized domains and outlines the architecture for constructing holistic evaluation platforms addressing capability, alignment, safety, and applicability.
**Relevance to the Field:** By structuring the highly fragmented domain into a cohesive framework and positioning robust evaluation as the "cornerstone" of responsible AI development, the survey guides LLM evolution toward maximizing societal benefits while minimizing risks.
**Future Work / Limitations:** The authors frame the survey as a catalyst to stimulate further research, emphasizing that future work must focus on the ongoing construction of comprehensive evaluation platforms capable of adapting to evolving LLM capabilities and specialized applications.

### [03] Laskar et al. (2024) — A Systematic Survey & Critical Review on Evaluating LLMs · arXiv:2407.04069 (EMNLP 2024)
**Research Gap:** Laskar et al. address the critical lack of standardization in assessing LLMs. The inherent complexity of current assessment processes has yielded highly fragmented setups, creating a significant gap that leads to inconsistent findings and unreliable interpretations of model performance across the literature.
**Data and Methodology:** The study employs a systematic survey methodology to critically examine the existing landscape of LLM evaluation frameworks, isolating challenges across various steps of the evaluation pipeline. (NotebookLM yalnız abstract+metadata'ya erişti; örnek sayısı/dahil-etme kriterleri belirsiz.)
**Main Contributions:** The systematic identification of bottlenecks causing inconsistent and unreliable evaluations. Building on this, the authors propose a synthesized set of perspectives and strategic recommendations to ensure future evaluations are reproducible, reliable, and robust.
**Relevance to the Field:** Accepted at EMNLP 2024, the paper diagnoses the root causes of evaluation inconsistencies and provides a foundational roadmap for standardizing benchmarking practices as LLM integration accelerates.
**Future Work / Limitations:** The conceptual nature of the recommendations means future empirical research will be required to operationalize and validate these proposed protocols across emerging LLM architectures.

### [04] Liang et al. (2022) — Holistic Evaluation of Language Models (HELM) · arXiv:2211.09110
**Research Gap:** The rapid integration of LMs into major technologies has outpaced understanding of their capabilities, risks, and limitations. Prior to this study, LM evaluation was severely fragmented, with models tested on an average of merely 17.9% of core scenarios, obstructing rigorous comparative analysis and leaving critical vulnerabilities unassessed.
**Data and Methodology:** A multi-metric benchmarking framework evaluating 30 prominent LMs (open, limited-access, closed) under standardized conditions. The methodology diverges from accuracy-centric evaluation by assessing seven metrics (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency) across 16 core and 26 targeted scenarios.
**Main Contributions:** The HELM framework, which improved core scenario benchmarking coverage to 96.0%. The study surfaced 25 top-level findings, exposed trade-offs between competing metrics, and publicly released a modular toolkit alongside all raw prompts and completions for transparency.
**Relevance to the Field:** HELM shifts LM assessment from siloed, single-metric testing to a unified, comprehensive standard, ensuring crucial metrics like fairness and toxicity are measured alongside accuracy—a diagnostic baseline vital for responsible foundation-model development.
**Future Work / Limitations:** The authors acknowledge coverage limitations (e.g., QA for neglected English dialects, lack of robust trustworthiness metrics). HELM is conceptualized as a "living benchmark" requiring continuous, community-driven updates.

### [05] Joshi (2025) — Evaluation of LLMs: Review of Metrics, Applications, Methodologies · Preprints.org 202504.0369
**Research Gap:** Joshi addresses the lack of standardized, domain-specific evaluation frameworks, critiquing ad-hoc methods that fail to capture multidimensional LLM capabilities and highlighting the stark performance disparity between structured tasks and open-ended reasoning in specialized fields.
**Data and Methodology:** Grounded in a systematic review of 70+ studies, a mixed-methods approach synthesizes quantitative metrics, mathematical models, and qualitative insights, proposing a Composite Evaluation Index (CEI) integrating accuracy, entropy-based stability, and domain-specific weighting.
**Main Contributions:** A hierarchical taxonomy of 50+ evaluation metrics and domain-specific adaptive weighting for finance, medicine, and law. It quantifies critical limitations, verifying a 36.4% output variance on repeated queries and a 28% hallucination rate.
**Relevance to the Field:** Bridges technical performance metrics with real-world deployment safety, supporting practitioners deploying LLMs in high-stakes environments and addressing workforce training implications.
**Future Work / Limitations:** Acknowledges the subjectivity of language assessment, output variability without ground truth, and high computational cost; calls for standardized cross-domain benchmarks, real-time observability, and explainable-AI integration. *(Hakem sürecini tamamlamamış preprint.)*

---

## B. Klasik NLG / Metin Üretim Metrikleri

### [06] Zhang et al. (2019) — BERTScore · arXiv:1904.09675
**Research Gap:** Common automatic evaluation metrics are structurally constrained by reliance on exact token matches between reference and candidate sentences, struggling to capture semantic similarity when diverse phrasing or synonyms are used.
**Data and Methodology:** The authors compute token similarity through contextual embeddings rather than exact string matching. Evaluated using outputs of 363 distinct machine translation and image captioning systems, plus an adversarial paraphrase detection task.
**Main Contributions:** Empirical validation that BERTScore correlates better with human judgments and provides stronger model selection performance than prior n-gram metrics, and is significantly more robust on adversarially paraphrased examples.
**Relevance to the Field:** A significant methodological advancement: by leveraging contextual embeddings, it aligns automated scoring more closely with human semantic understanding, offering a reliable, context-aware benchmarking tool.
**Future Work / Limitations:** (Abstract dışı, doğrula) — increased computational overhead vs. n-gram matching, and potential blind spots/biases inherited from the underlying pre-trained networks.

### [07] Sellam et al. (2020) — BLEURT · arXiv:2004.04696
**Research Gap:** Traditional metrics (BLEU, ROUGE) correlate poorly with human judgments, creating a critical gap requiring evaluation frameworks aligned with human assessment rather than surface-level heuristics.
**Data and Methodology:** BLEURT, a learned metric on the BERT architecture. To counter overfitting from few/biased training examples, the authors introduce a novel pre-training scheme leveraging millions of synthetic examples to enhance generalization before fine-tuning.
**Main Contributions:** State-of-the-art on the WebNLG Competition dataset and the last three years of the WMT Metrics shared tasks. Crucially, it yields superior results even on scarce and out-of-distribution data compared to vanilla BERT.
**Relevance to the Field:** Advances how the field benchmarks modern NLG by shifting toward robust, learned evaluation models that generalize well under diverse, challenging conditions.
**Future Work / Limitations:** The persistent scarcity and potential bias of human-judgment datasets; reliance on synthetic pre-training implies a need to critically evaluate whether synthetic examples introduce new biases.

### [08] Yuan et al. (2021) — BARTScore · arXiv:2106.11520
**Research Gap:** A major challenge in NLP applications (MT, dialog, summarization) is accurately evaluating whether generated texts are fluent, accurate, or effective.
**Data and Methodology:** Reframes evaluation as a text generation problem using pre-trained seq2seq architectures. Operationalized with BART in an unsupervised manner, measuring the model's ability to convert generated text to/from a reference or source; tested across 16 datasets.
**Main Contributions:** BARTScore and variants outperformed existing top-scoring metrics in 16 of 22 test settings; an interactive meta-evaluation leaderboard on ExplainaBoard.
**Relevance to the Field:** A conceptually simple yet highly flexible framework assessing text from 7 perspectives (e.g., informativeness, factuality), demonstrating that robust generation models inherently possess multidimensional evaluation capabilities.
**Future Work / Limitations:** The ExplainaBoard platform supports ongoing scrutiny of the strengths, weaknesses, and complementarity of BARTScore alongside other metrics.

### [09] Celikyilmaz et al. (2020) — Evaluation of Text Generation: A Survey · arXiv:2006.14799
**Research Gap:** As neural NLG models and novel generative tasks rapidly evolve, there is a critical need to systematically assess how these advanced systems are evaluated; the study synthesizes recent developments and identifies ongoing challenges.
**Data and Methodology:** A comprehensive literature survey categorizing NLG evaluation into three paradigms: human-centric metrics, automatic metrics requiring no training, and machine-learned metrics; grounded in summarization and long-text generation examples.
**Main Contributions:** A structured tripartite taxonomy of the contemporary NLG evaluation ecosystem, delineating both progress and persistent challenges within each category.
**Relevance to the Field:** Robust evaluation remains a significant bottleneck for AI; by focusing on recently proposed tasks and neural models, the survey offers a foundational guide to selecting, critiquing, and developing appropriate metrics.
**Future Work / Limitations:** The authors conclude by proposing targeted future research directions, positioning the survey as a catalyst for continued methodological advancement.

### [10] Klasik Metrikler — BLEU (Papineni et al. 2002) / ROUGE (Lin 2004) / METEOR (Banerjee & Lavie 2005)
*(NotebookLM: kaynaklar yalnız bibliyografik metadata; metodoloji detayı kısmen dış-bilgi, doğrula.)*
**Research Gap:** Historically, evaluating MT and summarization required expensive, time-consuming human judgment. BLEU addressed the need for rapid, automated MT evaluation; ROUGE filled the equivalent gap for summary evaluation; METEOR later targeted BLEU's strict exact-matching deficiency to improve correlation with human judgments.
**Data and Methodology:** BLEU employs modified n-gram precision with a brevity penalty; ROUGE measures n-gram recall and longest common subsequences; METEOR computes a harmonic mean of unigram precision and recall (recall-weighted) with a flexible matching pipeline incorporating exact matches, stemming, and WordNet synonymy.
**Main Contributions:** BLEU pioneered the n-gram overlap paradigm, making iterative MT training viable; ROUGE provided the standardized summarization toolkit; METEOR introduced linguistic flexibility, improving correlation with human evaluators.
**Relevance to the Field:** Together these metrics established the methodological bedrock of automated NLP evaluation, enabling the quantitative benchmarking that drove statistical and early neural language models.
**Future Work / Limitations:** Dependence on surface-level lexical overlap means they struggle with deep semantic equivalence, fail to reward creative paraphrasing, and cannot reliably penalize structural incoherence—motivating later neural/embedding-based metrics (e.g., BERTScore, COMET).

---

## C. Faithfulness / Factual Consistency Metrikleri

### [11] Li et al. (2022) — Faithfulness in NLG: A Systematic Survey · arXiv:2203.05227
**Research Gap:** Despite NLG advances, generating unfaithful or non-factual text remains a critical bottleneck; prior studies of the "faithfulness problem" were highly fragmented across tasks, lacking a cohesive synthesis.
**Data and Methodology:** A comprehensive systematic review synthesizing analytical, evaluative, and optimization approaches across abstractive summarization, dialogue generation, MT, and data-to-text into a unified comparative taxonomy.
**Main Contributions:** Structural unification of the faithfulness literature; by organizing disconnected methods into a single taxonomy, it facilitates cross-task learning and consolidates problem analysis, evaluation metrics, and optimization methods.
**Relevance to the Field:** The faithfulness deficit fundamentally restricts deployment of fluent, controllable NLG; establishing this cross-task baseline is theoretically and practically crucial.
**Future Work / Limitations:** The authors discuss several future research trends. (NotebookLM yalnız abstract'a erişti; tam taksonominin ampirik sağlamlığı bu metinden değerlendirilemiyor.)

### [12] Lamsiyah et al. (2025) — Trust but Verify: A Comprehensive Survey of Faithfulness Evaluation Methods · RANLP 2025
**Research Gap:** Prior surveys lack a focused, up-to-date (2020–2025) synthesis of faithfulness evaluation in abstractive summarization, particularly regarding LLM-driven metrics and domain-specific benchmarks. The authors review 40+ studies to bridge this.
**Data and Methodology:** A unified taxonomy classifying frameworks into human assessment, meta-evaluation, and automatic metrics (lexical, QA-based, NLI-based, graph-based, LLM-based); comparative analysis of general, long-form, and domain-specific benchmarks.
**Main Contributions:** Maps the evaluation landscape, highlighting persistent misalignment between automatic metrics and human judgments, and synthesizes structural limitations (NLI domain fragility, QA computational cost, LLM-evaluator opacity).
**Relevance to the Field:** Problematizes the "gold standard" of human evaluation via low inter-annotator agreement; framing human judgment as a subjective "moving target," it guides the field toward robust, graded, machine-verifiable metrics.
**Future Work / Limitations:** Reliance on reported claims without independent empirical validation; prioritizes breadth over depth. Calls for hybrid metrics, graded (not binary) scales, and rigorous cross-domain benchmarks to mitigate LLM-as-judge biases.

### [13] Fabbri et al. (2021) — QAFactEval · arXiv:2112.08542 (NAACL 2022)
**Research Gap:** A persistent methodological divide between entailment-based and QA-based evaluation paradigms, with inconsistent experimental setups producing contradictory conclusions about which is superior.
**Data and Methodology:** An extensive comparative analysis of both paradigms; rather than building a new model, the authors systematically optimize QA-metric components—question generation and answerability classification—evaluated on the SummaC benchmark.
**Main Contributions:** QAFactEval, achieving a 14% average improvement over previous QA-based metrics on SummaC and outperforming the best entailment-based metric; the insight that entailment and QA approaches produce complementary signals.
**Relevance to the Field:** Factual consistency is a prerequisite for safe deployment of summarization; by resolving conflicting conclusions, the work provides a rigorously tested, superior standard.
**Future Work / Limitations:** Because the two paradigms are complementary, future work should combine them into a single unified metric for further gains.

### [14] Zhang et al. (2024) — A Comparative Analysis of Faithfulness Metrics and Humans in Citation Evaluation · arXiv:2408.12398 (LLM4Eval@SIGIR)
**Research Gap:** Prior literature treats automated citation-support estimation as binary classification, neglecting fine-grained support levels—specifically partial support—that are essential in practical LLM applications.
**Data and Methodology:** A comparative evaluation framework expanding citation assessment into three categories (full, partial, no support), measuring alignment between automated faithfulness-metric scores and human judgments via correlation, classification, and retrieval evaluation.
**Main Contributions:** No single faithfulness metric consistently excels across all evaluation types; even the best metrics struggle to distinguish partial support from full or no support, yielding practical recommendations for better metrics.
**Relevance to the Field:** Directly relevant to mitigating LLM hallucinations and to source-cited (isnad) answers; it exposes the inadequacy of binary evaluations and the need for verifiable RAG systems.
**Future Work / Limitations:** The study diagnoses failures rather than introducing a metric that resolves the partial-support problem; future research must operationalize these recommendations without heavy reliance on human judgment.

---

## D. Hallucination & Factuality Benchmark/Metrikleri

### [15] Lin et al. (2021) — TruthfulQA · arXiv:2109.07958
**Research Gap:** Assessing whether language models avoid generating false answers learned from imitating human texts. While scaling generally improves task performance, the study investigates models' specific vulnerability to reproducing human falsehoods and misconceptions.
**Data and Methodology:** The TruthfulQA benchmark—817 questions across 38 categories (health, law, finance, politics) crafted to elicit false beliefs—evaluating GPT-3, GPT-Neo/J, GPT-2, and a T5-based model against human performance.
**Main Contributions:** An inverse-scaling trend: the largest models are generally the least truthful. The best model reached only 58% truthfulness vs. a 94% human baseline, confirming models mimic popular misconceptions embedded in their training distribution.
**Relevance to the Field:** Challenges the consensus that performance universally improves with model size, and highlights a critical AI-safety concern: models can deceive humans by confidently reproducing learned falsehoods.
**Future Work / Limitations:** Because false answers are a training-distribution artifact, scaling alone is unpromising; future research must develop fine-tuning objectives other than mere imitation of web text.

### [16] Li et al. (2023) — HaluEval · arXiv:2305.11747 (EMNLP 2023)
**Research Gap:** LLMs like ChatGPT frequently generate hallucinations—unverifiable content or content contradicting source material—and there was a clear need to systematically understand the types and extent of these hallucinations.
**Data and Methodology:** HaluEval, a large-scale benchmark using a hybrid approach: a ChatGPT-driven "sampling-then-filtering" framework supplemented with human-annotated hallucinated samples.
**Main Contributions:** Empirical evidence that ChatGPT fabricates unverifiable information in ~19.5% of responses on specific topics; while LLMs struggle to independently recognize hallucinations, providing external knowledge or reasoning steps significantly improves detection.
**Relevance to the Field:** Accepted to EMNLP 2023, it advances the field from observing hallucinations to providing a standardized diagnostic benchmark for testing and improving factual reliability.
**Future Work / Limitations:** Heavy reliance on a ChatGPT-based generation framework may bias the benchmark toward ChatGPT's hallucination patterns, limiting generalizability to other architectures. *(Analitik çıkarım; açık future-work abstract'ta yok.)*

### [17] Manakul et al. (2023) — SelfCheckGPT · arXiv:2303.08896
**Research Gap:** Existing fact-checking mechanisms depend on either inaccessible output-probability distributions or complex external knowledge databases, leaving a gap for verifying black-box LLM reliability.
**Data and Methodology:** SelfCheckGPT, a zero-resource, sampling-based method premised on the hypothesis that factual knowledge yields consistent responses while hallucinations cause stochastic divergence. Tested with GPT-3 on WikiBio biographies with manual factuality annotation.
**Main Contributions:** Validates response consistency as an effective proxy for hallucination detection; distinguishes factual from non-factual sentences, outperforming grey-box baselines with higher AUC-PR (sentence-level) and improved passage-level correlation.
**Relevance to the Field:** Operating independently of external databases and internal architecture, it offers a scalable, practical tool to audit opaque generative systems—valuable where a gold source is hard to obtain (e.g., religious answers).
**Future Work / Limitations:** Empirically validated only on biographical passages (WikiBio), indicating a need to test robustness across broader, more complex reasoning domains; consistency may equate to factuality and miss consistently-produced falsehoods.

### [18] Min et al. (2023) — FActScore · arXiv:2305.14251 (EMNLP 2023)
**Research Gap:** Binary factuality judgments are inadequate for long-form generation, which mixes supported and unsupported claims, while manual human evaluation remains prohibitively expensive.
**Data and Methodology:** FActScore decomposes generated text into atomic facts and computes the percentage supported by a reliable knowledge source. Initial human evaluation of biographies (InstructGPT, ChatGPT, PerplexityAI), then an automated estimator using retrieval plus a strong base LM.
**Main Contributions:** The FActScore metric and its automated estimator (<2% error). Applied to 6,500 generations across 13 LMs, finding proprietary models (GPT-4, ChatGPT) more factual than public models (Vicuna, Alpaca leading the open-source set).
**Relevance to the Field:** A scalable, fine-grained factuality metric; circumventing high human-labor cost (≈$26K saved for 6,500 generations), it lets developers precisely diagnose hallucination rates in long-form generation.
**Future Work / Limitations:** Reliance on "people biographies" as the sole domain and dependence on an accessible reliable knowledge source plus a strong evaluating LM; robustness across diverse/complex/domain-specific tasks needs future validation.

### [19] Huang et al. (2023) — Survey on Hallucination in LLMs · arXiv:2311.05232
**Research Gap:** The general-purpose, open-ended nature of LLMs introduces distinct hallucination vulnerabilities (unlike task-specific models), creating an urgent need for a synthesized framework explaining why models generate plausible yet nonfactual content.
**Data and Methodology:** A comprehensive literature survey synthesizing recent advances; the analytical methodology centers on an innovative taxonomy of LLM hallucinations, mapping contributing factors and evaluating detection benchmarks and mitigation strategies.
**Main Contributions:** A holistic, structural mapping of the hallucination lifecycle; by detailing causal factors and evaluating representative detection/mitigation methods—and critically assessing retrieval-augmented LLM vulnerabilities—it builds a cohesive foundation.
**Relevance to the Field:** Highly relevant to information-retrieval systems; as LLMs drive a paradigm shift in information acquisition, addressing nonfactual content is essential for reliable, safe deployment.
**Future Work / Limitations:** Current retrieval-augmented systems remain limited in combating hallucinations; future directions include hallucination in large vision-language models and a deeper theoretical understanding of LLM "knowledge boundaries."

### [20] Rahman et al. (2025) — Hallucination to Truth: Fact-Checking & Factuality Review · Springer AI Review, doi:10.1007/s10462-025-11454-w (arXiv:2508.03860)
**Research Gap:** Prior reviews neglect the impact of dataset quality—particularly domain-specific constraints—and under-examine the practical implementation challenges of RAG architectures.
**Data and Methodology:** A systematic literature review analyzing 64 articles (2021–2025) from Scopus, Web of Science, and arXiv (14,685 records screened to 64), filtered through five research questions on metrics, hallucination, datasets, prompting, and RAG.
**Main Contributions:** A comprehensive taxonomy of evaluation metrics and an overview of mitigation strategies (adversarial training, multi-agent systems), plus novel insight into how dataset characteristics (domain specificity, annotation quality, multilingual coverage) dictate fact-checking efficacy.
**Relevance to the Field:** Addresses high-stakes deployment (medicine, law); shifts the paradigm from static parametric knowledge toward dynamic, iterative RAG grounded in verifiable external evidence, emphasizing domain-specific adaptation.
**Future Work / Limitations:** Vulnerable to the rapid velocity of LLM innovation; advocates dynamic evaluation suites resilient to evolving adversarial misinformation and a shift from reactive correction to proactive prevention architectures.

### [21] Rahman et al. (2024) — DefAn: Definitive Answer Hallucination Dataset · arXiv:2406.09155
**Research Gap:** Current hallucination datasets are inadequately small and over-rely on multiple-choice formats, failing to assess models' true generative capabilities.
**Data and Methodology:** DefAn—75,000+ prompts across eight domains—evaluating six LLMs (GPT-3.5, LLaMA 2/3, Gemini, Mixtral, Zephyr) via a dual-segment (public + hidden) approach designed to elicit definitive, concise, informative generative responses.
**Main Contributions:** Empirical quantification of widespread vulnerabilities: factual hallucination up to 82%, prompt misalignment up to 95%, consistency as low as 21%; granular analysis showing major degradation on numeric queries (better on person/location/date).
**Relevance to the Field:** Shifts hallucination evaluation from restrictive multiple-choice to a large-scale generative framework, providing a pragmatic diagnostic tool for exposing factual contradictions.
**Future Work / Limitations:** The explicit focus on "concise/definitive" answers may not capture hallucinations in complex, long-form, or open-ended reasoning—an avenue for future inquiry. *(Analitik gözlem.)*

### [22] Bang et al. (2025) — HalluLens: LLM Hallucination Benchmark · arXiv:2504.17550
**Research Gap:** The lack of a unified evaluation framework; existing literature conflates hallucination with general "factuality," and current benchmarks suffer rapid saturation and training-data-leakage vulnerability.
**Data and Methodology:** HalluLens evaluates both intrinsic and novel extrinsic hallucination tasks, employing dynamic test-set generation (a shift from static datasets) to ensure robustness and mitigate leakage, plus an analytical review of existing benchmarks.
**Main Contributions:** A taxonomy strictly disentangling hallucination from factual inaccuracy; a new framework integrating dynamic data regeneration and extrinsic tasks assessing instances where LLM outputs contradict training data.
**Relevance to the Field:** Targets hallucinations that undermine user trust; by establishing categorical definitions and addressing saturation, it provides resilient, standardized infrastructure for evaluating evolving LLMs.
**Future Work / Limitations:** Dynamic test generation implies future benchmarking paradigms must continuously adapt to remain robust against persistent training-data contamination.

---

## E. RAG Değerlendirme Çerçeveleri (proje çekirdeği)

### [23] Es et al. (2023) — RAGAS · arXiv:2309.15217 (EACL 2024)
**Research Gap:** Evaluating RAG is multi-dimensional and complex, traditionally relying on ground-truth human annotations, creating bottlenecks in system evaluation and development.
**Data and Methodology:** A novel "reference-free" framework employing a suite of automated metrics to independently evaluate distinct RAG components—retrieval of focused context and faithful exploitation by the LLM—without human-annotated ground truth.
**Main Contributions:** The Ragas framework, which automatically and simultaneously assesses retrieval focus, LLM faithfulness, and overall generation quality.
**Relevance to the Field:** By drastically accelerating evaluation cycles without the cost and time of human annotation, it is a major methodological advance—directly applicable as GiraffeGraph's RAG measurement tool.
**Future Work / Limitations:** An inherent limitation of any reference-free approach is the ongoing need to validate automated metrics against complex human judgments across diverse databases. *(Analitik çıkarım.)*

### [24] Saad-Falcon et al. (2023) — ARES · arXiv:2311.09476
**Research Gap:** RAG evaluation traditionally relies on resource-intensive hand annotations for queries, passages, and responses, hindering rapid, cost-effective validation.
**Data and Methodology:** ARES uses synthetic training data to fine-tune lightweight LM judges, evaluated across eight knowledge-intensive tasks (KILT, SuperGLUE, AIS); prediction-powered inference (PPI) with minimal human annotation statistically mitigates prediction errors.
**Main Contributions:** An automated pipeline assessing context relevance, answer faithfulness, and answer relevance; the judges remain accurate even under domain shifts (changed query types or documents).
**Relevance to the Field:** Demonstrates reliable RAG evaluation with only a few hundred human annotations, providing a scalable, cost-efficient benchmarking tool without sacrificing statistical confidence.
**Future Work / Limitations:** Still requires a baseline of human annotation for PPI; future work may explore fully zero-shot evaluation removing the human-in-the-loop. *(Analitik çıkarım.)*

### [25] Chen et al. (2023) — Benchmarking LLMs in RAG (RGB) · arXiv:2309.01431
**Research Gap:** While RAG is widely adopted to mitigate hallucinations, there is a lack of rigorous evaluation of its specific capability bottlenecks and operational impact across different LLMs.
**Data and Methodology:** RGB, a bilingual (English/Chinese) corpus; six LLMs evaluated across four fundamental RAG competencies: noise robustness, negative rejection, information integration, and counterfactual robustness.
**Main Contributions:** Empirically deconstructs RAG vulnerabilities—LLMs show baseline noise robustness but struggle with negative rejection, multi-source integration, and navigating false information.
**Relevance to the Field:** Challenges the monolithic view of RAG as a definitive cure for hallucinations; RGB is a diagnostic tool isolating model-specific structural weaknesses—relevant for noisy/conflicting religious sources.
**Future Work / Limitations:** A "considerable journey ahead"; future algorithmic work must enhance intrinsic mechanisms for rejecting irrelevant context and resisting counterfactuals, not just retrieval accuracy.

### [26] Lyu et al. (2024) — CRUD-RAG · arXiv:2401.17043 (ACM TOIS)
**Research Gap:** Existing RAG benchmarks are narrow (mostly QA) and typically isolate the LLM component, neglecting retrieval mechanisms and external knowledge databases.
**Data and Methodology:** A large-scale Chinese benchmark organized around a novel CRUD (Create, Read, Update, Delete) taxonomy; the end-to-end pipeline (retrievers, context length, knowledge-base construction) is evaluated across datasets for content generation, complex reading, text revision, and summarization.
**Main Contributions:** Shifts RAG evaluation from a generation-centric focus to a comprehensive multi-component framework, providing actionable insights for optimizing RAG in complex scenarios.
**Relevance to the Field:** Improves ecological validity; the CRUD taxonomy is an operationally valid standard for measuring how external databases integrate with LLMs across real-world text-manipulation tasks.
**Future Work / Limitations:** Exclusive Chinese-language focus; future research must adapt CRUD to multilingual datasets to confirm generalizability. *(Analitik çıkarım.)*

### [27] Park et al. (2025) — MIRAGE · arXiv:2504.17137 (NAACL 2025 Findings)
**Research Gap:** The complex interplay between retrieval and generation has produced a scarcity of benchmarks enabling detailed, component-specific assessment.
**Data and Methodology:** MIRAGE—7,560 curated QA instances mapped to a controlled retrieval pool of 37,800 entries—enabling isolated evaluation of generation and retrieval across diverse retriever-LLM configurations.
**Main Contributions:** A metric-intensive framework evaluating RAG adaptability through novel dimensions: noise vulnerability, context acceptability, context insensitivity, and context misinterpretation; uncovers optimal model-pair alignment.
**Relevance to the Field:** Accepted to NAACL 2025 Findings; an open-sourced, standardized diagnostic tool for auditing RAG architectures.
**Future Work / Limitations:** Confined to QA tasks, limiting direct applicability to open-ended reasoning or multi-document summarization; future work should extend these dimensions to broader generative tasks.

### [28] Oche et al. (2025) — A Systematic Review of Key RAG Systems · arXiv:2507.18910
**Research Gap:** The fragmented transition of RAG from theoretical open-domain applications to enterprise deployments needs consolidated frameworks addressing proprietary data integration, security, and scalability.
**Data and Methodology:** A systematic review with year-by-year longitudinal analysis; diverse RAG implementations benchmarked on retrieval accuracy, generation fluency, computational efficiency, and latency.
**Main Contributions:** Critically deconstructs RAG into retrieval mechanisms, seq2seq generation models, and fusion strategies; evaluates enterprise deployment challenges, bridging academic models and industry requirements.
**Relevance to the Field:** Provides a cohesive roadmap for building reliable, context-aware NLP systems that mitigate hallucinations and outdated parametric knowledge.
**Future Work / Limitations:** Persistent retrieval-quality bottlenecks, integration overhead, and privacy concerns; advocates hybrid retrieval, privacy-preserving techniques, optimized fusion, and agentic RAG architectures.

---

## F. LLM-as-a-Judge

### [29] Zheng et al. (2023) — Judging LLM-as-a-Judge with MT-Bench & Chatbot Arena · arXiv:2306.05685
**Research Gap:** Traditional benchmarks inadequately evaluate the broad, open-ended capabilities of LLM chat assistants and their alignment with human preferences.
**Data and Methodology:** Two frameworks—MT-Bench (multi-turn questions) and Chatbot Arena (crowdsourced battles)—with 3,000 expert votes and 30,000 human-annotated conversations measuring agreement between LLM judges and human baselines (LLaMA, Vicuna variants).
**Main Contributions:** Strong LLM judges (GPT-4) achieve over 80% agreement with humans—mirroring human-to-human agreement; the authors diagnose evaluation biases and propose mitigations.
**Relevance to the Field:** Justifies LLM-as-a-judge as a scalable, explainable, cost-effective proxy for expensive human preference testing, complementary to traditional benchmarks.
**Future Work / Limitations:** Judges still exhibit position, verbosity, and self-enhancement biases and limited reasoning; future work must resolve these for unbiased, robust automated evaluation.

### [30] Liu et al. (2023) — G-Eval · arXiv:2303.16634 (EMNLP 2023)
**Research Gap:** Reference-based metrics (BLEU, ROUGE) correlate poorly with human judgments on creative/diverse tasks; early LLM-based reference-free evaluators paradoxically showed lower human alignment than medium-sized neural evaluators.
**Data and Methodology:** G-Eval employs LLMs with chain-of-thought (CoT) reasoning and a form-filling paradigm, evaluated on summarization and dialogue generation using GPT-4 as backbone.
**Main Contributions:** G-Eval (GPT-4) achieves a Spearman correlation of 0.514 with human assessments on summarization, outperforming prior methods by a large margin.
**Relevance to the Field:** Demonstrates that advanced LLMs, structured via CoT prompting, can function as effective reference-free metrics—a scalable alternative to human references for open-ended NLG.
**Future Work / Limitations:** LLM-based evaluators possess an inherent bias favoring LLM-generated texts; future research must mitigate self-preference bias to ensure objective evaluation.

### [31] Li et al. (2024) — LLMs-as-Judges: A Comprehensive Survey · arXiv:2412.05579
**Research Gap:** Rapid adoption of LLM evaluators has outpaced a unified framework to categorize and validate their deployment; the survey addresses this fragmentation.
**Data and Methodology:** Synthesizes existing literature across five dimensions: functionality, construction methodology, applications, meta-evaluation, and limitations.
**Main Contributions:** A definitive taxonomy systematizing the building and evaluation of LLM judges, plus a continuously updated online repository.
**Relevance to the Field:** At the intersection of CL and IR; because scalable evaluation is a critical bottleneck, it equips practitioners with theoretical and practical foundations for operationalizing automated evaluators.
**Future Work / Limitations:** Examines inherent limitations of LLM evaluators; mitigates survey obsolescence by maintaining a living, continuously updated repository.

---

## G. Knowledge Graph Soru-Cevap Değerlendirmesi (isnad graf)

### [32] Potdar et al. (2025) — Comprehensive Evaluation for a Large-Scale KGQA Service (Chronos) · arXiv:2501.17270
**Research Gap:** The lack of robust frameworks for evaluating complex, multi-component KGQA architectures at industry scale; real-world deployment requires rigorous, multi-faceted testing beyond theoretical mapping.
**Data and Methodology:** Chronos, a scalable evaluation framework processing diverse datasets, measuring both end-to-end accuracy and granular component-level metrics prior to system release.
**Main Contributions:** The architectural design of Chronos and its operationalization for data-driven decision-making; a pragmatic blueprint for testing multi-stage KGQA systems.
**Relevance to the Field:** At the intersection of CL and Databases; bridges theoretical NLP models and applied enterprise solutions, underscoring scrutiny of both final outputs and intermediate sub-component integrity—directly applicable to an isnad-graph query system.
**Future Work / Limitations:** Ongoing challenges in continuously measuring and improving live systems; abstract-only detail means future work should validate such frameworks against non-proprietary KGs for generalizability. *(Kısmen analitik gözlem.)*

### [33] Seo et al. (2022) — Structural Quality Metrics to Evaluate Knowledge Graphs · arXiv:2211.10011
**Research Gap:** Existing KG evaluations rely on scale-related indicators (volume of classes and properties), failing to capture internal structural quality and ontology utilization.
**Data and Methodology:** Six novel structural quality metrics assessing schema integrity and how actively instances and RDF triples utilize classes/properties; tested on Naver's 'Raftel' plus Wikidata, DBpedia, YAGO, Google Knowledge Graph, and Freebase.
**Main Contributions:** A framework redefining a "Good Knowledge Graph" by ontology detail and abundant real-world expression rather than size; the metrics expose structural characteristics hidden by volume-based indicators.
**Relevance to the Field:** A shift toward qualitative structural maturity over quantitative scale, offering a robust mechanism for diagnosing internal graph health—suited to measuring isnad-graph integrity and connectivity.
**Future Work / Limitations:** (Abstract-only) exclusive focus on general, cross-domain KGs; future research should test these metrics on domain-specific KGs and whether higher structural quality correlates with downstream task performance. *(Kısmen analitik.)*

### [34] Orogat et al. (2021) — CBench · arXiv:2105.00811
**Research Gap:** KGQA benchmark datasets vary drastically in linguistic, syntactic, and structural properties, so relying on a small subset is unreliable for assessing QA-system quality.
**Data and Methodology:** CBench, an extensible benchmarking suite analyzing QA systems across fine-grained structural, syntactic, and linguistic dimensions, integrating popular benchmarks augmentable with user-provided data.
**Main Contributions:** Shifts evaluation from reductive single-number metrics to a detailed diagnostic profile, analyzing the properties of both answered and unanswered questions to show where a system excels and struggles.
**Relevance to the Field:** Standardizes and deepens QA-evaluation rigor, equipping developers with granular analytical tools to understand model behavior beyond surface metrics.
**Future Work / Limitations:** Designed to facilitate evaluation "until further research improves the quality and comprehensiveness of benchmarks"; its analytical power is constrained by the quality and diversity of underlying benchmarks.

---

## H. Domain-Specific — Dini / İslami LLM Değerlendirme (en yakın bağlam)

### [35] Abdelaal et al. (2026) — IslamicMMLU · arXiv:2603.23750
**Research Gap:** While LLMs are increasingly consulted for religious inquiries, there is no comprehensive benchmark to formally evaluate their performance across core Islamic disciplines.
**Data and Methodology:** IslamicMMLU—10,013 multiple-choice questions across three tracks: Quran (2,013), Hadith (4,000), Fiqh (4,000)—systematically evaluating 26 LLMs and innovatively including a madhab (school of jurisprudence) bias-detection task in the Fiqh track.
**Main Contributions:** A public leaderboard exposing vast performance disparities (average accuracy 39.8%–93.8%, top by Gemini 3 Flash); frontier models significantly outperform Arabic-specific LLMs, and variable theological preferences are uncovered.
**Relevance to the Field:** Advances NLP and domain-specific evaluation; an open-source tool to audit LLMs for both factual reliability and latent doctrinal bias—essential for safe AI in religious contexts. Projenin doğrudan değerlendirme zemini.
**Future Work / Limitations:** Underperformance of Arabic-specific models signals a need for targeted culturally-specialized training; the multiple-choice format evaluates discriminative knowledge rather than the open-ended generative reasoning needed for complex theological consultation.

### [36] Bhatia et al. (2026) — From RAG to Agentic RAG for Faithful Islamic QA · arXiv:2601.07528
**Research Gap:** Islamic QA relies on MCQ/MRC evaluations that fail to assess real-world failure modes—free-form hallucinations and the capacity to abstain when evidence is insufficient—despite the severe religious implications of ungrounded responses.
**Data and Methodology:** IslamicFaithQA, a 3,810-item generative bilingual (Arabic/English) benchmark; an "agentic RAG" framework using structured tool calls for iterative evidence-seeking and answer revision, supported by 25K Arabic reasoning pairs, 5K bilingual preference samples, and a ~6K verse-level Qur'an corpus.
**Main Contributions:** Agentic RAG significantly outperforms standard RAG in correctness and Arabic-English robustness, achieving state-of-the-art even on compact models (Qwen3 4B); datasets publicly released.
**Relevance to the Field:** Shifts focus from static retrieval to dynamic, agentic verification in sensitive contexts; a new paradigm for evaluating LLM faithfulness and abstention. GiraffeGraph'a (mimari + metrik) literatürdeki en yakın referans.
**Future Work / Limitations:** The verse-level Qur'an focus suggests future expansion of agentic grounding to broader jurisprudential texts and Hadith collections. *(Analitik çıkarım.)*

### [37] Patel, Kane & Patel (2023) — Building Domain-Specific LLMs Faithful to the Islamic Worldview · arXiv:2312.06652 (NeurIPS 2023 Muslims-in-ML)
**Research Gap:** Mainstream LLMs perpetuate stereotypical biases and fabricate facts; there is a critical value-alignment gap requiring domain-specific systems that ensure accurate, factual representation of Islamic beliefs rooted in the Quran and Sunnah.
**Data and Methodology:** A conceptual framework that formalizes this open-ended goal as a technical problem, proposing solutions, critically analyzing each approach's challenges, and outlining evaluation methodologies.
**Main Contributions:** A foundational technical pathway to operationalize theological "faithfulness" within LLM architectures, with concrete development strategies and evaluation frameworks for a complex religious context.
**Relevance to the Field:** Relevant to AI ethics, value alignment, and cultural localization; advances discourse from identifying religious biases toward constructing culturally sensitive, aligned models.
**Future Work / Limitations:** Requires high-quality domain datasets and robust metrics; fundamentally requires interdisciplinary collaboration blending ML with formal Islamic scholarship.

### [38] Alzubaidi et al. (2025) — Evaluating Arabic LLMs: A Survey of Benchmarks · arXiv:2510.13430
**Research Gap:** The absence of unified evaluation standards in Arabic NLP; deficits include limited temporal evaluation, inadequate multi-turn dialogue assessment, and cultural misalignment from over-reliance on translated datasets.
**Data and Methodology:** Analyzes 40+ Arabic benchmarks and critically examines three creation approaches—native collection, translation, synthetic generation—evaluating trade-offs in authenticity, scale, and cost.
**Main Contributions:** A structured taxonomy with four pillars—Knowledge, NLP Tasks, Culture & Dialects, Target-Specific—plus analysis of reproducibility standards and metrics.
**Relevance to the Field:** As the first systematic review of its kind, a crucial reference moving the field from translation-centric testing toward culturally resonant evaluation; relevant to Quran/Hadith-language evaluation infrastructure.
**Future Work / Limitations:** Benchmarks are static and lack conversational depth; future development must prioritize dynamic temporal assessments and native multi-turn dialogue evaluation.

---

## Özet
- 38/38 makale, senin **tam** promptunla (5 madde, 300 kelime), her biri ayrı NotebookLM notebook'unda → grounded tam review.
- Bu dosya `efe_reviews.md`'nin (kısa Türkçe özet) yerini alan **tam İngilizce** versiyondur.
- Bu tam metinler Zotero notlarına da yazıldı (her makalenin altında `Akademik Review (NotebookLM)`).
