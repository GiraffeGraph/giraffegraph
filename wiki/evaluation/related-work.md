# Emsal çalışmalar: başkaları çıkarım doğruluğunu nasıl ölçmüş?

## Purpose

Hadis isnadı ve metinden bilgi grafı çıkaran çalışmaların doğruluğu hangi referansa karşı, hangi
metrikle ölçtüğünü ve nerede eksik kaldığını tek yerde tutmak. `correctness-measurement.md` içindeki
ölçüm tasarımının dayanağı, hazır referans veri adayları ve projenin konumlanacağı boşluk buradan okunur.

## Scope

- In: L1 (çıkarım) ve L2 (kimlik) için ölçüm emsalleri, sayıları, zayıf yanları, hazır veri adayları,
  projeye çıkarım
- Out: L4 cevap kalitesi literatürü (`literature-map.md`), metrik formülleri
  (`wiki/sources/claude-science-results/03_revize_deney_protokolu.md`)

Tarama 2026-10-08'de web araması ve birincil kaynak okumasıyla yapıldı. Sistematik tarama değildir;
"bulunmadı" ifadesi "yoktur" anlamına gelmez.

## BLUF

1. İsnad ayrıştırma için etiketli, sabit bölmeli bir veri kümesi ve üzerinde ölçülmüş bir baz çizgi
   vardır: İfta Sünnet platformundan türetilmiş 223.478 hadis; ince ayarlı modeller ilişki düzeyinde
   F1 0,95'e ulaşıyor (Oumer 2025). LLM tabanlı çıkarımı bu veride ölçen bir çalışma bulunmadı.
2. Ravi kimliği için de etiketli gerçek veri vardır: altı kitaptan 27.056 sened, her ravi kimlik
   numaralı (AR-Sanad 280K test kümesi). En iyi model senedlerin %60,6'sında en az bir raviyi yanlış
   tanıyor. Sonraki iki çalışma %94,6 (yapay doğrulama senedleri) ve %97,8 (yalnız yapay
   senedlerden oluşan v2 kümesi) accuracy bildiriyor; özetlerinde gerçek senedlerde ölçülmüş bir değer yok.
3. Pilotun referansı olan Sanadset etiketleri düzenli ifadelerle üretilmiştir; veri makalesi doğruluk
   ölçümü raporlamaz. Gümüş standart statüsü kesindir ve daha güçlü bir referans adayı mevcuttur.
4. "Katı mı gevşek mi eşleşme" bu işin bilinen sorunudur: aynı çıktı katı eşleşmede F1 0,254, kısmi
   eşleşmede 0,835 alıyor; uzmanlar bile bitiş noktasında %53 tam anlaşıyor (Muther ve Smith 2020).
5. "Çıktı metinde geçiyor mu" kontrolü literatürde ayrı bir metrik ailesidir. Text2KGBench'te özne
   hallucination oranı 0,17 iken precision 0,38: metinde geçme, doğru olmanın kanıtı değildir.
6. LLM ile hadis işleyen çalışmalar uzman puanı (0–10), 20 örneklik kontrol ya da tek kişinin 100
   kayıtlık karşılaştırması kullanıyor; P / R ve etiketleyiciler arası uyum raporlamıyor.
7. Hadis korpusundan bilgi grafı üretimi yapılmıştır (SemanticHadith 2.0.1: 34.458 hadis, 303.869
   varlık) ve zincir halkası ontolojide ayrı sınıftır. Bu çalışmada LLM, olgu başına insan kararı ve
   grounding kontrolü yoktur; belirsiz adların uzmana sunulması gelecek iş olarak bırakılmıştır.

## Çalışmalar

Okuma derinliği: **T** = tam metin doğrudan okundu (2026-10-08); **R** = tam metin kapalı, sonuçlar
yazarın açık deposundan okundu; **Ö** = tam metin kapalı, yalnız yayıncı sayfasındaki özet okundu
(2026-10-15).

### İsnad ve ravi çıkarımı (L1)

| Çalışma | Referansı kim üretti | Ölçüm düzeyi ve kriter | Sayılar | Not | Okuma |
|---|---|---|---|---|---|
| Oumer 2025, yüksek lisans tezi (Malta) + model deposu | İfta Sünnet platformunun işaretlemesinden türetilmiş ravi span'leri ve aktarım ilişkileri; 276.347 hadisten filtrelenmiş 223.478 | Ravi kümesi P / R / F1; ilişki ikilileri ve zincir numaralı üçlüler için birebir eşleşme. Test: 33.523 hadis | CAMeLBERT-CA: ravi F1 0,98, ikili F1 0,95. AraT5: ravi 0,97, ikili 0,95, zincir numaralı üçlü 0,93. AraBART: üçlü F1 0,48 | Bölme mainId üzerinden %70/15/15; kitaplar arası ayrım belirtilmemiş. "Uyuşmazlık içermeyen" alt küme seçilmiş. Paralel zincirler zincir numarasıyla ayrılıyor | R |
| Muther ve Smith 2020, *Tracing Traditions* (WANLP) | İslam tarihi uzmanları; 50 metin, 907.110 token, 3.071 isnad. Model önerisi üzerinden düzeltmeli etiketleme | Span düzeyi katı ve kısmi P / R / F1. Uyum: 5 etiketleyici, 2.000 satır | Krippendorff α 0,84; ikili Cohen κ 0,71–0,96. Başlangıç noktasında tam uyum %70, bitişte %53. CRF katı F1 0,254, kısmi F1 0,835. Başlangıç etiketi: en iyi model F1 0,476 | Uzun, noktalamasız metinlerde isnad aralığı bulma; ravi adı çıkarımı değil | T |
| Altammami vd. 2019 (ACL Arabic Corpus Linguistics) | Yazarlar; altı kitaptan 40'ar, 240 hadis, düzensiz örüntüler dahil | Hadis düzeyi doğruluk: sened-metin ayrım noktası doğru mu | Bi-gram 222 / 240 = %92,5; tri-gram %48 | Hata türleri: paralel isnad, isnad içinde metin kelimeleri, metin içinde kişi adları. Ayrım noktası uzman olmayan insan için de belirsiz | T |
| Mghari vd. 2022, *Sanadset 650K* (Data in Brief) | Kural: web'den kazınan metin düzenli ifade ve metin eşleme ile etiketlenmiş | Doğruluk ölçümü ve insan kontrolü raporlanmıyor | 650.986 kayıt, 926 kitap; 159.558 kayıtta sened yok; 56.053 kayıtta tek ravi | Veri makalesi yaklaşık 1.600 kelime; yöntem ayrıntısı yok | T |
| GTAF 2025, blog | Belirtilmemiş; "elle değerlendirildi" | Rivayet başına yüzde puan; kısmi puan kuralı yok | Muvatta'dan 20 rivayet; 15'i hatasız; ortalama %95 | Hata türleri: niteleyicinin (mevlâ) ayrı ravi sayılması, paralel raviler, isimsiz raviler. Yazarları Haque ve Islam derlemesinin yazarlarıyla aynı kurumdan | T |
| Asgari-Bidhendi vd. 2025, *Rezwan* (arXiv) | 6 alan uzmanı, 1.213 rastgele rivayet | Boyut başına 0–10 puan. Uyum istatistiği yok; belirsiz durumlar toplu kararla çözülmüş | Sened-metin ayırma 9,30 (özet 9,33). Elle hazırlanmış Noor korpusu aynı ölçekte 9,63 (67 rivayet) | Hata oranı %60'ı aşan %5,85 rivayet ortalamadan çıkarılmış; örneğin %15,25'i hadis olmayan metin. Makale içinde çelişen sayılar var | T |

### Ravi kimliği (L2)

| Çalışma | Referansı kim üretti | Ölçüm düzeyi ve kriter | Sayılar | Not | Okuma |
|---|---|---|---|---|---|
| Mahmoud vd. 2022, *AR-Sanad 280K* (Information) | Hâdimü'l-Harameyn sünnet sitesi; makaleye göre ravi tanımlama işini 30 kişilik uzman grubu yürütmüş. Eğitim: 279.625 yapay sened. Test: altı kitaptan 27.056 gerçek sened, 6.378 ravi | Mention başına sınıflandırma (18.298 sınıf): micro / macro F1; sened hata oranı (SER) = en az bir ravisi yanlış sened yüzdesi; top-k | Yapay doğrulama: micro F1 92,9, SER 30,2. Gerçek test: micro F1 83,5, macro 78,8, SER 60,6. Top-3 %95,3, top-5 %97,1. Kitap bazında SER %48,7 (Tirmizî) – %70,5 (Nesâî) | Doğrulama kümesinde yaygın adların (Muhammed, Abdullah vb.) 3.669 örneğinin %26'sı doğru; "babası / dedesi" biçimlerinin %71'i doğru. Yanlış tahminlerin %12,9'u 0,90 üstü güvenle verilmiş | T |
| Wirahman 2026 (arXiv) | Yok | Ölçülmemiş; eşikler gözle seçilmiş | Sanadset'in 185.216 ad varyantından 94.628'i (%51,1) bağlandı; 88.343'ü (%47,7) aday bulamadı | Yazar etiketli referans küme bulunmadığını, 1.000–2.000 uzman onaylı bağlantının gelecek iş olduğunu yazıyor. Grafın en yüksek dereceli iki düğümü "babası" (7.612) ve "babam" (5.550). Metin içinde çelişen oranlar var | T |
| Mahmoud, Nabil, Saif, Torki 2024 (Neural Computing and Applications) | AR-Sanad 280K'nın yapay senedleri | Doğrulama kümesinde accuracy | Özete göre AR-Sanad 280K doğrulama kümesinde %94,6. Yöntem: sened graf olarak (ravi düğüm, aktarım kenar) sorgu gömmesine çevriliyor, en yakın k ravi getiriliyor, AraBERT yeniden sıralıyor. k değeri özette yok | v2, yapay senedlerin güncellenmiş hâli. Depodaki `v2/` klasöründe yalnız eğitim ve doğrulama dosyaları var (223.564 + 55.764 sened); ravi etiket dosyaları v1 ile bayt bayt aynı, sened metin dosyaları farklı (eğitim dosyası v2'de 44,2 MB, v1'de 53,0 MB). Gerçek sened test kümesi v2'de yok (depo okundu ve dosyalar karşılaştırıldı, 2026-10-15) | Ö |
| Mosa 2025, *Digital Scholarship in the Humanities* 40(4) | AR-Sanad 280K-v2 | Accuracy; başka metrik özette yok | Özete göre %97,8. Yöntem: ravi ağının bilgi grafı aday kimlikleri üretiyor; hibrit skor ağdaki genel önemi ve bağlamsal anlam uyumunu birleştirip sıralıyor | Özet hangi bölmede ölçüldüğünü söylemiyor. v2 yalnız yapay senedlerden oluştuğu için değer büyük olasılıkla yapay senedlerdedir (çıkarımımız, makale okunmadı). v1'de yapay doğrulamadan gerçek teste geçince micro F1 92,9'dan 83,5'e indi | Ö |

### Hadis bilgi grafı üretimi ve LLM ile ricâl verisi yapılandırma

| Çalışma | Ne yapıyor | Doğruluğu nasıl ölçmüş | Sayılar | Projeye göre farkı | Okuma |
|---|---|---|---|---|---|
| Kamran, Butt, Basharat 2026, *SemanticHadith 2.0.1* (Semantic Web 17(2)) | Altı kitabın 34.458 hadisinden ontoloji güdümlü bilgi grafı. Metin içi varlıklar (kişi, peygamber, yer, kabile, konu vb.) özel eğitilmiş NER ile çıkarılıyor (spaCy + CAMeLBERT-CA, değiştirilmiş CANERCorpus: 14 sınıf, 57.763 etiketli varlık, %80/20 bölme). Çıkan varlık bir isim sözlüğüyle ontoloji örneğine eşleniyor; eşleşmeyen atılıyor. Ontolojide `NarratorChain`, `NarratorChainSegment`, `RootNarratorChainSegment` sınıfları var | NER için sınıf bazında P / R / F1. Graf için: üç alan uzmanı, her koleksiyondan rastgele 100 örnek, "uyuşmazlık raporlanmadı". Uyum istatistiği yok | NER micro F1 %97, macro %85, Person F1 %98; Crime recall %41. Graf: 303.869 varlık, 6.822 kişi, 47.496 `isSimilar` bağı. Kosinüs benzerliğiyle benzer hadis bulma başarısız bulunmuş, yalnız uzmanın verdiği çiftler grafa alınmış | LLM yok. Olgu başına insan kararı yok; uzman denetimi örneklemle. Kaynak alıntısı / grounding kontrolü yok. Aynı adı taşıyan kişiler (örnek: Zeyneb) elle incelemeye işaretleniyor ya da dışarıda bırakılıyor; belirsiz adların uzmana aday listesiyle sunulduğu doğrulama çerçevesi gelecek iş olarak yazılmış | T |
| Çinici 2026 (Mevzu 16) | Zehebî'nin *Siyeru a'lâmi'n-nübelâ* 23. cildinden RAG + sistem yönergesiyle 271 âlim için 21 değişkenli ricâl veri kümesi. Gemini 2.5 Flash, sıcaklık 0,1, `multilingual-e5-large` gömme | İlk 100 kayıt yazar tarafından eserin aslıyla karşılaştırılmış | Sayı verilmemiş: "doğruluk oranının yüksek bir düzeyde olduğu tespit edilmiştir". Maliyet yaklaşık 1,25 dolar, yaklaşık 1 saat | İsnad zinciri değil biyografi çıkarımı. Tek değerlendirici, P / R yok, uyum yok. Halüsinasyonun azaldığı iddiası boş alanların kaynakta da boş olmasına dayanıyor; ölçülmüş bir oran değil. Graf ve onay akışı yok | T |

### Genel KG çıkarımı ve doğruluk tahmini

| Çalışma | Ne ölçüyor | Sayılar | Not | Okuma |
|---|---|---|---|---|
| Mihindukulasooriya vd. 2023, *Text2KGBench* (ISWC) | Üç aile: (i) referans üçlülere karşı P / R / F1; (ii) ontoloji uyumu; (iii) hallucination: özne / nesne kök indirgemeden sonra cümlede ya da ontolojide substring mi | Wikidata-TekGen, Vicuna-13B: P 0,38 / R 0,34 / F1 0,35; ontoloji uyumu 0,83; özne hallucination 0,17. Görülmemiş cümlelerde F1 0,32 (Alpaca: 0,27 → 0,22) | Ezber kontrolü için uydurma olgulu 174 cümle. Referans eksik olabildiği için recall yalnız referanstaki ilişkiler üzerinden hesaplanıyor | T |
| Gao vd. 2019, *Efficient KG Accuracy Evaluation* (PVLDB) | Örneklemle KG doğruluğu; etiketleme maliyeti = varlık sayısı · c1 + üçlü sayısı · c2 | MOVIE: rastgele 174 üçlü / 174 varlık 3,53 saat; iki aşamalı küme örneklemesi 178 üçlü / 24 varlık 1,4 saat; hata payı her ikisinde yaklaşık %5 | Aynı varlığın üçlülerini birlikte denetlemek ucuzdur; tahmin yansızdır ve güven aralığı verir | T (§1–§7.1) |

### Derlemeler ve dolaylı ilgili

| Çalışma | Katkı | Okuma |
|---|---|---|
| Haque ve Islam 2026 (arXiv), eleştirel derleme | 32 kaydı altı boyutta değerlendiriyor: korpus gerçekçiliği, ölçüm düzeni, aktarım, tekrarlanabilirlik, uzman katkısı, bilimsel kullanım. Değerlendirme tablosundaki 8 satırdan uzman katkısı yalnız Rezwan'da tam, IslamicEval'de kısmi. Bulgular: altı kitaba dar benchmark kültürü, yapaydan gerçeğe aktarım boşluğu, karşılaştırılamayan metrikler, seyrek uzman doğrulaması. Ezber / sızıntı konusunu ele almıyor | T |
| Mhamedi vd. 2026 (TELKOMNIKA), derleme | 57 çalışma. Ravi çıkarımı tablosunda raporlanan değerler F1 %33 – %99,63 arasında; test kümeleri 102–200 hadis; metrikler karışık (accuracy, precision, F1). Yazarları Sanadset ekibi | T |
| Raja 2026 (arXiv), isnad benzetmeli provenance çerçevesi | Hadis verisi içermez. Yöntem notları: referans küme yokken yalnız precision raporlanıyor, recall iddia edilmiyor; modelin ön bilgisi ile metinden çıkarım ayrıştırılamadığı açıkça yazılıyor; seçici sunumda hata oranı eşit kapsama düzeyinde karşılaştırılıyor | T (§6–§8) |

### Okunmamış adaylar

Okunan makalelerin kaynakçalarından; künyeleri birincil kaynaktan çekilmedi.

- Muther ve Smith 2020, *Digital Scholarship in the Humanities* — aynı işin dergi sürümü
- Multi-IsnadSet 2024 (*Data in Brief*) — Sahîh-i Müslim için 2.092 ravili yönlü graf
- Kurt 2025, "İsnad Tenkidinde Yapay Zekanın Kullanılabilirliği" (İlahiyat Yayınları, ed. Ulupınar)
- Mubarak vd. 2025, IslamicEval — İslami içerikte LLM hallucination ortak görevi (L4)
- Alnefaie vd. 2023, HAQA / QUQA — hadis ve Kur'an soru-cevap korpusu (L4 soru kümesi adayı)
- Alan, Karaarslan, Aydın 2025, MufassirQAS — Türkçe İslami RAG sohbet sistemi (L4)

## Hazır referans veri adayları

Aşağıdaki verilerin tümü 2026-10-12'de indirildi; indirme komutları, dosya boyutları, sha256 değerleri ve
lisans beyanlarının kaynağı `data/README.md` içindedir. İfta ailesinden yalnız altı kitap ve ravi kataloğu
indirildi. Veri yalnız değerlendirme için kullanılır ve yeniden dağıtılmaz.

| Veri | İçerik | Etiketin kaynağı | Lisans beyanı, kaynağın yazdığı hâliyle (erişim 2026-10-12) |
|---|---|---|---|
| Ifta Sunnah Hadith & Narrators (Kaggle `jehadoumer/ifta-hadith-corpus-original`) | 33 kitap, 276.347 hadis, yapılandırılmış isnad zincirleri, 20.957 ravi profili | İfta Sünnet platformu | Kaggle lisans alanı "CC BY-SA 4.0". README: "Attribute the program and institution, and follow the platform's terms, notices, and licensing for your use case." |
| Ifta Hadith with Narrators Entities and Relations | Aynı hadisler; BIO etiketli ravi span'leri, ilişki ikilileri / üçlüleri; 223.478 hadislik sabit bölme (156.434 / 33.521 / 33.523) | Platform işaretlemesinden türetme | Kaggle lisans alanı "Unknown"; README'de lisans beyanı yok |
| Ifta Hadith Isnad Linked Graph Data | 257.840 hadis; her zincir adımı ravi kimlik numarasına bağlı | Platform; kimlik numaralarını derleyici atamış | Kaggle lisans alanı "Attribution-NonCommercial-ShareAlike 3.0 IGO (CC BY-NC-SA 3.0 IGO)" |
| AR-Sanad 280K (GitHub `somaia02/Narrator-Disambiguation`) | 27.056 gerçek sened + ravi kimlikleri; 18.298 ravinin adlandırma biçimleri, İbn Hacer derecesi, tarihleri | Hâdimü'l-Harameyn sitesi | Depoda LICENSE dosyası yok, README'de lisans beyanı yok. Makalenin Crossref kaydındaki lisans CC BY 4.0'dır; deponun bunu veri dosyalarına yayıp yaymadığı yazılı değil |
| Sanadset 650K (Hugging Face aynası `freococo/650k_sanadset`) | 650.986 kayıt, `<NAR>` etiketleri | Düzenli ifade | İki beyan çelişiyor: Hugging Face kartı `license: cc0-1.0`; özgün Mendeley Data kaydı (DOI 10.17632/5xth87zwb5.5) "CC BY 4.0". Makale CC BY |

GitHub `JehadOumer/Ifta-Sunnah-Hadith-and-Narrators-Dataset` deposunda LICENSE dosyası yoktur. İfta Sünnet
platformunun kendi kullanım koşulları alınmadı; kayıtlı değil (`data/README.md`, "Licence and terms").

Entities and Relations sürümünün altı kitap dosyaları 27.599 kayıt içerir; özgün korpusta aynı altı kitap
34.995 kayıttır. Sürümün manifesti özgün sayıları listeler, dosyalar ise yalnız sabit bölmeye giren
satırları taşır (`data/README.md`, "Observed in the downloaded files"; 2026-10-12'de indirilen dosyalarda
sayıldı). Graph sürümünde aynı altı kitap 34.241 kayıttır.

Bu verilerden kurulan değerlendirme kümeleri (`data/eval/`): 300 hadislik İfta etiketli test kümesi, aynı
hadisler için Sanadset etiketleri, AR-Sanad kimlik kümesi ve 50 pilot hadis. Üzerlerindeki ölçümler:
`wiki/evaluation/engine-experiments.md`.

### Kayıt biçimi (depolardan okundu, 2026-10-09)

| Veri | Bir kayıtta ne var | Okunan örnek | Hangi katmanı sınar |
|---|---|---|---|
| İfta, kimlik bağlı kayıt | `names`: [metindeki ad, harekeli ad, ravi numarası]; `chain_of_narrators`: ravi numaralarının sıralı listesi (zincir başına bir liste); `takhreej`: aynı hadisin diğer kitaplardaki kayıtları | `mainId` 237072, Musannef İbn Ebî Şeybe hadis 1: zincir 822 → 3479 → 6709 → 3889 (`json-to-cypher-scripts/_smoke_03_hadith_nodes.cypher`) | L1 ve L2 |
| İfta, ravi profili | `narrator_id`, ad, künye, nisbe, tabaka, İbn Hacer ve Zehebî hükmü, yer ve tarih alanları | `narrator_id` 3, Âdem b. Ebî İyâs (`_smoke_02_narrators.cypher`) | L2 otorite listesi |
| İfta, ilişki etiketi | Satır başına `<head>` alan, `<tail>` aktaran, zincir-duyarlı sürümde `<chain_number>` | Model deposu README'sindeki iki kollu örnek | L1 |
| AR-Sanad test | `sanads.test`: satır başına bir zincir, ravi adları `[فاصل]` ile ayrılmış; `labels.test`: aynı satırda virgülle ayrılmış ravi numaraları; numara `Narrators data.csv` içindeki `id` sütunudur | İlk satır: 6 ad, etiket `82,192,199,399,18,165`; altı numara ravi tablosunda aranıp eşleştirildi | Yalnız L2 |

AR-Sanad test kümesi ham hadis metni içermez; ravi adları ayrılmış gelir. Bu veriyle metinden çıkarım
(L1) ölçülmez. İfta kaydındaki `names` alanında sayfa işareti ad içine karışabilir (aynı kayıtta
`أنس بن [1/220] مالك`); eşleştirmeden önce temizlik gerekir.

## Projeye çıkarımlar

Bu tablo öneridir; ekip ve danışman kararı değildir.

| Emsalin gösterdiği | Projedeki karşılığı |
|---|---|
| Platform etiketli, ravi kimlikli veri mevcut; AR-Sanad test kümesi altı kitabı kapsıyor (İfta'nın 33 kitaplık listesi okunmadı) | Yapıldı (2026-10-12): 300 hadislik İfta etiketli test kümesi kuruldu, dört koşul ona karşı puanlandı; Sanadset etiketlerinin İfta etiketleriyle uyumu 253 hadiste ölçüldü (`wiki/evaluation/engine-experiments.md`). 50 pilot hadisin 43'ü bir İfta kaydına bağlandı (`data/README.md`, "eval/pilot50") |
| İnce ayarlı küçük modeller ilişki düzeyinde F1 0,95 veriyor | Projenin iddiası ham çıkarım doğruluğu olamaz. Baz çizgi olarak bu modeller koşulur; katkı insan onayı, kaynak izi, şema sapmasının önlenmesi ve eğitim verisi gerektirmeme üzerinden tanımlanır |
| Katı ve kısmi eşleşme çok farklı sayı verir (0,254 / 0,835); pilotta 0,628 / 0,879 | İki kriter de raporlanır; kriter protokolde sabitlenir |
| Uzmanlar bitiş noktasında %53 tam anlaşıyor | Etiketleme kılavuzu sınır kurallarını yazar (fiil, niteleyici, mevlâ); uyum sayısı sonuçla birlikte verilir |
| Mention F1 83,5 iken senedlerin %60,6'sı hatalı | Mention metriğiyle birlikte "tam doğru zincir oranı" raporlanır |
| Doğru ravi ilk 3 adayın içinde %95,3 | HITL panelinde uzmana tek tahmin yerine sıralı aday listesi sunulur; ölçüt top-k doğruluğudur |
| Ravi kimliğinde graf sorgusu ve bilgi grafı tabanlı yöntemler AR-Sanad'ın yapay senedli kümelerinde %94,6 ve %97,8 accuracy bildiriyor | Projenin kimlik katkısı otomatik tanıma doğruluğu olamaz. Fark, kimlik kararının bir kez saklanıp yeniden kullanılmasında ve kapsamının çelişkiden türetilmesinde aranır; ölçüm gerçek senedlerde (AR-Sanad test) yapılır |
| Yaygın tek adlarda doğruluk %26 | L2 ölçümü ad sıklığına göre tabakalı raporlanır; yaygın adlar insana yönlendirilir |
| Kitaplar arasında SER %48,7 – %70,5 | Sonuçlar koleksiyon bazında verilir; test kümesi eğitimde görülmeyen bir kitabı içerir |
| "Metinde geçiyor" olanların çoğu yanlış olabilir (hallucination 0,17, precision 0,38) | Üç test ayrımı (kaynakta var mı / referansla eşleşiyor mu / doğru kişi mi) korunur |
| Görülmemiş, uydurma cümlelerle ezber testi | Ezber kontrolü (T-mask, T-perturb) için emsal; ravi adları değiştirilmiş isnadlarla ölçüm |
| Paralel zincirler zincir numarası olmadan geçersiz yollar üretir | `wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md` C5 (hadis kapsamlı kenar anahtarı) için bağımsız gerekçe |
| "Babası" gibi ifadeler grafın en büyük düğümü oluyor | İsimsiz ravi ifadeleri ayrı sınıf olarak etiketlenir; birleştirme anahtarına girmez |
| Başarısız örnekleri ortalamadan çıkarmak puanı yükseltir (Rezwan) | Hiçbir hadis ortalamadan çıkarılmaz; kesilen ya da boş çıktı sıfır puan alır |
| Uzman puanı (0–10) karşılaştırılamaz | Birincil ölçü sayım tabanlıdır (TP / FP / FN) |
| Zincir halkası SemanticHadith ontolojisinde ayrı sınıf (`NarratorChainSegment`) | Aktarım olayının ayrı kayıt olması özgün katkı olarak sunulmaz; şema bu ontolojiyle hizalanır ve fark onay kaydı ile kaynak alıntısında aranır |
| SemanticHadith belirsiz adları dışarıda bırakıyor, uzman doğrulama çerçevesini gelecek iş sayıyor | Projenin inceleme kuyruğu bu boşluğa oturur; L2 ölçümünde belirsiz adların oranı ayrıca raporlanır |
| "Yönergeyle halüsinasyon en aza indi" iddiası sayısız (Çinici) | Aynı iddia sayımla sınanır: kaynakta olmayan değer, alıntıda olmayan değer ve boş bırakılan alan ayrı sayılır |
| Aynı varlığın üçlülerini birlikte denetlemek 2,5 kat ucuz (3,53 → 1,4 saat) | Korpus düzeyi doğruluk tahmini hadis bazlı küme örneklemesiyle yapılır; güven aralığı verilir |
| Seçici sunumda hata, eşit kapsama düzeyinde karşılaştırılır | HITL yönlendirme sinyalleri risk–kapsama eğrisiyle karşılaştırılır |

## Rules

- MUST: İfta, AR-Sanad ve Sanadset verileri yalnız değerlendirme için kullanılır ve yeniden dağıtılmaz.
  Yapılan budur: veri `data/` altında, sürüm kontrolü dışında durur ve lisans beyanları kaynakların
  yazdığı hâliyle kayıtlıdır (`data/README.md`). Beyanlar arasında çelişen ve eksik olanlar vardır;
  kaynaklardan alınmış yazılı izin ve bu kullanım için danışman onayı kayıtlı değil.
- MUST: verinin ya da ondan türetilen bir dosyanın yeniden dağıtımı (herkese açık depoya commit, yayın
  eki) lisans ve platform koşulları yazılı olarak teyit edilmeden yapılmaz; teyit `wiki/decisions/`
  altında kayda geçer. `giraffegraph-core/evaluation/results/` hadis metni ve alıntı taşıyan dosyalar
  içerir (`2026-10-12-sixbooks300/subset36.json`, koşu klasörlerindeki `candidates.jsonl`) ve depoda
  yok sayılan dosyalar arasında değildir.
- MUST: İfta etiketlerine karşı ölçülen değer raporlanırken etiketlerin platform işaretlemesi olduğu,
  üçüncü bir kişi tarafından yeniden yapılandırıldığı ve insan altın standardı olmadığı belirtilir.
- MUST: Sanadset `<NAR>` etiketlerine karşı ölçülen değer raporlanırken etiketlerin kural tabanlı
  üretildiği ve doğrulanmadığı belirtilir.
- MUST: Oumer 2025 sayılarına atıf, tez tam metni elde edilene kadar "yazarın model deposu" kaynağıyla
  yapılır.
- SHOULD: yeni bir emsal eklenirken dört soru cevaplanır: referansı kim üretti, eşleşme kriteri ne,
  hangi düzeyde ölçüldü (token / mention / zincir / kimlik), uyum raporlandı mı.

## Source anchors

- `wiki/literature/extraction_eval_precedents.bib` — Muther 2020, Altammami 2019, Oumer 2025, Mahmoud 2022,
  Mahmoud 2024, Mosa 2025, Text2KGBench 2023, Gao 2019, Mhamedi 2026, Kamran 2026, Çinici 2026 künyeleri
- `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` — `mghari2022sanadset`, `wirahman2026linking`,
  `asgari2025rezwan`, `haque2026hadith`, `raja2026grading` künyeleri
- https://github.com/JehadOumer/Automatic-Hadith-Isnad-Parsing-Models — Oumer sonuç tabloları, bölme sayıları
- https://github.com/JehadOumer/Ifta-Sunnah-Hadith-and-Narrators-Dataset — veri ailesi, bölme dosyaları
- https://github.com/somaia02/Narrator-Disambiguation — AR-Sanad verisi ve ravi tablosu; `v2/` klasörü ve README
- https://doi.org/10.1007/s00521-024-10194-2 — Mahmoud vd. 2024, yalnız özet
- https://doi.org/10.1093/llc/fqaf088 — Mosa 2025, yalnız özet
- https://aclanthology.org/2020.wanlp-1.12/ — Muther ve Smith, §4, Tablo 2, Tablo 3
- https://aclanthology.org/W19-5605/ — Altammami vd., §3–§5, Tablo 1
- https://doi.org/10.3390/info13020055 — AR-Sanad, Tablo 6–11, §5
- https://arxiv.org/abs/2308.02357 — Text2KGBench, §3–§5, Tablo 2
- https://arxiv.org/abs/1907.09657 — Gao vd., §3, Tablo 4
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9440281/ — Sanadset 650K, §2.1
- https://arxiv.org/abs/2607.05424 — Wirahman, §4.3, §5.3, §6.2
- https://arxiv.org/abs/2510.03781 — Rezwan, §4–§5
- https://arxiv.org/abs/2608.20364 — Haque ve Islam, Tablo 2, Tablo 4
- https://doi.org/10.12928/telkomnika.v24i3.27447 — Mhamedi vd., Tablo 4
- https://arxiv.org/abs/2607.24117 — Raja, §6, §8
- https://gtaf.org/blog/evaluating-the-performance-of-our-narrator-chain-extraction-system-for-hadith-analysis/
- https://doi.org/10.1177/22104968261431425 — Kamran, Butt, Basharat, §3.2, §3.6, §4.2–§4.4, §6, Tablo 2, Tablo 5
- https://doi.org/10.56720/msbd.2026.s16.326 — Çinici, §3.1–§3.4, dipnot 28
- `wiki/sources/claude-science-results/pilot_results.csv` — pilotun katı / gevşek F1 değerleri
- `data/README.md` — indirilen dış veri: komutlar, lisans beyanları, etiketlerin kaynağı, kayıt sayıları
- `data/raw_manifest.json` — indirilen her dosyanın boyutu ve sha256 değeri

## Verification checklist

- [ ] Tablodaki her sayı kaynağının belirtilen tablo ya da bölümünde bulunuyor
- [ ] Lisans sütunu `data/README.md` içindeki beyanlarla aynı; kaynak yeniden okunduysa erişim tarihi güncellendi
- [ ] `git -C giraffegraph-core status --short evaluation/results` çıktısındaki dosyalar herkese açık bir
      depoya gitmeden önce lisans teyidi `wiki/decisions/` altına yazıldı
- [ ] Okunan bir aday "Okunmamış adaylar" listesinden ilgili tabloya taşındı ve künyesi bib dosyasına eklendi

## Related docs

- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/engine-experiments.md`
- `wiki/evaluation/literature-map.md`
- `wiki/sources/claude-science-context/10_related_work_map.md`

## Last updated

2026-10-15
