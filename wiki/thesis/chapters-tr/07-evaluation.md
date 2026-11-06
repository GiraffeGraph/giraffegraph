# 7 Değerlendirme

Bu bölümde ölçülen unsurlar, kullanılan veriler, karşılaştırılan referans ve uygulanan eşleştirme kuralı raporlanmaktadır. Ölçüm değerleri, Bölüm 6'da açıklanan betiklerin ürettiği `giraffegraph-core/evaluation/results/` altındaki dosyalardan; veri kümelerinin istatistikleri ise veri manifestosundan alınmıştır [@internal-data-manifest]. Bütün koşular 12 Ekim 2026'da motorun bellek içi arka ucunda gerçekleştirilmiştir. PostgreSQL ve Neo4j arka ucu testlerle ayrıca doğrulanmış (Bölüm 6.7), ancak bu koşularda kullanılmamıştır.

## 7.1 Sorular

Değerlendirmede beş soruya yanıt aranmaktadır.

1. Her çıkarım koşulu, bir hadisin ravi geçişlerini ne ölçüde elde etmektedir?
2. Model ile graf arasına yerleştirilen doğrulama denetimleri neleri saptamaktadır ve bunların doğru çıktı kaybı açısından maliyeti nedir?
3. Modelin bildirdiği güven skoru, bir kişinin neyi incelemesi gerektiğine karar vermek için kullanılabilir bir sinyal midir?
4. Her koşul ne kadar inceleme işi ve parasal maliyet doğurmaktadır?
5. Yazılı bir ad, bir raviyi ne ölçüde tanımlamaktadır?

Yanıtlanamayan sorular Bölüm 7.11'de listelenmektedir.

## 7.2 Veriler ve referans etiketleri

Değerlendirmede iki hadis kümesi kullanılmıştır (Tablo 7.1). Her iki kümede de iki bağımsız etiketleyiciyle oluşturulmuş bir insan altın standardı bulunmamaktadır; hiçbir kaynak da bu etiketleri bu şekilde tanımlamamaktadır [@internal-data-manifest].

**Tablo 7.1** Değerlendirme kümeleri.

| Küme | Hadis sayısı | Referans geçişleri | Metin ve etiketlerin kaynağı | İşlev |
|---|---|---|---|---|
| Pilot | 50, beş kitap, Bukhari yok | 327 | Sanadset 650K [@mghari2022sanadset]; etiketler düzenli ifadelerle üretilmiş | Geliştirme kümesi. Kural tabanlı bölütleyici bu küme üzerinde ayarlanmıştır |
| Altı kitap | 300, altı temel hadis kitabının her birinden 50 | 1.778 | Ifta Sunnah veri ailesi [@oumer2025relation; @internal-data-manifest]; etiketler, Ifta platformunun üçüncü bir tarafça yeniden yapılandırılmış işaretlemeleridir | Test kümesi. Metni bir pilot hadisle eşleşen bütün kayıtlar çıkarıldıktan sonra sabit tohumla seçilmiştir |

Altı kitap kümesi, uzunluğu 100 ile 3.000 karakter arasında olan ve en az iki etiketli ravi içeren kayıtlardan örneklenmiştir. Normalizasyondan sonra her referans geçişinin kendi hadis metninde bulunduğu ve 300 hadisin tamamında geçişlerin metindeki sırayı izlediği belirlenmiştir. Bir hadiste 2 ile 11 arasında geçiş bulunmaktadır (medyan 6); 300 hadisin 74'ü birden fazla zincir içermektedir.

Platform etiketlerinde bilinen tutarsızlıklar bulunmaktadır. Derleyicinin açıklaması ya da destekleyici bir zincir içindeki raviler bazı durumlarda etiketlenirken bazı durumlarda etiketlenmemektedir. Bu nedenle söz konusu ravileri çıkaran bir sistem bazı hadislerde yanlış sayılmaktadır. Etiketler düzeltilmemiştir.

**Düzenli ifadelerle üretilen etiketlerin niteliği nedir?** 300 hadisin 253'ü için Sanadset'te eşleşen bir kayıt bulunmaktadır (metin benzerliği en az 0,9; 118'i normalizasyondan sonra aynıdır). Sanadset etiketleri Ifta etiketlerine karşı puanlandığında gevşek eşleştirmede kesinlik (precision) 0,939, duyarlılık (recall) 0,979 ve F1 0,959 (%95 aralığı 0,943 ile 0,972 arasında), katı eşleştirmede ise F1 0,931 elde edilmiştir. İki etiket kümesi bu hadislerde birbirine yakındır. Bu sonuç, herhangi bir etiket kümesinin doğruluğunu değil, iki küme arasındaki uyumu ifade etmektedir. Ayrıca bu 253 hadis, rastgele bir alt küme olmayıp metni her iki derlemde eşleşen hadislerden oluşmaktadır.

## 7.3 Protokol

Analiz birimi hadistir. Her hadis için sistemin ravi geçişleri, en büyük ağırlıklı iki parçalı eşleştirmeyle referans geçişlerine hizalanmış ve eşleşen çiftler doğru pozitif sayılmıştır. Koşulardan önce sabitlenen iki eşleştirme kuralı aşağıda sunulmaktadır:

- **Katı:** Normalize dizgiler eşittir. Normalizasyon, harekeleri ve noktalama işaretlerini kaldırmakta, harf varyantlarını birleştirmektedir.
- **Gevşek:** Dizgiler eşittir, biri diğerini içermektedir ya da belirteç F1 değerleri en az 0,60'tır.

Kesinlik, duyarlılık ve F1 için hadisler üzerinden mikro ortalama alınmıştır. Aralıklar, hadislerin 2.000 kez yeniden örneklenmesiyle elde edilen %95 yüzdelik bootstrap aralıklarıdır. İki koşulun farkı hesaplanırken her ikisi için de aynı yeniden örneklemeler kullanılmıştır. Sistemin hiçbir şey döndürmediği hadisler sıfır geçiş olarak sayılmış ve hiçbir zaman dışarıda bırakılmamıştır.

Bu bölümde "yanlış" geçiş, gevşek kurala göre bir referans geçişiyle eşleşmeyen önerilen geçişi; "doğru" geçiş ise eşleşen geçişi ifade etmektedir. Her iki tanım da etiketlerin yüzey biçimiyle uyuma ilişkindir. Bölüm 7.6'da eşleşmeyen geçişlerin nelerden oluştuğu gösterilmektedir.

Katı eşleştirme, geçişin nerede bittiğine duyarlıdır. Bu nedenle karşılaştırmalarda gevşek kural kullanılmıştır; iki ölçü arasındaki fark da bilgi verdiğinden katı F1 de birlikte sunulmaktadır [@muther2020tracing].

## 7.4 Koşullar

Bütün koşullar aynı motorun veri alımı, bölütleme, sağlayıcı çağrısı, doğrulama ve commit aşamalarından geçmektedir. Hiçbir koşuda inceleme kararı verilmediğinden sonuçlar yalnızca boru hattının otomatik kısmını göstermektedir.

**Tablo 7.2** Çıkarım koşulları.

| Koşul | Bölütleme | Sağlayıcı | Şema ipuçları |
|---|---|---|---|
| Kural | Kural tabanlı bölütleyicinin bulduğu zincir metin aralığı, ح işaretinde bölünür | `rule_based_isnad`, model yok | kullanılmaz |
| Model, yalnız şema | Hadisin tamamı, tek çağrı | Claude Haiku 5.5 | Yalnız tip adları ve JSON sözleşmesi; tip ve özellik açıklamaları çıkarılmış |
| Model, isnad bilgili | Hadisin tamamı, tek çağrı | Claude Haiku 5.5 | Açıklamalar ve şablon ipuçları: adları aynen kopyala, aktarım fiillerini dışarıda bırak, Peygamber ravi değildir |
| Model, isnad bilgili, zincir metin aralığı | Bölütleyiciden gelen zincir metin aralığı, segment başına bir çağrı | Claude Haiku 5.5 | Aynı açıklamalar ve ipuçları |

Model, `low` çaba ayarıyla ve yapılandırılmış çıktıyla çalışmaktadır. Yanıtlar içerikle adreslenen bir önbellekte saklandığından her koşu yeni çağrı yapılmadan yeniden üretilebilmektedir.

## 7.5 Çıkarım sonuçları

**Tablo 7.3** Altı kitap test kümesinde ravi geçişi çıkarımı (300 hadis, 1.778 referans geçişi, Ifta etiketleri). P, R ve F1 gevşek eşleştirmeye dayanmaktadır; aralık, gevşek F1 içindir.

| Koşul | P | R | F1 [%95 aralığı] | Katı F1 | Eksiksiz zincirler | TP / FP / FN |
|---|---|---|---|---|---|---|
| Kural | 0,968 | 0,881 | 0,923 [0,910, 0,935] | 0,633 | 0,490 | 1.567 / 51 / 211 |
| Model, yalnız şema | 0,914 | 0,868 | 0,890 [0,865, 0,914] | 0,826 | 0,567 | 1.543 / 145 / 235 |
| Model, isnad bilgili | 0,997 | 0,919 | 0,956 [0,946, 0,966] | 0,904 | 0,690 | 1.634 / 5 / 144 |
| Model, isnad bilgili, zincir metin aralığı | 0,998 | 0,903 | 0,948 [0,936, 0,959] | 0,897 | 0,650 | 1.605 / 3 / 173 |

![Şekil 7.1 Altı kitap test kümesinde koşula göre gevşek kesinlik, duyarlılık ve F1. F1 üzerindeki hata çubukları %95 bootstrap aralıklarıdır.](figures/fig-7-1-conditions.png)

"Eksiksiz zincirler", gevşek eşleştirmede her geçişin sırayla eşleştiği ve fazladan hiçbir geçişin bulunmadığı hadislerin payı olarak tanımlanmaktadır.

**Gevşek eşleştirmede tek başına şema, modeli kurallardan daha iyi hâle getirmemiştir.** Yalnız şema verilen model, kural tabanlı ayrıştırıcının F1'de 0,032 (aralık 0,006 ile 0,060 arasında), kesinlikte 0,054 (0,026 ile 0,083 arasında) altında kalmıştır. Duyarlılıkta fark bulunmamıştır (0,013, aralık −0,018 ile 0,044 arasında). Katı eşleştirmede ise sıralama tersine dönmüştür: katı F1, yalnız şema verilen model için 0,826, ayrıştırıcı için 0,633 olarak elde edilmiştir. Ayrıca model daha fazla zinciri bütünüyle doğru çıkarmıştır (0,490'a karşı 0,567). Ayrıştırıcı doğru adları bulmuş, ancak metin aralıkları çoğu zaman adın sonunu aşmıştır; model ise temiz adlar döndürmüş, bazı adları da eklemiş ya da değiştirmiştir.

**Kazanımın büyük kısmı açıklamalardan ve ipuçlarından kaynaklanmıştır.** Aynı modele tip ve özellik açıklamaları ile isnad ipuçlarının verilmesiyle kesinlik 0,083 (0,059 ile 0,108 arasında), duyarlılık 0,051 (0,024 ile 0,078 arasında), F1 ise 0,066 (0,041 ile 0,091 arasında) artmıştır. Eşleşmeyen öneriler 145'ten 5'e düşmüştür. İpuçları verilen model, kural tabanlı ayrıştırıcının gevşek F1'de 0,034 (0,021 ile 0,047 arasında) üzerinde yer almış; katı eşleştirmede ise çok daha yüksek sonuç vermiştir. Şemasız bir koşul çalıştırılmamıştır. Bu nedenle ölçülen etki, şema verildiğinde talimatların etkisidir; talimatlarla şemanın karşılaştırması değildir.

**Modelin zincir metin aralığıyla sınırlandırılması yardımcı olmamıştır.** Dördüncü koşulda modele yalnızca bölütleyicinin bulduğu zincir metin aralığı sunulmuştur. F1, hadisin tamamı için 0,956 iken bu koşulda 0,948 olarak elde edilmiştir; 0,008'lik farkın aralığı −0,002 ile 0,019 arasındadır. Bölütleyici yalnızca zincir değişimi işaretinde yeni segment başlattığından 300 hadisin yalnızca 10'u iki çağrıya bölünmüştür. Dolayısıyla bu koşul, zincir başına bir çağrıdan çok girdinin sınırlandırılmasını sınamaktadır. Birden fazla zincir içeren uzun hadislerde zincir başına çağrıların yardımcı olup olmadığı sorusu açık kalmaktadır. İki koşulda da hiçbir çağrı kesilmemiştir. 30 Eylül'deki tasarım analizinde, farklı bir modelde kesilmiş yanıtlar gözlemlenmesinin ardından zincir başına çağrı önerilmiştir; Claude Haiku 5.5 ve bu uzunluktaki hadislerle kesilme gözlemlenmemiştir. Zincir metin aralığı koşulunda, motorun tanımsız bir düğüme başvuran ilişkiyi reddetmesi nedeniyle 310 çağrıdan biri başarısız olmuştur.

**Tablo 7.4** Hadisin yapısına göre gevşek duyarlılık (altı kitap kümesi).

| Koşul | 1 zincir (226) | 2+ zincir (74) | 2–4 geçiş (22) | 5–6 geçiş (203) | 7–11 geçiş (75) |
|---|---|---|---|---|---|
| Kural | 0,924 | 0,778 | 0,843 | 0,923 | 0,806 |
| Model, yalnız şema | 0,886 | 0,824 | 0,928 | 0,876 | 0,844 |
| Model, isnad bilgili | 0,940 | 0,868 | 0,976 | 0,948 | 0,854 |
| Model, isnad bilgili, zincir metin aralığı | 0,915 | 0,874 | 0,964 | 0,930 | 0,841 |

Bütün koşullarda paralel zincirli ve uzun hadislerde duyarlılığın düştüğü gözlemlenmiştir. Paralel zincirlerde en büyük kayıp kural tabanlı ayrıştırıcıda gerçekleşmiştir (0,924'ten 0,778'e). Kitaplara göre gevşek F1, isnad bilgili model için 0,936 (Bukhari) ile 0,980 (Nasa'i), kural tabanlı ayrıştırıcı için 0,862 (Abu Dawud) ile 0,963 (Nasa'i) arasında değişmiştir.

Sanadset etiketlerine karşı puanlanan pilot kümede de koşulların sıralaması aynı bulunmuştur: kural 0,892, yalnız şema 0,828, isnad bilgili 0,945, zincir metin aralığı 0,919 (gevşek F1). Kural tabanlı ayrıştırıcı bu 50 hadis üzerinde ayarlandığından pilot değerleri ayrıştırıcı lehine iyimserdir.

## 7.6 Denetimlerin yakaladıkları

Denetimler, modelin metinden saptığı koşulda, yani yalnız şema verilen koşulda etkili olmuştur. Tablo 7.5'te, önerilen geçişin referansla eşleşme durumu ile bir denetim tarafından işaretlenme durumu çaprazlanmaktadır.

**Tablo 7.5** Yalnız şema verilen koşulda değerin alıntıda bulunması denetimi (altı kitap kümesi, önerilen 1.688 geçişin 145'i referansla eşleşmemektedir).

| | Eşleşmeyen | Eşleşen |
|---|---|---|
| Denetimin işaretledikleri | 122 | 33 |
| İşaretlenmeyenler | 23 | 1.510 |

![Şekil 7.2 Yalnız şema verilen koşulda önerilen geçişler: referansla eşleşme ve değerin alıntıda bulunması denetiminin işaretleyip işaretlememesi.](figures/fig-7-2-gate.png)

Denetim, 70 hadiste 155 geçişi (önerilerin %9,2'sini) işaretlemiştir. İşaretlenen geçişlerin %79'u eşleşmeyen geçişlerden oluşmuş ve bunlar bütün eşleşmeyen geçişlerin %84'ünü oluşturmuştur. Düğüm düzeyindeki diğer denetimlerin hiçbiri tetiklenmemiştir; modelin verdiği her alıntı, denetimlerin kullandığı karşılaştırmaya göre kaynak segmentinde bulunmuştur.

Denetim, modelin alıntıladığı metinde bulunmayan bir ad yazmasını saptamaktadır. Tablo 7.6'da, işaretlenen 155 ad sabit kurallarla sınıflandırılmaktadır (`evaluation/classify_value_flags.py`).

**Tablo 7.6** Yalnız şema verilen koşulda işaretlenen adların değişiklik türleri.

| Değişiklik türü | Örnek (alıntı, ad) | İşaretlenen | Eşleşmeyen | Eşleşen |
|---|---|---|---|---|
| Latin harflerine çevriyazı | `حَدَّثَنَا الْأَعْمَشُ`, "al-A'mash" | 79 | 79 | 0 |
| Adın ad hâli değiştirilmiş | `عَنْ أَبِي بِشْرٍ` (tamlayan hâli), `أَبُو بِشْرٍ` (yalın hâl) | 34 | 21 | 13 |
| Akrabalık ifadesi adla değiştirilmiş | `عَنْ أَبِيهِ` ("babasından"), `عُرْوَةَ` | 25 | 18 | 7 |
| Diğer, ad metnin başka yerinde bulunuyor | ad alıntıdan daha uzun | 7 | 3 | 4 |
| Diğer, ad metinde bulunmuyor | `حَدَّثَنَا يَحْيَى ، هُوَ ابْنُ سَعِيدٍ`, `يحيى بن سعيد` | 10 | 1 | 9 |
| Toplam | | 155 | 122 | 33 |

Üç gözlem, öne çıkan sayıların yorumlanmasını sınırlandırmaktadır.

Birincisi, "yanlış" geçişlerin çoğu uydurulmuş raviler değildir. Yetmiş dokuzunda doğru ravi Latin harfleriyle yazılmıştır; bunların tamamı modelin yazı değiştirdiği 14 hadisten gelmiştir. Yirmi birinde ise doğru ravi farklı bir ad hâlinde yazılmıştır. Hâl değişikliğinin eşleşme sayılıp sayılmaması adın uzunluğuna bağlıdır: iki sözcüklü bir adda belirteç örtüşmesi gevşek kuralın eşiğinin altına düşerken daha uzun bir adda düşmemektedir. Denetim de puanlayıcı da yüzey biçimlerini karşılaştırdığından aralarındaki uyumun bir kısmı yapılarından kaynaklanmaktadır.

İkincisi, akrabalık örnekleri uydurma değil, çıkarımdır. Örnekte metinde "Hisham ibn Urwa, babasından" ifadesi yer alırken model "Urwa" yazmıştır. Ad metinde bulunmakta, ancak alıntıda bulunmamaktadır. 25 akrabalık adının 15'i hadis metninde geçmektedir. Metin dışından bilgi gerektiren, işaretlenmiş bir ad bulunmuştur: alıntı `قَالَ عُثْمَانُ`, ad ise `عثمان بن عفان` olup ikinci kısım hadisin hiçbir yerinde geçmemektedir.

Üçüncüsü, Bölüm 2.3'teki sınıflar şu şekilde ayrılmaktadır. Eşleşmeyen 145 geçişin 102'sinde, normalize hadis metninde bulunmayan bir ad yer almıştır; denetim bu 102 geçişin tamamını işaretlemiştir. Kırk üçünde ad metinde bulunmuş; denetim bunların 20'sini, yani adı alıntının dışında kalanları işaretlemiştir. Eşleşmeyen on geçişte Peygamber ravi olarak adlandırılmıştır; bu bir kategori hatasıdır. Denetim bunların ikisini, her ikisi de Latin harfleriyle yazılmış olanları işaretlemiş; ad metinden doğru kopyalandığı için sekizini kaçırmıştır. Gerçekleştirilmiş hiçbir denetim bu sınıfı kapsamamaktadır.

İşaretlenen aday bir kişi karar verene kadar kabul edilmediğinden, bu koşulda incelemesiz kabul edilen adayların kesinliği 0,914 yerine 0,985, duyarlılığı ise 0,868 yerine 0,849 olarak elde edilmiştir (Tablo 7.7). Grafın kendisine daha az çıktı ulaşmıştır: açık inceleme öğesi olan koşu commit edilmemekte ve 300 hadisin 110'unda böyle bir öğe bulunmaktadır. Bu hadisler boş sayıldığında, bir inceleyici karar verene kadar commit edilen çıktının kesinliği 0,983, duyarlılığı 0,582 olarak hesaplanmıştır.

**Tablo 7.7** Yalnız şema verilen koşulun üç noktadaki çıktısı (altı kitap kümesi, gevşek eşleştirme).

| Çıktı | P | R | F1 | TP / FP / FN |
|---|---|---|---|---|
| Modelin önerdiği her şey | 0,914 | 0,868 | 0,890 | 1.543 / 145 / 235 |
| İncelemesiz kabul edilen adaylar | 0,985 | 0,849 | 0,912 | 1.510 / 23 / 268 |
| İncelemesiz grafa commit edilenler (190 hadis) | 0,983 | 0,582 | 0,731 | 1.034 / 18 / 744 |

İsnad bilgili koşulda 1.639 önerinin 5'i referansla eşleşmemiştir; denetim bunların 3'ünü işaretlemiş ve eşleşen hiçbir geçişi işaretlememiştir. İstem zaten modele adları yazıldığı gibi kopyalamasını söylediğinde denetimlerin saptayacağı pek az unsur kalmaktadır. Pilot kümede, Sanadset etiketlerine karşı yalnız şema verilen koşulun örüntüsü tekrarlanmıştır: 35 geçiş işaretlenmiş, 35'inin tamamı eşleşmeyen geçişlerden oluşmuş, eşleşmeyen 3 geçiş ise işaretlenmemiştir.

## 7.7 Modelin güven skoru

Yalnız şema verilen koşulda, eşleşen geçişi öngörmek için modelin güven skorunun ROC eğrisi altında kalan alanı 0,634 olarak hesaplanmıştır. Model yedi farklı güven skoru kullanmıştır; 1.688 geçişin 1.623'üne 0,8 ile 1,0 arasında bir değer verilmiştir.

![Şekil 7.3 Yalnız şema verilen koşulda eşleşen ve eşleşmeyen geçişlerin model güven skorları.](figures/fig-7-3-confidence.png)

Bir güven skoru eşiği ile bir denetim, ancak incelemeye gönderilen geçişlerin payı aynı olduğunda karşılaştırılabilmektedir. Tablo 7.8'de anlamlı bir pay seçen üç eşik listelenmektedir.

**Tablo 7.8** Güven skoru eşiğinin ve değerin alıntıda bulunması denetiminin incelemeye gönderdiği eşleşmeyen geçişler (yalnız şema verilen koşul, toplam 145 eşleşmeyen geçiş).

| Sinyal | İncelemeye gönderilen geçişler | Bunların içinde eşleşmeyenler |
|---|---|---|
| Güven skoru 0,80'in altında | 65 (%3,9) | 16 |
| Güven skoru 0,85'in altında | 275 (%16,3) | 50 |
| Güven skoru 0,90'ın altında | 1.018 (%60,3) | 110 |
| Değerin alıntıda bulunması denetimi | 155 (%9,2) | 122 |

Güven skoru eşiği, geçişlerin %16'sında eşleşmeyen 50 geçiş saptamış; denetim ise %9'unda 122 geçiş saptamıştır. Eşiğin 110 geçişi saptaması için bütün geçişlerin %60'ını inceleyiciye göndermesi gerekmektedir. Denetim, model çağrısı gerektirmemektedir.

## 7.8 İnceleme yükü, commit işlemleri ve maliyet

**Tablo 7.9** İnceleyiciye kalan iş ve koşul başına maliyet (altı kitap kümesi).

| Koşul | İncelemeye gönderilen adaylar | İncelenecek öğesi olmayan hadisler | İncelemesiz commit edilen koşular | 1.000 hadis başına maliyet | Çağrı başına medyan gecikme |
|---|---|---|---|---|---|
| Kural | 0 | %100 | 300'ün 300'ü | 0 | uygulanamaz |
| Model, yalnız şema | 538 | %63 | 300'ün 190'ı | USD 1,87 | 11,1 sn |
| Model, isnad bilgili | 16 | %98 | 300'ün 294'ü | USD 2,29 | 13,0 sn |
| Model, isnad bilgili, zincir metin aralığı | 6 | %99 | 300'ün 295'i | USD 2,21 | 12,8 sn |

Yalnız şema verilen koşuldaki 538 inceleme adayı, değer denetiminin işaretlediği 155 düğüm ve 383 ilişkiden oluşmuştur. İlişki bulguları arasında kimlik özelliği değeri bulunmayan 192, incelemedeki bir düğüme bağlı 208 ve güven skoru eşiğinin altında kalan 9 ilişki yer almıştır; bir ilişki birden fazla bulgu taşıyabilmektedir. Açık inceleme öğesi olan koşu commit edilemediğinden 300 hadisin 110'u bir kişinin kararını beklemektedir.

Maliyetler, deney betiğindeki fiyat sabitleri ve API'nin döndürdüğü belirteç sayılarıyla hesaplanmıştır. Sabitler, sağlayıcının 6 Ekim 2026 tarihli Claude Haiku 5.5 fiyat listesinden alınmıştır (bir milyon girdi belirteci için USD 0,10, bir milyon çıktı belirteci için USD 0,50). Hadis başına yaklaşık 3.200 ile 3.500 girdi, 3.100 ile 3.900 çıktı belirteci kullanılmıştır. Gecikme, yanıt önbelleğinden sunulmayan çağrıların medyanı olarak hesaplanmıştır (300, 300 ve 108 çağrı). Pilot koşular ve Bölüm 7.9'daki alt küme koşuları dahil bütün değerlendirmenin maliyeti, önbellekten yeniden oynatmalar sayılmadan sekiz model koşusu üzerinden toplandığında USD 3,49 olarak bulunmuştur.

Her koşuda commit edilen her olgu için iki özellik kontrol edilmiştir: alıntının, denetimlerin kullandığı karşılaştırmaya göre kaynak segmentinde bulunması ve bir kabul kaydının olması. Commit edilen bütün olgularda her iki özellik de sağlanmıştır. Bayt düzeyinde tam eşitlik karşılaştırmasında ise model koşuları ilk özelliği sağlamamıştır: model Arapça metni kaynaktan farklı bir Unicode bileşimiyle döndürmüştür; birkaç alıntı da kaynaktan, karşılaştırmanın yok saydığı harekeler bakımından farklılaşmıştır.

İnsan inceleme süresine ilişkin ölçüm bulunmamaktadır. Karar kaydı bu süreyi saklamakla birlikte bu koşular hiçbir kişi tarafından incelenmemiştir.

## 7.9 İkinci bir model: yapılandırma hatası

Sonuçların modele bağlı olup olmadığını incelemek amacıyla Claude Sonnet 5.5, aynı ayarlarla, tabakalı örneklenmiş 36 hadislik bir alt kümede (kitap başına altı hadis) çalıştırılmıştır. Koşu kullanılabilir bir karşılaştırma üretmemiştir; bunun nedeni aşağıda raporlanmaktadır.

Sonnet 5.5, `low` çaba ayarıyla isnad bilgili koşulda 36 hadisin 28'i için tek ravi döndürmüştür; bunların çoğunda ravinin adı, bir özelliğin anahtarını tutan alana yazılmıştır. Gevşek duyarlılık, aynı 36 hadiste Haiku 5.5 için 0,916 ve 0,828 iken Sonnet için 0,237 (isnad bilgili) ve 0,530 (yalnız şema) olarak elde edilmiştir.

Yapılandırmada iki unsurdan şüphelenilmektedir; bunların hiçbiri ek bir koşuyla sınanmamıştır. Sağlayıcı, özellikleri `name` ve `value` alanlarını içeren bir girdi listesi olarak göndermektedir; ravi adını tutan özelliğin adı da `name` olduğundan bu durum belirsizlik yaratmaktadır. İkinci olarak, çaba ayarı modeller arasında aynı biçimde kalibre edilmemiştir. Haiku 5.5'in, altı kitap kümesindeki 910 çağrısının biri dışında tamamında biçime uyduğu gözlemlenmiştir.

Motor, bozuk biçimli çıktıyı tasarlandığı gibi işlemiştir. Tanımsız özellik anahtarları şema önerisi olarak kaydedilmiş (bir koşulda 29 farklı anahtar), kimlik özelliği olmayan düğümler reddedilmiş, 36 koşunun 30'unun commit edilmesi engellenmiş ve önerilen çıktının kesinliği 0,966 ya da üzerinde kalmıştır. Bozuk biçimli hiçbir çıktı grafa ulaşmamıştır. Bu durum, ilk kodun tip düzeyindeki denetiminin göremediği, özellik düzeyindeki şema sapmasıdır.

Bu koşudan iki model hakkında sonuç çıkarılmamaktadır. Başka bir model değerlendirilmeden önce aktarım biçiminin değiştirilmesi gerekmektedir.

## 7.10 Ravi kimliği

Motor, ravi düğümünü yazılı adla tanımlamaktadır. Ifta etiketleri her geçişe bir kişi kimliği bağladığından, bu seçimin maliyeti hiçbir sistem çalıştırılmadan ölçülebilmektedir. Etiketlerde her zincir ayrı listelendiği için paralel zincirlerin paylaştığı ravi zincir başına bir kez sayılmaktadır. 300 test hadisi boyunca bu sayımla, 740 kişinin doldurduğu 2.150 zincir konumu elde edilmiştir (Tablo 7.1'deki 1.778 referans geçişi, her yazılı geçişi bir kez saymaktadır).

**Tablo 7.10** Zincir konumlarının kişi yerine dizgi anahtarıyla gruplanması (altı kitap kümesi, yalnız referans etiketleri). İkili kesinlik, aynı anahtara sahip konum çiftleri arasında aynı kişiye ait olanların payı; ikili duyarlılık ise aynı kişiye ait çiftler arasında anahtarı ortak olanların payıdır. B-cubed, konumlar üzerinden, aynı anahtarlı konumların aynı kişiye ait olan payının (kesinlik) ve kişinin konumlarının aynı anahtara sahip olan payının (duyarlılık) ortalamasını almaktadır.

| Anahtar | Farklı anahtarlar | Birden fazla kişiyi kapsayan anahtarlar | Bu anahtarların altındaki konumlar | Birden fazla anahtara bölünen kişiler | İkili P / R | B-cubed P / R |
|---|---|---|---|---|---|---|
| Tam olarak yazıldığı biçimiyle ad | 964 | 24 (%2,5) | 216 (%10,0) | 191 (%25,8) | 0,737 / 0,559 | 0,941 / 0,715 |
| Normalize ad | 878 | 28 (%3,2) | 262 (%12,2) | 161 (%21,8) | 0,759 / 0,703 | 0,931 / 0,792 |

Her on zincir konumundan birinin, birden fazla kişinin paylaştığı bir adın altında yer aldığı; kişilerin dörtte birinin ise birden fazla adla göründüğü belirlenmiştir. En belirsiz anahtarlar akrabalık ifadeleridir: `أَبِيهِ` ("babası"), bu örneklemde 34 farklı kişiyi temsil etmektedir. Adın normalizasyonuyla bölünme azalmış, farklı kişilerin birleştirilmesi artmıştır. İki anahtar da kimlik değildir. Aynı örüntü AR-Sanad test zincirlerinde de görülmektedir [@mahmoud2022arsanad]; burada 15.301 yüzey adının 815'i birden fazla kimliğe eşlenmektedir.

Bu değerlendirmede çözümün değil, sorunun ölçümü yapılmıştır. Geçişlerin bir otorite listesine bağlanması gelecek çalışma kapsamındadır.

## 7.11 Ölçülmeyen konular

- **İnsan altın standardı.** Bu değerlendirmedeki hiçbir hadis iki bağımsız etiketleyici tarafından etiketlenmemiştir. Etiketleme formu ve kılavuzu bulunmakta, ancak etiketleme yapılmamıştır.
- **İnsan incelemesi.** Hiçbir inceleyici hiçbir aday hakkında karar vermemiştir. Bu nedenle inceleme süresi, ret oranı ve içinde bir kişi bulunan boru hattına ilişkin ölçüm bulunmamaktadır.
- **İlişkiler.** Ravi geçişleri ve sıraları puanlanmış; `NARRATED_FROM` bağlantıları üçlüler olarak puanlanmamıştır.
- **Diğer modeller.** Bir model kullanılabilir sonuç üretmiştir. İkinci koşu bir yapılandırma gerekçesiyle başarısız olmuştur.
- **Şema sapması.** Haiku koşuları 910 çağrıda bir tanımsız özellik ve sıfır tanımsız tip üretmiştir. Bu nedenle sapmaya ilişkin ölçülen kanıt neredeyse bütünüyle başarısız ikinci model koşusundan gelmektedir.
- **Koşular arası değişkenlik.** Her koşul bir kez çalıştırılmıştır.
- **Ezberleme.** Modelin zincirleri okumak yerine iyi bilinen zincirleri hatırlayıp hatırlamadığı sınanmamıştır.
- **Soru cevaplama.** Graf henüz herhangi bir soru kümesinde metin getirmeyle karşılaştırılmamıştır.
- **Metin bütünlüğü.** Derlem metni basılı bir baskıyla karşılaştırılmamıştır.

## 7.12 Önceki pilot

30 Eylül 2026'daki pilotta, aynı 50 hadis farklı bir modelle (Claude Sonnet 5) motor dışında kullanılmıştır. Kural tabanlı ayrıştırıcı için gevşek F1 0,879, yalnız şema içeren istem için 0,865, isnad bilgili istem için 0,935 olarak raporlanmıştır; 605 model alıntısının 605'i de kaynakta bulunmuş; 318 adın 32'si modelin kendi alıntısında bulunmamış; güven skoru AUC değeri 0,626 olarak elde edilmiştir. Bu bölümdeki motor tabanlı koşularda, farklı bir modelle, altı kat daha fazla görülmemiş veri üzerinde ve farklı bir etiket kaynağına karşı bu örüntülerin her biri tekrar üretilmiştir.