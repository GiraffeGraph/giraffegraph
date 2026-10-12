# Literatür Taraması — LLM Başarı Ölçüm Metrikleri

**Sorumlu:** Efe · **Konu:** LLM evaluation / success metrics
**Proje bağlamı:** GiraffeGraph — dini sorular için Knowledge Graph + RAG sistemi (hadis isnad zinciri graf modellemesi dahil). Bu nedenle **RAG değerlendirme, faithfulness/factuality ve KG-QA metrikleri** bu çalışma için en kritik kümeler.

**Makale sayısı:** 38 (hedef ≥20 karşılandı).
**Kullanım:** Aşağıdaki her başlık için NotebookLM özetleme promptunu (toplantı notundaki 300-kelime akademik review promptu) çalıştır → kritik değerlendirme üret. Aşağıdaki notlar başlangıç çerçevesi: her giriş **Gap / Veri-Metot / Katkı / Alan ilgisi / Sınırlama** eksenlerini özetler.

> ⭐ = proje için çekirdek, ilk oku.

---

## A. Genel LLM Değerlendirme — Survey ve Çerçeveler

**[1] ⭐ Chang et al. (2023). A Survey on Evaluation of Large Language Models.** arXiv:2307.03109
Alan haritasının temel referansı. *Gap:* dağınık eval literatürünün "what/where/how to evaluate" ekseninde birleştirilmemesi. *Metot:* görev (task), toplum (societal) ve yetenek bazlı taksonomi. *Katkı:* en çok atıf alan eval survey'lerinden; metrik+benchmark sınıflandırması. *İlgi:* literatür bölümünün omurgası, diğer 37 makaleyi konumlandırır. *Sınırlama:* hızlı eskime; 2023 sonrası RAG/judge gelişmelerini kapsamaz.

**[2] Guo et al. (2023). Evaluating Large Language Models: A Comprehensive Survey.** arXiv:2310.19736
*Gap:* güvenilirlik/uyum (alignment, safety) eksenli eval'ın metrik perspektifiyle bütünleşmemesi. *Metot:* knowledge & capability / alignment / safety üç katmanlı çerçeve. *Katkı:* risk-odaklı değerlendirme taksonomisi. *İlgi:* dini içerikte güvenlik/uyum kritik → doğrudan ilgili. *Sınırlama:* genişlik var, metrik-derinliği sınırlı.

**[3] (2024). A Systematic Survey and Critical Review on Evaluating LLMs: Challenges, Limitations, and Recommendations.** arXiv:2407.04069
*Gap:* mevcut eval pratiklerinin metodolojik zayıflıkları (kaçak veri, reprodüksiyon). *Metot:* sistematik kritik review. *Katkı:* benchmark kontaminasyonu, reliability açıkları üzerine öneriler. *İlgi:* kendi eval kurgunuzun geçerliliğini savunmak için. *Sınırlama:* çözüm değil teşhis ağırlıklı.

**[4] ⭐ Liang et al. (2022). Holistic Evaluation of Language Models (HELM).** Stanford CRFM · arXiv:2211.09110
*Gap:* tek-metrik benchmark'ların (örn. yalnız accuracy) dar kalması. *Metot:* çok-metrikli (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency) standart senaryolar. *Katkı:* "holistic" çok-boyutlu eval paradigması, canlı leaderboard. *İlgi:* dini QA'da accuracy + calibration + bias birlikte ölçülmeli → metodolojik şablon. *Sınırlama:* hesaplama maliyeti yüksek, sürekli güncelleme gerektirir.

**[5] (2025). Evaluation of Large Language Models: Review of Metrics, Applications, and Methodologies.** Preprints.org 202504.0369
*Gap:* metrik–uygulama–metodoloji bağının pratik kılavuza dönüşmemesi. *Metot:* metrik tipolojisi + uygulama eşlemesi. *Katkı:* accuracy/coherence/relevance/safety eksenlerini uygulama alanlarıyla bağlar. *İlgi:* metrik seçim matrisi olarak kullanılabilir. *Sınırlama:* preprint, hakem-süreci tamamlanmamış.

---

## B. Klasik NLG / Metin Üretim Metrikleri (temel + referans)

**[6] ⭐ Zhang et al. (2019). BERTScore: Evaluating Text Generation with BERT.** arXiv:1904.09675
*Gap:* n-gram örtüşmesinin (BLEU/ROUGE) anlamsal eşdeğerliği yakalayamaması. *Metot:* contextual embedding token eşleştirme + cosine benzerliği. *Katkı:* insan yargısıyla daha yüksek korelasyon; 4000+ atıf. *İlgi:* RAG cevaplarının referansla anlamsal karşılaştırması. *Sınırlama:* faktüel hatayı yakalamaz, yüzeysel benzerlik ölçer.

**[7] Sellam et al. (2020). BLEURT: Learning Robust Metrics for Text Generation.** arXiv:2004.04696
*Gap:* öğrenilmiş metriklerin az/biased veriyle genelleşememesi. *Metot:* BERT + milyonlarca sentetik örnekle pre-training. *Katkı:* WMT Metrics SOTA; öğrenilmiş referans-tabanlı metrik. *İlgi:* fine-tune edilebilir metrik örneği. *Sınırlama:* referans gerektirir; domain shift'e duyarlı.

**[8] Yuan et al. (2021). BARTScore: Evaluating Generated Text as Text Generation.** arXiv:2106.11520
*Gap:* benzerlik metriklerinin üretim olasılığını göz ardı etmesi. *Metot:* seq2seq (BART) log-likelihood ile değerlendirme. *Katkı:* faithfulness'ta FactCC/QAGS'ı geçti; referanssız kullanılabilir. *İlgi:* RAG groundedness için likelihood-tabanlı ölçüm. *Sınırlama:* taban modele bağımlı.

**[9] Celikyilmaz et al. (2020). Evaluation of Text Generation: A Survey.** arXiv:2006.14799
*Gap:* NLG metriklerinin (insan/otomatik/öğrenilmiş) dağınıklığı. *Metot:* metrik taksonomisi survey. *Katkı:* tüm klasik metriklerin tek çatıda sınıflandırması. *İlgi:* metrik kategorileri için başvuru. *Sınırlama:* LLM öncesi dönem, judge/RAG yok.

**[10] Klasik referanslar:** Papineni et al. (2002) **BLEU** (ACL); Lin (2004) **ROUGE** (ACL Workshop); Banerjee & Lavie (2005) **METEOR** (ACL Workshop).
n-gram precision (BLEU), recall-odaklı özetleme (ROUGE), eş anlamlı/stem ile semantik (METEOR). *İlgi:* baseline metrikler; sınırlılıklarını (faktüellik körlüğü) tartışmak için zorunlu atıf.

---

## C. Faithfulness / Factual Consistency Metrikleri

**[11] ⭐ Maynez/Ji-grubu (2022). Faithfulness in NLG: A Systematic Survey of Analysis, Evaluation and Optimization Methods.** arXiv:2203.05227
*Gap:* faithfulness tanım ve ölçüm yöntemlerinin parçalı olması. *Metot:* analiz/eval/optimizasyon üç eksenli survey. *Katkı:* entailment / similarity / QA-tabanlı metrik sınıflaması. *İlgi:* RAG'ın merkez sorunu (cevap context'e sadık mı) → çekirdek. *Sınırlama:* hızlı genişleyen alanda kısmi eskime.

**[12] (2025). A Comprehensive Survey of Faithfulness Evaluation Methods.** RANLP 2025
*Gap:* faithfulness metriklerinin güncel (LLM-judge dahil) konsolidasyonu yok. *Metot:* güncel survey, dört tip (entailment/QA/fact/diğer). *İlgi:* [11]'in güncellenmiş hali. *Sınırlama:* workshop bildirisi.

**[13] Fabbri et al. (2021). QAFactEval: Improved QA-Based Factual Consistency Evaluation for Summarization.** arXiv:2112.08542
*Gap:* QA-tabanlı tutarlılık metriklerinin optimize edilmemesi. *Metot:* soru üretme + cevaplama tutarlılık skoru. *Katkı:* QA-tabanlı SOTA faktüel tutarlılık. *İlgi:* RAG cevap-context tutarlılığı için doğrudan uygulanabilir. *Sınırlama:* QG/QA hata yayılımı.

**[14] (2024). A Comparative Analysis of Faithfulness Metrics and Humans in Citation Evaluation.** arXiv:2408.12398
*Gap:* atıf/citation doğruluğunda metrik-insan uyumu belirsiz. *Metot:* metrik vs insan karşılaştırması. *Katkı:* citation faithfulness'ta metrik güvenilirlik analizi. *İlgi:* hadis/kaynak atıflı cevaplarda (isnad!) doğrudan örtüşür. *Sınırlama:* dar alan (citation).

---

## D. Hallucination & Factuality Benchmark/Metrikleri

**[15] ⭐ Lin et al. (2021). TruthfulQA: Measuring How Models Mimic Human Falsehoods.** arXiv:2109.07958
*Gap:* modellerin yaygın yanlış inançları taklit etmesini ölçen benchmark yok. *Metot:* 817 adversarial soru, 38 kategori. *Katkı:* truthfulness'ın standart benchmark'ı. *İlgi:* dini yanlış inanç/halk efsanesi ayrımı için metodolojik paralel. *Sınırlama:* artık doygun (training kaçağı), bazı altın cevaplar hatalı.

**[16] Li et al. (2023). HaluEval: A Large-Scale Hallucination Evaluation Benchmark.** arXiv:2305.11747
*Gap:* halüsinasyon tanıma yeteneğini ölçen büyük ölçekli set yok. *Metot:* 10.000 örnek, doğru/halüsinasyonlu cevap çiftleri + bilgi. *Katkı:* halüsinasyon tanıma benchmark standardı. *İlgi:* RAG cevaplarında halüsinasyon tespiti. *Sınırlama:* open-domain ağırlıklı, dini domain yok.

**[17] ⭐ Manakul et al. (2023). SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection.** arXiv:2303.08896
*Gap:* harici kaynak/logit gerektirmeyen halüsinasyon tespiti yok. *Metot:* örneklenmiş cevaplar arası tutarlılık (consistency) sampling. *Katkı:* sıfır-kaynak, kara-kutu cümle/pasaj seviyesi tespit. *İlgi:* harici altın kaynağın zor olduğu dini cevaplarda pratik. *Sınırlama:* çok örnekleme maliyeti; tutarlı-ama-yanlışı kaçırır.

**[18] ⭐ Min et al. (2023). FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long-Form Text.** arXiv:2305.14251
*Gap:* uzun-form üretimde ikili (doğru/yanlış) faktüellik kaba kalıyor. *Metot:* metni atomik gerçeklere bölüp güvenilir kaynakla doğrulanan oranı. *Katkı:* fine-grained faktüel precision metriği. *İlgi:* RAG uzun cevaplarının iddia-bazlı doğrulanması → çekirdek. *Sınırlama:* atomik ayrıştırma ve knowledge source kalitesine bağımlı.

**[19] Huang et al. (2023). A Survey on Hallucination in LLMs: Principles, Taxonomy, Challenges, Open Questions.** arXiv:2311.05232
*Gap:* halüsinasyon kavram/taksonomisi dağınık. *Metot:* kapsamlı survey. *Katkı:* factuality vs faithfulness ayrımı + ölçüm taksonomisi. *İlgi:* terminoloji ve metrik çerçevesi. *Sınırlama:* survey, ampirik değil.

**[20] (2025). Hallucination to Truth: A Review of Fact-Checking and Factuality Evaluation in LLMs.** Springer, AI Review · doi:10.1007/s10462-025-11454-w
*Gap:* fact-checking + factuality eval'ın birleşik güncel derlemesi yok. *Metot:* hakemli review. *Katkı:* fact-checking pipeline + metrik haritası. *İlgi:* dini iddia doğrulama (fact-check) hattı tasarımı. *Sınırlama:* genişlik/derinlik dengesi.

**[21] (2024). DefAn: Definitive Answer Dataset for LLMs Hallucination Evaluation.** arXiv:2406.09155
*Gap:* kesin-cevaplı (isim/tarih/sayı) halüsinasyon ölçümü zayıf. *Metot:* 9 alanda 75.000+ prompt; factual/faithfulness/consistency accuracy üç metrik. *Katkı:* kesin-cevap odaklı üçlü metrik. *İlgi:* hadis ravi/tarih gibi kesin-cevaplı sorgular. *Sınırlama:* açık-uçlu cevaplara uygun değil.

**[22] (2025). HalluLens: LLM Hallucination Benchmark.** arXiv:2504.17550
*Gap:* halüsinasyon benchmark'larının tutarsız taksonomisi. *Metot:* extrinsic/intrinsic ayrımıyla yeni benchmark. *Katkı:* güncel, taksonomi-tutarlı set. *İlgi:* güncel karşılaştırma noktası. *Sınırlama:* çok yeni, benimseme sınırlı.

---

## E. RAG Değerlendirme Çerçeveleri ve Metrikleri  (proje çekirdeği)

**[23] ⭐ Es et al. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation.** arXiv:2309.15217 · EACL 2024
*Gap:* RAG'ın referanssız, otomatik, bileşen-bazlı değerlendirmesi yok. *Metot:* faithfulness, answer relevancy, context precision, context recall metrikleri; LLM-tabanlı, etiketsiz. *Katkı:* RAG eval'in fiili standart metrik takımı. *İlgi:* GiraffeGraph RAG hattının doğrudan ölçüm aracı → en kritik. *Sınırlama:* LLM-judge'a dayanır (judge bias/maliyet).

**[24] ⭐ Saad-Falcon et al. (2023). ARES: Automated Evaluation Framework for RAG Systems.** arXiv:2311.09476
*Gap:* RAG bileşenlerinin az insan-etiketiyle güvenilir ölçümü. *Metot:* sentetik veriyle eğitilmiş hafif LM-judge + PPI (prediction-powered inference). *Katkı:* context relevance / answer faithfulness / answer relevance; az anotasyonla doğru. *İlgi:* RAGAS'a alternatif/tamamlayıcı, istatistiksel güvence. *Sınırlama:* domain'e uyarlama için sentetik veri gerekir.

**[25] ⭐ Chen et al. (2023). Benchmarking LLMs in Retrieval-Augmented Generation (RGB).** arXiv:2309.01431
*Gap:* RAG temel yeteneklerinin izole ölçülmemesi. *Metot:* noise robustness, negative rejection, information integration, counterfactual robustness; EN+ZH. *Katkı:* RAG'ı 4 temel yeteneğe ayıran benchmark. *İlgi:* gürültülü/çelişkili dini kaynaklarda dayanıklılık testi. *Sınırlama:* counterfactual kurgu sınırlı.

**[26] Lyu et al. (2024). CRUD-RAG: A Comprehensive Chinese Benchmark for RAG.** ACM TOIS · doi:10.1145/3701228 · arXiv:2401.17043
*Gap:* RAG senaryolarının (Create/Read/Update/Delete) bütünsel ölçülmemesi. *Metot:* CRUD işlem-tipi bazlı benchmark. *Katkı:* uygulama-senaryosu eksenli RAG eval. *İlgi:* RAG kullanım senaryosu tasarımı. *Sınırlama:* Çince; transfer doğrulaması gerek.

**[27] (2025). MIRAGE: A Metric-Intensive Benchmark for RAG Evaluation.** arXiv:2504.17137
*Gap:* RAG metriklerinin metrik-yoğun, ayrıştırılmış kıyası yok. *Metot:* çok-metrikli yoğun benchmark. *Katkı:* retrieval/generation etkileşimini ayrıştıran ölçüm. *İlgi:* metrik seçimi için kıyas referansı. *Sınırlama:* yeni, dış doğrulama az.

**[28] (2025). A Systematic Review of Key RAG Systems: Progress, Gaps, and Future Directions.** arXiv:2507.18910
*Gap:* RAG sistem+eval literatürünün bütünsel haritası yok. *Metot:* sistematik review. *Katkı:* RAG bileşen + değerlendirme açıklarının haritası. *İlgi:* proje konumlandırması ve gelecek-iş bölümü. *Sınırlama:* derleme.

---

## F. LLM-as-a-Judge (otomatik değerlendirici)

**[29] ⭐ Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.** arXiv:2306.05685
*Gap:* açık-uçlu sohbet kalitesini ölçen insan-tercihli benchmark yok. *Metot:* MT-Bench (çok-turlu) + Chatbot Arena (crowdsource); GPT-4 judge. *Katkı:* GPT-4 judge insan ile %80+ uyum; position/verbosity bias tespiti. *İlgi:* dini cevap kalitesi insan-değerlendirme maliyetli → judge alternatifi. *Sınırlama:* bias'lar; alan uzmanlığı gerektiren dini içerikte risk.

**[30] ⭐ Liu et al. (2023). G-Eval: NLG Evaluation Using GPT-4 with Better Human Alignment.** arXiv:2303.16634 · EMNLP 2023
*Gap:* BLEU/ROUGE'un yaratıcı/açık-uçlu görevlerde insan ile düşük korelasyonu. *Metot:* CoT + form-doldurma ile GPT-4 puanlama. *Katkı:* özet/diyalogta insan yargısıyla güçlü korelasyon. *İlgi:* özelleştirilmiş dini-kalite rubrikleri kurmak için şablon. *Sınırlama:* LLM-judge bias; reprodüksiyon zorluğu.

**[31] (2024). LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods.** arXiv:2412.05579
*Gap:* judge yöntemlerinin (bias, güvenilirlik, kalibrasyon) konsolide edilmemesi. *Metot:* survey. *Katkı:* judge bias taksonomisi + azaltma yöntemleri. *İlgi:* judge kullanımının metodolojik savunması. *Sınırlama:* derleme.

---

## G. Knowledge Graph QA Değerlendirme  (isnad graf için)

**[32] ⭐ (2025). Comprehensive Evaluation for a Large Scale Knowledge Graph Question Answering Service.** arXiv:2501.17270
*Gap:* üretim-ölçekli KGQA için uçtan-uca eval eksik. *Metot:* E2E coverage/precision, retrieval (MRR, Top-K), generative accuracy. *Katkı:* sistem+bileşen KGQA metrik takımı. *İlgi:* hadis isnad grafı sorgu sistemi eval'i → doğrudan. *Sınırlama:* servis-spesifik genellenebilirlik.

**[33] Seo et al. (2022). Structural Quality Metrics to Evaluate Knowledge Graphs.** arXiv:2211.10011
*Gap:* KG kalitesinin yapısal (graf-topolojik) metriklerle nesnel ölçülmemesi. *Metot:* yapısal kalite metrikleri (instance/schema, bağlantılılık) tanımı. *Katkı:* KG yapısal kalite metrik kataloğu. *İlgi:* inşa edilen KG'nin (isnad graf) bütünlük/bağlantılılık ölçümü. *Sınırlama:* yapısal odak; anlamsal doğruluk kapsam dışı.
> Not: ilk seçilen Springer IJDSA makalesi (doi:10.1007/s41060-025-00871-3) paywall nedeniyle NotebookLM'e eklenemedi; açık-erişim bu makaleyle değiştirildi.

**[34] Orogat & El-Roby (2021). CBench: Towards Better Evaluation of QA Over Knowledge Graphs.** arXiv:2105.00811
*Gap:* KGQA benchmark'larının tutarsız metrik/zorluk profili. *Metot:* Micro/Macro/Global F1 + sorgu-zorluk analizi. *Katkı:* fine-grained KGQA eval aracı. *İlgi:* KGQA metrik (F1 varyantları) seçimi. *Sınırlama:* SPARQL/structured sorgu odaklı.

---

## H. Domain-Specific — Dini / İslami LLM Değerlendirme  (en yakın bağlam)

**[35] ⭐ (2026). IslamicMMLU: A Benchmark for Evaluating LLMs on Islamic Knowledge.** arXiv:2603.23750
*Gap:* İslami bilgi (Kuran/Hadis/Fıkıh) için ayrıştırıcı benchmark yok. *Metot:* 12 görevde 10.013 soru; Quran/Hadith/Fiqh üç track; 26 LLM; madhab bias tespiti. *Katkı:* güçlü ayrıştırıcı dini benchmark (frontier ile eski-nesil modeller arası 54-puan fark). *İlgi:* projenin doğrudan değerlendirme zemini → çekirdek. *Sınırlama:* çoktan-seçmeli; açık-uçlu üretim/faithfulness ölçmez.

**[36] ⭐ (2026). From RAG to Agentic RAG for Faithful Islamic Question Answering.** arXiv:2601.07528
*Gap:* dini RAG'da faithfulness ve ajan-mimarisi eval'i yetersiz. *Metot:* RAG vs agentic RAG karşılaştırması, faithfulness odaklı. *Katkı:* dini QA'da agentic RAG faithfulness kazanımı. *İlgi:* GiraffeGraph mimari+metrik kararlarına en yakın çalışma. *Sınırlama:* yeni, sınırlı replikasyon.

**[37] (2023). Building Domain-Specific LLMs Faithful to the Islamic Worldview: Mirage or Technical Possibility?** arXiv:2312.06652
*Gap:* dünya-görüşüne sadık dini LLM'in teknik fizibilitesi belirsiz. *Metot:* kavramsal+teknik analiz. *Katkı:* dini faithfulness gereksinimleri ve eval kriterleri tartışması. *İlgi:* "faithful to worldview" eval kriteri tanımı. *Sınırlama:* ampirik benchmark sınırlı.

**[38] (2025). Evaluating Arabic Large Language Models: A Survey of Benchmarks, Methods, and Gaps.** arXiv:2510.13430
*Gap:* Arapça/dini LLM benchmark'larının dağınıklığı. *Metot:* survey, benchmark+metot+açık haritası. *İlgi:* Arapça kaynak (Kuran/Hadis dili) eval altyapısı. *Sınırlama:* Arapça-merkezli; Türkçe transfer açık.

---

## Tematik Kapsam Özeti

| Küme | Makale | Proje ilgisi |
|------|--------|--------------|
| A. Genel survey/çerçeve | 1–5 | Omurga, konumlandırma |
| B. Klasik NLG metrik | 6–10 | Baseline + sınırlılık |
| C. Faithfulness | 11–14 | RAG sadakat ölçümü |
| D. Hallucination/factuality | 15–22 | Cevap doğruluğu |
| E. RAG eval | 23–28 | **Çekirdek** |
| F. LLM-as-judge | 29–31 | Otomatik değerlendirici |
| G. KG-QA eval | 32–34 | İsnad graf eval |
| H. Dini/İslami eval | 35–38 | **En yakın bağlam** |

## Sonraki Adım
1. Bu 38 başlığı NotebookLM'e source olarak ekle (arXiv PDF linkleri).
2. Her biri için toplantıdaki 300-kelime akademik review promptunu çalıştır.
3. ⭐ işaretli 12 çekirdek makaleyle başla.

> ⚠️ Doğrulama notu: arXiv ID'leri arama sonuçlarından alındı; [4], [10], [16], [18], [30], [26] ID'leri yaygın-bilinen referanslardan teyit edildi — NotebookLM'e eklemeden önce link açılırlığını kontrol et.
