# 11 — Değerlendirme tasarımı notları (öneri, Claude Science sorgulamalı)

## 1. Ablation merdiveni (H1'in adil sınanması)

Formdaki "2 koşul"un yerine, her basamağın katkısını ayrı ölçen bir merdiven. TÜBİTAK'taki 2 koşul bu merdivenin uç noktaları olarak korunur (C0 ve C5).

| Kod | Koşul | Ne ölçer |
|---|---|---|
| C0 | Ham LLM → doğrudan graf (formdaki baz çizgi) | Referans |
| C1 | + şema-kısıtlı prompt (tip listesi, JSON kontratı) | Prompt etkisi |
| C2 | + deterministik şema doğrulama (per-item red/öneri) | Drift filtresi |
| C3 | + grounding kapısı (quote ⊂ segment, offset, isteğe bağlı NLI) | Halüsinasyon filtresi |
| C4 | + ER (otoriteye linking) + isnad kuralları (muâsara/likâ/tabaka) | Alan bilgisi |
| C5 | + HITL (yönlendirme politikası P ile) | İnsan katkısı ve maliyeti |
| Cx | Deterministik parser (sîga lügati + otorite eşleme, LLM yok) | "LLM'e gerek var mı?" baz çizgisi |

Otomatik C0–C4 koşulları ucuz. Tüm modellerde ve tüm 500 hadiste koşturulabilir. C5 pahalı: tek model × alt küme × kör protokol.

## 2. Metrikler (düzeltilmiş tanımlar)

- **Üçlü P/R/F1:** Eşleşme kriteri açıkça tanımlanmalı. Seçenekler: (a) otorite ID düzeyinde katı eşleşme, (b) mention span düzeyinde gevşek eşleşme. Her ikisi de raporlanmalı. Precision ağırlıklı özet olarak F0.5.
- **Zincir düzeyi:** Tam doğru zincir oranı, zincir düzenleme mesafesi (eksik/uydurma/sırası yanlış ravi).
- **Halüsinasyon oranı:** Kaynak metinde dayanağı olmayan üçlüler. İki ayrı tür raporlanmalı: *intrinsic* (metinle çelişen) ve *extrinsic* (metinde olmayan).
- **Şema sapması:** Ham model çıktısında şema-dışı tip ve alan oranı (C0/C1'de). Ayrıca C2'de **reddedilme kaynaklı recall kaybı**.
- **ER:** Pairwise P/R/F1, B-cubed, CEAF-e. **Yanlış-birleştirme oranı** ayrı raporlanmalı (asimetrik maliyet). H4 için duplicate-node oranı.
- **HITL:** Reddetme oranı (yönlendirme politikasına koşullu olarak), **doğrulanmış üçlü başına uzman saniyesi**, düzenleme oranı, insan kararları arası uyum.
- **Kalibrasyon:** LLM güven skorunun ECE değeri ve reliability diagram. Yönlendirme politikası bunun üzerine kuruluyor.
- **Maliyet:** Token, $, süre (ilk kurulum ve artımlı güncelleme ayrı).
- **Tüketim kalitesi:** Katman üzerinden cevaplanan soru setinde doğruluk. Aynı soru seti ham kaynak + RAG ile de cevaplanıp karşılaştırılır.

## 3. İstatistik

- Analiz birimi **hadis**. Aynı hadis tüm koşullarda işlendiği için tasarım eşleştirilmiş (paired).
- Birincil analiz: Karışık etkili modeller. Örnek: `correct ~ condition * model + (1|hadith)` (lojistik, üçlü düzeyinde) veya hadis düzeyinde F1 üzerinden lineer karışık model. Güven aralıkları hadis düzeyinde cluster bootstrap ile. İkili koşul karşılaştırmaları paired permutation ile, Holm düzeltmesiyle.
- İki yönlü ANOVA (formda taahhüt edildi) yardımcı analiz olarak raporlanabilir. Birim hadis olmalı, 30 agrega değil.
- **Tekrarlar:** `temperature=0` ile tekrarlar varyans üretmez. Ya T>0 ile (ör. 0.7) örnekleme varyansı ölçülür ya da tekrar yerine prompt paraphrase varyansı raporlanır. Bu karar gerekçelendirilmeli.
- **H3:** Model düzeyinde n=5 ile korelasyon yerine, aday düzeyinde "insan reddi ~ halüsinasyon etiketi" ilişkisi test edilmeli. Ya da HITL'in halüsinasyon tespitindeki duyarlılık ve özgüllüğü raporlanmalı.
- **Güç analizi:** Beklenen ΔPrecision ve hadis başına üçlü sayısıyla gerekli n simülasyonla tahmin edilmeli. 500 hadisin yeterli olup olmadığı gösterilmeli.

## 4. Altın standart protokolü

- İki katman: (a) span + zincir sırası (metinden doğrulanabilir, iki öğrenci kodlayıcı), (b) otorite ID (uzman).
- Uyum: Katman (a) için kodlayıcılar arası F1 (IE literatüründeki standart), katman (b) için sabit aday kümesinde Cohen's/Fleiss' κ. Formdaki κ ≥ 0,75 hedefi (b) katmanına bağlanabilir.
- **Kör protokol:** Altın standardı üreten kodlayıcılar sistem çıktısını görmemeli. HITL koşulunda karar veren kişi, o hadisin altın standardını yapan kişiden farklı olmalı.
- Etiketleme kılavuzu sürümlenmeli. Mutabakat oturumlarının kararları da bir karar defterine yazılmalı (`12`, dogfooding).

## 5. Genelleme deneyi (asıl meta-soru için)

Aynı çekirdek mimari iki farklı alanda:
- **Kod (vaka B):** Açık kaynak, orta ölçekli bir repo seçilir (yayınlanabilir olması için şirket kodu kullanılmaz). Git geçmişinden zaman dilimleri alınır. Koşullar: (i) wiki yok, ajan grep/read kullanır, (ii) LLM-üretimli wiki (DeepWiki tarzı), (iii) anchor'lı + linter'lı wiki (`07` kuralları), (iv) karar defteri + türetilmiş görünüm (`12`). Ölçümler: ajan soru-cevap doğruluğu (niyet/karar soruları ile yapısal sorular ayrı), zaman içindeki drift, bakım maliyeti.
- **Kur'an/meal (vaka C):** Provenance doğruluğu, kaynak onarımı sonrası türetilmiş artefaktların (embedding) doğru invalidation'ı.
- Hadis (vaka A) birincil ve derin deney. B ve C "transfer" kanıtı. Bitirme kapsamı için B hafif tutulabilir.

## 6. Tehditler
Veri sızıntısı (LLM'ler Kütüb-i Sitte isnadlarını ezberlemiş olabilir; ezber ile çıkarım ayrılmalı, ör. metinden isnad silinerek kontrol), dil seçimi (Arapça/Türkçe), otorite listesinin hataları, uzman sayısının 1 olması, yönlendirme politikasının sonuçları belirlemesi.
