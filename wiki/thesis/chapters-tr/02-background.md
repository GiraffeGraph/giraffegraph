# 2 Arka plan

Bu bölümde vaka çalışmasının alanını ve tezin geri kalanının dayandığı kavramları tanıtıyoruz.

## 2.1 Hadis, isnad ve metin

Hadis iki parçadan oluşan bir rivayettir. İsnad (إسناد), rivayetin aktarıldığı ravilerin zinciridir; metin (متن) ise rivayet edilen sözün kendisidir. Bazı kaynaklar ve veri kümesi adları aynı zincir için sened sözcüğünü kullanır. Bundan sonra isnad için "zincir", metin için "rivayet metni" yazıyoruz.

Zincir, kitabı derleyen kişiden başlayarak yazılır ve Hz. Muhammad'e ya da ilk ravi kuşağı olan sahabilerinden birine kadar geriye gider. Zincirde adı geçen her ravi, rivayeti kendisinden sonra adı geçen raviden almıştır. Örneğin Sanadset derleminde al-Nasai'nin kitabındaki 693 numaralı hadis için etiketlenen zincirde beş ravi vardır: Muhammad ibn Mansur, Sufyan, al-Zuhri, Sa'id ve Abu Hurayra [@mghari2022sanadset].

Raviler, aktarım kalıplarıyla (sigha, صيغة) birbirine bağlanır. Yaygın kalıplar arasında haddathana ("bize rivayet etti"), akhbarana ("bize haber verdi"), sami'tu ("işittim") ve 'an (عن, "-den") vardır. Kalıp, rivayetin bir raviden diğerine nasıl geçtiğini belirtir; 'an ise bunu açık bırakır. Bu yüzden graf modeli, kalıbı iki ravi arasındaki ilişkinin bir özelliği olarak tutar.

Bir hadis, derleyiciye birden çok zincir üzerinden ulaşabilir. Bu paralel zincirler art arda yazıldığında, tahvil (تحويل) denen ح harfi yeni bir zincire geçişi belirtir; buna zincir geçiş işareti diyoruz. Altı temel hadis kitabından seçtiğimiz 300 hadislik örneklemde, kaynak etiketlerine göre 74 hadisin birden çok zinciri vardır [@internal-data-manifest]. Bir hadisin zincirleri ayrı tutulmazsa grafta hiçbir zincirin belirtmediği aktarım yolları oluşur.

Zor olan ravi kimliğidir. Aynı kişi "Sufyan ibn Uyayna", "Ibn Uyayna" ya da "Sufyan" olarak geçebilir; farklı kişiler de aynı kısa adı paylaşabilir. Yukarıdaki zincirde metin, hangi Sufyan'ın ya da hangi Sa'id'in kastedildiğini söylemez. "Babasından, dedesinden" gibi bazı zincirlerde hiç kimsenin adı verilmez.

Her adın bir ravi kimliği taşıdığı AR-Sanad test kümesindeki 27.056 gerçek zincirde, 15.301 farklı ad dizgisinin 815'i birden çok kimliğe karşılık gelir. Muhammad adı 27 raviye, "babası" ifadesi ise 421 raviye karşılık gelir [@mahmoud2022arsanad; @internal-data-manifest].

Kimlik gereklidir; çünkü zincir, ravileri üzerinden değerlendirilir. Rical (رجال) denen ravi biyografisi literatürü, her ravinin kim olduğunu ve âlimlerin onu ne kadar güvenilir bulduğunu kaydeder. Kuşaklara göre düzenlenmiş eserler bu literatürün bir parçasıdır [@aslan2017tabakat]. Kullandığımız veri kümeleri, tabaka ve Ibn Hajar ile al-Dhahabi'ye atfedilen güvenilirlik dereceleri gibi bu geleneğe ait alanlar taşır [@internal-data-manifest]. İki farklı raviyi tek düğümde birleştirmek zincir hakkındaki hükmü değiştirebilir; birleştirmenin atlanması ise yalnızca yinelenen bir düğüm bırakır. Metin tek başına bu durumları çözemez; bunlar için ravilerin yetkili bir kimlik listesine ve bir uzmana ihtiyaç vardır.

Altı temel hadis kitabı (Türkçede Kütüb-i Sitte), al-Bukhari, Muslim, Abu Dawud, al-Tirmidhi, al-Nasai ve Ibn Majah'ın kitaplarıdır. Eleştirel bir derleme, değerlendirme ölçütlerinin bu altı kitaba dar biçimde odaklanmasını alanın zayıflıkları arasında sayar [@haque2026hadith].

## 2.2 Bilgi grafları ve şemayla sınırlandırılmış çıkarım

Bilgi grafıyla, tipli ilişkilerle birbirine bağlanmış tipli düğümler kümesini kastediyoruz; düğümler ve ilişkiler özellik taşır. Kavrama ve alana özgü graf kurulumuna ilişkin derlemeler [@hogan2021knowledge; @kejriwal2019domain] kaynaklarında bulunabilir. Şema, hangi düğüm tiplerine, ilişki tiplerine ve özelliklere izin verildiğini belirler. Ravi zincirleri için bir şemada az sayıda öğe yeterlidir: ravi düğümü, hadis düğümü ve hadis referansını, zincir numarasını, zincirdeki konumu ve aktarım kalıbını taşıyan bir "-den rivayet etti" ilişkisi.

Graf bu alana uygundur; çünkü zincirler hakkındaki sorular yol ve ağ sorularıdır. İki zincirin ortak ravisi herhangi bir tek metin parçasında yazmaz; onu bulmak için her iki zinciri de dolaşmak gerekir.

Büyük dil modelleri (BDM), metinden bu tür graflar kurabilir [@ye2022generative; @pan2024unifying]. İki strateji vardır. Önce şemanın belirlendiği çıkarımda model, izin verilen tipleri ve bir çıktı sözleşmesini alır; çıktısı şemaya göre doğrulanır. İkinci stratejide model serbestçe çıkarım yapar, sonraki bir adım ise ürettiklerini tanımlar ve kanonikleştirir. Extract, Define, Canonicalize çerçevesi buna örnektir [@zhang2024edc]. Bu yaklaşım önceden şema gerektirmez. Bizim değerlendirmemize göre bunun bedeli ikinci bir geçiştir; kanonikleştirme de hataların oluşabileceği bir adım daha ekler.

## 2.3 İki hata türü: kaynağın desteklemediği olgular ve şema sapması

Projenin başlığı iki hata türünü adlandırır. Şema sapması, çıktının şemada tanımlanmayan tipler ya da özellikler kullanmasıdır. Aynı ilişki bir grupta HEARD_FROM, sonraki grupta TOLD ya da narratedBy olarak adlandırılabilir. Tip düzeyinde model, tanımsız bir düğüm ya da ilişki tipi yazar. Özellik düzeyinde ise tanımsız bir özellik anahtarı ya da izin verilen listenin dışında bir değer yazar.

Halüsinasyon, kaynağın desteklemediği üretilmiş içerik için kullanılan yaygın addır. Ji ve arkadaşları, doğal dil üretimindeki halüsinasyonları derler [@ji2023survey]. Bu derleme, bilgi grafı çıkarımını bir görev olarak ele almaz; dolayısıyla verdiği sayılar bizim düzenimize aktarılamaz. Biz daha yalın olan "kaynağın desteklemediği olgu" terimini kullanıyoruz.

Tek bir "halüsinasyon oranı", çıkarım için fazla genel kalır; çünkü bu başlık altında en az üç farklı durum sayılır:

- **Değer kaynakta yoktur.** Çıkarılan değer, örneğin bir ravi adı, kaynak metinde hiç geçmez.
- **Değer modelin kendi alıntısında yoktur.** Model, kaynakta gerçekten geçen bir parçayı alıntılar; ancak bildirdiği değer o parçada geçmez. Bu durum, gerçek hataları ve sessiz normalizasyonu kapsar. Örneğin metinde belirtme hâlinde bulunan bir ad, yalın hâlde döndürülmüş olabilir. İkinci durumda model, hiçbir yerde kaydedilmeyen bir karar vermiştir.
- **Kategori hatası.** Değer metinde geçer ve tip şemada vardır; ancak çıkarılan öğe o tipe ait değildir. Örneğin Peygamber'in ravi olarak çıkarılması böyledir.

Bu üç sınıfı farklı kontroller yakalar; bu yüzden Bölüm 7.6'da ayrı ayrı raporluyoruz. Text2KGBench, metinde bulunmanın neden doğru olmakla aynı şey olmadığını gösterir. Halüsinasyon ölçüsü, bir üçlünün öznesinin ya da nesnesinin cümlede veya ontolojide bulunup bulunmadığını sınar. Değerlendirme ölçütünün Wikidata-TekGen bölümünde Vicuna-13B ile özne halüsinasyonu 0,17 iken referans üçlülere karşı precision 0,38 olmuştur [@mihindukulasooriya2023text2kgbench].

## 2.4 Kaynağa dayandırma ve kaynakla ilişkilendirme

Kaynağa dayandırma, her çıktıyı kaynaktaki kanıta bağlar. İki yöntem ailesi burada ilgilidir.

Alıntı tabanlı kontroller, modelden her aday olguyla birlikte birebir alıntı döndürmesini ister ve ardından dizgi testleri uygular: alıntı kaynak segmentte geçiyor mu, çıkarılan değer alıntıda geçiyor mu? Bu testler deterministiktir, maliyetleri yok denecek kadar azdır ve her adayda çalıştırılabilir. Bir şeyin yanlış olduğunu gösterebilirler; adayın doğru olduğunu gösteremezler.

İddia düzeyindeki yöntemler, serbest metnin değerlendirilmesinden gelir. FActScore, uzun bir yanıtı atomik iddialara ayırıp her birini doğrular; SAFE de uzun metinlerin olgusal doğruluğunu benzer biçimde ele alır [@min2023factscore; @wei2024longform]. Rashkin ve arkadaşları, üretilen metnin belirlenmiş kaynaklara dayandırılabilirliğinin nasıl ölçüleceğini tanımlar [@rashkin2023measuring]. SummaC ve AlignScore, çıkarımsal gerektirme ya da hizalama modelleri kullanarak bir iddianın bir metinle tutarlılığını puanlar [@laban2022summac; @zha2023alignscore]. RARR ve Chain-of-Verification, çıktıyı düzeltmek ya da doğrulamak için ek model çağrıları kullanır [@gao2023rarr; @dhuliawala2024chainofverification]. Bu yöntemler cümle ya da iddia düzeyinde çalışır; otomatik olanlar öğe başına en az bir model çağrısı gerektirir. Ravi adı gibi kısa, yapılandırılmış bir değer için dizgi testleri daha ucuz bir ilk adımdır. Anlamı değerlendiremedikleri için ardından bir insan adımı gelir.

## 2.5 İnsan-döngülü inceleme ve yönlendirme sinyali olarak güven skoru

İnsan-döngülü tasarımda bir insan, aday olgular grafa yazılmadan önce onlar hakkında karar verir. Uzman zamanı kıt kaynaktır; bu yüzden sistemin, insanın görmesi gereken adayları seçen bir yönlendirme sinyaline ihtiyacı vardır.

İlk akla gelen sinyal, modelin kendi çıktısı için bildirdiği güven skorunu bir eşikle karşılaştırmaktır. Modelin bildirdiği bu güven skorunun doğrulukla örtüşüp örtüşmediği, kalibrasyon problemi olarak incelenir [@kadavath2022language; @xiong2024can]. Hadis alanı, eğitilmiş bir sınıflandırıcıda bile ihtiyat gerektirir: Mahmoud ve arkadaşları, ravi tanıma modellerinin yanlış tahminlerinin %12,9'unun 0,90'ın üzerinde güven skoruyla yapıldığını bildirir [@mahmoud2022arsanad]. Bölüm 2.6'da ele aldığımız deneme yazısı, modelin hatalarının dışarıdan doğru çıktısına benzediğini savunur [@internal-cache-ledger].

İki alternatif vardır. Bölüm 2.4'teki bir testin başarısız olması gibi deterministik risk işaretleri, modelin kendisi hakkındaki değerlendirmesini kullanmadan adayı incelemeye yönlendirebilir. Konformal tahmin, bir kalibrasyon kümesi bulunduğunda dağılımdan bağımsız hata güvenceleri sunar [@angelopoulos2021gentle]. Sinyal ne olursa olsun, iki yönlendirme politikası ancak aynı kapsama oranında karşılaştırılabilir. Raja, seçici yanıt sunmanın hata oranlarını bu şekilde karşılaştırır [@raja2026grading]. Bölüm 7.7'de güven skoru sinyalini bir kontrolle, incelemeye gönderilen geçişlerin karşılaştırılabilir paylarında karşılaştırıyoruz.

## 2.6 Türetilebilir olgular ve kararlar

Son kavram, projenin "The Cache and the Ledger" adlı iç deneme yazısından gelir [@internal-cache-ledger]. İlkesi şudur: doğruluğun esas alındığı bir kaynaktan türetilebilen olgu önbellektir ve saklanmak yerine yeniden üretilmelidir; türetilemeyen olgu ise karardır ve bir kez saklanmalıdır.

Deneme yazısının örneği bir belgelendirme sayfasıdır. "Denetleyici bu dosyadadır" bilgisi koddan yeniden elde edilebilir. "Başka bir tasarımı düşündük ve reddettik" bilgisi ise elde edilemez; çünkü kod, seçilmeyen seçeneği içermez.

Deneme yazısı, ilkeyi kendi betiklerinin yeniden ürettiği sayımlarla destekler. 733 Python Enhancement Proposals belgesi içinde, bir linter başlığı kontrol ettiği hâlde 42 ileri yönlü "replaces" bağlantısının 27'sine geri bağlantı verilmiştir (%64). Yazı, saklanan türetilebilir değerlerin zamanla bozulduğu, geri bağlantıları türetilen ve yalnızca yeni kayıt eklenen karar kayıtlarının ise tasarımları gereği bu sorunu önlediği sonucuna varır. Sınırları da belirtir: kararların yerleşik bir sağlama toplamı yoktur ve otomatik bir kontrol problemi işaretleyebilir, ancak bir ifadenin doğru olduğunu onaylayamaz.

Çıkarıma uyguladığımızda: ayrıştırıcının ya da modelin metinden çıkardığı aday olgu türetilebilirdir; çünkü model her seferinde aynı çıktıyı vermese de aynı metinden yeniden çıkarılabilir. Bir insanın kabulü, reddi, düzeltmesi ya da iki raviyi birleştirmesi ise hiçbir kaynaktan türetilemez; kimin, ne zaman karar verdiğiyle birlikte bir kez kaydedilmelidir. Sistem bu yüzden her olgu için kararların izini tutar.

Bu ilke, Bölüm 2.3'teki ikinci sınıfı da açıklar. Modelin sessizce normalize ettiği bir değer, ne metinden doğrudan türetilmiş bir değerdir ne de kaydedilmiş bir insan kararıdır. Kabul edilmeden önce adı kayıtlı bir kural ya da bir insan tarafından doğrulanmalıdır.

<!-- keys: mghari2022sanadset, internal-data-manifest, mahmoud2022arsanad, aslan2017tabakat, haque2026hadith, hogan2021knowledge, kejriwal2019domain, ye2022generative, pan2024unifying, zhang2024edc, ji2023survey, mihindukulasooriya2023text2kgbench, min2023factscore, wei2024longform, rashkin2023measuring, laban2022summac, zha2023alignscore, gao2023rarr, dhuliawala2024chainofverification, kadavath2022language, xiong2024can, internal-cache-ledger, angelopoulos2021gentle, raja2026grading -->
