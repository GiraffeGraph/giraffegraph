# Literatür Taraması: Büyük Dil Modellerinde Başarı Ölçüm Metrikleri

> Akademik literatür-bölümü taslağı. Atıf stili: **APA 7** (yazar-tarih). Proje bağlamı: dini sorular için Knowledge Graph + RAG sistemi (hadis isnad zinciri graf modellemesi).

## 1. Giriş

Büyük dil modellerinin (LLM) akademi ve sanayide hızla yaygınlaşması, bu sistemlerin yetenek, sınır ve risklerinin güvenilir biçimde ölçülmesini kritik bir disiplin hâline getirmiştir (Chang vd., 2023). Chang vd. (2023), değerlendirmenin yalnızca görev (task) düzeyinde değil, toplumsal etki ve potansiyel riskler düzeyinde de ele alınması gerektiğini savunarak alana "what / where / how to evaluate" eksenli bir taksonomi kazandırmıştır. Guo vd. (2023) ise bu çerçeveyi knowledge & capability, alignment ve safety olmak üzere üç katmana ayırarak güvenilirlik perspektifini metrik tartışmasının merkezine taşımıştır. Bu iki temel derleme, mevcut çalışmanın metrik tartışmasının omurgasını oluşturur; ancak her ikisi de hızlı eskimeye açıktır ve 2023 sonrası RAG ile LLM-as-judge gelişmelerini sınırlı biçimde kapsar. Laskar vd. (2024) tam da bu noktada değerlendirme kurgularındaki parçalılığa ve benchmark kontaminasyonuna dikkat çekerek, bulguların yeniden-üretilebilir (reproducible) ve güvenilir olması için metodolojik öneriler sunar.

Dini bağlamda otomatik soru-cevap üreten bir RAG ve bilgi grafı sisteminin değerlendirilmesi, bu genel çerçevelerin ötesinde, faktüellik, sadakat (faithfulness) ve kaynak-temellilik (groundedness) metriklerinin özel önem kazandığı bir alt-alandır. Bu nedenle bu tarama, metrikleri sekiz tematik küme altında, genel çerçevelerden başlayıp dini-domain değerlendirmelerine doğru daralan bir yapıda ele alır.

## 2. Çok-Boyutlu Değerlendirme Çerçeveleri

Tek-metrikli benchmark'ların darlığına karşı en etkili yanıt, Stanford HELM çerçevesidir (Liang vd., 2022). Liang vd. (2022), modellerin HELM öncesinde ortalama yalnızca %17.9 oranında çekirdek senaryolarda test edildiğini gösterip, accuracy'nin yanına calibration, robustness, fairness, bias, toxicity ve efficiency'yi ekleyen çok-metrikli bir yaklaşımla bu kapsamı %96'ya çıkarmıştır. HELM'in "living benchmark" tasarımı ve metrik trade-off'larını açığa çıkarması, dini QA gibi accuracy'nin tek başına yetersiz kaldığı (bias ve calibration'ın eşit önemde olduğu) alanlar için doğrudan bir metodolojik şablon sunar. Joshi (2025) ise 50'den fazla metriği hiyerarşik bir taksonomide toplayarak ve domain-özgü ağırlıklandırma (örn. Composite Evaluation Index) önererek bu çok-boyutluluğu pratik bir metrik-seçim matrisine dönüştürmeyi dener; ancak hakem sürecini tamamlamamış bir ön-baskı (preprint) olması bulgularının ihtiyatla kullanılmasını gerektirir.

## 3. Klasik Metrikler ve Sınırlılıkları

Otomatik değerlendirmenin metodolojik temelini BLEU (Papineni vd., 2002), ROUGE (Lin, 2004) ve METEOR (Banerjee & Lavie, 2005) oluşturur: BLEU n-gram precision'a, ROUGE özetlemede recall'a, METEOR ise stemming ve eş-anlamlılıkla anlamsal esnekliğe dayanır. Bu metrikler istatistiksel ve erken-nöral modelleri mümkün kılmış olsa da, yüzeysel sözcük örtüşmesine bağımlılıkları nedeniyle anlamsal eşdeğerliği, yaratıcı parafrazı ve faktüel hataları yakalamakta yetersizdir (Celikyilmaz vd., 2020). Bu boşluğa yanıt olarak BERTScore, contextual embedding'lerle token benzerliği hesaplayarak insan yargısıyla korelasyonu belirgin biçimde artırmıştır (Zhang vd., 2019); BLEURT bu fikri milyonlarca sentetik örnekle ön-eğitilmiş öğrenilmiş bir metriğe taşıyarak veri kıt veya dağıtım-dışı koşullarda dahi sağlamlık sağlamıştır (Sellam vd., 2020); BARTScore ise değerlendirmeyi bir metin-üretim problemi olarak yeniden çerçeveleyip seq2seq log-likelihood ile faktüellik dahil çok-perspektifli, referanssız ölçüm imkânı sunmuştur (Yuan vd., 2021). Celikyilmaz vd. (2020) bu metrikleri human-centric, untrained automatic ve machine-learned olmak üzere üç kategoride sistematize ederek alanın haritasını çıkarır. Bu evrim, alanın yüzeysel örtüşmeden anlamsal ve model-tabanlı değerlendirmeye doğru kaydığını gösterir; ancak BERTScore gibi benzerlik-temelli metrikler hâlâ faktüel hatayı doğrudan ölçmez (Zhang vd., 2019), bu da sadakat-odaklı metriklere geçişi zorunlu kılar.

## 4. Sadakat (Faithfulness) ve Faktüel Tutarlılık

RAG sistemlerinin merkezî sorunu, üretilen cevabın sağlanan bağlama sadık kalıp kalmadığıdır. Li vd. (2022), NLG'de sadakat metriklerini entailment-tabanlı, benzerlik-tabanlı ve QA-tabanlı olmak üzere birleşik bir taksonomide toplayarak bu parçalı literatürü konsolide etmiştir. Lamsiyah vd. (2025), "Trust but Verify" başlıklı güncel derlemesinde (2020–2025) bu taksonomiyi LLM-as-judge yaklaşımlarını da kapsayacak şekilde genişletir ve kritik bir gözlem yapar: insan yargısının kendisi düşük değerlendirici-arası uyumla bir "hareketli hedef" olduğundan, kusursuz otomatik metrik arayışı epistemolojik olarak sorunludur. QA-tabanlı yaklaşımlar içinde Fabbri vd. (2021), soru-üretimi ve cevaplanabilirlik sınıflamasını optimize ederek SummaC benchmark'ında önceki QA metriklerine %14 iyileşme sağlamış ve entailment ile QA sinyallerinin tümleyici olduğunu göstermiştir. Projemiz açısından en doğrudan ilgili çalışma ise Zhang vd. (2024) tarafından yürütülen atıf (citation) değerlendirmesidir: mevcut metriklerin atıf desteğini ikili (binary) ele aldığını, oysa pratikte "kısmi destek" düzeyinin yaygın olduğunu ve en iyi metriklerin bile kısmi desteği ayırt edemediğini ortaya koymuşlardır — bu bulgu, hadis isnad zincirinde kaynak-atıflı cevapların değerlendirilmesi için doğrudan uyarıcıdır.

## 5. Halüsinasyon ve Faktüellik Benchmark'ları

Faktüelliğin ölçümü, faithfulness'tan ayrı olarak, modelin gerçek-dünya bilgisiyle çelişip çelişmediğini sınar. Lin vd. (2021), modellerin yaygın insan yanlış-inançlarını taklit etme eğilimini 817 adversarial soruyla ölçen TruthfulQA ile çarpıcı bir "ters ölçeklenme" (inverse scaling) bulgusu sunar: en büyük modeller en az doğrucu olanlardır. Ancak bu benchmark'ın eğitim-verisi sızıntısı nedeniyle doygunlaştığı bilinmektedir (Lin vd., 2021), bu da dinamik benchmark'lara olan ihtiyacı doğurur. Li, Cheng vd. (2023) geliştirdiği HaluEval, 10.000 örnekle halüsinasyon tanıma yeteneğini ölçer ve harici bilgi sağlamanın tespiti iyileştirdiğini gösterir. Manakul vd. (2023) geliştirdiği SelfCheckGPT, harici kaynak veya logit gerektirmeyen sıfır-kaynak, kara-kutu bir tutarlılık-tabanlı tespit yöntemi sunarak altın-kaynağın zor olduğu dini cevaplarda pratik bir araç sağlar; ancak tutarlı biçimde üretilen yanlışları kaçırması temel sınırlamasıdır. Min vd. (2023) ise FActScore ile uzun-form üretimi atomik gerçeklere bölüp güvenilir kaynakla desteklenen oranını hesaplayarak fine-grained bir faktüel-precision metriği sunar ve RAG'ın uzun cevaplarının iddia-bazlı doğrulanması için doğrudan uygulanabilirdir. Huang vd. (2023) factuality ile faithfulness ayrımını netleştirip kapsamlı bir halüsinasyon taksonomisi sunarken, Rahman, Islam vd. (2025) hakemli derlemesi fact-checking ile factuality değerlendirmesini birleştirip statik parametrik bilgiden dinamik RAG-tabanlı doğrulamaya kayışı belgeler. Güncel benchmark'lardan DefAn (Rahman, Anwar vd., 2024), kesin-cevaplı (isim/tarih/sayı) sorgularda 75.000+ prompt ile faktüel hata oranlarının %82'ye ulaşabildiğini ve özellikle numerik sorgularda performansın düştüğünü göstermiştir — hadis ravi ve tarih gibi kesin-cevaplı sorgular için ilgili bir bulgu. HalluLens (Bang vd., 2025) ise intrinsic/extrinsic ayrımı ve veri-sızıntısına karşı dinamik test-seti üretimiyle benchmark doygunluğu sorununu doğrudan ele alır.

## 6. RAG Değerlendirme Çerçeveleri

Projenin çekirdeğini RAG değerlendirme literatürü oluşturur. Es vd. (2023) geliştirdiği RAGAS, RAG hattını referanssız ve etiketsiz biçimde değerlendiren ilk yaygın çerçeve olup faithfulness, answer relevancy, context precision ve context recall metriklerini sunar; insan-anotasyon darboğazını kaldırarak hızlı değerlendirme döngüleri sağladığından GiraffeGraph RAG hattının doğrudan ölçüm aracıdır. Saad-Falcon vd. (2023) geliştirdiği ARES bu yaklaşımı istatistiksel olarak güçlendirir: sentetik veriyle eğitilmiş hafif LM-judge'ları prediction-powered inference (PPI) ile birleştirerek yalnızca birkaç yüz insan-anotasyonuyla domain-shift'e dayanıklı, güvence-altına-alınmış ölçüm yapar. Benchmark cephesinde Chen vd. (2023) önerdiği RGB, RAG'ı noise robustness, negative rejection, information integration ve counterfactual robustness olmak üzere dört temel yeteneğe ayrıştırarak "RAG halüsinasyonun panzehiridir" varsayımına meydan okur ve modellerin reddetme/sentez/counterfactual-direnci konularında zayıf olduğunu gösterir — gürültülü veya çelişkili dini kaynaklar için kritik bir tanı çerçevesi. Lyu vd. (2024) geliştirdiği CRUD-RAG, değerlendirmeyi yalnız QA'dan Create/Read/Update/Delete senaryolarına genişleterek ekolojik geçerliliği artırır; Park vd. (2025) önerdiği MIRAGE, kontrollü bir retrieval havuzu üzerinde noise vulnerability ve context misinterpretation gibi metrik-yoğun boyutlar tanımlar; Oche vd. (2025) ise RAG literatürünü enterprise-dağıtım, gizlilik ve agentic-RAG yönelimleriyle bütünsel bir yol haritasına sentezler.

## 7. Otomatik Değerlendirici Olarak LLM (LLM-as-a-Judge)

Dini cevap kalitesinin insan-uzman değerlendirmesi maliyetli olduğundan, otomatik değerlendiriciler önemli bir alternatiftir. Zheng vd. (2023), GPT-4'ün MT-Bench ve Chatbot Arena üzerinde insan tercihleriyle %80'in üzerinde — insanlar-arası uyum düzeyinde — örtüştüğünü göstererek LLM-as-judge'ı ölçeklenebilir ve açıklanabilir bir vekil (proxy) olarak meşrulaştırmıştır. Liu vd. (2023) geliştirdiği G-Eval, chain-of-thought ve form-doldurma paradigmasıyla GPT-4'ü kullanarak özetlemede 0.514 Spearman korelasyonuna ulaşmış ve özelleştirilmiş rubrikler kurmak için bir şablon sunmuştur. Ancak her iki çalışma da kritik bir uyarı paylaşır: judge'lar position, verbosity ve self-enhancement bias'larından muzdariptir ve LLM-üretimi metinlere sistemik bir eğilim gösterirler (Zheng vd., 2023; Liu vd., 2023). Li, Dong vd. (2024) kapsamlı derlemesi bu bias taksonomisini ve azaltma yöntemlerini konsolide ederek judge kullanımının metodolojik savunmasını sağlar. Bu sınırlamalar, alan-uzmanlığı gerektiren dini içerikte judge kullanımının dikkatli kalibrasyon ve insan-doğrulamasıyla desteklenmesi gerektiğini ima eder.

## 8. Bilgi Grafı Soru-Cevap Değerlendirmesi

İsnad zincirinin graf olarak modellenmesi, projeyi KGQA değerlendirme literatürüne bağlar. Potdar vd. (2025) geliştirdiği Chronos çerçevesi, KGQA'yı uçtan-uca ve bileşen-seviyesi metriklerle (E2E coverage/precision, MRR, Top-K, generative accuracy) endüstri-ölçeğinde değerlendirir ve nihai cevap doğruluğunun yanında ara-bileşen bütünlüğünün de ölçülmesi gerektiğini vurgular — isnad graf sorgu sistemi için doğrudan uygulanabilir. Grafın kendisinin kalitesi için Seo vd. (2022), ölçek-göstergelerinin (sınıf/property sayısı) ötesine geçen altı yapısal kalite metriği önererek "iyi bir bilgi grafı"nı büyüklüğüyle değil ontoloji-detayı ve aktif kullanımıyla tanımlar; bu, inşa edilen isnad grafının bütünlük ve bağlantılılığını ölçmek için uygundur. Orogat vd. (2021) geliştirdiği CBench ise KGQA benchmark'larının linguistik/sentaktik/yapısal farklarını analiz ederek tek-sayı metrikten tanısal profillemeye geçişi savunur ve Micro/Macro/Global F1 gibi fine-grained metrikler sunar.

## 9. Dini ve İslami Bağlamda Değerlendirme

Projeye en yakın küme, dini-domain değerlendirmeleridir. Abdelaal vd. (2026) geliştirdiği IslamicMMLU, Kuran, Hadis ve Fıkıh üzerinde 10.013 çoktan-seçmeli soruyla 26 LLM'i değerlendiren ve madhab (mezhep) bias-tespit görevi içeren ilk kapsamlı İslami benchmark olup, frontier modellerin Arapça-özgü modelleri geçtiğini ortaya koyar; ancak çoktan-seçmeli yapısı açık-uçlu teolojik reasoning ve üretim-faithfulness'ını ölçemez. Bu boşluğu Bhatia vd. (2026) doldurur: IslamicFaithQA adlı 3.810-maddelik üretici benchmark ile free-form halüsinasyonu ve kanıt-yokken abstain (çekimserlik) yeteneğini doğrudan ölçer ve agentic RAG'ın (yapısal tool-call ile iteratif kanıt-arama) standart RAG'ı büyük farkla geçtiğini gösterir — bu çalışma, hem mimari (agentic RAG) hem metrik (faithfulness + ölçülen abstain) açısından GiraffeGraph'a literatürdeki en yakın referanstır. Patel vd. (2023), dünya-görüşüne sadık dini LLM'in teknik fizibilitesini ve değerlendirme kriterlerini kavramsal düzeyde tartışırken, ML pratisyenleri ile İslami âlimler arasında disiplinlerarası işbirliğinin zorunluluğunu vurgular. Son olarak Alzubaidi vd. (2025), 40'tan fazla Arapça LLM benchmark'ını inceleyen derlemesinde translation-merkezli testlerin kültürel uyumsuzluğunu ve çok-turlu/temporal değerlendirme açıklarını ortaya koyarak Kuran/Hadis dilindeki değerlendirme altyapısı için kritik bir çerçeve sunar.

## 10. Sentez ve Araştırma Boşluğu

Literatür üç ana eğilim gösterir. Birincisi, metriklerin yüzeysel n-gram örtüşmesinden (Papineni vd., 2002; Lin, 2004) anlamsal (Zhang vd., 2019; Sellam vd., 2020; Yuan vd., 2021), oradan da iddia-bazlı faktüellik (Min vd., 2023) ve bileşen-ayrıştırmalı RAG değerlendirmesine (Es vd., 2023; Saad-Falcon vd., 2023; Chen vd., 2023) doğru evrimidir. İkincisi, statik benchmark'ların doygunluk ve veri-sızıntısı nedeniyle dinamik üretime (Bang vd., 2025) ve otomatik LLM-judge paradigmalarına (Zheng vd., 2023; Liu vd., 2023; Li, Dong vd., 2024) yönelimidir. Üçüncüsü, genel-amaçlı değerlendirmeden domain-özgü, kültürel-hizalı değerlendirmeye (Abdelaal vd., 2026; Bhatia vd., 2026; Patel vd., 2023; Alzubaidi vd., 2025) geçiştir.

Bu üç eğilimin kesişiminde belirgin bir boşluk vardır: dini bilgi grafı + RAG sistemlerinin değerlendirilmesi için, (i) hadis isnad zincirinin graf-bütünlüğünü (Seo vd., 2022) KGQA cevap-doğruluğuyla (Potdar vd., 2025) birleştiren, (ii) kaynak-atıflı cevaplarda kısmi-desteği (Zhang vd., 2024) ve iddia-bazlı faktüelliği (Min vd., 2023) ölçen, (iii) çekimserlik (abstain) yeteneğini (Bhatia vd., 2026) içeren bütünleşik bir metrik çerçevesi henüz olgunlaşmamıştır. IslamicMMLU çoktan-seçmeliyle (Abdelaal vd., 2026), IslamicFaithQA üretici-faithfulness ile (Bhatia vd., 2026) bu boşluğun parçalarını ele alsa da, isnad grafının yapısal kalitesini RAG faithfulness'ı ve faktüellikle birleştiren bir değerlendirme bütünü literatürde mevcut değildir. Bu çalışma, GiraffeGraph sistemini tam da bu kesişimde konumlandırmayı ve adı geçen metrikleri (RAGAS/ARES faithfulness, FActScore iddia-doğrulama, yapısal KG-kalite, abstain ölçümü) entegre bir değerlendirme protokolünde birleştirmeyi hedeflemektedir.

---

## Kaynakça (APA 7)

Abdelaal, A., Al Haffar, M. N., Fawzi, M., & Magdy, W. (2026). *IslamicMMLU: A benchmark for evaluating LLMs on Islamic knowledge*. arXiv. https://doi.org/10.48550/arXiv.2603.23750

Alzubaidi, A., Alsuwaidi, S., Boussaha, B. E. A., AlQadi, L., Alkaabi, O., Alyafeai, M., Alobeidli, H., & Hacid, H. (2025). *Evaluating Arabic large language models: A survey of benchmarks, methods, and gaps*. arXiv. https://doi.org/10.48550/arXiv.2510.13430

Banerjee, S., & Lavie, A. (2005). METEOR: An automatic metric for MT evaluation with improved correlation with human judgments. In *Proceedings of the ACL Workshop on Intrinsic and Extrinsic Evaluation Measures for Machine Translation and/or Summarization* (pp. 65–72). Association for Computational Linguistics.

Bang, Y., Ji, Z., Schelten, A., Hartshorn, A., Fowler, T., Zhang, C., Cancedda, N., & Fung, P. (2025). *HalluLens: LLM hallucination benchmark*. arXiv. https://doi.org/10.48550/arXiv.2504.17550

Bhatia, G., Alam, F., vd. (2026). *From RAG to agentic RAG for faithful Islamic question answering*. arXiv. https://doi.org/10.48550/arXiv.2601.07528

Celikyilmaz, A., Clark, E., & Gao, J. (2020). *Evaluation of text generation: A survey*. arXiv. https://doi.org/10.48550/arXiv.2006.14799

Chang, Y., Wang, X., Wang, J., Wu, Y., Yang, L., Zhu, K., Chen, H., Yi, X., Wang, C., Wang, Y., Ye, W., Zhang, Y., Chang, Y., Yu, P. S., Yang, Q., & Xie, X. (2023). *A survey on evaluation of large language models*. arXiv. https://doi.org/10.48550/arXiv.2307.03109

Chen, J., Lin, H., Han, X., & Sun, L. (2023). *Benchmarking large language models in retrieval-augmented generation*. arXiv. https://doi.org/10.48550/arXiv.2309.01431

Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). *RAGAS: Automated evaluation of retrieval augmented generation*. arXiv. https://doi.org/10.48550/arXiv.2309.15217

Fabbri, A. R., Wu, C.-S., Liu, W., & Xiong, C. (2021). *QAFactEval: Improved QA-based factual consistency evaluation for summarization*. arXiv. https://doi.org/10.48550/arXiv.2112.08542

Guo, Z., vd. (2023). *Evaluating large language models: A comprehensive survey*. arXiv. https://doi.org/10.48550/arXiv.2310.19736

Huang, L., vd. (2023). *A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions*. arXiv. https://doi.org/10.48550/arXiv.2311.05232

Joshi, S. (2025). *Evaluation of large language models: Review of metrics, applications, and methodologies* (Preprint No. 202504.0369). Preprints.org. https://doi.org/10.20944/preprints202504.0369.v1

Lamsiyah, S., Nourbakhsh, A., & Schommer, C. (2025). Trust but verify: A comprehensive survey of faithfulness evaluation methods in abstractive text summarization. In *Proceedings of RANLP 2025*. ACL Anthology.

Laskar, M. T. R., Alqahtani, S., Bari, M. S., Rahman, M., Khan, M. A. M., Khan, H., Jahan, I., Bhuiyan, A., Tan, C. W., Parvez, M. R., Hoque, E., Joty, S., & Huang, J. (2024). A systematic survey and critical review on evaluating large language models: Challenges, limitations, and recommendations. In *Proceedings of EMNLP 2024*. Association for Computational Linguistics. https://doi.org/10.48550/arXiv.2407.04069

Li, H., Dong, Q., Chen, J., Su, H., Zhou, Y., Ai, Q., Ye, Z., & Liu, Y. (2024). *LLMs-as-judges: A comprehensive survey on LLM-based evaluation methods*. arXiv. https://doi.org/10.48550/arXiv.2412.05579

Li, J., Cheng, X., Zhao, W. X., Nie, J.-Y., & Wen, J.-R. (2023). HaluEval: A large-scale hallucination evaluation benchmark for large language models. In *Proceedings of EMNLP 2023*. Association for Computational Linguistics. https://doi.org/10.48550/arXiv.2305.11747

Li, W., Wu, W., Chen, M., Liu, J., Xiao, X., & Wu, H. (2022). *Faithfulness in natural language generation: A systematic survey of analysis, evaluation and optimization methods*. arXiv. https://doi.org/10.48550/arXiv.2203.05227

Liang, P., vd. (2022). *Holistic evaluation of language models*. arXiv. https://doi.org/10.48550/arXiv.2211.09110

Lin, C.-Y. (2004). ROUGE: A package for automatic evaluation of summaries. In *Text Summarization Branches Out* (pp. 74–81). Association for Computational Linguistics.

Lin, S., Hilton, J., & Evans, O. (2021). *TruthfulQA: Measuring how models mimic human falsehoods*. arXiv. https://doi.org/10.48550/arXiv.2109.07958

Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-Eval: NLG evaluation using GPT-4 with better human alignment. In *Proceedings of EMNLP 2023*. Association for Computational Linguistics. https://doi.org/10.48550/arXiv.2303.16634

Lyu, Y., Li, Z., Niu, S., Xiong, F., Tang, B., Wang, W., Wu, H., Liu, H., Xu, T., & Chen, E. (2024). CRUD-RAG: A comprehensive Chinese benchmark for retrieval-augmented generation of large language models. *ACM Transactions on Information Systems*. https://doi.org/10.1145/3701228

Manakul, P., Liusie, A., & Gales, M. J. F. (2023). *SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models*. arXiv. https://doi.org/10.48550/arXiv.2303.08896

Min, S., vd. (2023). FActScore: Fine-grained atomic evaluation of factual precision in long form text generation. In *Proceedings of EMNLP 2023*. Association for Computational Linguistics. https://doi.org/10.48550/arXiv.2305.14251

Oche, A. J., Folashade, A. G., Ghosal, T., & Biswas, A. (2025). *A systematic review of key retrieval-augmented generation (RAG) systems: Progress, gaps, and future directions*. arXiv. https://doi.org/10.48550/arXiv.2507.18910

Orogat, A., Liu, I., & El-Roby, A. (2021). *CBench: Towards better evaluation of question answering over knowledge graphs*. arXiv. https://doi.org/10.48550/arXiv.2105.00811

Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). BLEU: A method for automatic evaluation of machine translation. In *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics* (pp. 311–318). Association for Computational Linguistics. https://doi.org/10.3115/1073083.1073135

Park, C., Moon, H., Park, C., & Lim, H. (2025). MIRAGE: A metric-intensive benchmark for retrieval-augmented generation evaluation. In *Findings of NAACL 2025*. Association for Computational Linguistics. https://doi.org/10.48550/arXiv.2504.17137

Patel, S., Kane, H., & Patel, R. (2023). *Building domain-specific LLMs faithful to the Islamic worldview: Mirage or technical possibility?* [Muslims in ML Workshop, NeurIPS 2023]. arXiv. https://doi.org/10.48550/arXiv.2312.06652

Potdar, S., Lee, D., Attia, O., Embar, V., Meng, D., Balaji, R., Seivwright, C., Choi, E., Farid, M. H., Sun, Y., & Li, Y. (2025). *Comprehensive evaluation for a large scale knowledge graph question answering service*. arXiv. https://doi.org/10.48550/arXiv.2501.17270

Rahman, A B M A., Anwar, S., Usman, M., & Mian, A. (2024). *DefAn: Definitive answer dataset for LLMs hallucination evaluation*. arXiv. https://doi.org/10.48550/arXiv.2406.09155

Rahman, S. S., Islam, M. A., Alam, M. M., Zeba, M., Rahman, M. A., Chowa, S. S., Raiaan, M. A. K., & Azam, S. (2025). Hallucination to truth: A review of fact-checking and factuality evaluation in large language models. *Artificial Intelligence Review*. https://doi.org/10.1007/s10462-025-11454-w

Saad-Falcon, J., Khattab, O., Potts, C., & Zaharia, M. (2023). *ARES: An automated evaluation framework for retrieval-augmented generation systems*. arXiv. https://doi.org/10.48550/arXiv.2311.09476

Sellam, T., Das, D., & Parikh, A. P. (2020). *BLEURT: Learning robust metrics for text generation*. arXiv. https://doi.org/10.48550/arXiv.2004.04696

Seo, S., Cheon, H., Kim, H., & Hyun, D. (2022). *Structural quality metrics to evaluate knowledge graphs*. arXiv. https://doi.org/10.48550/arXiv.2211.10011

Yuan, W., Neubig, G., & Liu, P. (2021). *BARTScore: Evaluating generated text as text generation*. arXiv. https://doi.org/10.48550/arXiv.2106.11520

Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2019). *BERTScore: Evaluating text generation with BERT*. arXiv. https://doi.org/10.48550/arXiv.1904.09675

Zhang, W., Aliannejadi, M., Pei, J., Yuan, Y., Huang, J.-H., & Kanoulas, E. (2024). *A comparative analysis of faithfulness metrics and humans in citation evaluation*. arXiv. https://doi.org/10.48550/arXiv.2408.12398

Zheng, L., vd. (2023). *Judging LLM-as-a-judge with MT-bench and Chatbot Arena*. arXiv. https://doi.org/10.48550/arXiv.2306.05685

---

> **Notlar (teslim öncesi):**
> - Atıf stili APA 7'ye çevrildi (in-text yazar-tarih + kaynakça).
> - Bazı çok-yazarlı kaynaklarda tam liste yerine "vd." kullanıldı (Guo, Liang, Huang, Min, Zheng, Bhatia). APA tam-liste (≤20 yazar) ister → bu girdileri arXiv'den tamamla.
> - Metinde iki ayrı "Li" ([16] Li, J. vd. 2023 — HaluEval; [31] Li, H. vd. 2024 — LLMs-as-judges) ve iki ayrı "Zhang/Rahman" var; in-text'te ad-baş harfi/yıl ile ayrıştırıldı. Kontrol et.
> - Türkçe APA'da "et al." yerine "vd." kullanıldı.
