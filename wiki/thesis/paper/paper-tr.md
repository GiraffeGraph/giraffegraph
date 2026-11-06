# Alıntı doğru, çıkarılan değer farklı: hadis ravi zincirlerinde dil modeli ile bilgi grafı arasındaki denetimlerin ölçülmesi

::: {.authors}
Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya

Bilgisayar Mühendisliği Bölümü, Akdeniz Üniversitesi, Antalya, Türkiye

Ön baskı taslağı, 13 Ekim 2026. Hakem değerlendirmesinden geçmemiştir.
:::

::: {.abstract}
**Özet.** Büyük dil modelleri (BDM) ile bilgi grafı oluşturan sistemler, genellikle modelden bir kaynak alıntısı ve güven skoru istemekte ve çıkarılan olguların hangilerine güvenileceğine bu bilgilerle karar vermektedir. Bu uygulama, Arapça hadis metinlerinin ravi zincirleri (isnad) üzerinde çalışan bir çıkarım motorunda sınanmıştır. Motor, modeli öneri üreten bir bileşen olarak ele almaktadır. Her aday bir alıntı taşımakta, deterministik denetimler kuşkulu adayları insan incelemesine yönlendirmekte ve kabul edilen her olgunun kabulü kaydedilmektedir. Altı temel hadis kitabından alınan 300 hadis, platform kaynaklı ravi etiketleriyle karşılaştırılarak puanlanmıştır. Yalnız şema verilen modelin bütün alıntıları kaynakta bulunduğundan alıntı denetimi hiçbir öneriyi işaretlememiştir. Değerin alıntıda bulunması denetimi ise önerilerin %9,2'sini işaretlemiştir. İşaretlenenler, referansla eşleşmeyen 145 önerinin 122'sini içermektedir. Bunların çoğu uydurulmuş raviler değildir; modelin adı çevriyazıya çevirdiği, ad hâlini değiştirdiği ya da akrabalık ifadesinin yerine bir ad yazdığı görülmüştür. İncelemeye gönderilen önerilerin payı birbirine yakın tutulduğunda, denetimin belirlediği 122 eşleşmeyen öneriye karşılık modelin güven skoruyla 50 öneri belirlenmiştir. İsteme tip açıklamaları ve birkaç alan ipucu eklenmesi, eşleşmeyen öneri sayısını 145'ten 5'e indirmiş ve denetimlerin belirleyebileceği pek az öneri bırakmıştır. Hiçbir model çağrısı yapmayan kural tabanlı ayrıştırıcı, gevşek eşleştirmede diğer koşullarla yarışabilirken katı eşleştirmede belirgin biçimde daha kötü sonuç vermiştir. Motor, insan kararlarını saklamakta ve geri kalan her şeyi yeniden türetmektedir. Etiketli 27.056 zincir üzerindeki bir benzetimde, yalnız yazılı ada bağlanan kimlik kararının on geçişin birinde yanlış yeniden kullanıldığı gözlemlenmiştir. Deterministik bir kural çelişki bulduğunda kararın kapsamının daraltılması, sabit dar anahtarın yaklaşık yarısı kadar inceleyici sorusuyla bu oranı 0,014'e indirmiştir. Referans etiketleri insanlarca oluşturulmuş bir altın standart değildir; koşulara hiçbir inceleyici katılmamış ve yalnız bir model kullanılabilir sonuç üretmiştir. Ölçümlerden hangi sonuçların çıkarılabileceği ve çıkarılamayacağı belirtilmiştir.
:::

# 1 Giriş

Modellerle çıkarım, metnin graf olgularına dönüştürülmesinin maliyetini düşürmüştür. Model, bir metin parçası ve şema alarak düğümler ve ilişkiler üretmektedir. Güçlük, olgu üretmekten çok, insanların güveneceği bir grafa hangi olguların girebileceğine karar verilmesidir. Bu amaçla yaygın olarak iki önlem kullanılmaktadır: modelden her olgu için kaynaktan alıntı yapması ve ne kadar emin olduğunu bildirmesi istenmektedir. Alıntının olgunun nereden geldiğini göstermesi, güven skorunun ise insanın kontrol etmesi gereken olguları seçmesi beklenmektedir.

Bu iki önlem, yanlış bir olgunun sonuç doğurduğu ve etiketli verinin bulunduğu bir alanda incelenmiştir. Hadis, rivayeti aktaran kişilerin zinciri olan isnadla başlamaktadır: "A bize anlattı, o B'den, o C'den". Araştırmacılar hadisi zincirindeki kişilere göre değerlendirmekte, dolayısıyla tek bir yanlış ad hükmü değiştirmektedir. Büyük etiketli eğitim kümeleri bulunduğunda ince ayar yapılmış modeller ravileri ve aralarındaki bağları zaten başarıyla çıkarmaktadır [@oumer2025relation]. Altı temel hadis kitabının bilgi grafı oluşturulmuş [@kamran2023semantichadith; @kamran2026semantic] ve ravi adları biyografik veritabanlarına bağlanmıştır [@wirahman2026linking]. Bu çalışmaların sonuçlarının iyileştirilmesi amaçlanmamıştır. Bunun yerine, genel amaçlı bir model olgu önerdiğinde model ile graf arasındaki hangi denetimlerin metinden sapan önerileri belirlediği ve bu denetimlerin maliyeti ele alınmıştır.

Kullanılan motor, iki tür olgu arasındaki ayrıma dayanmaktadır. Bir ayrıştırıcının ya da modelin metinden çıkardığı aday yeniden çıkarılabilmektedir. Bu nedenle aday türetilmiş olarak değerlendirilmekte ve doğrudan güvenilmek yerine denetlenmektedir. İnsanın bir olguyu kabul etmesi, düzeltmesi ya da ravinin kimliğini belirlemesi ise metinden türetilememekte ve bir kez saklanmaktadır. Makalenin büyük bölümünde ilk türün denetimi ele alınmıştır. Bölüm 5.7'de ikinci türe ilişkin bir benzetim sunularak kimlik kararını saklamanın ne sağladığı ve yeniden kullanımının maliyeti ölçülmüştür.

Çalışmanın katkıları aşağıda sunulmaktadır.

- Modelin yalnız öneri üretebildiği, deterministik denetimlerin adayları bir gerekçe koduyla incelemeye yönlendirdiği ve kabul edilen her olgunun bir inceleyiciyi ya da otomatik politikayı belirten kabul kaydı taşıdığı bir motor geliştirilmiştir (Bölüm 3).
- Daha önce görülmemiş 300 hadiste, bu motor içinde iki düşük maliyetli denetimin neleri işaretlediği ölçülmüştür: alıntının kaynakta bulunması denetimi ve değerin alıntıda bulunması denetimi. İlki hiçbir öneriyi işaretlememiştir. İkincisi, referans etiketleriyle eşleşmeyen önerilerin %84'ünü işaretlemiştir (Bölüm 5.2).
- İşaretlenen öneriler sınıflandırılmıştır. Bu etiketlere göre, yalnız şema verilen modelin "hatalarının" çoğunun, uydurulmuş ravilerden değil, doğru bir ada uygulanan ve kaydedilmeyen dönüşümlerden oluştuğu gözlemlenmiştir.
- Denetim, eşit inceleme bütçesinde modelin güven skoruyla karşılaştırılmıştır (Bölüm 5.3). Ayrıca aynı boru hattında çalıştırılan dört çıkarım koşulu eşli bootstrap aralıklarıyla karşılaştırılmıştır (Bölüm 5.1).
- Etiketli zincirlerde yazılı bir adın ne sıklıkla birden çok raviyi temsil ettiğini nicel olarak gösteren bir taban çizgisi sunulmuştur (Bölüm 5.6).
- İki etiketli derlem üzerinde kimlik karar defterinin benzetimi yapılmıştır. Saklanan kararın kapsamı, deterministik bir kuralın saptadığı çelişkilerden türetilmiştir (Bölüm 5.7).

# 2 İlgili çalışmalar

**Hadis derlemleri ve çıkarım.** Sanadset 650K, düzenli ifadeler ve metin eşleştirmeyle üretilmiş ravi etiketleri taşıyan 650.986 kayıt sunmaktadır; veri makalesinde doğruluk ölçümü raporlanmamaktadır [@mghari2022sanadset]. Ifta Sunnah veri ailesi, resmî bir hadis platformunun işaretlemelerini ravi metin aralıkları, aktarım ilişkileri ve ravi kimlikleri biçiminde yeniden düzenlemektedir. Yazarın model deposuna göre, bu verilerle eğitilen ince ayarlı modeller ravilerde 0,98, ilişki çiftlerinde 0,95 F1 değerine ulaşmaktadır [@oumer2025relation]. Önceki bir çalışmada, uzun ve noktalamasız metinlerde isnad aralıkları bulunmuş ve eşleştirme kuralının sonucu ne kadar değiştirdiği gösterilmiştir: aynı CRF çıktısıyla tam eşleştirmede 0,254, kısmi eşleştirmede 0,835 F1 elde edilmiş; uzmanlar isnadın bittiği yerde vakaların %53'ünde tam olarak anlaşmıştır [@muther2020tracing]. İsnadı rivayet metninden n-gramlarla ayıran bir çalışmada ise 240 hadiste %92,5'e ulaşılmıştır [@altammami2019text].

**Ravi kimliği.** AR-Sanad 280K, ravi kimliğini belirleme görevini 18.298 ravi üzerinde bir sınıflandırma problemi olarak tanımlamaktadır. En iyi modeli, 27.056 gerçek zincirde mikro F1 83,5'e ulaşırken zincirlerin %60,6'sı en az bir yanlış ravi içermektedir [@mahmoud2022arsanad]. Yakın tarihli bir boru hattı, 185.216 ad varyantını iki biyografik veritabanına bağlamakta; ancak etiketli bağlantılara karşı bir değerlendirme sunmamaktadır [@wirahman2026linking].

**Hadis bilgi grafları ve modeller.** SemanticHadith, altı kitap için bir ontoloji ve graf yayımlamaktadır. Genişletilmiş sürümü, varlıkları özel bir NER modeliyle çıkarmakta ve uzmanların her kitaptan 100 örneği kontrol etmesine dayanmaktadır. Ayrıca belirsiz adların uzmanlarca doğrulanacağı bir çerçeve, gelecek çalışma olarak sıralanmaktadır [@kamran2026semantic]. Hadis derlemlerinin modellerle işlenmesi, uzmanların 0 ile 10 arasındaki puanlarıyla [@asgari2025rezwan] ya da bir yazarın 100 kaydı kaynakla karşılaştırmasıyla değerlendirilmiştir [@cinici2026hadis]. Eleştirel bir derlemede, ölçütlerin karşılaştırılabilirliğinin zayıf olması ve uzman doğrulamasının seyrekliği alanın açık sorunları arasında sayılmaktadır [@haque2026hadith].

**Çıkarılan olguların denetimi.** Text2KGBench, referans üçlülere karşı kesinlik (precision) ve duyarlılık (recall) yanında, üçlünün özne ve nesnesinin cümlede geçip geçmediğini ölçmektedir. Bir model ve veri kümesinde 0,38 kesinlik değerine karşılık 0,17 özne halüsinasyonu raporlanmaktadır; metinde bulunmak, doğru olmak anlamına gelmemektedir [@mihindukulasooriya2023text2kgbench]. Üretilen metnin kaynağa dayandırılmasını ve olgusal doğruluğunu ölçen ölçütler, cümle ya da atomik iddia düzeyinde çalışmaktadır [@rashkin2023measuring; @min2023factscore]. Modellerin bildirdiği güven skorları ise bir kalibrasyon problemi olarak incelenmiştir [@kadavath2022language; @xiong2024can].

**Graf kurmada doğrulama ve inceleme.** Grafa hangi olguların gireceğine uzun süredir güven skoru karar vermektedir: Knowledge Vault, çıkarıcının güven skorunu ön bilgiyle birleştirerek kalibre edilmiş bir olasılık üretmektedir. Bu olasılığın AUC değeri otomatik etiketlere karşı 0,959, insan etiketlerine karşı 0,869 olmuştur [@dong2014vault]. Yakın tarihli sistemlerde, çıkarıcı ile graf arasına model tabanlı doğrulama yerleştirilmektedir. ODKE+, her olgunun bağlamı tarafından desteklenip desteklenmediğini ikinci bir modele sormakta ve ölçümü açıklamadan halüsinasyon içeren çıkarımların azaldığını raporlamaktadır [@khorshidi2025odke]. KARMA, doğrulama ajanlarını birer birer kaldırmakta ve sonucu bir model hakemle puanlamaktadır [@lu2025karma]. Tsaneva ve arkadaşları, model ve insan doğrulayıcılardan oluşan dokuz iş akışını karşılaştırmakta ve insanlara yalnızca doğrulayıcıların görüş ayrılığına düştüğü üçlüleri göndermektedir. Bununla birlikte, modüller ayrı ayrı değerlendirilmemektedir [@tsaneva2025validation]. Diğer sistemler, tasarımları gereği metinde ifade edilmemiş çıktıları kabul etmektedir [@edge2024local]. Çıkarılan değerin modelin kendi alıntısında geçip geçmediğini kontrol eden ya da böyle bir deterministik denetimi çıkarımı yapan modelin güven skoruyla aynı inceleme bütçesinde ve dış bir referansa karşı karşılaştıran bir çalışmaya rastlanmamıştır. Tarama sistematik olarak yürütülmemiştir.

# 3 Sistem

GiraffeGraph Core, şemayı temel alan bir çıkarım motorudur. FastAPI arka ucu, üstveri için PostgreSQL, grafa işlenen veriler için Neo4j ve bir web paneli kullanmaktadır. Projede düğüm tipleri, ilişki tipleri, bunların özellikleri ve düğümün ya da ilişkinin kimliğini oluşturan özellikler tanımlanmaktadır. Kaynak metin, bir kaynak birimi olarak alınmakta ve segmentlere ayrılmaktadır. Dil modeli ya da kural tabanlı program olabilen sağlayıcı, segmentler için aday düğümler ve ilişkiler önermektedir. Her aday, segment referansıyla birlikte bir ya da daha fazla alıntı taşımaktadır. Doğrulama aşamasında her adaya bir durum atanmaktadır: doğrulandı, inceleme gerekiyor ya da reddedildi. Bir koşu, ancak adaylarının hiçbiri inceleme beklemiyorsa grafa işlenebilmektedir.

**Denetimler.** Bu çalışmada üç denetim ele alınmıştır. (i) *Şema*: tipi şemada bulunmayan aday tek başına çıkarılmakta, çağrının diğer adayları korunmakta ve tanımsız tip bir inceleme öğesi olarak kaydedilmektedir. Tanımlanmamış özellik anahtarları da kaldırılmakta ve aynı şekilde kaydedilmektedir. (ii) *Alıntının kaynakta bulunması*: adayın alıntısı, atıfta bulunduğu segmentin metninde geçmelidir. (iii) *Değerin alıntıda bulunması*: ravi adı gibi, düğümün kimliğini oluşturan bir dizgi değeri adayın alıntılarından birinde geçmelidir. Karşılaştırmalarda Arapça harekeler ve harf varyantları dikkate alınmamaktadır. (ii) ya da (iii) denetiminden geçemeyen aday, güven skoru ne olursa olsun incelemeye yönlendirilmektedir. Denetimden geçememek olgunun yanlış olduğunu göstermediği için aday reddedilmemektedir.

**Kabul kaydı.** İnceleme kararı, inceleyicinin adı, karar zamanı, harcanan süre ve bir düzeltme yapıldıysa önceki ve sonraki değerle birlikte saklanmaktadır. Kararlar eklenmekte ve hiçbir zaman üzerlerine yazılmamaktadır. Daha sonraki doğrulamalar, inceleyicinin karar verdiği bir adayı değiştirmemektedir. Motor, grafa işlenen her olgu için ya insan kararını ya da onu kabul eden otomatik politikayı bildirmektedir.

**İlişki kimliği.** Bir ilişki tipi kimlik özellikleri tanımlayabilmektedir. Zincir ilişkisinde bunlar hadis referansı, zincir numarası ve konumdur. Böylece farklı hadislerde aynı iki ravi arasındaki iki aktarım iki ayrı kenar oluşturmaktadır. Bu ayrım olmadığında ikinci aktarımın ilkinin üzerine yazıldığı gözlemlenmiştir.

**Vaka çalışmasına özgü bileşenler.** Hadise özgü üç bileşen bulunmaktadır: 26 aktarım kalıbından oluşan bir sözlükle zincirin metin aralığını bulup zincir değiştirme işaretinde bölen kural tabanlı bir bölütleyici; kısa çıkarım ipuçları içeren bir şema şablonu (ravi, hadis, "rivayet etti", "aktarır"); bölütleyicinin çıktısını model çağrısı yapmadan adaylara dönüştüren bir sağlayıcı.

# 4 Deney düzeni

**Veri.** Test kümesi, altı temel hadis kitabının her birinden 50 olmak üzere 300 hadis içermektedir. Geliştirme sırasında kullanılan 50 hadisten biriyle metni eşleşen bütün kayıtlar çıkarıldıktan sonra Ifta verilerinden sabit bir rastgelelik tohumu ile örneklem alınmıştır [@internal-data-manifest]. Referans etiketleri platformda işaretlenmiş ravi geçişleridir. Toplam 1.778 geçiş bulunmakta ve hadis başına sayı 2 ile 11 arasında değişmektedir (medyan 6). Hadislerin 74'ü birden çok zincir içermektedir. Etiketler, bağımsız kodlayıcıların etiketlemesi değil, üçüncü bir tarafın yeniden düzenlediği platform işaretlemeleridir. Yer yer tutarsızlıklar bulunmaktadır; derleyicinin yorumundaki raviler bazen işaretlenmiş, bazen işaretlenmemiştir. 300 hadisin 253'ü için Sanadset'te eşleşen bir kayıt bulunmaktadır. Bu kayıtların düzenli ifadelerle üretilmiş etiketleri, gevşek eşleştirmede Ifta etiketleriyle 0,959 F1 düzeyinde uyuşmaktadır (%95 aralık 0,943 ile 0,972).

**Puanlama.** Analiz birimi hadistir. Sistem ve referans geçişleri en büyük ağırlıklı iki parçalı eşleştirmeyle hizalanmıştır. *Katı* eşleştirmede iki geçiş, normalize edilmiş dizgileri eşitse eşleşmektedir. *Gevşek* eşleştirmede ise birinin diğerini içermesi ya da belirteç F1 değerinin en az 0,60 olması da yeterlidir. Kesinlik, duyarlılık ve F1 için mikro ortalama kullanılmıştır. Aralıklar, hadislerin 2.000 kez yeniden örneklenmesiyle elde edilen %95 yüzdelik bootstrap aralıklarıdır. Koşullar arasındaki farklarda eşli yeniden örnekleme kullanılmıştır. Gevşek eşleştirmede bir referans geçişiyle hizalanmayan öneri *eşleşmeyen* olarak adlandırılmıştır. Eşleşmeme, doğrulukla değil, etiketlerin yüzey biçimiyle ilgili bir ifadedir.

**Koşullar.** Bütün koşullar aynı motorda, hiçbir inceleme kararı olmadan çalıştırılmıştır.

| Koşul | Sağlayıcının girdisi | Sağlayıcı | İstem |
|---|---|---|---|
| Kural | Bölütleyiciden gelen zincir metin aralığı | Kural tabanlı, model yok | Yok |
| Şema-only | Hadisin tamamı, tek çağrı | Claude Haiku 5.5 | Tip adları ve çıktı sözleşmesi; açıklamalar çıkarıldı |
| İsnad bilgisi eklenen | Hadisin tamamı, tek çağrı | Claude Haiku 5.5 | Açıklamalar ve ipuçları: adları aynen kopyala, aktarım fiillerini dışarıda bırak, Peygamber ravi değildir |
| İsnad bilgisi eklenen, zincir metin aralığı | Bölütleyiciden gelen zincir metin aralığı | Claude Haiku 5.5 | İsnad bilgisi eklenen koşulla aynı |

Model, yapılandırılmış çıktı vermektedir; çaba parametresi `low` olarak ayarlanmıştır. Yanıtlar içerik adreslemeli bir önbellekte saklanmakta, böylece her koşu yeni çağrı yapmadan yeniden yürütülebilmektedir. Koşularda motorun bellek içi depolaması kullanılmıştır. Aynı boru hattı, PostgreSQL ve Neo4j üzerinde bütünleştirme testleriyle de sınanmaktadır.

# 5 Bulgular

## 5.1 Çıkarım

**Tablo 1.** 300 hadiste ravi geçişleri (1.778 referans geçişi). Gevşek eşleştirmede P, R ve F1; F1 için %95 aralık.

| Koşul | P | R | F1 | Katı F1 | Tam eşleşen zincirler |
|---|---|---|---|---|---|
| Kural | 0,968 | 0,881 | 0,923 [0,910, 0,935] | 0,633 | 0,490 |
| Şema-only | 0,914 | 0,868 | 0,890 [0,865, 0,914] | 0,826 | 0,567 |
| İsnad bilgisi eklenen | 0,997 | 0,919 | 0,956 [0,946, 0,966] | 0,904 | 0,690 |
| İsnad bilgisi eklenen, zincir metin aralığı | 0,998 | 0,903 | 0,948 [0,936, 0,959] | 0,897 | 0,650 |

![Şekil 1. Koşullara göre gevşek kesinlik, duyarlılık ve F1. F1 üzerindeki hata çubukları %95 bootstrap aralıklarıdır.](../figures/fig-7-1-conditions.png)

Gevşek eşleştirmede yalnız şema verilen modelin, kural tabanlı ayrıştırıcının 0,032 F1 altında kaldığı belirlenmiştir (aralık 0,006 ile 0,060). Katı eşleştirmede ise sıralama tersine dönmüş ve değerler 0,633'e karşı 0,826 olarak elde edilmiştir. Ayrıştırıcının doğru adları bulduğu, ancak metin aralıklarının adın sonunu aştığı gözlemlenmiştir. Modelin ise sınırları düzgün adlar döndürdüğü ve bazılarının biçimini değiştirdiği görülmüştür. Yalnız şema içeren isteme açıklama ve ipuçları eklenmesiyle F1 değeri 0,066 (0,041 ile 0,091), kesinlik değeri 0,083 (0,059 ile 0,108) artmıştır. Eşleşmeyen öneri sayısı 145'ten 5'e düşmüştür. Modelin girdisinin zincir metin aralığıyla sınırlanması yarar sağlamamıştır (fark 0,008, aralık −0,002 ile 0,019). 300 hadisten yalnız 10'u birden çok çağrıya bölündüğünden bu koşul, uzun hadislerde zincir başına çağrı yapılmasını sınamamaktadır. Paralel zincirli hadislerde bütün koşulların duyarlılık değerinin düştüğü gözlemlenmiştir. En büyük düşüş ayrıştırıcıda görülmüştür (tek zincirli hadislerde 0,924, diğerlerinde 0,778).

## 5.2 Denetimlerin işaretledikleri

Şema-only koşulda denetime ulaşan bütün alıntılar kendi segmentlerinde bulunmuştur. Alıntı denetimi hiçbir adayı işaretlememiştir. Değerin alıntıda bulunması denetimi, önerilen 1.688 geçişin 155'ini (%9,2) işaretlemiştir.

**Tablo 2.** Şema-only koşul: referansla eşleşme ve değerin alıntıda bulunması denetimine göre öneriler.

| | Eşleşmeyen | Eşleşen |
|---|---|---|
| İşaretlenen | 122 | 33 |
| İşaretlenmeyen | 23 | 1.510 |

İşaretlenen önerilerin %79'unun eşleşmeyen öneriler olduğu ve bunların toplam 145 eşleşmeyen önerinin %84'ünü oluşturduğu belirlenmiştir. Tablo 3'te işaretlenen adlar sabit kurallarla sınıflandırılmıştır.

**Tablo 3.** Değişiklik türüne göre işaretlenen adlar (şema-only koşul).

| Değişiklik türü | Örnek: önce alıntı, sonra ad | İşaretlenen | Eşleşmeyen | Eşleşen |
|---|---|---|---|---|
| Latin harfleriyle çevriyazıya çevrilen | `حَدَّثَنَا الْأَعْمَشُ`, "al-A'mash" | 79 | 79 | 0 |
| Ad hâli değiştirilen | `عَنْ أَبِي بِشْرٍ`, `أَبُو بِشْرٍ` | 34 | 21 | 13 |
| Akrabalık ifadesi yerine ad yazılan | `عَنْ أَبِيهِ` ("babasından"), `عُرْوَةَ` | 25 | 18 | 7 |
| Diğer, ad metnin başka yerinde var | | 7 | 3 | 4 |
| Diğer, ad metinde yok | | 10 | 1 | 9 |

Bu sayıların yorumlanmasında üç noktanın dikkate alınması gerekmektedir. İlk olarak, eşleşmeyen önerilerin çoğu doğru raviyi adlandırmaktadır. Bunların yetmiş dokuzu Latin harfli çevriyazılardır ve tamamı modelin alfabe değiştirdiği 14 hadisten gelmektedir; 21'i ise ad hâli değişikliğidir. Gevşek eşleştirme kuralının belirteç eşiği nedeniyle aynı hâl değişikliği iki sözcüklü bir adda eşleşmezken daha uzun bir adda eşleşmektedir. Denetim de puanlayıcı da yüzey biçimlerini karşılaştırdığından aralarındaki uyumun bir bölümü tasarımdan kaynaklanmaktadır. İkinci olarak, akrabalık örnekleri metnin desteklediği çıkarımlardır; örnekte metin "Hisham ibn Urwa, babasından" ifadesini içermektedir. 25 adın on beşi hadis metninde bulunmaktadır. Metinde hiçbir biçimiyle bulunmayan bir işaretlenmiş ad belirlenmiştir. Üçüncü olarak, denetim kategori hatalarını kapsamamaktadır. Eşleşmeyen on öneri Peygamber'i ravi olarak adlandırmaktadır; denetim Latin harfleriyle yazılan ikisini işaretlemekte, doğru kopyalanmış sekizini kaçırmaktadır.

Denetimin ortaya koyduğu durum, modelin alıntıladığından farklı bir şey yazıp bunu bildirmemesidir. Eşleşmeyen 145 önerinin 102'sinde hadis metninde bulunmayan bir ad bulunmaktadır; bu 102 önerinin tamamı denetim tarafından işaretlenmiştir.

İşaretlenen aday, bir insan karar verene kadar kabul edilmediğinden incelemesiz kabul edilen adayların kesinlik değeri 0,914 yerine 0,985, duyarlılık değeri ise 0,868 yerine 0,849 olarak elde edilmiştir. İnceleyici karar verene kadar grafa daha az veri girmektedir; açık inceleme öğesi bulunan koşu grafa işlenmemektedir. Bu durum nedeniyle 300 hadisin 110'u bekletilmiş ve grafa işlenen çıktının kesinlik değeri 0,983, duyarlılık değeri 0,582 olarak elde edilmiştir.

İsnad bilgisi eklenen koşulda 1.639 önerinin 5'inin eşleşmediği belirlenmiştir. Denetim bunların 3'ünü işaretlemiş, eşleşen hiçbir öneriyi işaretlememiştir.

## 5.3 Güven skoru ile denetimin karşılaştırılması

Şema-only koşulda, modelin güven skorunun önerinin eşleşmesini öngörmede ROC eğrisi altında kalan alanı 0,634 olarak hesaplanmıştır. Modelin yedi ayrı değer kullandığı ve 1.688 önerinin 1.623'ünün güven skorunun 0,8 ile 1,0 arasında olduğu belirlenmiştir.

**Tablo 4.** Güven skoru eşiği ve denetim aracılığıyla incelemeye gönderilen eşleşmeyen öneriler (toplam 145 eşleşmeyen öneri).

| Sinyal | İncelemeye gönderilen öneriler | İçlerindeki eşleşmeyenler |
|---|---|---|
| Güven skoru 0,80'in altında | 65 (%3,9) | 16 |
| Güven skoru 0,85'in altında | 275 (%16,3) | 50 |
| Güven skoru 0,90'ın altında | 1.018 (%60,3) | 110 |
| Değerin alıntıda bulunması denetimi | 155 (%9,2) | 122 |

## 5.4 İnceleme yükü ve maliyet

Şema-only koşulda, 538 aday (155 düğüm ve 383 ilişki) incelemeye gönderilmiş ve 300 hadisin 190'ı incelemesiz grafa işlenmiştir. İsnad bilgisi eklenen koşulda bu sayılar 16 ve 294 olarak elde edilmiştir. Sağlayıcının 6 Ekim 2026 tarihli liste fiyatlarıyla, 1.000 hadis başına çıkarım maliyeti şema-only koşulda 1,87 USD, isnad bilgisi eklenen koşulda 2,29 USD olarak hesaplanmıştır. Çağrı başına medyan gecikme 11 ile 13 saniye arasındadır. Bu makaledeki bütün koşuların maliyeti 3,49 USD olmuştur. İnsan incelemesinin süresi ölçülmemiştir.

## 5.5 İkinci modelle başarısız bir koşu

Aynı aileden daha büyük bir model olan Claude Sonnet 5.5, aynı ayarlarla hadislerin 36'sında çalıştırılmıştır. İsnad bilgisi eklenen koşulda bunların 28'i için tek ravi döndürüldüğü ve genellikle ravi adının özellik anahtarı alanına yazıldığı gözlemlenmiştir. Gevşek duyarlılık değeri, aynı hadislerde Haiku 5.5'in 0,916 değerine karşılık 0,237 olarak elde edilmiştir. Kullanılan yapılandırmada iki olası nedenden kuşkulanılmaktadır: hem liste öğesinin hem özelliğin `name` olarak adlandırıldığı belirsiz bir veri aktarım biçimi ve modeller arasında aynı şekilde kalibre edilmemiş bir akıl yürütme ayarı. Bu olasılıkların ikisi de sınanmamıştır. Bu koşu bir model karşılaştırması değildir. Bununla birlikte, motorun hata durumunda güvenli davrandığını göstermektedir: 29 tanımsız özellik anahtarı inceleme için kaydedilmiş, kimlik değeri bulunmayan düğümler reddedilmiş, 36 koşunun 30'unun grafa işlenmesi engellenmiş ve önerilerin kesinlik değeri 0,966 ya da üzerinde kalmıştır.

## 5.6 Yazılı ad kimlik değildir

Motor, ravi düğümünü yazılı adıyla tanımlamaktadır. Ifta etiketleri her zincir konumuna bir kişi kimliği bağladığından bu tercihin sonucu bir sistem çalıştırılmadan ölçülebilmiştir. 300 hadisteki 2.150 zincir konumunda 740 kişi yer almaktadır. Konumların adın yazıldığı biçime göre gruplanmasıyla 964 grup elde edilmiştir. Bunların 24'ünün birden çok kişiyi kapsadığı ve konumların %10,0'ını içerdiği, kişilerin %25,8'inin ise birden çok gruba bölündüğü belirlenmiştir (ikili kesinlik 0,737, duyarlılık 0,559; B-cubed 0,941 ve 0,715). Adın normalize edilmesiyle bölünme azalmış (%21,8), farklı kişilerin birleştirilmesi artmıştır (konumların %12,2'si). En belirsiz ad, 34 kişiyi temsil eden "babası" akrabalık ifadesidir.

## 5.7 Kimlik kararının saklanması

Ad kimlik değilse, kimin kastedildiğine bir insanın karar vermesi gerekmektedir ve bu kararın saklanması yararlıdır. Etiketli zincirleri her seferinde bir geçiş okuyarak işleyen, daha önce görmediği bir anahtarla karşılaştığında inceleyiciye soran ve daha sonra cevabı yeniden kullanan bir defterin benzetimi yapılmıştır. İnceleyicinin cevabı veri kümesinin etiketidir. İnceleyiciye yöneltilen her öğe soru, yeniden kullanılan ve etiketle uyuşmayan cevap ise sessiz hata olarak değerlendirilmiştir. Veriler, AR-Sanad 280K'nin 27.056 test zincirinden (150.904 geçiş, 6.378 kişi) [@mahmoud2022arsanad] ve başka bir kaynağın etiketleriyle tekrar için, altı Ifta kitabının ravi kimliği taşıyan 34.681 hadisinden (205.514 geçiş) oluşmaktadır. Değerler, beş rastgele sıralamanın ortalamalarıdır.

Belirleyici olan, saklanan kararın kapsamıdır; bu kapsam, cevabın yeniden kullanılabilmesi için sonraki bir geçişin öncekiyle ne kadar ortak bağlam taşıması gerektiğini belirlemektedir. Kapsamı daraltan politikada her ad için başlangıçta yalnız ad kullanılmaktadır. Ancak o ad için bir çelişki görüldükten sonra anahtara addan önce gelen ravi eklenmektedir. Çelişkiyi saptayan mekanizma, ravi kataloğu üzerinde çalışan bir kuraldır. Önerilen kişi ile komşu ravi arasında çok fazla tabaka ya da vefat yılı farkı varsa inceleyiciye sorulmaktadır. Kuralın sınırları AR-Sanad üzerinde seçilmiş ve Ifta verilerine değiştirilmeden uygulanmıştır.

**Tablo 5.** Geçiş başına soru ve sessiz hata.

| Politika | AR-Sanad: sorular | AR-Sanad: sessiz hatalar | Ifta: sorular | Ifta: sessiz hatalar |
|---|---|---|---|---|
| Sabit kapsam: ad | 0,101 | 0,100 | 0,077 | 0,102 |
| Sabit kapsam: ad; kural yalnız işaretlenen geçişi sorar | 0,204 | 0,054 | 0,229 | 0,049 |
| Kuralın daralttığı kapsam | 0,178 | 0,014 | 0,199 | 0,010 |
| Sabit kapsam: önceki ravi ve ad | 0,340 | 0,006 | 0,292 | 0,007 |

Yalnız ada bağlanan kararın on geçişin birinde yanlış yeniden kullanıldığı belirlenmiştir. Kuralın çelişki gördüğü yerlerde kapsamın daraltılmasıyla, dar anahtarın yaklaşık yarısı ile üçte ikisi kadar soruyla onun hata düzeyine yaklaşılmıştır. Aynı kural yalnız işaretlenen geçişi inceleyiciye göndermek için kullanıldığında hata 0,05 dolayında kalmıştır. Yararı sağlayan, tek bir çelişkinin o adın daha sonraki bütün geçişlerinin nasıl ele alınacağını değiştirmesidir. Defter beş Ifta kitabıyla doldurulup altıncı kitapta ölçüm yapıldığında, kapsamı daraltan politikada geçiş başına 0,004 ile 0,016 arasında sessiz hata elde edilmiş ve altı kitabın her birinde dar anahtardan daha az soru sorulmuştur.

Metinden ikinci kez çıkarım yapıldıktan sonra saklanan kararın yeniden bulunabilmesi de gerekmektedir. Hedef olarak hadis ve normalize ad çifti kullanıldığında, bir model koşusundaki ravi adaylarının 0,857 ile 0,977 arasındaki bölümünün farklı bir istemle yapılan koşuda karşılık bulduğu belirlenmiştir. Kural tabanlı ayrıştırıcı ile bir model koşusu arasında ise bu oran 0,561 ile 0,634 arasında elde edilmiştir.

# 6 Tartışma

**Modelin metinden saptığı yer alıntı değildir.** Gerçek metnin gösterilmesi, alıntı gereksinimini karşılamaktadır. Yürütülen koşularda modelin bunu her seferinde yaptığı ve ardından alıntılanan metinde bulunmayan bir değer yazdığı gözlemlenmiştir. Dolayısıyla yalnız alıntıya uygulanan denetim, değer hakkında bir şey söylememektedir. Değerin alıntıyla karşılaştırılması bir ek dizgi karşılaştırması gerektirmektedir ve eşleşen önerileri eşleşmeyenlerden ayıran tek sinyalin bu olduğu belirlenmiştir.

**İşaretlenmek yanlış olmak anlamına gelmemektedir.** İşaretlenen her beş addan birinin referansla eşleştiği, eşleşmeyenlerin çoğunun da doğru kişinin başka biçimde yazılmış adı olduğu görülmüştür. Bu tür bir denetim, adayı reddetmek yerine bir insana ya da açık bir kurala yönlendirmelidir. Ad hâli değişikliklerini kabul edip bunu kaydeden bir kuralın, işaretlenen 33 eşleşen adın 13'ünü inceleme gereğinden kurtarması mümkündür.

**Talimatların denetimlerden daha etkili olduğu, denetimlerin ise talimatlar başarısız olduğunda gerekli olduğu görülmüştür.** Birkaç kısa ipucu ve tip açıklamalarıyla, eşleşmeyen önerilerin neredeyse tamamı ortadan kaldırılmıştır. Bu sayı, herhangi bir denetimin belirlediğinden fazladır. Başarısız koşunun gösterdiği gibi, denetimler istemin, modelin ya da yapılandırmanın yanlış olduğu durumlarda işlev görmektedir.

**Katı kabul politikası işi inceleyiciye aktarmaktadır.** Bir aday inceleme beklerken hadisin tamamının grafın dışında tutulması grafı korumakta ve eksik bırakmaktadır; şema-only koşulda, herhangi bir inceleme öncesindeki duyarlılık değeri 0,582'dir. Tasarımın başarısı, ölçülmemiş olan inceleme adımının başarısına bağlıdır.

**Saklanan şey karardır.** Çıkarımın adayları değiştirilebilmekte, aynı metin başka bir istemle ya da modelle yeniden okunabilmektedir. Ravinin kimliği ve bir olgunun kabulü metinde bulunmamaktadır. Benzetim, bu kararların sık yeniden kullanıldığını, yalnız ada göre yeniden kullanımın güvenli olmadığını ve düşük maliyetli bir kural çelişki bulana kadar kararın kapsamının geniş tutulabileceğini düşündürmektedir. Motor bunu henüz yapmamaktadır; kararı bir adaya bağlamakta ve tarih kuralı içermemektedir.

# 7 Sınırlılıklar

Referans, bağımsız kodlayıcıların oluşturduğu altın standart değil, platform işaretlemesidir; mutlak puanlar doğruluk olarak okunmamalıdır. Değerin alıntıda bulunması denetiminin eşleşmeyen önerilerin ne kadarını işaretlediği, bu göreve ve isteme özgüdür. İnsan etiketli BC5CDR derleminin 300 özetinde [@li2016bc5cdr], aynı model ve yalnız şema içeren bir istemle, denetim 2.269 önerinin %3,9'unu işaretlemiştir. Bunların, etiketlerle eşleşmeyen 303 önerinin 53'ünü içerdiği; modelin güven skorunun ise aynı inceleme payında 58'ini bulduğu belirlenmiştir. Buradaki eşleşmeyen önerilerin çoğu, kodlayıcıların etiketlemediği metin aralıklarının aynen kopyalarıdır. Hiçbir inceleyici katılmadığından döngünün insan kısmı uygulanmış ve test edilmiş, ancak değerlendirilmemiştir. Karar defteri benzetiminde inceleyici veri kümesinin etiketidir: ilk cevap ücretsiz ve her zaman doğrudur, soru ne kadar zaman alacak olursa olsun bir birim sayılmaktadır ve altı kitabın ravilerinin çoğu ortaktır. Kullanılabilir bütün sonuçlar tek modelden, tek ayardan ve koşul başına tek koşudan elde edilmiştir. Eşleşmeyen öneri mutlaka yanlış bir ifade değildir. İlişkiler değil, ravi geçişleri puanlanmıştır. Hadisler iyi bilinmektedir ve muhtemelen modelin eğitim verisinde bulunmaktadır; adlar değiştirilerek ezberleme sınanmamıştır. Tip ve özellik denetimlerinin geliştirilmesine yol açan şema sapması, çalışan modelde neredeyse hiç görülmediğinden normal kullanım sıklığı belirlenememiştir. Kural tabanlı bölütleyici, test kümesinin dışında tutulan 50 hadiste ayarlanmıştır.

# 8 Sonuç

Çalışan bir çıkarım motorunda, daha önce görülmemiş 300 hadis üzerinde, değerin alıntıda bulunması denetimi, yetersiz talimat verilmiş modelin referansla eşleşmeyen önerilerinin çoğunu işaretlemiştir. Alıntının kaynakta bulunması denetimi hiçbirini işaretlememiş; modelin güven skoru ise aynı inceleme bütçesinde çok daha azını bulmuştur. Denetimin belirledikleri çoğunlukla doğru adların kaydedilmemiş dönüşümleridir. Daha iyi talimatlarla bu modelde sorun neredeyse ortadan kaldırılmıştır. Benzetimde, kapsamı çelişki görüldüğünde daralan bir kimlik kararıyla, daha az soruyla dar anahtarın hata düzeyine yaklaşılmıştır. Sonraki adımlar kapsamında insan etiketli bir referans oluşturulması, inceleme süresi ölçülerek bir inceleyicinin döngüye katılması, defterin bu inceleyicinin kararlarıyla yeniden sınanması, daha fazla model kullanılması, ilişki düzeyinde puanlama yapılması ve ravi adlarının bir otorite listesine bağlanması planlanmaktadır.

# Yapay zekâ araçlarının kullanımına ilişkin beyan

Yapay zekâ asistanları tarafından, yazarların yönlendirmesiyle değerlendirilen sistemin kodunun büyük kısmı, analiz betikleri ve bu metnin ilk taslağı yazılmıştır. Kaynakça kayıtları dizinlerden ya da yayıncı sayfalarından alınmıştır. Ölçülen her sayı, saklanan model yanıtlarından bir betikle üretilmektedir. Bir taslak, bağımsız bir yapay zekâ inceleyicisi tarafından sonuç dosyalarıyla karşılaştırılmış ve dosyaların desteklemediği yerlerde iddialar daraltılmıştır. İçeriğin sorumluluğu yazarlara aittir.

# Veri ve kod

Kod, değerlendirme betikleri, önbelleğe alınmış model yanıtları ve sonuç dosyaları proje deposundadır. Depo geliştirme süresince özeldir; proje sonunda motorun açık kaynak lisansıyla yayımlanması planlanmaktadır. Hadis verileri üçüncü taraf kaynaklardan gelmekte ve yalnız değerlendirme için kullanılmaktadır. Veri envanteri, her kaynağı, kaynağın kendi lisans beyanıyla birlikte listelemektedir [@internal-data-manifest].
