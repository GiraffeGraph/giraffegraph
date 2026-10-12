# Literatür haritası: 38 makale hangi ölçüm katmanına hizmet ediyor?

## Purpose

Efe'nin "LLM başarı ölçüm metrikleri" taramasını `correctness-measurement.md` içindeki katmanlara
eşlemek ve projenin ölçüm sorusu için taramada eksik kalan alanı göstermek.

## Scope

- In: kümelerin katmanlara eşlenmesi, boşluk, okuma önceliği, doğrulama durumu
- Out: makale bazında review metinleri (`wiki/literature/efe_reviews_full.md`), APA metni
  (`wiki/literature/efe_literature_review_section.md`)

## Tarama dosyaları

| Dosya | İçerik |
|---|---|
| `wiki/literature/efe_llm_eval_metrics_review.md` | 38 makalenin listesi, arXiv kimlikleri, 8 küme (A–H) |
| `wiki/literature/efe_reviews_full.md` | Makale başına 300 kelimelik İngilizce review; NotebookLM çıktısı, düzenlenmemiş |
| `wiki/literature/efe_reviews.md` | Aynı makalelerin kısa Türkçe özetleri |
| `wiki/literature/efe_literature_review_section.md` | 10 bölümlük Türkçe literatür bölümü + APA 7 kaynakça |
| `wiki/literature/llm_eval_metrics.bib` | 40 BibTeX kaydı |
| `wiki/literature/extraction_eval_precedents.bib` | Çıkarım doğruluğunu ölçen 7 emsal çalışmanın künyesi (`related-work.md`) |

Durum (2026-10-08): makaleler toplandı ve review'lar üretildi; Efe makaleleri okumadı ve review
metinlerini denetlemedi. arXiv kimliklerinden altısı ([4], [10], [16], [18], [26], [30]) teyitli,
kalanı arama sonucundan alınmış (`wiki/literature/efe_llm_eval_metrics_review.md`, doğrulama notu).

## Çalışma alanındaki üç kaynak kümesi

| Küme | Yer | Odak | Zotero'da |
|---|---|---|---|
| LLM değerlendirme metrikleri, 38 makale | `wiki/literature/`, Zotero `LLM-Eval-Metrics` | Üretilen cevabın kalitesi (L4). İslami bağlam 4 makale ([35]–[38]); Kur'an'a özgü makale yok | Evet |
| Tasarım ve hadis literatürü, 53 kayıt | `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` | KG inşası, grounding, ER, provenance, dijital hadis (L1–L3) | 49'u kişisel kütüphanede `KG-Hadith-Design` koleksiyonunda; etiketler: `hadith`, `kg-construction`, `grounding-attribution`, `entity-resolution`, `confidence-hitl`, `provenance-memory`, `method` |
| Bilgi katmanı tezi | `cache-and-ledger/README.md`, `PAPER.md` | Türetilebilen / karar ayrımı. Kaynakça listesi yoktur; kanıt kendi ölçümleridir (`cache-and-ledger/data/`) | Hayır |

## Küme → katman eşlemesi

| Küme | Makaleler | Hizmet ettiği katman | Projede kullanımı |
|---|---|---|---|
| A Genel survey / çerçeve | [01]–[05] | Çerçeve | Çok boyutlu değerlendirme fikri; tek metriğe güvenmeme gerekçesi |
| B Klasik NLG metrikleri | [06]–[10] | L4, zayıf | BLEU / ROUGE / BERTScore serbest metin benzerliği ölçer; yapılandırılmış çıktı (üçlü, zincir) için uygun değildir. Rolü: neden kullanılmadığının gerekçesi |
| C Faithfulness | [11]–[14] | L4 | Cevabın getirilen kaynağa sadakati; [14] atıf doğruluğunda kısmi destek |
| D Halüsinasyon / faktüellik | [15]–[22] | L4, fikir olarak L1 | FActScore [18] cevabı atomik iddialara böler; bu, üçlü düzeyi precision'ın metin tarafındaki karşılığıdır |
| E RAG değerlendirme | [23]–[28] | **L4 çekirdeği** | RAGAS [23], ARES [24]: retrieval ve üretimi ayrı ölçen bileşenli metrikler |
| F LLM-as-a-judge | [29]–[31] | L4, ölçüm yöntemi | Otomatik puanlayıcı; insan etiketiyle doğrulanmadan birincil ölçüt olamaz |
| G KG soru-cevap | [32]–[34] | L3 ve L4 | [33] grafın yapısal kalite metrikleri; [32], [34] KGQA cevap doğruluğu |
| H Dini / İslami | [35]–[38] | L4, alan bağlamı | [36] İslami soru-cevapta faithfulness ve çekimserlik ölçümü; projeye en yakın çalışma |

## Boşluk

Taramanın ağırlığı L4'tedir: sistem bir **cevap** ürettiğinde o cevap iyi mi. Projenin sorduğu soru
ise ağırlıkla L1 ve L2'dir: metinden çıkardığımız **yapı** doğru mu. 38 makalenin içinde bilgi
çıkarımı değerlendirmesi, entity resolution metrikleri, etiketleme uyumu ve KG doğruluk tahmini
üzerine doğrudan çalışma yoktur; G kümesinin üç makalesi graf üzerinden soru-cevabı ve yapısal
kaliteyi ele alır, çıkarımın doğruluğunu değil.

| Eksik konu | Hangi katman | Neden gerekli |
|---|---|---|
| Metinden KG çıkarımının değerlendirilmesi (üçlü düzeyi P/R, eşleşme kriterleri) | L1 | Projenin birincil ölçümü |
| Entity resolution / linking metrikleri | L2 | H4 hipotezi ve over-merge ölçümü |
| Kodlayıcılar arası uyum ve etiket kalitesi | Altın standart | K-5 taahhüdü, κ ≥ 0,75 |
| Örneklemle KG doğruluk tahmini | Tüm korpus | 500 hadisin ötesine genelleme |
| LLM güven kalibrasyonu ve seçici tahmin | HITL yönlendirme | Pilotta AUC 0,626 |
| Dijital hadis çalışmaları (isnad ayrıştırma, ravi ağı) | Alan | Konumlanma ve baz çizgi |

## Boşluğu kapatan, künyesi doğrulanmış kaynaklar

Hepsi `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` içinde, Crossref / arXiv'den çekilmiş.

| Konu | BibTeX anahtarı |
|---|---|
| LLM ile KG inşası ve değerlendirmesi | `zhang2024edc`, `mo2025kggen`, `lavie2024itext2kg`, `ye2022generative` |
| ER metrikleri ve yöntemleri | `bagga1998algorithms` (B-cubed), `luo2005coreference` (CEAF), `fellegi1969theory`, `li2020ditto` |
| Etiket kalitesi | `dawid1979maximum` |
| Atıf ve grounding | `rashkin2023measuring` (AIS), `wei2024longform` (SAFE), `zha2023alignscore`, `laban2022summac` |
| Güven ve yönlendirme | `kadavath2022language`, `xiong2024can`, `angelopoulos2021gentle` |
| Dijital hadis | `wirahman2026linking`, `raja2026grading`, `haque2026hadith`, `asgari2025rezwan`, `kamran2023semantichadith`, `mghari2022sanadset`, `alam2021social` |

## Künyesi doğrulanmamış adaylar

Aşağıdakiler bellekten gelen önerilerdir; birincil kaynaktan teyit edilmeden atıf yapılmaz.

- Paulheim, KG refinement survey'i — KG değerlendirme yöntemlerinin sınıflaması `[UNVERIFIED]`
- Zaveri vd., linked data kalite değerlendirmesi survey'i — kalite boyutları `[UNVERIFIED]`

Text2KGBench ve Gao vd. doğrulandı; künyeleri `wiki/literature/extraction_eval_precedents.bib` içinde,
içerikleri `related-work.md` içinde.

## Okuma önceliği

Ölçüm sorusuna en çok katkı verenler, sırayla:

1. `haque2026hadith` — alanın eleştirel derlemesi; benchmark ve uzman doğrulaması eksikliği
2. `wirahman2026linking` — Sanadset üzerinde ravi ER; L2 için baz çizgi ve metrik örneği
3. [23] RAGAS — L4 metriklerinin tanımları
4. [18] FActScore — atomik iddia doğrulama; L1 ile L4 arasındaki köprü
5. [36] Bhatia vd. — İslami soru-cevapta faithfulness ve çekimserlik
6. `zhang2024edc` — LLM ile KG çıkarımının nasıl değerlendirildiğine örnek
7. [33] Seo vd. — referans veri gerektirmeyen yapısal KG metrikleri
8. [31] LLMs-as-Judges survey — otomatik puanlayıcının sınırları

## Rules

- MUST: bir makaleye atıf yapılmadan önce künyesi birincil kaynaktan çekilir ve tam metinde iddia aranır.
  NotebookLM review'u makalenin yerine geçmez.
- MUST: taramaya eklenen her makale bir katmana (L0–L4) ya da altın standart / yönlendirme başlığına bağlanır.
- SHOULD: B kümesi metrikleri L1–L3 için önerilmez.

## Verification checklist

- [ ] Tablodaki makale numaraları `wiki/literature/efe_reviews_full.md` başlıklarıyla eşleşiyor
- [ ] "Doğrulanmış" tablosundaki her anahtar `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` içinde var
- [ ] Doğrulanan bir aday `[UNVERIFIED]` listesinden çıkarılıp `wiki/literature/` altındaki bir bib dosyasına eklendi

## Related docs

- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/related-work.md`
- `wiki/sources/claude-science-context/10_related_work_map.md`
- `wiki/sources/claude-science-results/09_yayin_plani.md`

## Last updated

2026-10-08
