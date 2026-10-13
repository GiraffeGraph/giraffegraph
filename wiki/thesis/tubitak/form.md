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

Büyük dil modelleri (BDM) metinden bilgi grafı olguları çıkarabilir, ancak kaynakta olmayan olgular ekler ve kendilerine verilen şemadan sapar. Bu öneri, modelin yalnızca öneride bulunduğu bir motoru ve bu motorun dayandığı iddiayı sınar: böyle bir sistemde saklanması gereken şey insanın verdiği karardır; kaynaktan türetilebilen her şey yeniden türetilir ve güvenilmeden önce kontrol edilir. Vaka, hadis metninin başındaki ravi zinciridir (isnad).

Ekip, motoru ve ilk ölçümleri TÜBİTAK desteği olmadan ön çalışma olarak tamamlamıştır. Altı temel hadis kitabından 300 hadiste, platform kaynaklı ravi etiketlerine karşı yapılan ölçümde, modelin çıkardığı adın modelin kendi alıntısında geçip geçmediğine bakan kontrol, yalnız şema verilen modelin etiketle eşleşmeyen 145 önerisinin 122'sini işaretlemiş; alıntının kaynakta geçip geçmediğine bakan kontrol hiçbirini işaretlememiştir. Modelin bildirdiği güven skoru, benzer bir inceleme payında bu önerilerin 50'sini bulmuştur. Etiketli 27.056 zincir üzerindeki bir benzetimde, yalnız ada bağlanan bir ravi kimliği kararı on geçişin birinde yanlış yeniden kullanılmış; kararın kapsamı, deterministik bir kuralın gördüğü çelişkide daraltıldığında sessiz hata geçiş başına 0,014'e inmiştir. Bu ölçümlerin hiçbirinde insan altın standardı ya da gerçek bir inceleyici yoktur.

Önerilen proje bu eksiği kapatır. Yöntem: (1) 300 hadisin iki bağımsız kodlayıcı tarafından etiketlenmesi ve uyumun ölçülmesi; (2) kontrollerin ve dört çıkarım koşulunun en az üç modelle bu etiketlere karşı yeniden ölçülmesi; (3) bir inceleyicinin motorun inceleme kuyruğunda karar vermesi ve karar başına sürenin ölçülmesi; (4) ravi kimliği kararlarını saklayan, kapsamı çelişkide daralan bir karar defterinin motora eklenmesi ve gerçek kararlarla sınanması; (5) iddianın ikinci bir alanda tekrar sınanması.

Proje altı aya yayılan dört iş paketinden oluşur. Lisans, kodlayıcı uyumu, model erişimi ve takvim riskleri için B planları tanımlanmıştır. Çıktılar: insan etiketli bir isnad referans kümesi, ölçüm betikleriyle birlikte açık kaynak olarak yayımlanacak motor, en az bir hakemli bildiri ve bir ön baskı.

**Anahtar Kelimeler:** büyük dil modelleri, bilgi grafı, insan-döngülü sistem, kaynağa dayandırma, karar kaydı, hadis isnad zinciri

# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

BDM'ler serbest metinden bilgi grafı kurabilir [@ye2022generative; @pan2024unifying] ve bunu ucuzlatmıştır. Güçlük olgu üretmekte değil, üretilen olguların hangisinin insanların güveneceği bir grafa girebileceğine karar vermektedir. İki hata türü sonradan görülmesi zor olduğu için öne çıkar: model kaynağın desteklemediği bir olgu yazar, ya da kimsenin tanımlamadığı bir tip ya da özellik kullanarak şemadan sapar. Kaynağın desteklemediği üretim, doğal dil üretimi için "halüsinasyon" adıyla incelenmiştir [@ji2023survey]; o derleme bilgi grafı çıkarımını ayrı bir görev olarak ele almaz. Ontoloji güdümlü çıkarım için hazırlanan Text2KGBench ölçütünün Wikidata-TekGen bölümünde, Vicuna-13B ile özne halüsinasyonu 0,17 iken referans üçlülere karşı precision 0,38 olarak raporlanmıştır [@mihindukulasooriya2023text2kgbench]; yani "metinde geçiyor" olmak "doğru" olmayı garanti etmez.

Yaygın önlem modelden bir kaynak alıntısı ve bir güven skoru istemektir. Ön çalışmamız, denediğimiz modelde ikisinin de varsayıldığı gibi çalışmadığını göstermiştir: model kaynağı doğru alıntılar, sonra alıntıda olmayan bir değer yazar; güven skoru etiketle eşleşen ve eşleşmeyen önerileri zayıf ayırır.

**Vaka.** Hadis, kendisini aktaran kişilerin zinciriyle başlar: "A bize anlattı, o B'den, o C'den". Zincir doğası gereği bir graftır; hadisin değeri zincirdeki kişilere göre belirlendiğinden tek bir yanlış ad hükmü değiştirir; ve etiketli veri vardır [@mghari2022sanadset; @mahmoud2022arsanad]. Alan boş değildir: altı kitabın ontolojisi ve bilgi grafı yayımlanmıştır [@kamran2023semantichadith; @kamran2026semantic], büyük etiketli eğitim kümeleriyle ince ayar yapılmış modeller ravileri ve bağlarını yüksek başarıyla çıkarır [@oumer2025relation], ravi adları biyografik veritabanlarına bağlanmıştır [@wirahman2026linking]. Alanın eleştirel bir derlemesi, ölçütlerin karşılaştırılamazlığını ve uzman doğrulamasının seyrekliğini açık sorun olarak sayar [@haque2026hadith]. Bulamadığımız şey, genel amaçlı bir model ile graf arasındaki adımın ölçümüdür: oraya hangi kontroller konur, her biri neyi yakalar, bir olgunun kabulü nasıl kaydedilir ve insanın verdiği karar ne kadar yeniden kullanılabilir. Taramamız sistematik değildir; bu, bulduklarımız hakkında bir ifadedir.

**İddia.** Bir ayrıştırıcının ya da modelin metinden çıkardığı aday yeniden çıkarılabilir; bu yüzden türetilmiş sayılır, güvenilmez, kontrol edilir ve saklanması gerekmez. Bir insanın kabulü, düzeltmesi ya da "bu ad burada şu kişidir" kararı hiçbir metinden türetilemez; bir kez, kimin ne zaman karar verdiğiyle birlikte saklanmalıdır. Motor bu ayrım üzerine kuruludur.

**Ön çalışma.** Ekip aşağıdakileri TÜBİTAK desteği olmadan, kendi olanaklarıyla yapmıştır. Kodun büyük kısmı yapay zekâ kodlama asistanlarıyla, ekibin yönlendirmesiyle yazılmıştır (Bölüm 5).

- *Motor (GiraffeGraph Core).* Model yalnız aday üretir. Her aday bir kaynak alıntısı taşır; deterministik kontroller adayı gerekçe koduyla inceleme kuyruğuna yollar; bir olgu grafa yalnız kayıtlı bir kabulle girer: ya bir inceleyicinin kararıyla ya da adı kayıtlı bir otomatik politikayla. Kararlar silinmez ve üzerine yazılmaz. Arka uçta 285 otomatik test vardır; on ikisi akışı gerçek PostgreSQL ve Neo4j üzerinde sınar.
- *Kontrollerin ölçümü.* Altı kitaptan 300 hadis, platform kaynaklı ravi etiketlerine karşı, sabit bir eşleştirme protokolü ve hadis düzeyinde bootstrap aralıklarıyla puanlanmıştır. Gevşek eşleştirmede kural tabanlı ayrıştırıcı F1 0,923, yalnız şema verilen model 0,890, tip açıklamaları ve alan ipuçları eklenen aynı model 0,956 vermiştir. Değer-alıntıda kontrolü yalnız şema verilen modelin önerilerinin %9,2'sini işaretlemiş, bunlar etiketle eşleşmeyen 145 önerinin 122'sini içermiştir; işaretlenenlerin çoğu uydurulmuş ravi değil, modelin çevriyazıya çevirdiği ya da hâlini değiştirdiği doğru adlardır. İncelemesiz kabul edilen adaylarda precision 0,914'ten 0,985'e çıkmıştır. Güven skorunun ayırıcılığı düşüktür (AUC 0,634).
- *Ad kimlik değildir.* Aynı 300 hadisin 2.150 zincir konumunu 740 kişi doldurur. Konumların %10,0'ı birden çok kişiyi kapsayan bir yazımın altındadır; kişilerin %25,8'i birden çok yazıma bölünür.
- *Kimlik kararının yeniden kullanımı (benzetim).* AR-Sanad'ın 27.056 test zincirinde (150.904 geçiş) inceleyici, veri kümesinin etiketiyle benzetilmiştir. Yalnız ada bağlanan karar geçiş başına 0,100 sessiz hata üretir. Öğrenci (zincirde addan önce gelen ravi) ve ada bağlanan karar bunu 0,006'ya indirir, ama üç katı soru sorar (0,340'a karşı 0,101). Kapsam yalnız tabaka ve vefat yılı üzerine kurulu deterministik bir kuralın çelişki gördüğü adlarda daraltıldığında hata 0,014, soru 0,178 olur. Sonuç bağımsız bir kaynaktan gelen ikinci etiket kümesinde (34.681 hadis, 205.514 geçiş) ve defterin görmediği kitaplarda tekrar etmiştir.
- *İkinci alan.* Motorun kendi kaynak kodu hakkında soru cevaplayan bir kod ajanı, kodun neden öyle yazıldığını soran soruların %0–4'ünü yalnız koddan, %88–100'ünü bir karar defteriyle doğru cevaplamıştır (12 soru, ikişer koşu); yapısal soruları ise yeterli araç çağrısı hakkı olduğunda belgesiz %94–98 doğru cevaplamıştır.
- *Tutmayan.* Değer-alıntıda kontrolü hadis dışında aynı işi görmemiştir: insan etiketli bir biyomedikal derlemde [@li2016bc5cdr] aynı model ve yalnız şema içeren istemle, etiketle eşleşmeyen 303 önerinin 53'ünü işaretlemiş, güven skoru aynı inceleme payında 58'ini bulmuştur.

Bu ölçümlerin ortak sınırı şudur: referans etiketleri insan altın standardı değildir, hiçbir koşuda bir insan karar vermemiştir ve kullanılabilir sonuç tek bir modelden gelmiştir. Önerilen proje tam olarak bu üç eksiği hedefler.

**Bu projenin bilimsel katkıları.**

- **K-1. İnsan etiketli isnad referans kümesi.** Altı kitaptan 300 hadisin ravi geçişleri ve sırası, iki bağımsız kodlayıcı tarafından yazılı bir kılavuzla ve sistem çıktısı görülmeden etiketlenir; anlaşmazlıklarda alan uzmanı hakemlik eder. Uyum ve hadis başına etiketleme süresi raporlanır.
- **K-2. Kontrollerin ve çıkarım koşullarının insan etiketine karşı ölçümü.** Dört koşul (kural tabanlı ayrıştırıcı; yalnız şema verilen model; alan ipuçlu model; alan ipuçlu model ve yalnız zincir metni) en az üç modelle, en az biri açık ağırlıklı olmak üzere, ikişer tekrarla koşulur.
- **K-3. İnceleyicinin döngüde ölçümü.** Bir hadisin referans etiketini üretmemiş bir kişi, motorun inceleme kuyruğunda o hadisin öğelerine karar verir. İnceleme sonrası precision ve recall, gerekçe koduna göre red oranı ve karar başına süre raporlanır.
- **K-4. Motorda kimlik karar defteri.** Karar aday kimliğine değil içeriğe bağlanır; ravi kimliği kararı defterde saklanır; kararın kapsamı, tabaka ve vefat yılı kuralının gördüğü çelişkide daralır. Benzetimdeki ölçüm gerçek inceleyici kararlarıyla tekrarlanır.
- **K-5. İddianın ikinci alanda tekrar sınanması.** Kod ajanı deneyi başka bir model ailesinden en az bir modelle ve ikinci bir kod tabanıyla tekrarlanır.

**Araştırma sorusu.** BDM ile metinden bilgi grafı üretiminde, (a) modelin önerisi ile graf arasına konan deterministik kontroller, insan etiketine göre kaynaktan sapan önerilerin ne kadarını, hangi inceleme emeğiyle yakalar; (b) insanın verdiği kararlar saklanıp yeniden kullanıldığında inceleme emeği ve fark edilmeyen hata nasıl değişir?

**Hipotezler.** Eşikler ön çalışmadaki ölçümlerin altında seçilmiştir, çünkü o ölçümler insan etiketine karşı yapılmamıştır.

- **H1.** Yalnız şema verilen model koşulunda değer-alıntıda kontrolü, insan etiketiyle eşleşmeyen önerilerin en az %60'ını işaretler ve aynı inceleme payında modelin güven skorundan daha fazla eşleşmeyen öneri bulur. (Ön çalışma, platform etiketi: %84; 122'ye karşı 50.)
- **H2.** Kontrollerden geçip incelemesiz kabul edilen önerilerde hata oranı (1 − precision), modelin ham önerilerine göre en az %50 düşer. (Ön çalışma: 0,086'dan 0,015'e.)
- **H3.** Bir inceleyicinin bir adayı reddetme ya da düzeltme olasılığı, kontrollerin işaretlediği adaylarda işaretlemediklerine göre anlamlı biçimde yüksektir (aday düzeyinde lojistik model, hadis düzeyinde kümelenmiş, p < 0,05).
- **H4.** Gerçek inceleyici kararlarıyla çalışan ve kapsamı çelişkide daralan kimlik defteri, öğrenci ve ada sabitlenmiş deftere göre en az %20 daha az soru sorar; iki defterin geçiş başına sessiz hata farkı 0,02'yi aşmaz. (Benzetim: %32–48 daha az soru; fark 0,003–0,008.)

## 1.2. Amaç ve Hedefler

**Genel amaç.** Modelin yalnız önerdiği, kontrollerin ve insanın karar verdiği, her kabulün kaydedildiği bir bilgi grafı üretim motorunu insan etiketine ve gerçek inceleyiciye karşı ölçmek; insan kararının saklanıp yeniden kullanılmasının inceleme emeğini ne kadar azalttığını göstermek.

**Özgül ve ölçülebilir hedefler.**

- **Hedef 1 (referans kümesi).** 300 hadis iki bağımsız kodlayıcı tarafından etiketlenir. İki kodlayıcının karşılıklı F1 değeri (gevşek eşleştirme) en az 0,85'tir; altında kalırsa kılavuz düzeltilir ve tur tekrarlanır. Hadis başına ortalama etiketleme süresi raporlanır.
- **Hedef 2 (ölçüm).** Dört koşul, en az üç model ve ikişer tekrar için precision, recall ve F1; katı ve gevşek eşleştirmede, hadis düzeyinde bootstrap güven aralıklarıyla raporlanır. H1 ve H2 sınanır.
- **Hedef 3 (inceleyici).** 300 hadisin inceleme öğelerinin tamamına bir inceleyici karar verir; inceleme sonrası precision ve recall, red oranı ve karar başına medyan süre raporlanır. H3 sınanır.
- **Hedef 4 (karar defteri).** Defter motora eklenir ve testleri gerçek veritabanlarında geçer; inceleyicinin kimlik kararlarıyla soru sayısı ve sessiz hata ölçülür. H4 sınanır.
- **Hedef 5 (yaygın etki ve açık bilim).** Motor, ölçüm betikleri ve referans etiketleri açık lisansla yayımlanır; sonuçlar en az bir hakemli bilimsel etkinlikte bildiri olarak sunulur ve ön baskı olarak paylaşılır.

Hedefler, motorun ve ölçüm betiklerinin ön çalışma olarak hazır olması sayesinde altı ayda ve üç kişilik bir ekiple erişilebilir tutulmuştur.

# 2. YÖNTEM

Araştırma, tasarım bilimi yaklaşımını [@hevner2004design; @wieringa2014design] kontrollü deneysel değerlendirmeyle birleştirir: bir yapıt (motor) kurulur ve ölçülebilir ölçütlere karşı değerlendirilir.

## 2.1. Mevcut Motor ve Bu Projede Eklenecekler

Motorun akışı şudur: kaynak birimi → isnad bölütleyici → model önerisi → kontroller → inceleme → kanonik graf. Modelin grafa yazma yetkisi yoktur.

Ön çalışmada hazır olanlar: şema sürümleme; hadisin tek kaynak birimi olarak alınması; kural tabanlı isnad bölütleyici; şemaya bağlı model çıkarımı; on iki gerekçe kodu üreten doğrulama (alıntı kaynakta mı, değer alıntıda mı, tip şemada mı ve diğerleri); inceleme kuyruğu; kimin, ne zaman, ne kadar sürede karar verdiğini tutan karar kaydı; aynı iki ravi arasındaki ayrı aktarımları ayrı tutan ilişki kimliği; zincir görünümü; puanlama ve analiz betikleri.

Bu projede eklenecekler:

- **E-1. Kararın içeriğe bağlanması.** İnceleme kararı aday kimliği yerine (hadis, normalize ad) hedefine bağlanır; böylece metin yeniden çıkarıldığında karar kaybolmaz. Ön çalışmada, aynı modelin iki istemi arasında adayların 0,857–0,977'sinin, kural tabanlı ayrıştırıcı ile model arasında 0,561–0,634'ünün hedefi bulunmuştur.
- **E-2. Kimlik karar defteri.** Her kimlik kararı tam bağlamıyla (önceki ravi, ad, sonraki ravi) saklanır. Kararın hangi bağlamda yeniden kullanılacağı saklanmaz; her ad için en geniş kapsamla başlar ve çelişki görüldükçe daralır.
- **E-3. Alan kuralı kancası.** Defterin önerdiği kişi ile komşu ravi arasındaki tabaka ve vefat yılı farkı sınırların dışındaysa öğe inceleyiciye sorulur ve o adın kapsamı daraltılır. Kural olguyu reddetmez; soru üretir.
- **E-4. Dönüşüm kuralı.** Yalnız hâl eki değişmiş adlar otomatik kabul edilir ve kabul eden kural kayda geçer.

## 2.2. Değişkenler ve Ölçütler

Bağımsız değişkenler: çıkarım koşulu (dört düzey); model (en az üç düzey); kontrol (yok, alıntı-kaynakta, değer-alıntıda); defter politikası (yalnız ad; öğrenci ve ad; kuralla daralan kapsam).

Bağımlı değişkenler, ravi geçişi düzeyinde ve insan etiketine karşı:

- Precision, recall ve F1; katı (normalize diziler eşit) ve gevşek (eşit, alt dizi ya da belirteç F1 ≥ 0,60) eşleştirme, sistem ve referans geçişleri arasında en büyük ağırlıklı eşleştirme ile. Eşleştirme ölçütü ölçümden önce sabittir.
- Kontrolün işaretlediği öneri payı ve bunların içinde etiketle eşleşmeyenlerin payı.
- İnceleme: gerekçe koduna göre red ve düzeltme oranı, karar başına süre.
- Defter: geçiş başına soru sayısı; geçiş başına sessiz hata (yeniden kullanılan ve inceleyicinin kararıyla çelişen cevap).

Analiz birimi hadistir.

## 2.3. Veri ve Referans Kümesinin Oluşturulması

300 hadis, altı kitaptan tabakalı örneklemdir; ön çalışmadaki test kümesiyle aynıdır, böylece platform etiketiyle insan etiketi aynı hadislerde karşılaştırılabilir. Metin Arapçadır. Telifsiz, tam isnad içeren bir Türkçe kaynak bulunamadığı için Türkçe metin kapsam dışıdır; kılavuz ve arayüz Türkçedir.

İki ekip üyesi aynı hadisleri yazılı bir kılavuzla, birbirinden bağımsız ve sistem çıktısını görmeden etiketler. Kontrolleri yazan kişi etiketlemez. Önce 50 hadislik bir kalibrasyon turu yapılır, uyum ve süre ölçülür, kılavuz düzeltilir; sonra kalan hadisler etiketlenir. Anlaşmazlıklar alan uzmanının hakemliğiyle çözülür. Uzman inceleme kuyruğunda karar vermez; inceleyici, o hadisin etiketini üretmemiş ekip üyesidir. Böylece aynı kişi hem sistemi düzeltip hem ölçütü belirlemez.

Uyum, iki kodlayıcının karşılıklı F1 değeriyle ölçülür. Açık uçlu çıkarımda birim sayısı baştan belli olmadığından Cohen kappa yerine bu ölçü seçilmiştir.

Yayımlanan küme yalnız etiketleri ve kaynak kimliklerini içerir; hadis metnini içermez.

## 2.4. Deney Tasarımı ve İstatistiksel Yöntem

- **Koşullar ve modeller.** 4 koşul × en az 3 model × 2 tekrar × 300 hadis. Model yanıtları önbelleğe alınır; aynı koşu yeniden üretilebilir. Koşullar arası fark, hadis düzeyinde eşli bootstrap aralığıyla verilir.
- **H1 ve H2.** Kontrolün işaretlediği ve işaretlemediği önerilerin insan etiketiyle eşleşme tablosundan hesaplanır; güven skoruyla karşılaştırma, aynı sayıda önerinin incelemeye gönderildiği noktada yapılır.
- **H3.** Aday düzeyinde lojistik regresyon; sonuç değişkeni inceleyicinin reddi ya da düzeltmesi, açıklayıcılar gerekçe kodları ve güven skoru; standart hatalar hadis düzeyinde kümelenir.
- **H4.** İnceleyicinin kimlik kararları sırayla defterden geçirilir; üç politika aynı kararlar üzerinde karşılaştırılır; belirsizlik, hadis sırasının yeniden karıştırılmasıyla verilir.
- **K-5.** Kod ajanı deneyi aynı sorular ve aynı cevap anahtarıyla başka bir model ailesinden bir modelle ve ikinci bir kod tabanı için yazılacak yeni bir soru kümesiyle tekrarlanır; analiz birimi sorudur.

Bir koşunun başarısız olması (örneğin modelin çıktı biçimini üretememesi) sonuç olarak raporlanır, veri dışı bırakılmaz.

## 2.5. Ön Çalışma ve Bu Projenin Sınırı

Ön çalışma motoru, ölçüm betiklerini ve platform etiketine karşı ilk ölçümleri kapsar (Bölüm 1.1). TÜBİTAK desteği bunların yeniden yapılmasına değil, eksik olan üç şeye harcanır: insan etiketi, gerçek inceleyici ve karar defterinin motora alınıp gerçek kararlarla sınanması. Yöntem adımları Bölüm 3'teki çalışma takvimiyle birebir eşleştirilmiştir.

# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

| Tarih Aralığı | Faaliyetler | Kim(ler) Tarafından Gerçekleştirileceği | Başarı Ölçütü ve Araştırmanın Başarısına Katkısı |
|---|---|---|---|
| 1.–2. Ay | İP1: Etiketleme kılavuzu; 50 hadislik kalibrasyon turu; uyum ve süre ölçümü; kılavuzun düzeltilmesi. Kararın içeriğe bağlanması (E-1). | Tüm ekip (alan uzmanı danışmanlığında) | Çıktı: kılavuz v2, 50 hadiste iki kodlayıcının etiketleri. Başarı: karşılıklı F1 ve hadis başına süre raporlanmıştır; E-1 testleri geçer. Katkı: %20 |
| 2.–4. Ay | İP2: Kalan 250 hadisin etiketlenmesi ve uzman hakemliği; dört koşulun en az üç modelle, ikişer tekrarla koşulması; kontrollerin insan etiketine karşı ölçümü. | Tüm ekip (alan uzmanı hakemliğinde) | Çıktı: 300 hadislik referans kümesi, sonuç tablosu. Başarı: karşılıklı F1 ≥ 0,85; H1 ve H2 sınanmıştır. Katkı: %30 |
| 3.–5. Ay | İP3: Kimlik karar defteri, alan kuralı kancası ve dönüşüm kuralı (E-2, E-3, E-4); inceleyicinin 300 hadisin inceleme öğelerine karar vermesi; defterin gerçek kararlarla ölçümü. | Tüm ekip | Çıktı: defterli motor sürümü, inceleme kayıtları. Başarı: testler gerçek veritabanlarında geçer; H3 ve H4 sınanmıştır; karar başına süre raporlanmıştır. Katkı: %30 |
| 5.–6. Ay | İP4: İkinci alanda tekrar (K-5); motorun, betiklerin ve etiketlerin açık yayını; sonuç raporu; bildiri ve ön baskı. | Tüm ekip | Çıktı: açık kod ve veri, sonuç raporu, bildiri taslağı. Başarı: sonuçlar temiz bir klondan betiklerle yeniden üretilir. Katkı: %20 |

İş paketleri planlı olarak örtüşür; etiketleme sürerken motor geliştirmesi ilerler.

## 3.2. Risk Yönetimi

| En Önemli Riskler | Alınacak Tedbirler (B Planı) |
|---|---|
| R1: Kullanılan etiketli derlemlerin ya da ravi kataloğunun lisansı teyit edilemez. | Yalnız lisansı açık metin ve ekibin kendi etiketleri kullanılır; diğer derlemler yeniden dağıtılmadan, yalnız ölçüm için kullanılır. Yayımlanan küme metin içermez. |
| R2: İki kodlayıcının uyumu hedefin altında kalır. | Kılavuza sınır kuralları eklenir ve kalibrasyon turu tekrarlanır; gerekirse küme 300'den 200 hadise indirilir ve kalite önceliklendirilir. |
| R3: Etiketleme ve inceleme planlanandan uzun sürer. | Süre ilk 50 hadiste ölçülür ve kalan iş buna göre boyutlandırılır; inceleme, yalnız kontrollerin işaretlediği öğelerle sınırlandırılabilir. |
| R4: Model erişimi kesilir, maliyet aşılır ya da bir model istenen çıktı biçimini üretemez. | Aynı arayüzden açık ağırlıklı bir model kullanılır; hadis sayısı azaltılır. Biçim hatasıyla sonuçlanan koşu sonuç olarak raporlanır. |
| R5: Akademik dönem yoğunluğu takvimi kaydırır. | Motor ve betikler hazır olduğu için kritik yol etiketlemedir; her iş paketine %15 zaman payı bırakılmıştır; tekrar sayısı ikiden bire indirilebilir. |
| R6: Ön çalışmanın kapsamı, projenin büyük kısmının yapılmış olduğu izlenimini verir. | Bu formda neyin yapıldığı ve neyin yapılmadığı ayrı ayrı yazılmıştır. Destek yalnız eksik olan insan etiketi, inceleyici ölçümü ve karar defteri için kullanılır. |
| R7: Yapay zekâ asistanlarıyla yazılmış kod, ekibin tam anlamadığı davranışlar içerir. | Kod yalnız testleriyle kabul edilir; her iş paketinin başında ilgili modül ekipçe gözden geçirilir; ölçülen her sayı bir betikle yeniden üretilir. |

## 3.3. Araştırma Olanakları

| Kuruluşta Bulunan Altyapı/Ekipman Türü, Modeli | Projede Kullanım Amacı |
|---|---|
| Akdeniz Üniversitesi Bilgisayar Mühendisliği Bölümü yazılım geliştirme laboratuvarı | Geliştirme ortamı, kod gözden geçirme oturumları, etiketleme oturumları |
| Bölüm sunucu altyapısı ve kampüs ağı | PostgreSQL ve Neo4j örneklerinin barındırılması |
| Akdeniz Üniversitesi İlahiyat Fakültesi, Prof. Dr. Rifat Atay'ın alan uzmanı desteği | Etiketleme kılavuzunun gözden geçirilmesi, anlaşmazlıklarda hakemlik, ravi kaynaklarına akademik erişim |
| GiraffeGraph Core motoru, ölçüm betikleri ve ön çalışma sonuçları (ekibin önceki çalışması) | Projenin üzerine kurulduğu yapıt; geliştirme süresince özel bir depoda tutulur |

# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Çıktı, Etki ve Kazanımlar | Öngörülen Çıktı(lar), Etki(ler) ve Kazanım(lar) |
|---|---|
| **Bilimsel/Akademik Çıktılar** | (i) En az bir ulusal ya da uluslararası hakemli etkinlikte bildiri. (ii) Sonuçların ön baskı olarak yayımlanması. (iii) Bitirme tezi. |
| **Ekonomik/Ticari/Sosyal Çıktılar** | (i) Motorun ve ölçüm betiklerinin açık kaynak lisansıyla yayımlanması. (ii) İki kodlayıcılı, uyumu raporlanmış 300 hadislik isnad referans kümesinin, metin içermeden, açık veri olarak yayımlanması. (iii) Bölüm öğrencilerine yönelik bir seminer. |
| **Yeni Proje(ler) Oluşturmasına Yönelik Çıktılar** | (i) Ravi adlarının bir otorite listesine bağlanması ve graf üzerinden soru cevaplama için takip çalışması. (ii) Kontrollerin ve karar defterinin hadis dışı bir alanda ikinci vaka çalışması. (iii) Bilgisayar Mühendisliği ile İlahiyat arasındaki iş birliğinin sürdürülmesi. |

Çıktıların sınırı açıkça belirtilir: motorun başka bir alanda aynı sonucu vereceği gösterilmemiştir; ön çalışmada bir kontrol hadis dışında aynı işi görmemiştir (Bölüm 1.1).

# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

**Ön çalışma beyanı.** Motor, ölçüm betikleri ve Bölüm 1.1'deki ölçümler TÜBİTAK desteği ve başka bir finansman olmadan yapılmıştır. Destek yalnız bu öneride tanımlanan işler için kullanılacaktır.

**Yapay zekâ kullanımı beyanı.** Üretken yapay zekâ araçları bu projede yaygın biçimde kullanılmıştır: literatür aramasında, motor kodunun büyük kısmının ve analiz betiklerinin yazımında, ön çalışma deneylerinin yürütülmesinde ve bu formun taslağında. Kullanım, TÜBİTAK'ın üretken yapay zekâ rehberi [@tubitak2024uyz] gözetilerek beyan edilmektedir. Riskleri sınırlamak için uygulanan kurallar: kaynakça kayıtları bellekten yazılmaz, dizinlerden çekilir; ölçülen her sayı bir betikle üretilir ve bir sonuç dosyasında durur; kod yalnız testleriyle kabul edilir; başka çalışmalar hakkındaki ifadeler okunan kaynakla sınırlıdır. İçeriğin sorumluluğu ekibe aittir. Ayrıca çıkarım deneylerinde dil modeli, sınanan sistemin kendisidir.

**Veri ve lisans.** Hadis metinleri üçüncü taraf kaynaklardan gelir ve yalnız değerlendirme için kullanılır; yeniden dağıtılmaz. Yayımlanacak referans kümesi metin içermez.

**Açık bilim.** Kod, üçüncü taraf metinle aynı depoda bulunduğu için geliştirme süresince özel tutulmaktadır; proje sonunda motor ve betikler açık kaynak lisansıyla yayımlanacaktır.

**Alan uzmanı desteği.** Prof. Dr. Rifat Atay etiketleme kılavuzunun gözden geçirilmesinde ve anlaşmazlıkların hakemliğinde danışmanlık verecektir.

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
