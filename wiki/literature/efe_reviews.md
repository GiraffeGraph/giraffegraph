# LLM Başarı Ölçüm Metrikleri — Akademik Review'lar (NotebookLM)

**Sorumlu:** Efe · **Konu:** LLM evaluation / success metrics
**Üretim:** Her makale ayrı NotebookLM notebook'unda, toplantı notundaki 300-kelime akademik review promptuyla. Her review 5 eksen: Research Gap / Data & Methodology / Main Contributions / Relevance / Future Work-Limitations.
**Kaynak makale listesi + arXiv ID'leri:** bkz. `efe_llm_eval_metrics_review.md`.

> Not: Review'lar NotebookLM tarafından kaynak PDF'lerden grounded üretildi (her cümle source-cited). Bazı makalelerde NotebookLM yalnız abstract'a erişti → "Future Work" bölümünde bunu işaretledi.

---

## A. Genel LLM Değerlendirme — Survey ve Çerçeveler

### [01] Chang et al. (2023) — A Survey on Evaluation of LLMs · arXiv:2307.03109
**Research Gap:** LLM değerlendirmesinin parçalı manzarası; task-level performansın ötesine geçip toplumsal etki ve riskleri kritik biçimde ölçen kapsamlı çerçeve ihtiyacı.
**Data & Methodology:** Ampirik değil, taksonomik survey. NLP, reasoning, etik, tıp, eğitim, doğa/sosyal bilimler, agent uygulamaları boyunca benchmark+metot taraması.
**Main Contributions:** "What / where / how to evaluate" üç-boyutlu taksonomi; modellerin başarı/başarısızlık vakalarının sentezi.
**Relevance:** Araştırmacılar için temel yol haritası; değerlendirmeyi post-hoc test değil, "essential discipline" olarak konumlandıran paradigma kayması.
**Future Work/Limitations:** Hızlı evrilen yeteneklerle metrik/benchmark'ların sürekli adaptasyon gereksinimi; gelecek zorluklara ayrı bölüm.

### [02] Guo et al. (2023) — Evaluating LLMs: A Comprehensive Survey · arXiv:2310.19736
**Research Gap:** LLM yayılımının risk değerlendirme protokollerini geride bırakması (veri sızıntısı, zararlı içerik, denetimsiz süper-zekâ).
**Data & Methodology:** Taksonomik survey; üç ana grup — knowledge & capability, alignment, safety değerlendirmesi.
**Main Contributions:** Değerlendirme metodolojilerinin "panoramik" görünümü; capability+alignment+safety kapsayan platform inşası bileşenleri.
**Relevance:** Parçalı manzarayı yapılandırılmış çerçeveye indirger; sorumlu LLM geliştirme için temel metin.
**Future Work/Limitations:** Survey'lerin hızlı eskimesi; sürekli adapte olan dinamik değerlendirme platformları gereği.

### [03] Laskar et al. (2024) — A Systematic Survey & Critical Review on Evaluating LLMs · arXiv:2407.04069 (EMNLP 2024)
**Research Gap:** Değerlendirme sürecinin karmaşıklığı → parçalı setup'lar, bulgu/yorumda tutarsızlık; standardizasyon eksiği.
**Data & Methodology:** Sistematik kritik review; değerlendirme adımlarındaki birincil zorluk ve sınırlamaların izolasyonu.
**Main Contributions:** Metodolojik darboğazları yapılandırılmış öneri setine sentezler; reproducible/reliable/robust değerlendirme yol haritası.
**Relevance:** EMNLP 2024; gerçek-dünya dağıtımı öncesi standart, titiz değerlendirme çerçeveleri için zorunlu.
**Future Work/Limitations:** Önerilerin ampirik validasyonu gerekiyor; yeni mimarilerde tutarsızlıkları azaltma testi.

### [04] Liang et al. (2022) — HELM (Holistic Evaluation of LMs) · arXiv:2211.09110
**Research Gap:** Parçalı değerlendirme — modeller ortalama yalnız %17.9 core senaryoda test ediliyordu; temel yetenek/risk/sınır anlaşılmıyordu.
**Data & Methodology:** Çok-metrikli; 30 model, 16 core + 26 hedef senaryo; 7 metrik (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency).
**Main Contributions:** HELM çerçevesi core kapsamı %96'ya çıkardı; 25 üst-düzey bulgu; metrik trade-off'larını açığa çıkardı; modüler toolkit + ham prompt/completion açık.
**Relevance:** LM değerlendirmesini şeffaf, birleşik benchmark standardına dönüştürür; fairness/toxicity göz ardı edilmesini engeller.
**Future Work/Limitations:** Eksik alanlar (ihmal edilen İngilizce diyalektlerde QA, trustworthiness metrikleri); "living benchmark" — sürekli topluluk güncellemesi gerekli.

### [05] Joshi (2025) — Evaluation of LLMs: Review of Metrics, Applications, Methodologies · Preprints.org 202504.0369
**Research Gap:** Standart protokol eksiği; ad-hoc yöntemler LLM'in çok-boyutlu doğasını yakalayamıyor; yapılandırılmış vs açık-uçlu görev başarımı uçurumu.
**Data & Methodology:** 70+ çalışma; karma yöntem (nicel metrik + matematiksel modelleme + nitel). Composite Evaluation Index (CEI) = accuracy + entropy-stability + domain weighting.
**Main Contributions:** 50+ metrik hiyerarşik taksonomi; %36.4 çıktı varyansı, %28 halüsinasyon oranı gibi operasyonel kusurların nicelleştirilmesi; domain-özgü ağırlıklandırma (finans/hukuk/tıp).
**Relevance:** Yüksek-riskli profesyonel ortamlarda LLM dağıtımı için domain-adapte metodoloji; teknik metrik + güvenlik köprüsü.
**Future Work/Limitations:** Dilin öznelliği, hesaplama maliyeti, insan-gözetimi varyansı; standart cross-domain benchmark, real-time observability, açıklanabilir AI gereği. *(Peer-review tamamlanmamış preprint.)*

---

## B. Klasik NLG / Metin Üretim Metrikleri

### [06] Zhang et al. (2019) — BERTScore · arXiv:1904.09675
**Research Gap:** Tam token-eşleşmesine dayanan metriklerin (BLEU) parafraz/anlamsal eşdeğerliği tanıyamaması; insan yargısını yansıtmada açık.
**Data & Methodology:** Contextual embedding ile token benzerliği; 363 MT+image-captioning sistemi çıktısı; adversarial parafraz tespiti testi.
**Main Contributions:** İnsan yargısıyla daha yüksek korelasyon + üstün model seçimi; adversarial örneklerde daha dayanıklı.
**Relevance:** Değerlendirmeyi yüzeysel eşleşmeden anlamsal kavrayışa kaydıran metodolojik dönüm.
**Future Work/Limitations:** (NotebookLM: abstract dışı, doğrula) — hesaplama yükü; taban dil modelinin bias/kör noktaları.

### [07] Sellam et al. (2020) — BLEURT · arXiv:2004.04696
**Research Gap:** BLEU/ROUGE'un insan yargısıyla zayıf korelasyonu; öğrenilmiş metriklerin az/biased veriyle genelleşememesi.
**Data & Methodology:** BERT-tabanlı öğrenilmiş metrik; milyonlarca sentetik örnekle yeni pre-training şeması.
**Main Contributions:** WMT Metrics (son 3 yıl) + WebNLG'de SOTA; veri kıt/out-of-distribution olduğunda bile vanilla-BERT'ü geçer.
**Relevance:** Rijit n-gram eşleşmesini sağlam semantik öğrenilmiş değerlendirmeyle değiştirir.
**Future Work/Limitations:** İnsan-yargı verisinin kıt/biased olması; sentetik veri yeni bias getirebilir; özelleşmiş domain'lere ölçeklenme.

### [08] Yuan et al. (2021) — BARTScore · arXiv:2106.11520
**Research Gap:** NLG'de fluency/accuracy/factuality çok-boyutlu kalitenin ölçümü zor; benzerlik metrikleri üretim olasılığını yok sayar.
**Data & Methodology:** Değerlendirmeyi metin-üretim problemi olarak yeniden çerçeveler; BART seq2seq log-likelihood; denetimsiz.
**Main Contributions:** BARTScore + varyantları; 22 test ortamının 16'sında üstün; ExplainaBoard meta-değerlendirme leaderboard'u.
**Relevance:** Rijit metrikler yerine seq2seq olasılığı; çok-perspektifli, model-güdümlü dinamik değerlendirme.
**Future Work/Limitations:** ExplainaBoard ile metriklerin güç/zayıflık/tümleyiciliğinin sürekli analizi.

### [09] Celikyilmaz et al. (2020) — Evaluation of Text Generation: A Survey · arXiv:2006.14799
**Research Gap:** Nöral NLG'nin değerlendirme tekniklerini geride bırakması; parçalı manzara.
**Data & Methodology:** Literatür survey'i; üçlü taksonomi — human-centric, untrained automatic, machine-learned metrikler; özetleme + uzun-metin vaka çalışmaları.
**Main Contributions:** Modern NLG değerlendirme ekosisteminin yapılandırılmış haritası; her kategoride ilerleme+engel sentezi.
**Relevance:** Standart değerlendirme çerçeveleri modern NLP'nin en kritik darboğazı; temel başvuru kılavuzu.
**Future Work/Limitations:** Gelecek araştırma yönleri önerir; nihai çözüm değil basamak.

### [10] Klasik Metrikler — BLEU (Papineni 2002) / ROUGE (Lin 2004) / METEOR (Banerjee & Lavie 2005)
**Research Gap:** Pahalı insan yargısının yerini alacak otomatik MT (BLEU) ve özetleme (ROUGE) değerlendirmesi; METEOR BLEU'nun katı tam-eşleşme zaafını giderir.
**Data & Methodology:** BLEU — modified n-gram precision + brevity penalty; ROUGE — n-gram recall + LCS; METEOR — unigram precision/recall harmonik ortalaması + stemming/WordNet synonymy.
**Main Contributions:** BLEU n-gram örtüşme paradigmasını başlattı; ROUGE özetleme standart toolkit'i; METEOR dilbilimsel esneklik + daha iyi insan korelasyonu.
**Relevance:** Otomatik NLP değerlendirmesinin metodolojik temeli; istatistiksel/erken-nöral modelleri mümkün kıldı.
**Limitations:** Yüzeysel sözcük örtüşmesine bağımlı; derin anlamsal eşdeğerliği, yaratıcı parafrazı, yapısal tutarsızlığı yakalayamaz. *(NotebookLM: kaynaklar yalnız bibliyografik metadata; metodoloji detayı dış-bilgi, doğrula.)*

---

## C. Faithfulness / Factual Consistency Metrikleri

### [11] Li et al. (2022) — Faithfulness in NLG: A Systematic Survey · arXiv:2203.05227
**Research Gap:** Faithfulness analiz/eval/optimizasyon çalışmalarının parçalı; tek çatıda karşılaştırılmamış olması.
**Data & Methodology:** Sistematik survey; problem-analizi + evaluation + optimization birleşik taksonomi.
**Main Contributions:** Entailment / similarity / QA-tabanlı metrik sınıflaması; özetleme/diyalog/MT/data-to-text köprüsü.
**Relevance:** Faktüel güvenilirlik pratik dağıtımı kısıtlıyor; hızla genişleyen alanı merkezî çerçevede toplar.
**Future Work/Limitations:** Birkaç araştırma trendi önerir. *(NotebookLM: yalnız abstract+metadata erişti.)*

### [12] Lamsiyah et al. (2025) — Trust but Verify: Comprehensive Survey of Faithfulness Eval Methods · RANLP 2025
**Research Gap:** LLM-tabanlı değerlendirme dahil güncel (2020–2025) faithfulness sentezinin eksikliği.
**Data & Methodology:** 40+ çalışma; birleşik taksonomi — human / automatic (QA-, NLI-, graph-, LLM-tabanlı) / meta-evaluation; benchmark karşılaştırması.
**Main Contributions:** Metrik-insan yargısı sürekli kayması (misalignment); metrik kırılganlığı, domain shift, hesaplama verimsizliği formalizasyonu.
**Relevance:** İnsan yargısının "moving target" olması — kusursuz otomatik metrik arayışını sorunsallaştırır.
**Future Work/Limitations:** Breadth>depth, bağımsız ampirik re-evaluation yok; hibrit/graded yöntemler + cross-domain benchmark + LLM-judge bias azaltma.

### [13] Fabbri et al. (2021) — QAFactEval · arXiv:2112.08542 (NAACL 2022)
**Research Gap:** Özetlemede faktüel tutarlılıkta entailment vs QA-tabanlı metrik çelişkili sonuçlar; tutarsız deney setup'ları.
**Data & Methodology:** İki paradigmanın kapsamlı kıyası; QA bileşenleri (question generation, answerability classification) optimize; SummaC benchmark.
**Main Contributions:** QAFactEval — önceki QA metriklerine %14 ortalama iyileşme; en iyi entailment metriğini geçti; iki paradigma tümleyici.
**Relevance:** Çelişkili sonuçları çözer; titiz test edilmiş üstün faktüel tutarlılık metriği.
**Future Work/Limitations:** Tümleyici sinyaller → birleşik metrik gelecek yönü.

### [14] Zhang et al. (2024) — Faithfulness Metrics vs Humans in Citation Evaluation · arXiv:2408.12398 (LLM4Eval@SIGIR)
**Research Gap:** Citation desteği ikili (binary) sınıflama olarak ele alınıyor; pratikteki "partial support" ihmal ediliyor.
**Data & Methodology:** Üç-kategori çerçeve (full/partial/no support); korelasyon + sınıflama + retrieval değerlendirmesiyle metrik-insan hizası.
**Main Contributions:** Hiçbir metrik tüm değerlendirmelerde tutarlı üstün değil; en iyi metrikler bile "partial"ı ayırt edemiyor; metrik tasarım önerileri.
**Relevance:** Hadis/kaynak-atıflı (isnad) cevaplarda doğrudan örtüşür; ikili değerlendirmenin sınırını ifşa eder.
**Future Work/Limitations:** Partial-support sorununu çözen yeni metrik sunmuyor; operasyonalize edilmeli.

---

## D. Hallucination & Factuality Benchmark/Metrikleri

### [15] Lin et al. (2021) — TruthfulQA · arXiv:2109.07958
**Research Gap:** Modellerin yaygın insan yanlış-inançlarını taklit etme zaafının az incelenmesi.
**Data & Methodology:** 817 adversarial soru, 38 kategori; GPT-3, GPT-Neo/J, GPT-2, T5; insan baseline.
**Main Contributions:** "Inverse scaling" — en büyük modeller en az truthful; en iyi model %58 vs insan %94.
**Relevance:** "Ölçek tek başına factuality'yi çözer" konsensüsüne meydan okur; AI safety/alignment için kritik.
**Future Work/Limitations:** Yalnız imitasyon-optimize modeller; web-metni taklidi dışı fine-tuning hedefleri gerekli.

### [16] Li et al. (2023) — HaluEval · arXiv:2305.11747 (EMNLP 2023)
**Research Gap:** Halüsinasyon tip/kapsamını ve LLM tanıma yeteneğini ölçen büyük-ölçek benchmark eksiği.
**Data & Methodology:** ChatGPT "sampling-then-filtering" + insan anotasyon; 10K örnek.
**Main Contributions:** ChatGPT ~%19.5 doğrulanamaz içerik; LLM'ler halüsinasyon tanımada zorlanıyor; harici bilgi/akıl yürütme tespiti iyileştiriyor.
**Relevance:** Gözlemden tanı-benchmarking'e geçiş; güvenilirlik test temel veri seti.
**Future Work/Limitations:** ChatGPT-tabanlı üretim model-bias gömebilir; çeşitli mimarilere genişletme + dinamik retrieval.

### [17] Manakul et al. (2023) — SelfCheckGPT · arXiv:2303.08896
**Research Gap:** Kara-kutu (logit/harici DB gerektirmeyen) halüsinasyon tespiti eksiği.
**Data & Methodology:** Sampling-tabanlı tutarlılık; GPT-3 ile WikiBio biyografi üretimi + manuel factuality anotasyonu.
**Main Contributions:** Yanıt tutarlılığı = factuality proxy; cümle+pasaj seviyesi tespit; grey-box baseline'lara göre daha yüksek AUC-PR.
**Relevance:** Sıfır-kaynak, model-agnostik; opak proprietary modelleri denetlemede ölçeklenebilir.
**Future Work/Limitations:** Tutarlı-ama-yanlışı kaçırır; yalnız biyografi domain'i; çok-örnekleme maliyeti.

### [18] Min et al. (2023) — FActScore · arXiv:2305.14251 (EMNLP 2023)
**Research Gap:** Uzun-form üretimde destekli+desteksiz iddia karışımı → ikili yargı yetersiz; insan değerlendirmesi pahalı.
**Data & Methodology:** Metni atomik gerçeklere bölüp güvenilir kaynakla desteklenen %; InstructGPT/ChatGPT/PerplexityAI biyografi; retrieval+güçlü LM ile otomatik tahmin (<%2 hata).
**Main Contributions:** Fine-grained faktüel precision metriği; 13 model 6.500 üretim ($26K insan-maliyeti tasarrufu); GPT-4/ChatGPT > public modeller.
**Relevance:** Ölçeklenebilir iddia-bazlı doğrulama; tüm metni atmak yerine halüsinasyon oranını pinpoint.
**Future Work/Limitations:** Güvenilir knowledge source + güçlü LM bağımlılığı; biyografi-ötesi domain validasyonu.

### [19] Huang et al. (2023) — Survey on Hallucination in LLMs · arXiv:2311.05232
**Research Gap:** LLM'lerin açık-uçlu/genel-amaçlı doğasının task-özgü modellerden farklı halüsinasyon zorlukları; nüanslı çerçeve eksiği.
**Data & Methodology:** Literatür survey'i; halüsinasyon taksonomisi + katkı faktörleri + tespit/azaltma benchmark'ları.
**Main Contributions:** Yapısal taksonomi + halüsinasyon yaşam-döngüsü; retrieval-augmented LLM sınırlarının kritiği.
**Relevance:** Bilgi-edinim paradigma kayması; IR sistemlerinde güvenilirlik için zorunlu.
**Future Work/Limitations:** Vision-language modellerde halüsinasyon; knowledge boundary teorik anlayışı.

### [20] Rahman et al. (2025) — Hallucination to Truth: Fact-Checking & Factuality Review · Springer AI Review, doi:10.1007/s10462-025-11454-w
**Research Gap:** Önceki survey'ler dataset kalitesi (domain-özgü) ve RAG implementasyon zorluklarını ihmal ediyor.
**Data & Methodology:** Sistematik review; 64 hakemli makale (2021–2025); Scopus/WoS/arXiv/OpenReview; 5 araştırma sorusu (14.685→64 eleme).
**Main Contributions:** Metrik taksonomisi + halüsinasyon azaltma (adversarial tuning, multi-agent); dataset karakteristiklerinin (çok-dillilik, anotasyon) fact-check başarımına etkisi.
**Relevance:** Statik parametrik bilgiden dinamik RAG+doğrulanabilir kanıta kayış; tıp/hukuk yüksek-risk.
**Future Work/Limitations:** Statik→dinamik değerlendirme suite'leri; reaktif düzeltme→proaktif önleme; hızlı yenilik kapsam riski.

### [21] Rahman et al. (2024) — DefAn: Definitive Answer Hallucination Dataset · arXiv:2406.09155
**Research Gap:** Mevcut setler küçük + çoktan-seçmeli; LLM üretim yeteneğini ölçemiyor.
**Data & Methodology:** 75.000+ prompt, 8 domain; public+hidden segment; GPT-3.5/LLaMA2-3/Gemini/Mixtral/Zephyr; kesin-üretici cevaplar.
**Main Contributions:** Factual hatası %82'ye, prompt-misalignment %95'e, consistency %21'e kadar; numeric sorgularda ciddi düşüş (person/location/date daha iyi).
**Relevance:** Geleneksel paradigmaya göre daha gerçekçi üretici benchmark.
**Future Work/Limitations:** Yalnız "definitive/concise" cevap odağı; uzun-form/açık-uçlu halüsinasyonu kapsamayabilir.

### [22] Bang et al. (2025) — HalluLens: LLM Hallucination Benchmark · arXiv:2504.17550
**Research Gap:** Birleşik çerçeve yok; halüsinasyon factuality ile karıştırılıyor; benchmark doygunluğu + veri sızıntısı.
**Data & Methodology:** Intrinsic/extrinsic ayrımıyla taksonomi; dynamic test set generation (sızıntıya karşı).
**Main Contributions:** Yeni extrinsic görevler + mevcut intrinsic entegrasyonu; içerik-tutarsızlığını faktüel hatadan izole eden taksonomi.
**Relevance:** Benchmark doygunluğunu dinamik üretimle aşar; dayanıklı değerlendirme altyapısı.
**Future Work/Limitations:** Evrilen LLM'lerde sürekli adaptasyon + dinamik üretim gereği.

---

## E. RAG Değerlendirme Çerçeveleri (proje çekirdeği)

### [23] Es et al. (2023) — RAGAS · arXiv:2309.15217 (EACL 2024)
**Research Gap:** RAG'ın çok-boyutlu (retrieval + faithful generation + kalite) referanssız otomatik değerlendirmesi yok; insan-anotasyon darboğazı.
**Data & Methodology:** Reference-free çerçeve; bileşenleri bağımsız değerlendiren metrik takımı; altın-veri gerektirmez.
**Main Contributions:** Context relevance + faithfulness + generation kalitesi otomatik ölçümü.
**Relevance:** İnsan-anotasyon bağımlılığını kaldırır → hızlı değerlendirme döngüsü; GiraffeGraph RAG için doğrudan araç.
**Future Work/Limitations:** Otomatik metrikleri karmaşık insan-yargısına karşı sürekli validasyon gereği.

### [24] Saad-Falcon et al. (2023) — ARES · arXiv:2311.09476
**Research Gap:** RAG değerlendirmesinin pahalı el-anotasyonuna bağımlılığı.
**Data & Methodology:** Sentetik veriyle fine-tune hafif LM-judge'lar; prediction-powered inference (PPI) + az insan-anotasyon; KILT/SuperGLUE/AIS (8 görev).
**Main Contributions:** Context relevance + answer faithfulness + answer relevance; birkaç yüz anotasyonla doğru; domain-shift'e dayanıklı.
**Relevance:** İstatistiksel güvenceyle ölçeklenebilir; RAGAS'a tümleyici/alternatif.
**Future Work/Limitations:** Hâlâ baseline insan-anotasyon gerekir; tam zero-shot + özelleşmiş domain ölçeklenmesi.

### [25] Chen et al. (2023) — RGB (Benchmarking LLMs in RAG) · arXiv:2309.01431
**Research Gap:** RAG'ın farklı modellere etkisinin titiz değerlendirilmemesi; yetenek darboğazlarının belirsizliği.
**Data & Methodology:** Bilingual (EN+ZH) RGB korpusu; 4 yetenek testbed'i — noise robustness, negative rejection, information integration, counterfactual robustness; 6 model.
**Main Contributions:** RAG'ı 4 yeteneğe ayrıştırır; modeller noise'a dayanıklı ama negative rejection / integration / counterfactual'da zayıf.
**Relevance:** "RAG halüsinasyon panzehiri" varsayımına meydan; yapısal zayıflık tanı aracı.
**Future Work/Limitations:** Retrieval doğruluğunun ötesinde reddetme/sentez/counterfactual-direnci gerekli.

### [26] Lyu et al. (2024) — CRUD-RAG · arXiv:2401.17043 (ACM TOIS)
**Research Gap:** Mevcut benchmark'lar dar (yalnız QA); retrieval bileşeni + bilgi-tabanı mimarisi ihmal.
**Data & Methodology:** Büyük Çince benchmark; CRUD taksonomisi (Create/Read/Update/Delete); retriever, context-length, KB-construction bileşen analizi.
**Main Contributions:** Generation-merkezli paradigmadan bütünsel çok-bileşenli çerçeveye geçiş; senaryo-özgü optimizasyon içgörüleri.
**Relevance:** Ekolojik geçerlilik; harici bilginin gerçek-dünya metin-manipülasyonuna entegrasyonu.
**Future Work/Limitations:** Yalnız Çince; çok-dilli adaptasyon — retriever-LLM etkileşimi dil-yapısına göre değişebilir.

### [27] Park et al. (2025) — MIRAGE · arXiv:2504.17137 (NAACL 2025 Findings)
**Research Gap:** Retrieval-generation etkileşimini izole eden bileşen-özgü benchmark kıtlığı.
**Data & Methodology:** 7.560 QA örneği + 37.800 kontrollü retrieval havuzu; retriever-LLM konfigürasyonları.
**Main Contributions:** Metrik-yoğun çerçeve; noise vulnerability, context acceptability, context insensitivity, context misinterpretation; optimal model-eşleşme içgörüleri.
**Relevance:** Standart tanı aracı; açık-kaynak dataset+kod.
**Future Work/Limitations:** Yalnız QA; kontrollü havuz web-ölçek kadar ekolojik değil; özetleme/açık-uçlu görevlere genişletme.

### [28] Oche et al. (2025) — Systematic Review of Key RAG Systems · arXiv:2507.18910
**Research Gap:** RAG genişlemesinin enterprise-ölçek değerlendirme çerçevelerini (proprietary veri, güvenlik) geride bırakması.
**Data & Methodology:** Sistematik review; yıl-bazlı analiz; retrieval accuracy / fluency / efficiency / latency kıyası.
**Main Contributions:** Retrieval + seq2seq generation + fusion stratejileri kritiği; enterprise dağıtım odağı.
**Relevance:** Parçalı literatürü yol haritasına sentezler; RAG'ı teoriden uygulamaya taşır.
**Future Work/Limitations:** Retrieval-kalite darboğazı, integration overhead, gizlilik; hybrid retrieval, privacy-preserving, agentic RAG.

---

## F. LLM-as-a-Judge

### [29] Zheng et al. (2023) — Judging LLM-as-a-Judge (MT-Bench & Chatbot Arena) · arXiv:2306.05685
**Research Gap:** Geleneksel benchmark'ların açık-uçlu sohbet yeteneği + insan-tercihini yakalayamaması.
**Data & Methodology:** MT-Bench (çok-turlu) + Chatbot Arena (crowdsource); 3K uzman oyu + 30K konuşma; GPT-4 judge.
**Main Contributions:** GPT-4 judge insanla %80+ uyum (insan-insan seviyesi); bias tanı + azaltma.
**Relevance:** "LLM-as-judge"ı ölçeklenebilir, açıklanabilir, ucuz insan-tercih proxy'si olarak meşrulaştırır.
**Future Work/Limitations:** Position/verbosity/self-enhancement bias + sınırlı reasoning; çözüm gerekli.

### [30] Liu et al. (2023) — G-Eval · arXiv:2303.16634 (EMNLP 2023)
**Research Gap:** BLEU/ROUGE'un yaratıcı görevlerde düşük korelasyonu; erken LLM-değerlendiricilerin orta-boy nöral değerlendiricilerden düşük insan-uyumu.
**Data & Methodology:** GPT-4 + chain-of-thought + form-doldurma; özetleme + diyalog görevleri.
**Main Contributions:** Özetlemede Spearman 0.514 (önceki yöntemleri büyük farkla geçer); referanssız.
**Relevance:** Gelişmiş LLM'lerin referanssız metrik olabildiğini doğrular; insan-referans bağımlılığını azaltır.
**Future Work/Limitations:** LLM-üretimi metinlere sistemik bias; tespit + azaltma şart.

### [31] Li et al. (2024) — LLMs-as-Judges: Comprehensive Survey · arXiv:2412.05579
**Research Gap:** Judge kullanımını kategorize eden + güvenilirliği doğrulayan birleşik çerçeve eksiği.
**Data & Methodology:** Nitel sentez; beş perspektif — functionality, methodology, applications, meta-evaluation, limitations.
**Main Contributions:** "LLMs-as-judges" sistematik tanım + taksonomi; sürekli güncel online repo.
**Relevance:** Ölçeklenebilir değerlendirme darboğaz; otomatik değerlendiricileri operasyonalize içgörü.
**Future Work/Limitations:** Bias/tutarsızlık analizi; survey hızlı eskime — yaşayan kaynak olarak azaltır.

---

## G. Knowledge Graph QA Değerlendirme (isnad graf)

### [32] Potdar et al. (2025) — Comprehensive Evaluation for Large-Scale KGQA Service (Chronos) · arXiv:2501.17270
**Research Gap:** KGQA'nın izole benchmark'tan enterprise dağıtıma geçişinde çok-bileşenli endüstri-ölçek değerlendirme eksiği.
**Data & Methodology:** Chronos çerçevesi; uçtan-uca + bileşen-seviyesi metrik; çeşitli dataset; release-öncesi ölçüm.
**Main Contributions:** Chronos mimarisi + veri-güdümlü karar; endüstri-ölçek KGQA zorluk haritası.
**Relevance:** Teorik NLP ↔ enterprise köprüsü; nihai cevap + ara-bileşen bütünlüğü; isnad graf sorgu eval'i için doğrudan.
**Future Work/Limitations:** Gerçek-sistem ölçüm zorlukları; non-proprietary KG'lerde genellenebilirlik validasyonu.

### [33] Seo et al. (2022) — Structural Quality Metrics to Evaluate Knowledge Graphs · arXiv:2211.10011
**Research Gap:** KG değerlendirmesinin ölçek-göstergelerine (sınıf/property sayısı) dayanması; iç yapısal kalite + ontoloji-kullanımını yakalayamaması.
**Data & Methodology:** 6 yapısal kalite metriği; Wikidata, DBpedia, YAGO, Google KG, Freebase + Naver 'Raftel'.
**Main Contributions:** "Good KG" = ontoloji detayı + instance/triple aktif kullanımı (büyüklük değil); ölçek-gizli yapısal karakteristikleri ifşa.
**Relevance:** Niceliksel ölçek yerine niteliksel yapısal olgunluk; iç graf-sağlığı tanısı (isnad graf bütünlüğü).
**Future Work/Limitations:** (NotebookLM: kısmen dış-bilgi) — yalnız cross-domain KG; domain-özgü KG + downstream-görev korelasyonu.

### [34] Orogat et al. (2021) — CBench · arXiv:2105.00811
**Research Gap:** KGQA benchmark seçiminin keyfîliği; setlerin linguistik/sentaktik/yapısal farkları → küçük-altküme değerlendirmesi güvenilmez.
**Data & Methodology:** Genişletilebilir benchmark suite; fine-grained linguistik/sentaktik/yapısal boyut analizi; kullanıcı-veri eklenebilir.
**Main Contributions:** Tek-sayı metrikten tanısal profillemeye kayış; cevaplanan/cevaplanmayan soru özelliklerinin granüler analizi.
**Relevance:** QA değerlendirme titizliğini standardize eder; yüzeysel metrik-optimizasyonunu caydırır.
**Future Work/Limitations:** Benchmark kalitesi iyileşene dek köprü çözüm; mevcut/kullanıcı-set çeşitliliğine bağımlı.

---

## H. Domain-Specific — Dini / İslami LLM Değerlendirme (en yakın bağlam)

### [35] Abdelaal et al. (2026) — IslamicMMLU · arXiv:2603.23750
**Research Gap:** LLM'ler dini sorgularda kullanılıyor ama core İslami disiplinlerde standart benchmark yok.
**Data & Methodology:** 10.013 çoktan-seçmeli; 3 track — Quran (2.013) / Hadith (4.000) / Fiqh (4.000); 26 LLM; madhab bias-tespit görevi.
**Main Contributions:** Public leaderboard; ortalama %39.8–93.8 (Gemini 3 Flash); frontier modeller Arapça-özgü modelleri geçer; school-of-thought bias.
**Relevance:** Kültürel-hizalı AI; factuality + teolojik bias denetim aracı; projenin doğrudan zemini.
**Future Work/Limitations:** Arapça-özgü model zayıflığı; yalnız çoktan-seçmeli — açık-uçlu teolojik reasoning'i kapsamaz.

### [36] Bhatia et al. (2026) — From RAG to Agentic RAG for Faithful Islamic QA · arXiv:2601.07528
**Research Gap:** Standart MCQ/MRC değerlendirmeleri free-form halüsinasyonu + kanıt-yokken abstain yeteneğini yakalayamıyor; dini ungrounded cevap ciddi sonuç.
**Data & Methodology:** IslamicFaithQA (3.810 bilingual AR/EN üretici); agentic RAG (yapısal tool-call, iteratif kanıt-arama); 25K AR reasoning + 5K tercih + ~6K ayet korpusu.
**Main Contributions:** Agentic RAG standart RAG'ı büyük farkla geçer; SOTA AR-EN doğruluk + halüsinasyon azaltma (Qwen3 4B'de bile).
**Relevance:** GiraffeGraph mimari+metrik kararlarına en yakın; statik retrieval'dan dinamik agentic doğrulamaya + ölçülen abstain.
**Future Work/Limitations:** Ayet-seviyesi korpus odağı; fıkıh/hadis külliyatına genişletme (dış-bilgi, doğrula).

### [37] Patel, Kane & Patel (2023) — Domain-Specific LLMs Faithful to Islamic Worldview · arXiv:2312.06652 (NeurIPS 2023 Muslims-in-ML)
**Research Gap:** LLM'lerin bias/fabrikasyonu; Kuran-Sünnet temelli factual İslami temsil için kültürel hizalama eksiği.
**Data & Methodology:** Kavramsal çerçeve; hedefi teknik problem olarak tanımlar; çözüm-önerileri + zorluk-analizi + değerlendirme metodolojileri.
**Main Contributions:** İslami "faithfulness"ı LLM mimarisinde operasyonalize yol; domain-özgü inşa+değerlendirme stratejileri.
**Relevance:** AI etik/value-alignment/lokalizasyon; bias-tespitinden kültürel-duyarlı model inşasına.
**Future Work/Limitations:** Yüksek-kalite domain dataset + sağlam metrik; ML-İslami-âlim disiplinlerarası işbirliği zorunlu.

### [38] Alzubaidi et al. (2025) — Evaluating Arabic LLMs: Survey of Benchmarks · arXiv:2510.13430
**Research Gap:** Parçalı Arapça NLP test manzarası; birleşik değerlendirme standardı yok.
**Data & Methodology:** 40+ Arapça benchmark; üç dataset-üretim paradigması (native / translation / synthetic) trade-off analizi.
**Main Contributions:** Dört-domain taksonomi — Knowledge / NLP Tasks / Culture & Dialects / Target-Specific; reproducibility + metrik içgörüleri.
**Relevance:** Arapça (Kuran/Hadis dili) eval altyapısı; translation-merkezli testten kültürel-rezonanslıya.
**Future Work/Limitations:** Temporal/multi-turn/kültürel-misalignment açıkları; dinamik, native, interaktif değerlendirme; 40+ benchmark sürekli genişletme.

---

## Özet
- 38/38 makale ayrı NotebookLM notebook'unda, grounded review üretildi.
- Çekirdek (proje için): RAG eval ([23][24][25]), faithfulness ([11][14][18]), dini eval ([35][36]), KG-QA ([32][33]).
- NotebookLM notebook URL'leri: NotebookLM ana sayfanda `[01]…[38]` başlıklarıyla.
- Sonraki: bu review'ları akademik literatür-bölümü taslağına dönüştür; ⭐ çekirdeklerden başla.
