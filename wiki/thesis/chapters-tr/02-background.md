# 2 Arka plan

Bu bölümde vaka çalışmasının alanı ve tezin geri kalanının dayandığı kavramlar tanıtılmaktadır.

## 2.1 Hadis, isnad ve metin

Hadis, iki parçadan oluşan bir rivayettir. İsnad (إسناد), rivayetin aktarıldığı ravilerin zinciri; metin (متن) ise rivayet edilen sözün kendisidir. Bazı kaynaklarda ve veri kümesi adlarında aynı zincir için sened sözcüğü kullanılmaktadır. Bu bölümden itibaren isnad için "zincir", metin için "rivayet metni" ifadeleri kullanılmaktadır.

Zincir, kitabı derleyen kişiden başlayarak yazılmakta ve Hz. Muhammad'e ya da ilk ravi kuşağı olan sahabilerinden birine kadar geriye gitmektedir. Zincirde adı geçen her ravi, rivayeti kendisinden sonra adı geçen raviden almıştır. Örneğin Sanadset derleminde al-Nasai'nin kitabındaki 693 numaralı hadis için etiketlenen zincirde beş ravi bulunmaktadır: Muhammad ibn Mansur, Sufyan, al-Zuhri, Sa'id ve Abu Hurayra [@mghari2022sanadset].

Raviler, aktarım kalıplarıyla (sigha, صيغة) birbirine bağlanmaktadır. Yaygın kalıplar arasında haddathana ("bize rivayet etti"), akhbarana ("bize haber verdi"), sami'tu ("işittim") ve 'an (عن, "-den") bulunmaktadır. Kalıp, rivayetin bir raviden diğerine nasıl geçtiğini belirtmekte; 'an ise bunu açık bırakmaktadır. Bu nedenle graf modelinde kalıp, iki ravi arasındaki ilişkinin bir özelliği olarak tutulmaktadır.

Bir hadis, derleyiciye birden çok zincir üzerinden ulaşabilmektedir. Bu paralel zincirler art arda yazıldığında, tahvil (تحويل) denen ح harfi yeni bir zincire geçişi belirtmektedir; bu harf, zincir geçiş işareti olarak adlandırılmaktadır. Altı temel hadis kitabından seçilen 300 hadislik örneklemde, kaynak etiketlerine göre 74 hadisin birden çok zinciri bulunmaktadır [@internal-data-manifest]. Bir hadisin zincirleri ayrı tutulmadığında grafta hiçbir zincirin belirtmediği aktarım yolları oluşmaktadır.

Güçlük, ravi kimliğinin belirlenmesindedir. Aynı kişi "Sufyan ibn Uyayna", "Ibn Uyayna" ya da "Sufyan" olarak geçebilmekte; farklı kişiler de aynı kısa adı paylaşabilmektedir. Yukarıdaki zincirde metin, hangi Sufyan'ın ya da hangi Sa'id'in kastedildiğini belirtmemektedir. "Babasından, dedesinden" gibi bazı zincirlerde ise hiç kimsenin adı verilmemektedir.

Her adın bir ravi kimliği taşıdığı AR-Sanad test kümesindeki 27.056 gerçek zincirde, 15.301 farklı ad dizgisinin 815'i birden çok kimliğe karşılık gelmektedir. Muhammad adı 27 raviye, "babası" ifadesi ise 421 raviye karşılık gelmektedir [@mahmoud2022arsanad; @internal-data-manifest].

Zincir ravileri üzerinden değerlendirildiğinden kimlik gereklidir. Rical (رجال) denen ravi biyografisi literatüründe, her ravinin kim olduğu ve âlimler tarafından ne kadar güvenilir bulunduğu kaydedilmektedir. Kuşaklara göre düzenlenmiş eserler bu literatürün bir parçasıdır [@aslan2017tabakat]. Kullanılan veri kümeleri, tabaka ve Ibn Hajar ile al-Dhahabi'ye atfedilen güvenilirlik dereceleri gibi bu geleneğe ait alanlar taşımaktadır [@internal-data-manifest]. İki farklı ravinin tek düğümde birleştirilmesi zincir hakkındaki hükmü değiştirebilmekte; birleştirmenin atlanması ise yalnızca yinelenen bir düğüm bırakmaktadır. Metin tek başına bu durumları çözemediğinden, raviler için yetkili bir kimlik listesine ve bir uzmana ihtiyaç duyulmaktadır.

Altı temel hadis kitabı (Türkçede Kütüb-i Sitte), al-Bukhari, Muslim, Abu Dawud, al-Tirmidhi, al-Nasai ve Ibn Majah'ın kitaplarıdır. Eleştirel bir derlemede, değerlendirme ölçütlerinin bu altı kitaba dar biçimde odaklanması alanın zayıflıkları arasında sayılmaktadır [@haque2026hadith].

## 2.2 Bilgi grafları ve şemayla sınırlandırılmış çıkarım

Bilgi grafı, tipli ilişkilerle birbirine bağlanmış tipli düğümler kümesi olarak ele alınmaktadır; düğümler ve ilişkiler özellik taşımaktadır. Kavrama ve alana özgü graf kurulumuna ilişkin derlemeler [@hogan2021knowledge; @kejriwal2019domain] kaynaklarında bulunabilmektedir. Şema, hangi düğüm tiplerine, ilişki tiplerine ve özelliklere izin verildiğini belirlemektedir. Ravi zincirleri için bir şemada az sayıda öğe yeterlidir: ravi düğümü, hadis düğümü ve hadis referansını, zincir numarasını, zincirdeki konumu ve aktarım kalıbını taşıyan bir "-den rivayet etti" ilişkisi.

Zincirler hakkındaki sorular yol ve ağ soruları olduğundan graf bu alana uygundur. İki zincirin ortak ravisi herhangi bir tek metin parçasında yazılmamakta; bu ravinin bulunması için her iki zincirin de dolaşılması gerekmektedir.

Büyük dil modelleri (BDM), metinden bu tür graflar kurabilmektedir [@ye2022generative; @pan2024unifying]. Bu kapsamda iki strateji bulunmaktadır. Önce şemanın belirlendiği çıkarımda modele izin verilen tipler ve bir çıktı sözleşmesi verilmekte, çıktısı şemaya göre doğrulanmaktadır. İkinci stratejide model serbestçe çıkarım yapmakta, sonraki bir adımda ise ürettikleri tanımlanmakta ve kanonikleştirilmektedir. Extract, Define, Canonicalize çerçevesi buna örnektir [@zhang2024edc]. Bu yaklaşım, önceden şema gerektirmemektedir. Çalışma kapsamında yapılan değerlendirmeye göre bunun bedeli ikinci bir geçiştir; kanonikleştirme de hataların oluşabileceği bir adım daha eklemektedir.

## 2.3 İki hata türü: kaynağın desteklemediği olgular ve şema sapması

Projenin başlığında iki hata türü adlandırılmaktadır. Şema sapması, çıktının şemada tanımlanmayan tipler ya da özellikler kullanmasıdır. Aynı ilişki bir grupta HEARD_FROM, sonraki grupta TOLD ya da narratedBy olarak adlandırılabilmektedir. Tip düzeyinde model, tanımsız bir düğüm ya da ilişki tipi yazmaktadır. Özellik düzeyinde ise tanımsız bir özellik anahtarı ya da izin verilen listenin dışında bir değer üretmektedir.

Halüsinasyon, kaynağın desteklemediği üretilmiş içerik için kullanılan yaygın addır. Ji ve arkadaşları, doğal dil üretimindeki halüsinasyonları derlemektedir [@ji2023survey]. Bu derlemede bilgi grafı çıkarımı bir görev olarak ele alınmadığından, verilen sayılar bu çalışmanın düzenine aktarılamamaktadır. Bu çalışmada daha yalın olan "kaynağın desteklemediği olgu" terimi kullanılmaktadır.

Tek bir "halüsinasyon oranı", bu başlık altında en az üç farklı durum sayıldığından çıkarım için fazla genel kalmaktadır:

- **Değer kaynakta yoktur.** Çıkarılan değer, örneğin bir ravi adı, kaynak metinde hiç geçmemektedir.
- **Değer modelin kendi alıntısında yoktur.** Model, kaynakta gerçekten geçen bir parçayı alıntılamakta; ancak bildirdiği değer o parçada geçmemektedir. Bu durum, gerçek hataları ve sessiz normalizasyonu kapsamaktadır. Örneğin metinde belirtme hâlinde bulunan bir ad, yalın hâlde döndürülmüş olabilmektedir. İkinci durumda model, hiçbir yerde kaydedilmeyen bir karar vermiştir.
- **Kategori hatası.** Değer metinde geçmekte ve tip şemada bulunmakta; ancak çıkarılan öğe o tipe ait olmamaktadır. Peygamber'in ravi olarak çıkarılması buna örnektir.

Bu üç sınıf farklı denetimlerle yakalandığından, Bölüm 7.6'da ayrı ayrı raporlanmaktadır. Text2KGBench, metinde bulunmanın neden doğru olmakla aynı şey olmadığını göstermektedir. Halüsinasyon ölçüsü, bir üçlünün öznesinin ya da nesnesinin cümlede veya ontolojide bulunup bulunmadığını sınamaktadır. Değerlendirme ölçütünün Wikidata-TekGen bölümünde Vicuna-13B ile özne halüsinasyonu 0,17 iken referans üçlülere karşı kesinlik (precision) 0,38 olmuştur [@mihindukulasooriya2023text2kgbench].

## 2.4 Kaynağa dayandırma ve kaynakla ilişkilendirme

Kaynağa dayandırma, her çıktıyı kaynaktaki kanıta bağlamaktadır. Bu kapsamda iki yöntem ailesi ele alınmaktadır.

Alıntı tabanlı denetimlerde, modelden her aday olguyla birlikte birebir alıntı döndürmesi istenmekte; ardından alıntının kaynak segmentte ve çıkarılan değerin alıntıda bulunup bulunmadığını sınayan dizgi testleri uygulanmaktadır. Bu testler deterministiktir, maliyetleri yok denecek kadar azdır ve her adayda çalıştırılabilmektedir. Bir şeyin yanlış olduğunu gösterebilmekte, ancak adayın doğru olduğunu gösterememektedir.

İddia düzeyindeki yöntemler, serbest metnin değerlendirilmesine dayanmaktadır. FActScore, uzun bir yanıtı atomik iddialara ayırarak her birini doğrulamakta; SAFE de uzun metinlerin olgusal doğruluğunu benzer biçimde ele almaktadır [@min2023factscore; @wei2024longform]. Rashkin ve arkadaşları, üretilen metnin belirlenmiş kaynaklara dayandırılabilirliğinin nasıl ölçüleceğini tanımlamaktadır [@rashkin2023measuring]. SummaC ve AlignScore, çıkarımsal gerektirme ya da hizalama modelleri kullanarak bir iddianın bir metinle tutarlılığını puanlamaktadır [@laban2022summac; @zha2023alignscore]. RARR ve Chain-of-Verification, çıktıyı düzeltmek ya da doğrulamak için ek model çağrıları kullanmaktadır [@gao2023rarr; @dhuliawala2024chainofverification]. Bu yöntemler cümle ya da iddia düzeyinde çalışmakta; otomatik olanlar öğe başına en az bir model çağrısı gerektirmektedir. Ravi adı gibi kısa ve yapılandırılmış bir değer için dizgi testleri daha ucuz bir ilk adımdır. Anlamı değerlendiremediklerinden, bu testleri bir insan adımı izlemektedir.

## 2.5 İnsan-döngülü inceleme ve yönlendirme sinyali olarak güven skoru

İnsan-döngülü tasarımda, aday olgular grafa yazılmadan önce bir insan tarafından bu olgular hakkında karar verilmektedir. Uzman zamanı kıt kaynak olduğundan, sistemin insanın görmesi gereken adayları seçen bir yönlendirme sinyaline ihtiyacı bulunmaktadır.

İlk akla gelen sinyal, modelin kendi çıktısı için bildirdiği güven skorunun bir eşikle karşılaştırılmasıdır. Modelin bildirdiği bu güven skorunun doğrulukla örtüşüp örtüşmediği, kalibrasyon problemi olarak incelenmektedir [@kadavath2022language; @xiong2024can]. Hadis alanında, eğitilmiş bir sınıflandırıcıda bile ihtiyat gerekmektedir: Mahmoud ve arkadaşları, ravi tanıma modellerinin yanlış tahminlerinin %12,9'unun 0,90'ın üzerinde güven skoruyla yapıldığını bildirmektedir [@mahmoud2022arsanad]. Bölüm 2.6'da ele alınan deneme yazısında, modelin hatalarının dışarıdan doğru çıktısına benzediği savunulmaktadır [@internal-cache-ledger].

İki alternatif bulunmaktadır. Bölüm 2.4'teki bir testin başarısız olması gibi deterministik risk işaretleri, modelin kendisi hakkındaki değerlendirmesi kullanılmadan adayı incelemeye yönlendirebilmektedir. Konformal tahmin, bir kalibrasyon kümesi bulunduğunda dağılımdan bağımsız hata güvenceleri sunmaktadır [@angelopoulos2021gentle]. Sinyal ne olursa olsun, iki yönlendirme politikası ancak aynı kapsama oranında karşılaştırılabilmektedir. Raja, seçici yanıt sunmanın hata oranlarını bu şekilde karşılaştırmaktadır [@raja2026grading]. Bölüm 7.7'de güven skoru sinyali bir denetimle, incelemeye gönderilen geçişlerin karşılaştırılabilir paylarında karşılaştırılmaktadır.

## 2.6 Türetilebilir olgular ve kararlar

Son kavram, projenin "The Cache and the Ledger" adlı iç deneme yazısına dayanmaktadır [@internal-cache-ledger]. Bu yazının ilkesine göre, doğruluğun esas alındığı bir kaynaktan türetilebilen olgu önbellektir ve saklanmak yerine yeniden üretilmelidir; türetilemeyen olgu ise karardır ve bir kez saklanmalıdır.

Deneme yazısında örnek olarak bir belgelendirme sayfası kullanılmaktadır. "Denetleyici bu dosyadadır" bilgisi koddan yeniden elde edilebilmektedir. "Başka bir tasarım değerlendirildi ve reddedildi" bilgisi ise kod seçilmeyen seçeneği içermediğinden elde edilememektedir.

Deneme yazısında ilke, yazıya ait betiklerin yeniden ürettiği sayımlarla desteklenmektedir. 733 Python Enhancement Proposals belgesi içinde, bir linter başlığı kontrol ettiği hâlde 42 ileri yönlü "replaces" bağlantısının 27'sine geri bağlantı verilmiştir (%64). Yazıda, saklanan türetilebilir değerlerin zamanla bozulduğu, geri bağlantıları türetilen ve yalnızca yeni kayıt eklenen karar kayıtlarının ise tasarımları gereği bu sorunu önlediği sonucuna varılmaktadır. Ayrıca sınırlar belirtilmektedir: kararların yerleşik bir sağlama toplamı bulunmamakta ve otomatik bir denetim problemi işaretleyebilmekte, ancak bir ifadenin doğru olduğunu onaylayamamaktadır.

Bu ilke çıkarıma uygulandığında, ayrıştırıcının ya da modelin metinden çıkardığı aday olgu türetilebilirdir; çünkü model her seferinde aynı çıktıyı vermese de aday olgu aynı metinden yeniden çıkarılabilmektedir. Bir insanın kabulü, reddi, düzeltmesi ya da iki raviyi birleştirmesi ise hiçbir kaynaktan türetilememekte; kimin, ne zaman karar verdiğiyle birlikte bir kez kaydedilmesi gerekmektedir. Bu nedenle sistem, her olgu için kararların izini tutmaktadır.

Bu ilke, Bölüm 2.3'teki ikinci sınıfı da açıklamaktadır. Modelin sessizce normalize ettiği bir değer, ne metinden doğrudan türetilmiş bir değerdir ne de kaydedilmiş bir insan kararıdır. Kabul edilmeden önce adı kayıtlı bir kural ya da bir insan tarafından doğrulanması gerekmektedir.

<!-- keys: mghari2022sanadset, internal-data-manifest, mahmoud2022arsanad, aslan2017tabakat, haque2026hadith, hogan2021knowledge, kejriwal2019domain, ye2022generative, pan2024unifying, zhang2024edc, ji2023survey, mihindukulasooriya2023text2kgbench, min2023factscore, wei2024longform, rashkin2023measuring, laban2022summac, zha2023alignscore, gao2023rarr, dhuliawala2024chainofverification, kadavath2022language, xiong2024can, internal-cache-ledger, angelopoulos2021gentle, raja2026grading -->
