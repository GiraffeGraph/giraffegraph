# 7 Değerlendirme

Bu bölümde neyi, hangi veriler üzerinde, hangi referansa karşı ve hangi eşleştirme kuralıyla ölçtüğümüzü raporluyoruz. Ölçülen sayılar, Bölüm 6'da açıklanan betiklerin ürettiği `giraffegraph-core/evaluation/results/` altındaki dosyalardan; veri kümelerinin istatistikleri ise veri manifestosundan gelir [@internal-data-manifest]. Bütün koşuları 12 Ekim 2026'da motorun bellek içi arka ucunda gerçekleştirdik. PostgreSQL ve Neo4j arka ucu testlerle ayrıca doğrulandı (Bölüm 6.7); bu koşularda kullanılmadı.

## 7.1 Sorular

Değerlendirme beş soruyu yanıtlar.

1. Her çıkarım koşulu, bir hadisin ravi geçişlerini ne ölçüde elde ediyor?
2. Model ile graf arasına yerleştirilen doğrulama kontrolleri neyi yakalıyor ve bunların doğru çıktı kaybı açısından maliyeti nedir?
3. Modelin bildirdiği güven skoru, bir kişinin neyi incelemesi gerektiğine karar vermek için kullanılabilir bir sinyal midir?
4. Her koşul ne kadar inceleme işi ve parasal maliyet doğuruyor?
5. Yazılı bir ad, bir raviyi ne ölçüde tanımlıyor?

Yanıtlayamadığımız soruları Bölüm 7.11'de listeliyoruz.

## 7.2 Veriler ve referans etiketleri

İki hadis kümesi kullanıyoruz (Tablo 7.1). İkisinin de iki bağımsız etiketleyiciyle oluşturulmuş bir insan altın standardı yoktur; hiçbir kaynak da bu etiketleri böyle tanımlamaz [@internal-data-manifest].

**Tablo 7.1** Değerlendirme kümeleri.

| Küme | Hadis sayısı | Referans geçişleri | Metin ve etiketlerin kaynağı | İşlev |
|---|---|---|---|---|
| Pilot | 50, beş kitap, Bukhari yok | 327 | Sanadset 650K [@mghari2022sanadset]; etiketler düzenli ifadelerle üretilmiş | Geliştirme kümesi. Kural tabanlı bölütleyici bu küme üzerinde ayarlandı |
| Altı kitap | 300, altı temel hadis kitabının her birinden 50 | 1.778 | Ifta Sunnah veri ailesi [@oumer2025relation; @internal-data-manifest]; etiketler, Ifta platformunun üçüncü bir tarafça yeniden yapılandırılmış işaretlemeleridir | Test kümesi. Metni bir pilot hadisle eşleşen bütün kayıtlar çıkarıldıktan sonra sabit tohumla seçildi |

Altı kitap kümesini, uzunluğu 100 ile 3.000 karakter arasında olan ve en az iki etiketli ravi içeren kayıtlardan örnekledik. Normalizasyondan sonra her referans geçişi kendi hadis metninde bulunur ve 300 hadisin tamamında geçişler metindeki sırayı izler. Bir hadiste 2 ile 11 arasında geçiş vardır (medyan 6); 300 hadisin 74'ü birden fazla zincir içerir.

Platform etiketlerinde bilinen tutarsızlıklar vardır. Derleyicinin açıklaması ya da destekleyici bir zincir içindeki raviler bazen etiketlenir, bazen etiketlenmez; dolayısıyla bunları çıkaran bir sistem bazı hadislerde yanlış sayılır. Etiketleri düzeltmedik.

**Düzenli ifadelerle üretilen etiketler ne kadar iyi?** 300 hadisin 253'ü için Sanadset'te eşleşen bir kayıt vardır (metin benzerliği en az 0,9; 118'i normalizasyondan sonra aynıdır). Sanadset etiketlerini Ifta etiketlerine karşı puanladığımızda gevşek eşleştirmede precision 0,939, recall 0,979 ve F1 0,959 (%95 aralığı 0,943 ile 0,972 arasında), katı eşleştirmede ise F1 0,931 elde ettik. İki etiket kümesi bu hadislerde birbirine yakındır. Bu, iki etiket kümesinin uyumudur, herhangi birinin doğruluğu değildir. Ayrıca bu 253 hadis, rastgele bir alt küme değil, metni her iki derlemde eşleşen hadislerdir.

## 7.3 Protokol

Analiz birimi hadistir. Her hadis için sistemin ravi geçişlerini, en büyük ağırlıklı iki parçalı eşleştirmeyle referans geçişlerine hizalıyoruz; eşleşen çiftleri doğru pozitif sayıyoruz. Koşulardan önce sabitlediğimiz iki eşleştirme kuralını raporluyoruz:

- **Katı:** Normalize dizgiler eşittir. Normalizasyon harekeleri ve noktalama işaretlerini kaldırır, harf varyantlarını birleştirir.
- **Gevşek:** Dizgiler eşittir, biri diğerini içerir ya da belirteç F1 değerleri en az 0,60'tır.

Precision, recall ve F1 için hadisler üzerinden mikro ortalama alıyoruz. Aralıklar, hadislerin 2.000 kez yeniden örneklenmesiyle elde edilen %95 yüzdelik bootstrap aralıklarıdır. İki koşulun farkını hesaplarken ikisi için de aynı yeniden örneklemeleri kullanıyoruz. Sistemin hiçbir şey döndürmediği hadis sıfır geçiş olarak sayılır ve hiçbir zaman dışarıda bırakılmaz.

Bu bölüm boyunca "yanlış" geçiş, gevşek kurala göre bir referans geçişiyle eşleşmeyen önerilen geçiş; "doğru" geçiş ise eşleşen geçiştir. Her iki ifade de etiketlerin yüzey biçimiyle uyuma ilişkindir. Bölüm 7.6, eşleşmeyen geçişlerin nelerden oluştuğunu gösterir.

Katı eşleştirme, geçişin nerede bittiğine duyarlıdır. Karşılaştırmalarda gevşek kuralı kullanıyoruz; iki ölçü arasındaki fark da bilgi verdiği için yanında katı F1'i de sunuyoruz [@muther2020tracing].

## 7.4 Koşullar

Bütün koşullar aynı motordan geçer: veri alımı, bölütleme, sağlayıcı çağrısı, doğrulama ve commit. Hiçbir koşuda inceleme kararı verilmediği için sonuçlar yalnız boru hattının otomatik kısmını gösterir.

**Tablo 7.2** Çıkarım koşulları.

| Koşul | Bölütleme | Sağlayıcı | Şema ipuçları |
|---|---|---|---|
| Kural | Kural tabanlı bölütleyicinin bulduğu zincir metin aralığı, ح işaretinde bölünür | `rule_based_isnad`, model yok | kullanılmaz |
| Model, yalnız şema | Hadisin tamamı, tek çağrı | Claude Haiku 5.5 | Yalnız tip adları ve JSON sözleşmesi; tip ve özellik açıklamaları çıkarılmış |
| Model, isnad bilgili | Hadisin tamamı, tek çağrı | Claude Haiku 5.5 | Açıklamalar ve şablon ipuçları: adları aynen kopyala, aktarım fiillerini dışarıda bırak, Peygamber ravi değildir |
| Model, isnad bilgili, zincir metin aralığı | Bölütleyiciden gelen zincir metin aralığı, segment başına bir çağrı | Claude Haiku 5.5 | Aynı açıklamalar ve ipuçları |

Model, `low` çaba ayarıyla ve yapılandırılmış çıktıyla çalışır. Yanıtlar içerikle adreslenen bir önbellekte saklandığından her koşu yeni çağrı yapılmadan yeniden üretilebilir.

## 7.5 Çıkarım sonuçları

**Tablo 7.3** Altı kitap test kümesinde ravi geçişi çıkarımı (300 hadis, 1.778 referans geçişi, Ifta etiketleri). P, R ve F1 gevşek eşleştirmeyi kullanır; aralık, gevşek F1 içindir.

| Koşul | P | R | F1 [%95 aralığı] | Katı F1 | Eksiksiz zincirler | TP / FP / FN |
|---|---|---|---|---|---|---|
| Kural | 0,968 | 0,881 | 0,923 [0,910, 0,935] | 0,633 | 0,490 | 1.567 / 51 / 211 |
| Model, yalnız şema | 0,914 | 0,868 | 0,890 [0,865, 0,914] | 0,826 | 0,567 | 1.543 / 145 / 235 |
| Model, isnad bilgili | 0,997 | 0,919 | 0,956 [0,946, 0,966] | 0,904 | 0,690 | 1.634 / 5 / 144 |
| Model, isnad bilgili, zincir metin aralığı | 0,998 | 0,903 | 0,948 [0,936, 0,959] | 0,897 | 0,650 | 1.605 / 3 / 173 |

![Şekil 7.1 Altı kitap test kümesinde koşula göre gevşek precision, recall ve F1. F1 üzerindeki hata çubukları %95 bootstrap aralıklarıdır.](figures/fig-7-1-conditions.png)

"Eksiksiz zincirler", gevşek eşleştirmede her geçişin sırayla eşleştiği ve fazladan hiçbir geçişin bulunmadığı hadislerin payıdır.

**Gevşek eşleştirmede tek başına şema, modeli kurallardan daha iyi yapmaz.** Yalnız şema verilen model, kural tabanlı ayrıştırıcının F1'de 0,032 (aralık 0,006 ile 0,060 arasında), precision'da 0,054 (0,026 ile 0,083 arasında) altındadır. Recall farklı değildir (0,013, aralık −0,018 ile 0,044 arasında). Katı eşleştirmede sıralama tersine döner: katı F1, yalnız şema verilen model için 0,826, ayrıştırıcı için 0,633'tür. Model ayrıca daha fazla zinciri bütünüyle doğru çıkarır (0,490'a karşı 0,567). Ayrıştırıcı doğru adları bulur ama metin aralıkları çoğu zaman adın sonunu aşar; model temiz adlar döndürür, bazı adları da ekler ya da değiştirir.

**Kazanımın büyük kısmı açıklamalardan ve ipuçlarından gelir.** Aynı modele tip ve özellik açıklamaları ile isnad ipuçlarını vermek precision'ı 0,083 (0,059 ile 0,108 arasında), recall'u 0,051 (0,024 ile 0,078 arasında), F1'i 0,066 (0,041 ile 0,091 arasında) artırır. Eşleşmeyen öneriler 145'ten 5'e düşer. İpuçlarıyla model, kural tabanlı ayrıştırıcının gevşek F1'de 0,034 (0,021 ile 0,047 arasında) üzerindedir; katı eşleştirmede ise çok daha üstündedir. Şemasız bir koşul çalıştırmadık. Bu nedenle ölçtüğümüz, şema verildiğinde talimatların etkisidir; talimatlarla şemanın karşılaştırması değildir.

**Modeli zincir metin aralığıyla sınırlamak yardımcı olmadı.** Dördüncü koşulda model yalnız bölütleyicinin bulduğu zincir metin aralığını görür. F1, hadisin tamamı için 0,956 iken bu koşulda 0,948'dir; 0,008'lik farkın aralığı −0,002 ile 0,019 arasındadır. Bölütleyici yalnız zincir değişimi işaretinde yeni segment başlattığından 300 hadisin yalnız 10'u iki çağrıya bölündü. Dolayısıyla koşul, zincir başına bir çağrıdan çok girdinin sınırlandırılmasını sınar. Birden fazla zincir içeren uzun hadislerde zincir başına çağrıların yardımcı olup olmadığı sorusu açık kalır. İki koşulda da hiçbir çağrı kesilmedi. 30 Eylül'deki tasarım analizi, farklı bir modelde kesilmiş yanıtlar gördükten sonra zincir başına çağrı önermişti; Claude Haiku 5.5 ve bu uzunluktaki hadislerle kesilme gözlemlemiyoruz. Zincir metin aralığı koşulunda, motorun tanımsız bir düğüme başvuran ilişkiyi reddetmesi yüzünden 310 çağrıdan biri başarısız oldu.

**Tablo 7.4** Hadisin yapısına göre gevşek recall (altı kitap kümesi).

| Koşul | 1 zincir (226) | 2+ zincir (74) | 2–4 geçiş (22) | 5–6 geçiş (203) | 7–11 geçiş (75) |
|---|---|---|---|---|---|
| Kural | 0,924 | 0,778 | 0,843 | 0,923 | 0,806 |
| Model, yalnız şema | 0,886 | 0,824 | 0,928 | 0,876 | 0,844 |
| Model, isnad bilgili | 0,940 | 0,868 | 0,976 | 0,948 | 0,854 |
| Model, isnad bilgili, zincir metin aralığı | 0,915 | 0,874 | 0,964 | 0,930 | 0,841 |

Bütün koşullarda paralel zincirli ve uzun hadislerde recall düşer. Paralel zincirlerde en büyük kayıp kural tabanlı ayrıştırıcıdadır (0,924'ten 0,778'e). Kitaplara göre gevşek F1, isnad bilgili model için 0,936 (Bukhari) ile 0,980 (Nasa'i), kural tabanlı ayrıştırıcı için 0,862 (Abu Dawud) ile 0,963 (Nasa'i) arasında değişir.

Sanadset etiketlerine karşı puanlanan pilot kümede koşulların sıralaması aynıdır: kural 0,892, yalnız şema 0,828, isnad bilgili 0,945, zincir metin aralığı 0,919 (gevşek F1). Kural tabanlı ayrıştırıcı bu 50 hadis üzerinde ayarlandığı için pilot sayıları onun lehine iyimserdir.

## 7.6 Kontrollerin yakaladıkları

Kontroller, modelin metinden saptığı koşulda, yani yalnız şema verilen koşulda etkili olur. Tablo 7.5, önerilen geçişin referansla eşleşip eşleşmediğini ve bir kontrolün onu işaretleyip işaretlemediğini çaprazlar.

**Tablo 7.5** Yalnız şema verilen koşulda değer-alıntıda kontrolü (altı kitap kümesi, önerilen 1.688 geçişin 145'i referansla eşleşmiyor).

| | Eşleşmeyen | Eşleşen |
|---|---|---|
| Kontrolün işaretledikleri | 122 | 33 |
| İşaretlenmeyenler | 23 | 1.510 |

![Şekil 7.2 Yalnız şema verilen koşulda önerilen geçişler: referansla eşleşme ve değer-alıntıda kontrolünün işaretleyip işaretlememesi.](figures/fig-7-2-gate.png)

Kontrol, 70 hadiste 155 geçişi (önerilerin %9,2'sini) işaretler. İşaretlenen geçişlerin %79'u eşleşmeyendir ve bunlar bütün eşleşmeyen geçişlerin %84'ünü oluşturur. Düğüm düzeyindeki diğer kontrollerin hiçbiri tetiklenmedi: modelin verdiği her alıntı, kontrollerin kullandığı karşılaştırmaya göre kaynak segmentinde bulundu.

Kontrolün saptadığı, modelin alıntıladığı metinde bulunmayan bir ad yazmasıdır. Tablo 7.6, işaretlenen 155 adı sabit kurallarla sınıflandırır (`evaluation/classify_value_flags.py`).

**Tablo 7.6** Yalnız şema verilen koşulda işaretlenen adların değişiklik türleri.

| Değişiklik türü | Örnek (alıntı, ad) | İşaretlenen | Eşleşmeyen | Eşleşen |
|---|---|---|---|---|
| Latin harflerine çevriyazı | `حَدَّثَنَا الْأَعْمَشُ`, "al-A'mash" | 79 | 79 | 0 |
| Adın ad hâli değiştirilmiş | `عَنْ أَبِي بِشْرٍ` (tamlayan hâli), `أَبُو بِشْرٍ` (yalın hâl) | 34 | 21 | 13 |
| Akrabalık ifadesi adla değiştirilmiş | `عَنْ أَبِيهِ` ("babasından"), `عُرْوَةَ` | 25 | 18 | 7 |
| Diğer, ad metnin başka yerinde bulunuyor | ad alıntıdan daha uzun | 7 | 3 | 4 |
| Diğer, ad metinde bulunmuyor | `حَدَّثَنَا يَحْيَى ، هُوَ ابْنُ سَعِيدٍ`, `يحيى بن سعيد` | 10 | 1 | 9 |
| Toplam | | 155 | 122 | 33 |

Üç gözlem, öne çıkan sayıların nasıl okunacağını sınırlar.

Birincisi, "yanlış" geçişlerin çoğu uydurulmuş raviler değildir. Yetmiş dokuzunda doğru ravi Latin harfleriyle yazılmıştır; hepsi modelin yazı değiştirdiği 14 hadisten gelir. Yirmi birinde doğru ravi farklı bir ad hâlindedir. Hâl değişikliğinin eşleşme sayılıp sayılmaması adın uzunluğuna bağlıdır: iki sözcüklü bir adda belirteç örtüşmesi gevşek kuralın eşiğinin altına düşer, daha uzun bir adda düşmez. Kontrol de puanlayıcı da yüzey biçimlerini karşılaştırdığı için uyumlarının bir kısmı yapılarından kaynaklanır.

İkincisi, akrabalık örnekleri uydurma değil, çıkarımdır. Örnekte metin "Hisham ibn Urwa, babasından" der; model ise "Urwa" yazmıştır. Ad metinde vardır, alıntıda yoktur. 25 akrabalık adının 15'i hadis metninde geçer. Metin dışından bilgi gerektiren, işaretlenmiş bir ad bulduk: alıntı `قَالَ عُثْمَانُ`, ad ise `عثمان بن عفان` olup ikinci kısım hadisin hiçbir yerinde geçmez.

Üçüncüsü, Bölüm 2.3'teki sınıflar şöyle ayrılır. Eşleşmeyen 145 geçişin 102'sinde, normalize hadis metninde bulunmayan bir ad vardır; kontrol bu 102 geçişin hepsini işaretler. Kırk üçünde ad metinde bulunur; kontrol bunların 20'sini, yani adı alıntının dışında kalanları işaretler. Eşleşmeyen on geçiş, Peygamber'i ravi olarak adlandırır; bu bir kategori hatasıdır. Kontrol bunların ikisini, ikisi de Latin harfleriyle yazılmış olanları işaretler; ad metinden doğru kopyalandığı için sekizini kaçırır. Gerçekleştirilmiş hiçbir kontrol bu sınıfı kapsamaz.

İşaretlenen aday, bir kişi karar verene kadar kabul edilmediğinden bu koşulda incelemesiz kabul edilen adayların precision'ı 0,914 yerine 0,985, recall'u ise 0,868 yerine 0,849'dur (Tablo 7.7). Grafın kendisine daha az çıktı ulaşır: açık inceleme öğesi olan koşu commit edilmez ve 300 hadisin 110'unda böyle bir öğe vardır. Bu hadisleri boş saydığımızda, bir inceleyici karar verene kadar commit edilen çıktının precision'ı 0,983, recall'u 0,582'dir.

**Tablo 7.7** Yalnız şema verilen koşulun üç noktadaki çıktısı (altı kitap kümesi, gevşek eşleştirme).

| Çıktı | P | R | F1 | TP / FP / FN |
|---|---|---|---|---|
| Modelin önerdiği her şey | 0,914 | 0,868 | 0,890 | 1.543 / 145 / 235 |
| İncelemesiz kabul edilen adaylar | 0,985 | 0,849 | 0,912 | 1.510 / 23 / 268 |
| İncelemesiz grafa commit edilenler (190 hadis) | 0,983 | 0,582 | 0,731 | 1.034 / 18 / 744 |

İsnad bilgili koşulda 1.639 önerinin 5'i eşleşmeyendir; kontrol bunların 3'ünü işaretler ve eşleşen hiçbir geçişi işaretlemez. İstem zaten modele adları yazıldığı gibi kopyalamasını söylediğinde kontrollerin bulacağı pek az şey kalır. Pilot kümede, Sanadset etiketlerine karşı yalnız şema verilen koşulun örüntüsü tekrarlanır: 35 geçiş işaretlenir, 35'inin tamamı eşleşmeyendir, eşleşmeyen 3 geçiş ise işaretlenmez.

## 7.7 Modelin güven skoru

Yalnız şema verilen koşulda, eşleşen geçişi öngörmek için modelin güven skorunun ROC eğrisi altında kalan alanı 0,634'tür. Model yedi farklı güven skoru kullanmıştır; 1.688 geçişin 1.623'ü 0,8 ile 1,0 arasında bir değer taşır.

![Şekil 7.3 Yalnız şema verilen koşulda eşleşen ve eşleşmeyen geçişlerin model güven skorları.](figures/fig-7-3-confidence.png)

Bir güven skoru eşiği ile bir kontrol, ancak incelemeye gönderilen geçişlerin payı aynı olduğunda karşılaştırılabilir. Tablo 7.8, anlamlı bir pay seçen üç eşiği listeler.

**Tablo 7.8** Güven skoru eşiğinin ve değer-alıntıda kontrolünün incelemeye gönderdiği eşleşmeyen geçişler (yalnız şema verilen koşul, toplam 145 eşleşmeyen geçiş).

| Sinyal | İncelemeye gönderilen geçişler | Bunların içinde eşleşmeyenler |
|---|---|---|
| Güven skoru 0,80'in altında | 65 (%3,9) | 16 |
| Güven skoru 0,85'in altında | 275 (%16,3) | 50 |
| Güven skoru 0,90'ın altında | 1.018 (%60,3) | 110 |
| Değer-alıntıda kontrolü | 155 (%9,2) | 122 |

Güven skoru eşiği, geçişlerin %16'sında eşleşmeyen 50 geçiş bulur; kontrol ise %9'unda 122 geçiş bulur. Eşiğin 110 geçişi bulması için bütün geçişlerin %60'ını inceleyiciye göndermesi gerekir. Kontrol, model çağrısı gerektirmez.

## 7.8 İnceleme yükü, commit işlemleri ve maliyet

**Tablo 7.9** İnceleyiciye kalan iş ve koşul başına maliyet (altı kitap kümesi).

| Koşul | İncelemeye gönderilen adaylar | İncelenecek öğesi olmayan hadisler | İncelemesiz commit edilen koşular | 1.000 hadis başına maliyet | Çağrı başına medyan gecikme |
|---|---|---|---|---|---|
| Kural | 0 | %100 | 300'ün 300'ü | 0 | uygulanamaz |
| Model, yalnız şema | 538 | %63 | 300'ün 190'ı | USD 1,87 | 11,1 sn |
| Model, isnad bilgili | 16 | %98 | 300'ün 294'ü | USD 2,29 | 13,0 sn |
| Model, isnad bilgili, zincir metin aralığı | 6 | %99 | 300'ün 295'i | USD 2,21 | 12,8 sn |

Yalnız şema verilen koşuldaki 538 inceleme adayı, değer kontrolünün işaretlediği 155 düğüm ve 383 ilişkiden oluşur. İlişki bulguları arasında kimlik özelliği değeri bulunmayan 192, incelemedeki bir düğüme bağlı 208 ve güven skoru eşiğinin altında kalan 9 ilişki vardır; bir ilişki birden fazla bulgu taşıyabilir. Açık inceleme öğesi olan koşu commit edilemediğinden 300 hadisin 110'u bir kişiyi bekler.

Maliyetleri, deney betiğindeki fiyat sabitleri ve API'nin döndürdüğü belirteç sayılarıyla hesapladık. Sabitler, sağlayıcının 6 Ekim 2026 tarihli Claude Haiku 5.5 fiyat listesinden alınmıştır (bir milyon girdi belirteci için USD 0,10, bir milyon çıktı belirteci için USD 0,50). Hadis başına yaklaşık 3.200 ile 3.500 girdi, 3.100 ile 3.900 çıktı belirteci kullanılmıştır. Gecikme, yanıt önbelleğinden sunulmayan çağrıların medyanıdır (300, 300 ve 108 çağrı). Pilot koşular ve Bölüm 7.9'daki alt küme koşuları dahil bütün değerlendirmenin maliyeti, önbellekten yeniden oynatmalar sayılmadan sekiz model koşusu üzerinden toplandığında USD 3,49'dur.

Her koşuda commit edilen her olgu için iki özelliği kontrol ettik: alıntının, kontrollerin kullandığı karşılaştırmaya göre kaynak segmentinde bulunması ve bir kabul kaydının olması. İkisi de commit edilen bütün olgular için sağlanır. Bayt düzeyinde tam eşitlik karşılaştırmasında model koşuları ilkini sağlamaz: model Arapça metni kaynaktan farklı bir Unicode bileşimiyle döndürür; birkaç alıntı da kaynaktan, karşılaştırmanın yok saydığı harekeler bakımından farklıdır.

İnsan inceleme süresine ilişkin ölçümümüz yoktur. Karar kaydı bu süreyi saklar, ancak bu koşuları hiçbir kişi incelemedi.

## 7.9 İkinci bir model: yapılandırma hatası

Sonuçların modele bağlı olup olmadığını görmek için Claude Sonnet 5.5'i aynı ayarlarla, tabakalı örneklenmiş 36 hadislik bir alt kümede (kitap başına altı hadis) çalıştırdık. Koşu, kullanılabilir bir karşılaştırma üretmedi; nedenini raporluyoruz.

Sonnet 5.5, `low` çaba ayarıyla isnad bilgili koşulda 36 hadisin 28'i için tek ravi döndürdü; bunların çoğunda ravinin adını bir özelliğin anahtarını tutan alana yazdı. Gevşek recall, aynı 36 hadiste Haiku 5.5 için 0,916 ve 0,828 iken Sonnet için 0,237 (isnad bilgili) ve 0,530 (yalnız şema) oldu.

Yapılandırmamızda iki şeyden şüpheleniyoruz; ikisini de ek bir koşuyla sınamadık. Sağlayıcı, özellikleri `name` ve `value` alanlarını içeren bir girdi listesi olarak gönderir; ravi adını tutan özelliğin adı da `name` olduğundan bu belirsizlik yaratır. İkincisi, çaba ayarı modeller arasında aynı biçimde kalibre edilmemiştir. Haiku 5.5, altı kitap kümesindeki 910 çağrısının biri dışında hepsinde biçime uydu.

Motor, bozuk biçimli çıktıyı tasarlandığı gibi ele aldı. Tanımsız özellik anahtarları şema önerisi olarak kaydedildi (bir koşulda 29 farklı anahtar), kimlik özelliği olmayan düğümler reddedildi, 36 koşunun 30'unun commit edilmesi engellendi ve önerilen çıktının precision'ı 0,966 ya da üzerinde kaldı. Bozuk biçimli hiçbir çıktı grafa ulaşmadı. Bu, ilk kodun tip düzeyindeki kontrolünün göremediği, özellik düzeyindeki şema sapmasıdır.

Bu koşudan iki model hakkında sonuç çıkarmıyoruz. Başka bir model değerlendirilmeden önce aktarım biçimi değiştirilmelidir.

## 7.10 Ravi kimliği

Motor, ravi düğümünü yazılı adla tanımlar. Ifta etiketleri her geçişe bir kişi kimliği bağlar; böylece hiçbir sistem çalıştırmadan bu seçimin maliyetini ölçebiliriz. Etiketler her zinciri ayrı listeler; dolayısıyla paralel zincirlerin paylaştığı ravi, zincir başına bir kez sayılır. 300 test hadisi boyunca bu, 740 kişinin doldurduğu 2.150 zincir konumu verir (Tablo 7.1'deki 1.778 referans geçişi, her yazılı geçişi bir kez sayar).

**Tablo 7.10** Zincir konumlarını kişi yerine dizgi anahtarıyla gruplama (altı kitap kümesi, yalnız referans etiketleri). İkili precision, aynı anahtara sahip konum çiftleri arasında aynı kişiye ait olanların payı; ikili recall ise aynı kişiye ait çiftler arasında anahtarı ortak olanların payıdır. B-cubed, konumlar üzerinden, aynı anahtarlı konumların aynı kişiye ait olan payını (precision) ve kişinin konumlarının aynı anahtara sahip olan payını (recall) ortalar.

| Anahtar | Farklı anahtarlar | Birden fazla kişiyi kapsayan anahtarlar | Bu anahtarların altındaki konumlar | Birden fazla anahtara bölünen kişiler | İkili P / R | B-cubed P / R |
|---|---|---|---|---|---|---|
| Tam olarak yazıldığı biçimiyle ad | 964 | 24 (%2,5) | 216 (%10,0) | 191 (%25,8) | 0,737 / 0,559 | 0,941 / 0,715 |
| Normalize ad | 878 | 28 (%3,2) | 262 (%12,2) | 161 (%21,8) | 0,759 / 0,703 | 0,931 / 0,792 |

Her on zincir konumundan biri, birden fazla kişinin paylaştığı bir adın altında yer alır; kişilerin dörtte biri birden fazla adla görünür. En belirsiz anahtarlar akrabalık ifadeleridir: `أَبِيهِ` ("babası"), bu örneklemde 34 farklı kişiyi temsil eder. Adın normalizasyonu bölünmeyi azaltır, farklı kişilerin birleştirilmesini artırır. İki anahtar da kimlik değildir. Aynı örüntü AR-Sanad test zincirlerinde de görünür [@mahmoud2022arsanad]; burada 15.301 yüzey adının 815'i birden fazla kimliğe eşlenir.

Bu, çözümün değil sorunun ölçümüdür. Geçişleri bir otorite listesine bağlamak gelecek çalışmadır.

## 7.11 Ölçmediklerimiz

- **İnsan altın standardı.** Bu değerlendirmedeki hiçbir hadis iki bağımsız etiketleyici tarafından etiketlenmedi. Etiketleme formu ve kılavuzu vardır; etiketleme yapılmamıştır.
- **İnsan incelemesi.** Hiçbir inceleyici hiçbir aday hakkında karar vermedi. Bu yüzden inceleme süremiz, ret oranımız ve içinde bir kişi bulunan boru hattı ölçümümüz yoktur.
- **İlişkiler.** Ravi geçişlerini ve sıralarını puanladık; `NARRATED_FROM` bağlantılarını üçlüler olarak puanlamadık.
- **Diğer modeller.** Bir model kullanılabilir sonuç üretti. İkinci koşu bir yapılandırma gerekçesiyle başarısız oldu.
- **Şema sapması.** Haiku koşuları 910 çağrıda bir tanımsız özellik ve sıfır tanımsız tip üretti. Bu yüzden sapmaya ilişkin ölçülen kanıt neredeyse bütünüyle başarısız ikinci model koşusundan gelir.
- **Koşular arası değişkenlik.** Her koşul bir kez çalıştırıldı.
- **Ezberleme.** Modelin zincirleri okumak yerine iyi bilinen zincirleri hatırlayıp hatırlamadığını sınamadık.
- **Soru cevaplama.** Graf henüz herhangi bir soru kümesinde metin getirmeyle karşılaştırılmadı.
- **Metin bütünlüğü.** Derlem metnini basılı bir baskıyla karşılaştırmadık.

## 7.12 Önceki pilot

30 Eylül 2026'daki pilot, aynı 50 hadisi farklı bir modelle (Claude Sonnet 5) motor dışında kullandı. Kural tabanlı ayrıştırıcı için gevşek F1 0,879, yalnız şema içeren istem için 0,865, isnad bilgili istem için 0,935 raporladı; 605 model alıntısının 605'i de kaynakta bulundu; 318 adın 32'si modelin kendi alıntısında bulunmadı; güven skoru AUC değeri 0,626 oldu. Bu bölümdeki motor tabanlı koşular, farklı bir modelle, altı kat daha fazla görülmemiş veri üzerinde ve farklı bir etiket kaynağına karşı bu örüntülerin her birini tekrar üretir.
