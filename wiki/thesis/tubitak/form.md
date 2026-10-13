# TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı: Araştırma Önerisi Formu

> **Taslak, gönderilmedi (2026-10-13).** Ekip ve danışman okumadı. Göndermeden önce karara bağlanacak
> noktalar en sondaki "Göndermeden önce" bölümündedir; o bölüm ve bu kutu başvuru metnine girmez.

# A. GENEL BİLGİLER

| | |
|---|---|
| **Başvuru Sahibinin Adı Soyadı** | Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya |
| **Araştırma Önerisinin Başlığı** | Büyük Dil Modellerinde Halüsinasyon ve Şema Sapmasını Önleyen İnsan-Döngülü Bilgi Grafı Üretim Motoru: Hadis İsnad Zincirleri Üzerine Bir Uygulama |
| **Danışmanın Adı Soyadı** | Dr. Öğr. Üyesi Taha Yiğit Alkan |
| **Araştırmanın Yürütüleceği Kurum/Kuruluş** | Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü (alan uzmanı desteği: Akdeniz Üniversitesi İlahiyat Fakültesi, Prof. Dr. Rifat Atay) |

# ÖZET

Büyük dil modelleri (BDM) metinden bilgi grafı olguları çıkarabilir; ancak kaynakta bulunmayan olgular da ekler ve kendilerine verilen şemadan sapar. Bu projede, modelin yalnızca öneri ürettiği bir motoru ve tasarımının dayandığı iddiayı sınayacağız. İddiamız, böyle bir sistemde saklanması gerekenin insan kararı olduğudur. Kaynaktan türetilebilen her şey yeniden türetilir ve güvenilmeden önce kontrol edilir. Çalışmayı, hadis metninin başındaki ravi zinciri (isnad) üzerinde yürüteceğiz.

Motoru ve ilk ölçümleri TÜBİTAK desteği olmadan ön çalışma olarak tamamladık. Altı temel hadis kitabından 300 hadisi platform kaynaklı ravi etiketlerine karşı değerlendirdik. Yalnız şema verilen modelin etiketle eşleşmeyen 145 önerisinin 122'sini, çıkarılan adın modelin kendi alıntısında geçip geçmediğini denetleyen kontrol işaretledi. Alıntının kaynakta geçip geçmediğini denetleyen kontrol ise hiçbirini işaretlemedi. Modelin bildirdiği güven skoru, benzer bir inceleme payında bu önerilerin 50'sini buldu. Etiketli 27.056 zincir üzerindeki benzetimde, yalnız ada bağlanan ravi kimliği kararı on geçişin birinde yanlış yeniden kullanıldı. Deterministik bir kural çelişki bulduğunda kararın kapsamını daraltmak, sessiz hatayı geçiş başına 0,014'e indirdi. Bu ölçümlerin hiçbirinde insan altın standardı ya da gerçek bir inceleyici bulunmuyordu.

Önerdiğimiz proje bu eksiği kapatacaktır. Yöntemi şu adımlarla uygulayacağız: (1) 300 hadisi iki bağımsız kodlayıcı etiketleyecek ve aralarındaki uyumu ölçeceğiz; (2) kontrolleri ve dört çıkarım koşulunu en az üç modelle bu etiketlere karşı yeniden değerlendireceğiz; (3) bir inceleyici motorun inceleme kuyruğunda karar verecek ve karar başına süreyi ölçeceğiz; (4) ravi kimliği kararlarını saklayan ve kapsamı çelişki görüldüğünde daralan karar defterini motora ekleyip gerçek kararlarla sınayacağız; (5) iddiayı ikinci bir alanda tekrar sınayacağız.

Proje, altı aya yayılan dört iş paketinden oluşmaktadır. Lisans, kodlayıcı uyumu, model erişimi ve takvim riskleri için B planları hazırladık. Projenin çıktıları, insan etiketli bir isnad referans kümesi, ölçüm betikleriyle birlikte açık kaynak olarak yayımlanacak motor, en az bir hakemli bildiri ve bir ön baskı olacaktır.

**Anahtar Kelimeler:** büyük dil modelleri, bilgi grafı, insan-döngülü sistem, kaynağa dayandırma, karar kaydı, hadis isnad zinciri

# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

BDM'ler serbest metinden bilgi grafı kurabilir [@ye2022generative; @pan2024unifying] ve bu işlemin maliyetini düşürmüştür. Güçlük, olgu üretmekten çok, insanların güveneceği bir grafa hangi olguların girebileceğine karar vermektir. Sonradan fark edilmesi zor olan iki hata türünü ele alıyoruz: modelin kaynağın desteklemediği bir olgu yazması ve tanımlanmamış bir tip ya da özellik kullanarak şemadan sapması. Kaynağın desteklemediği üretim, doğal dil üretiminde "halüsinasyon" adıyla incelenmiştir [@ji2023survey]. Bu derleme bilgi grafı çıkarımını ayrı bir görev olarak ele almaz. Ontoloji güdümlü çıkarım için hazırlanan Text2KGBench ölçütünün Wikidata-TekGen bölümünde, Vicuna-13B ile özne halüsinasyonu 0,17, referans üçlülere karşı precision ise 0,38 olarak raporlanmıştır [@mihindukulasooriya2023text2kgbench]. Metinde bulunmak, doğru olmayı garanti etmez.

Yaygın bir önlem, modelden kaynak alıntısı ve güven skoru istemektir. Ön çalışmamızda, denediğimiz model için ikisinin de beklendiği gibi çalışmadığını gördük. Model kaynağı doğru alıntıladıktan sonra alıntıda bulunmayan bir değer yazdı. Güven skoru da etiketle eşleşen ve eşleşmeyen önerileri ayırmakta zayıf kaldı.

**Vaka.** Hadis, kendisini aktaran kişilerin zinciriyle başlar: "A bize anlattı, o B'den, o C'den". Bu zincir doğası gereği bir graftır. Hadisin değeri zincirdeki kişilere göre belirlendiğinden tek bir yanlış ad hükmü değiştirir. Ayrıca bu alanda etiketli veri bulunmaktadır [@mghari2022sanadset; @mahmoud2022arsanad]. Altı kitabın ontolojisi ve bilgi grafı yayımlanmıştır [@kamran2023semantichadith; @kamran2026semantic]. Büyük etiketli eğitim kümeleriyle ince ayar yapılmış modeller ravileri ve bağlarını yüksek başarıyla çıkarır [@oumer2025relation]; ravi adları da biyografik veritabanlarına bağlanmıştır [@wirahman2026linking]. Alanın eleştirel bir derlemesi, ölçütlerin karşılaştırılamazlığını ve uzman doğrulamasının seyrekliğini açık sorunlar arasında sayar [@haque2026hadith]. Genel amaçlı bir model ile graf arasındaki adımı ölçen bir çalışma bulamadık. Araştırmak istediğimiz, bu adımda hangi kontrollerin kullanılacağı, her birinin neyi yakaladığı, olgu kabulünün nasıl kaydedileceği ve insan kararının ne kadar yeniden kullanılabileceğidir. Taramamız sistematik olmadığı için bu tespit, bulabildiğimiz çalışmalarla sınırlıdır.

**İddia.** Bir ayrıştırıcının ya da modelin metinden çıkardığı aday yeniden çıkarılabilir. Bu nedenle adayı türetilmiş sayarız; doğrudan güvenmek yerine kontrol ederiz ve saklanmasını gerekli görmeyiz. İnsanın kabulü, düzeltmesi ya da "bu ad burada şu kişidir" kararı ise hiçbir metinden türetilemez. Bu karar, kimin ne zaman verdiği bilgisiyle birlikte bir kez saklanmalıdır. Motoru bu ayrım üzerine kurduk.

**Ön çalışma.** Aşağıdaki çalışmaları TÜBİTAK desteği olmadan, kendi olanaklarımızla tamamladık. Kodun büyük kısmını, yönlendirmemiz altında yapay zekâ kodlama asistanları yazdı (Bölüm 5).

- *Motor (GiraffeGraph Core).* Model yalnız aday üretir. Her aday bir kaynak alıntısı taşır; deterministik kontroller adayı gerekçe koduyla inceleme kuyruğuna gönderir. Olgu, ancak bir inceleyicinin kararı ya da adı kayıtlı bir otomatik politika tarafından kabul edildiği kaydedilirse grafa girer. Kararlar silinmez ve üzerlerine yazılmaz. Arka uçta 285 otomatik test bulunur; bunların on ikisi akışı gerçek PostgreSQL ve Neo4j üzerinde sınar.
- *Kontrollerin ölçümü.* Altı kitaptan 300 hadisi, sabit bir eşleştirme protokolü ve hadis düzeyinde bootstrap aralıklarıyla platform kaynaklı ravi etiketlerine karşı puanladık. Gevşek eşleştirmede kural tabanlı ayrıştırıcının F1 değeri 0,923, yalnız şema verilen modelin 0,890, tip açıklamaları ve alan ipuçları eklenen aynı modelin ise 0,956 oldu. Değer-alıntıda kontrolü, yalnız şema verilen modelin önerilerinin %9,2'sini işaretledi. Bunlar, etiketle eşleşmeyen 145 önerinin 122'sini içeriyordu. İşaretlenenlerin çoğu uydurulmuş raviler değil, modelin çevriyazıya çevirdiği ya da hâlini değiştirdiği doğru adlardı. İncelemesiz kabul edilen adaylarda precision 0,914'ten 0,985'e çıktı. Güven skorunun ayırıcılığı düşüktü (AUC 0,634).
- *Ad kimlik değildir.* Aynı 300 hadisteki 2.150 zincir konumunda 740 kişi yer alır. Konumların %10,0'ı birden çok kişiyi kapsayan bir yazımla temsil edilir; kişilerin %25,8'i ise birden çok yazıma bölünür.
- *Kimlik kararının yeniden kullanımı (benzetim).* AR-Sanad'ın 27.056 test zincirinde (150.904 geçiş), inceleyicinin cevabı yerine veri kümesinin etiketini kullandık. Yalnız ada bağlanan karar, geçiş başına 0,100 sessiz hata üretti. Öğrenciye (zincirde addan önce gelen ravi) ve ada bağlanan karar bu değeri 0,006'ya indirdi, ancak üç katı soru sordu (0,340'a karşı 0,101). Kapsamı yalnız tabaka ve vefat yılına dayalı deterministik kuralın çelişki gördüğü adlarda daralttığımızda, hata 0,014, soru 0,178 oldu. Sonuç, bağımsız bir kaynaktan gelen ikinci etiket kümesinde (34.681 hadis, 205.514 geçiş) ve defterin görmediği kitaplarda da tekrarlandı.
- *İkinci alan.* Motorun kendi kaynak kodu hakkında soru cevaplayan bir kod ajanı, kodun neden o şekilde yazıldığını soran soruların %0–4'ünü yalnız kodla, %88–100'ünü ise bir karar defteriyle doğru cevapladı (12 soru, ikişer koşu). Yeterli araç çağrısı hakkı verildiğinde yapısal soruları belgesiz %94–98 doğrulukla cevapladı.
- *Tutmayan.* Değer-alıntıda kontrolü hadis dışında aynı işi görmedi. İnsan etiketli bir biyomedikal derlemde [@li2016bc5cdr], aynı model ve yalnız şema içeren istemle etiketle eşleşmeyen 303 önerinin 53'ünü işaretledi. Güven skoru aynı inceleme payında 58'ini buldu.

Bu ölçümlerde referans etiketleri insan altın standardı değildir, hiçbir koşuda bir insan karar vermemiştir ve kullanılabilir sonuçlar tek bir modelden gelmiştir. Önerdiğimiz projede bu üç eksiği gidermeyi hedefliyoruz.

**Bu projenin bilimsel katkıları.**

- **K-1. İnsan etiketli isnad referans kümesi.** İki bağımsız kodlayıcı, yazılı bir kılavuz kullanarak ve sistem çıktısını görmeden altı kitaptan 300 hadisin ravi geçişlerini ve sırasını etiketleyecektir. Anlaşmazlıklarda alan uzmanı hakemlik edecektir. Kodlayıcılar arasındaki uyumu ve hadis başına etiketleme süresini raporlayacağız.
- **K-2. Kontrollerin ve çıkarım koşullarının insan etiketine karşı ölçümü.** Dört koşulu (kural tabanlı ayrıştırıcı; yalnız şema verilen model; alan ipuçlu model; alan ipuçlu model ve yalnız zincir metni) en az üç modelle ikişer kez çalıştıracağız. Modellerin en az biri açık ağırlıklı olacaktır.
- **K-3. İnceleyicinin döngüde ölçümü.** Bir hadisin referans etiketini üretmemiş bir kişi, motorun inceleme kuyruğunda o hadisin öğeleri hakkında karar verecektir. İnceleme sonrası precision ve recall değerlerini, gerekçe koduna göre ret oranını ve karar başına süreyi raporlayacağız.
- **K-4. Motorda kimlik karar defteri.** Kararı aday kimliğine değil, içeriğe bağlayacağız ve ravi kimliği kararını defterde saklayacağız. Tabaka ve vefat yılı kuralı çelişki bulduğunda kararın kapsamı daralacaktır. Benzetimdeki ölçümü gerçek inceleyici kararlarıyla tekrarlayacağız.
- **K-5. İddianın ikinci alanda tekrar sınanması.** Kod ajanı deneyini başka bir model ailesinden en az bir modelle ve ikinci bir kod tabanıyla tekrarlayacağız.

**Araştırma sorusu.** BDM ile metinden bilgi grafı üretiminde şu soruları ele alacağız: (a) Modelin önerisi ile graf arasına konan deterministik kontroller, insan etiketine göre kaynaktan sapan önerilerin ne kadarını ve ne kadar inceleme emeğiyle yakalar? (b) İnsan kararları saklanıp yeniden kullanıldığında inceleme emeği ve fark edilmeyen hata nasıl değişir?

**Hipotezler.** Ön çalışmadaki ölçümler insan etiketine karşı yapılmadığı için eşikleri bu ölçümlerin altında seçtik.

- **H1.** Yalnız şema verilen model koşulunda değer-alıntıda kontrolü, insan etiketiyle eşleşmeyen önerilerin en az %60'ını işaretler ve aynı inceleme payında modelin güven skorundan daha fazla eşleşmeyen öneri bulur. (Ön çalışma, platform etiketi: %84; 122'ye karşı 50.)
- **H2.** Kontrollerden geçip incelemesiz kabul edilen önerilerde hata oranı (1 − precision), modelin ham önerilerine göre en az %50 düşer. (Ön çalışma: 0,086'dan 0,015'e.)
- **H3.** İnceleyicinin bir adayı reddetme ya da düzeltme olasılığı, kontrollerin işaretlediği adaylarda işaretlemediklerine göre anlamlı biçimde daha yüksektir (aday düzeyinde lojistik model, hadis düzeyinde kümelenmiş, p < 0,05).
- **H4.** Gerçek inceleyici kararlarıyla çalışan ve kapsamı çelişki görüldüğünde daralan kimlik defteri, öğrenci ve ada sabitlenmiş deftere göre en az %20 daha az soru sorar. İki defterin geçiş başına sessiz hata farkı 0,02'yi aşmaz. (Benzetim: %32–48 daha az soru; fark 0,003–0,008.)

## 1.2. Amaç ve Hedefler

**Genel amaç.** Modelin yalnız öneri ürettiği, kontrollerin ve insanın karar verdiği, her kabulün kaydedildiği bir bilgi grafı üretim motorunu insan etiketleri ve gerçek inceleyici kararlarıyla değerlendirmeyi amaçlıyoruz. İnsan kararını saklayıp yeniden kullanmanın inceleme emeğini ne kadar azalttığını göstermek istiyoruz.

**Özgül ve ölçülebilir hedefler.**

- **Hedef 1 (referans kümesi).** İki bağımsız kodlayıcı 300 hadisi etiketleyecektir. İki kodlayıcının karşılıklı F1 değeri (gevşek eşleştirme) en az 0,85 olacaktır. Bu değerin altında kalırsa kılavuzu düzeltecek ve turu tekrarlayacağız. Hadis başına ortalama etiketleme süresini raporlayacağız.
- **Hedef 2 (ölçüm).** Dört koşul, en az üç model ve ikişer tekrar için precision, recall ve F1 değerlerini katı ve gevşek eşleştirmede, hadis düzeyinde bootstrap güven aralıklarıyla raporlayacağız. H1 ve H2'yi sınayacağız.
- **Hedef 3 (inceleyici).** Bir inceleyici, 300 hadisin inceleme öğelerinin tamamı hakkında karar verecektir. İnceleme sonrası precision ve recall değerlerini, ret oranını ve karar başına medyan süreyi raporlayacağız. H3'ü sınayacağız.
- **Hedef 4 (karar defteri).** Defteri motora ekleyeceğiz ve testlerinin gerçek veritabanlarında geçmesini sağlayacağız. İnceleyicinin kimlik kararlarıyla soru sayısını ve sessiz hatayı ölçerek H4'ü sınayacağız.
- **Hedef 5 (yaygın etki ve açık bilim).** Motoru, ölçüm betiklerini ve referans etiketlerini açık lisansla yayımlayacağız. Sonuçları en az bir hakemli bilimsel etkinlikte bildiri olarak sunacak ve ön baskı olarak paylaşacağız.

Motor ve ölçüm betikleri ön çalışmada hazırlandığı için hedefleri, üç kişilik ekibimizin altı ayda tamamlayabileceği şekilde belirledik.

# 2. YÖNTEM

Araştırmada tasarım bilimi yaklaşımını [@hevner2004design; @wieringa2014design] kontrollü deneysel değerlendirmeyle birleştireceğiz. Bir yapıt, yani motor geliştirecek ve onu ölçülebilir ölçütlere göre değerlendireceğiz.

## 2.1. Mevcut Motor ve Bu Projede Eklenecekler

Motorun akışı şudur: kaynak birimi → isnad bölütleyici → model önerisi → kontroller → inceleme → kanonik graf. Modelin grafa yazma yetkisi yoktur.

Ön çalışmada şema sürümlemeyi, hadisin tek kaynak birimi olarak alınmasını, kural tabanlı isnad bölütleyiciyi ve şemaya bağlı model çıkarımını hazırladık. Doğrulama, alıntının kaynakta, değerin alıntıda ve tipin şemada bulunması gibi kontrollerden on iki gerekçe kodu üretir. İnceleme kuyruğu ile kimin, ne zaman ve ne kadar sürede karar verdiğini tutan karar kaydı da hazırdır. İlişki kimliği, aynı iki ravi arasındaki ayrı aktarımları birbirinden ayırır. Zincir görünümünü, puanlama ve analiz betiklerini de tamamladık.

Bu projede aşağıdaki bileşenleri ekleyeceğiz:

- **E-1. Kararın içeriğe bağlanması.** İnceleme kararını aday kimliği yerine (hadis, normalize ad) hedefine bağlayacağız. Böylece metinden yeniden çıkarım yapıldığında karar kaybolmayacaktır. Ön çalışmada aynı modelin iki istemi arasında adayların 0,857–0,977'sinin, kural tabanlı ayrıştırıcı ile model arasında ise 0,561–0,634'ünün hedefini bulduk.
- **E-2. Kimlik karar defteri.** Her kimlik kararını tam bağlamıyla (önceki ravi, ad, sonraki ravi) saklayacağız. Kararın hangi bağlamda yeniden kullanılacağını saklamayacağız. Kapsam her ad için en geniş biçimde başlayacak ve çelişki görüldükçe daralacaktır.
- **E-3. Alan kuralı kancası.** Defterin önerdiği kişi ile komşu ravi arasındaki tabaka ve vefat yılı farkı sınırların dışındaysa öğe inceleyiciye sorulacak ve o adın kapsamı daraltılacaktır. Kural, olguyu reddetmek yerine soru üretecektir.
- **E-4. Dönüşüm kuralı.** Yalnız hâl eki değişmiş adlar otomatik kabul edilecek ve kabul eden kural kayda geçirilecektir.

## 2.2. Değişkenler ve Ölçütler

Bağımsız değişkenler, çıkarım koşulu (dört düzey), model (en az üç düzey), kontrol (yok, alıntı-kaynakta, değer-alıntıda) ve defter politikasıdır (yalnız ad; öğrenci ve ad; kuralla daralan kapsam).

Bağımlı değişkenleri ravi geçişi düzeyinde, insan etiketine karşı şu şekilde ölçeceğiz:

- Precision, recall ve F1 değerlerini katı (normalize diziler eşit) ve gevşek (eşit, alt dizi ya da belirteç F1 ≥ 0,60) eşleştirmede hesaplayacağız. Sistem ve referans geçişlerini en büyük ağırlıklı eşleştirmeyle hizalayacağız. Eşleştirme ölçütü ölçümden önce sabit olacaktır.
- Kontrolün işaretlediği önerilerin payını ve bunların içinde etiketle eşleşmeyenlerin payını hesaplayacağız.
- İncelemede, gerekçe koduna göre ret ve düzeltme oranını ve karar başına süreyi ölçeceğiz.
- Defterde, geçiş başına soru sayısını ve sessiz hatayı ölçeceğiz. Sessiz hata, yeniden kullanılan ve inceleyicinin kararıyla çelişen cevaptır.

Analiz birimi hadistir.

## 2.3. Veri ve Referans Kümesinin Oluşturulması

300 hadis, altı kitaptan alınmış tabakalı örneklemi oluşturur ve ön çalışmadaki test kümesiyle aynıdır. Böylece platform etiketleriyle insan etiketlerini aynı hadislerde karşılaştırabileceğiz. Metinler Arapçadır. Telifsiz ve tam isnad içeren bir Türkçe kaynak bulamadığımız için Türkçe metni kapsam dışında tuttuk. Kılavuz ve arayüz Türkçedir.

İki ekip üyesi aynı hadisleri yazılı bir kılavuzla, birbirinden bağımsız olarak ve sistem çıktısını görmeden etiketleyecektir. Kontrolleri yazan kişi etiketleme yapmayacaktır. Önce 50 hadislik bir kalibrasyon turunda uyumu ve süreyi ölçecek, kılavuzu düzelteceğiz. Ardından kalan hadisler etiketlenecektir. Anlaşmazlıkları alan uzmanının hakemliğiyle çözeceğiz. Uzman inceleme kuyruğunda karar vermeyecektir; inceleyici, o hadisin etiketini üretmemiş ekip üyesi olacaktır. Böylece sistemi düzelten kişi ölçütü de belirlemeyecektir.

Uyumu iki kodlayıcının karşılıklı F1 değeriyle ölçeceğiz. Açık uçlu çıkarımda birim sayısı baştan belli olmadığı için Cohen kappa yerine bu ölçüyü seçtik.

Yayımlayacağımız küme yalnız etiketleri ve kaynak kimliklerini içerecek, hadis metnini içermeyecektir.

## 2.4. Deney Tasarımı ve İstatistiksel Yöntem

- **Koşullar ve modeller.** Deney düzeni 4 koşul × en az 3 model × 2 tekrar × 300 hadis olacaktır. Model yanıtlarını önbelleğe alarak aynı koşunun yeniden üretilmesini sağlayacağız. Koşullar arasındaki farkı hadis düzeyinde eşli bootstrap aralığıyla vereceğiz.
- **H1 ve H2.** Kontrolün işaretlediği ve işaretlemediği önerilerin insan etiketiyle eşleşme tablosundan hesaplama yapacağız. Güven skoruyla karşılaştırmayı, aynı sayıda önerinin incelemeye gönderildiği noktada yapacağız.
- **H3.** Aday düzeyinde lojistik regresyon kullanacağız. Sonuç değişkeni inceleyicinin reddi ya da düzeltmesi, açıklayıcı değişkenler ise gerekçe kodları ve güven skoru olacaktır. Standart hataları hadis düzeyinde kümeleyeceğiz.
- **H4.** İnceleyicinin kimlik kararlarını sırayla defterden geçirerek üç politikayı aynı kararlar üzerinde karşılaştıracağız. Belirsizliği hadis sırasını yeniden karıştırarak vereceğiz.
- **K-5.** Kod ajanı deneyini, aynı sorular ve cevap anahtarıyla başka bir model ailesinden bir model üzerinde tekrarlayacağız. Ayrıca ikinci bir kod tabanı için yeni bir soru kümesi yazarak deneyi tekrarlayacağız. Analiz birimi soru olacaktır.

Bir koşu başarısız olursa, örneğin model istenen çıktı biçimini üretemezse, bunu sonuç olarak raporlayacak ve veri dışında bırakmayacağız.

## 2.5. Ön Çalışma ve Bu Projenin Sınırı

Ön çalışmada motoru, ölçüm betiklerini ve platform etiketine karşı ilk ölçümleri tamamladık (Bölüm 1.1). TÜBİTAK desteğini bunları yeniden yapmak için kullanmayacağız. Destek, eksik olan üç çalışmaya ayrılacaktır: insan etiketlerinin üretilmesi, gerçek inceleyiciyle değerlendirme yapılması ve karar defterinin motora eklenip gerçek kararlarla sınanması. Yöntem adımlarını Bölüm 3'teki çalışma takvimiyle birebir eşleştirdik.

# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

| Tarih Aralığı | Faaliyetler | Kim(ler) Tarafından Gerçekleştirileceği | Başarı Ölçütü ve Araştırmanın Başarısına Katkısı |
|---|---|---|---|
| 1.–2. Ay | İP1: Etiketleme kılavuzunu hazırlayacağız. 50 hadislik kalibrasyon turunda uyumu ve süreyi ölçerek kılavuzu düzelteceğiz. Kararı içeriğe bağlayacağız (E-1). | Tüm ekip (alan uzmanı danışmanlığında) | Çıktılar, kılavuz v2 ve iki kodlayıcının 50 hadisteki etiketleri olacaktır. Karşılıklı F1 ve hadis başına süre raporlandığında ve E-1 testleri geçtiğinde paket başarılı sayılacaktır. Başarıya katkısı %20'dir. |
| 2.–4. Ay | İP2: Kalan 250 hadisi etiketleyerek anlaşmazlıkları uzman hakemliğiyle çözeceğiz. Dört koşulu en az üç modelle ikişer kez çalıştıracak ve kontrolleri insan etiketine karşı ölçeceğiz. | Tüm ekip (alan uzmanı hakemliğinde) | Çıktılar, 300 hadislik referans kümesi ve sonuç tablosu olacaktır. Karşılıklı F1 ≥ 0,85 olduğunda ve H1 ve H2 sınandığında paket başarılı sayılacaktır. Başarıya katkısı %30'dur. |
| 3.–5. Ay | İP3: Kimlik karar defterini, alan kuralı kancasını ve dönüşüm kuralını ekleyeceğiz (E-2, E-3, E-4). İnceleyici, 300 hadisin inceleme öğeleri hakkında karar verecektir. Defteri bu gerçek kararlarla ölçeceğiz. | Tüm ekip | Çıktılar, defterli motor sürümü ve inceleme kayıtları olacaktır. Testler gerçek veritabanlarında geçtiğinde, H3 ve H4 sınandığında ve karar başına süre raporlandığında paket başarılı sayılacaktır. Başarıya katkısı %30'dur. |
| 5.–6. Ay | İP4: Deneyi ikinci alanda tekrarlayacağız (K-5). Motoru, betikleri ve etiketleri açık olarak yayımlayacağız. Sonuç raporunu, bildiriyi ve ön baskıyı hazırlayacağız. | Tüm ekip | Çıktılar, açık kod ve veri, sonuç raporu ve bildiri taslağı olacaktır. Sonuçlar temiz bir klondan betiklerle yeniden üretildiğinde paket başarılı sayılacaktır. Başarıya katkısı %20'dir. |

İş paketlerini birbirleriyle örtüşecek şekilde planladık; etiketleme sürerken motor geliştirmesi de ilerleyecektir.

## 3.2. Risk Yönetimi

| En Önemli Riskler | Alınacak Tedbirler (B Planı) |
|---|---|
| R1: Kullanılan etiketli derlemlerin ya da ravi kataloğunun lisansı teyit edilemez. | Yalnız lisansı açık metinleri ve kendi etiketlerimizi kullanacağız. Diğer derlemleri yeniden dağıtmadan, yalnız ölçüm için kullanacağız. Yayımlayacağımız küme metin içermeyecektir. |
| R2: İki kodlayıcının uyumu hedefin altında kalır. | Kılavuza sınır kuralları ekleyerek kalibrasyon turunu tekrarlayacağız. Gerekirse kaliteyi önceleyerek kümeyi 300'den 200 hadise indireceğiz. |
| R3: Etiketleme ve inceleme planlanandan uzun sürer. | İlk 50 hadiste süreyi ölçecek ve kalan işi buna göre planlayacağız. İncelemeyi yalnız kontrollerin işaretlediği öğelerle sınırlandırabiliriz. |
| R4: Model erişimi kesilir, maliyet aşılır ya da bir model istenen çıktı biçimini üretemez. | Aynı arayüzden açık ağırlıklı bir model kullanacak ve hadis sayısını azaltacağız. Biçim hatasıyla biten koşuyu da sonuç olarak raporlayacağız. |
| R5: Akademik dönem yoğunluğu takvimi kaydırır. | Motor ve betikler hazır olduğu için takvimi belirleyen iş etiketlemedir. Her iş paketine %15 zaman payı bıraktık. Tekrar sayısını ikiden bire indirebiliriz. |
| R6: Ön çalışmanın kapsamı, projenin büyük kısmının yapılmış olduğu izlenimini verir. | Bu formda tamamladığımız ve henüz yapmadığımız işleri ayrı ayrı belirttik. Desteği yalnız eksik olan insan etiketi, inceleyici ölçümü ve karar defteri için kullanacağız. |
| R7: Yapay zekâ asistanlarıyla yazılmış kod, ekibin tam anlamadığı davranışlar içerir. | Kodu yalnız testleriyle kabul edeceğiz. Her iş paketinin başında ilgili modülü ekip olarak gözden geçirecek ve ölçülen her sayıyı bir betikle yeniden üreteceğiz. |

## 3.3. Araştırma Olanakları

| Kuruluşta Bulunan Altyapı/Ekipman Türü, Modeli | Projede Kullanım Amacı |
|---|---|
| Akdeniz Üniversitesi Bilgisayar Mühendisliği Bölümü yazılım geliştirme laboratuvarı | Yazılım geliştirme, kod gözden geçirme ve etiketleme oturumları için kullanacağız. |
| Bölüm sunucu altyapısı ve kampüs ağı | PostgreSQL ve Neo4j örneklerini barındırmak için kullanacağız. |
| Akdeniz Üniversitesi İlahiyat Fakültesi, Prof. Dr. Rifat Atay'ın alan uzmanı desteği | Etiketleme kılavuzunun gözden geçirilmesi, anlaşmazlıklarda hakemlik ve ravi kaynaklarına akademik erişim için destek alacağız. |
| GiraffeGraph Core motoru, ölçüm betikleri ve ön çalışma sonuçları (ekibin önceki çalışması) | Projeyi bu yapıt üzerine kuracağız ve geliştirme süresince özel bir depoda tutacağız. |

# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Çıktı, Etki ve Kazanımlar | Öngörülen Çıktı(lar), Etki(ler) ve Kazanım(lar) |
|---|---|
| **Bilimsel/Akademik Çıktılar** | (i) En az bir ulusal ya da uluslararası hakemli etkinlikte bildiri sunacağız. (ii) Sonuçları ön baskı olarak yayımlayacağız. (iii) Bitirme tezini hazırlayacağız. |
| **Ekonomik/Ticari/Sosyal Çıktılar** | (i) Motoru ve ölçüm betiklerini açık kaynak lisansıyla yayımlayacağız. (ii) İki kodlayıcının etiketlediği ve uyumu raporlanmış 300 hadislik isnad referans kümesini, metin içermeden, açık veri olarak yayımlayacağız. (iii) Bölüm öğrencilerine yönelik bir seminer düzenleyeceğiz. |
| **Yeni Proje(ler) Oluşturmasına Yönelik Çıktılar** | (i) Ravi adlarını bir otorite listesine bağlamak ve graf üzerinden soru cevaplamak için takip çalışması yapacağız. (ii) Kontrolleri ve karar defterini hadis dışı bir alanda ikinci vaka çalışmasında ele alacağız. (iii) Bilgisayar Mühendisliği ile İlahiyat arasındaki iş birliğini sürdüreceğiz. |

Çıktıların sınırını açıkça belirteceğiz. Motorun başka bir alanda aynı sonucu vereceği gösterilmemiştir; ön çalışmada bir kontrol hadis dışında aynı işi görmemiştir (Bölüm 1.1).

# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

**Ön çalışma beyanı.** Motoru, ölçüm betiklerini ve Bölüm 1.1'deki ölçümleri TÜBİTAK desteği ya da başka bir finansman almadan tamamladık. Desteği yalnız bu öneride tanımlanan işler için kullanacağız.

**Yapay zekâ kullanımı beyanı.** Bu projede üretken yapay zekâ araçlarını yaygın biçimde kullandık. Literatür aramasında, motor kodunun büyük kısmının ve analiz betiklerinin yazımında, ön çalışma deneylerinin yürütülmesinde ve bu formun taslağının hazırlanmasında bu araçlardan yararlandık. Kullanımı, TÜBİTAK'ın üretken yapay zekâ rehberini [@tubitak2024uyz] gözeterek beyan ediyoruz. Riskleri sınırlamak için kaynakça kayıtlarını bellekten yazmak yerine dizinlerden alıyoruz. Ölçülen her sayıyı bir betikle üretiyor ve sonuç dosyasında saklıyoruz. Kodu yalnız testleriyle kabul ediyor, başka çalışmalar hakkındaki ifadeleri okuduğumuz kaynaklarla sınırlıyoruz. İçeriğin sorumluluğu ekibimize aittir. Çıkarım deneylerinde dil modeli, sınadığımız sistemin kendisidir.

**Veri ve lisans.** Hadis metinleri üçüncü taraf kaynaklardan gelmektedir. Bu metinleri yalnız değerlendirme için kullanıyoruz ve yeniden dağıtmıyoruz. Yayımlayacağımız referans kümesi metin içermeyecektir.

**Açık bilim.** Kod, üçüncü taraf metinlerle aynı depoda bulunduğu için depoyu geliştirme süresince özel tutuyoruz. Proje sonunda motoru ve betikleri açık kaynak lisansıyla yayımlayacağız.

**Alan uzmanı desteği.** Prof. Dr. Rifat Atay, etiketleme kılavuzunun gözden geçirilmesi ve anlaşmazlıklarda hakemlik yapılması için danışmanlık verecektir.

# 6. EKLER

## EK-1: KAYNAKLAR

<!-- references -->

# Göndermeden önce (başvuru metnine girmez)

1. **Başvuru dönemi ve form şablonu.** Bu metin 2026 yılı I. dönem formunun başlıklarını izler. Güncel dönemin şablonu ve sayfa sınırı başvuru sisteminden kontrol edilir.
2. **Başvuru sahipleri.** Liste bitirme projesi ekibidir. Sıra ve yürütücü, başvuru sistemindeki role göre yazılır.
3. **Çerçeve.** İddia ve iki destek çalışması proje sahibinin 13 Ekim kararıdır; danışman onaylamamıştır.
4. **Alan uzmanının desteği.** Destek beyanının güncel olduğu ve bu formdaki rolü (hakemlik; inceleme kuyruğunda karar yok) kapsadığı teyit edilir.
5. **Eşikler.** H1 (%60), H2 (%50), H4 (%20 ve 0,02) ve Hedef 1 (karşılıklı F1 ≥ 0,85) öneridir. Verilen söz bağlar; ekip ve danışman onaylar.
6. **Metin kaynağı ve lisans.** 300 hadislik test kümesinin metin ve etiket kaynaklarının lisansı teyit edilmemiştir (`data/README.md`). R1'deki B planı buna göre yazılmıştır.
7. **Kalkınma planı ve program öncelikleri.** Önceki taslaktaki "12. Kalkınma Planı ile doğrudan ilişkilidir" cümlesi buraya alınmamıştır, çünkü plan metni okunmamıştır. Eklenecekse planı okuyan biri yazar.
8. **Bütçe.** Bu formda bütçe bölümü yoktur; başvuru sisteminde girilir. Model kullanım bedeli ve varsa etiketleme giderleri orada yazılır.
