# TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı: Araştırma Önerisi Formu

> **Taslak, gönderilmedi (2026-10-25).** Bu sürüm ekibin 25 Ekim proje özetini izler ve danışmanın okuması içindir. Göndermeden önce karara bağlanacak noktalar en sondaki "Göndermeden önce" bölümündedir; o bölüm ve bu kutu başvuru metnine girmez.

# A. GENEL BİLGİLER

| | |
|---|---|
| **Başvuru Sahibinin Adı Soyadı** | Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya |
| **Araştırma Önerisinin Başlığı** | Büyük Dil Modellerinde Halüsinasyon ve Şema Sapmasını Önleyen İnsan-Döngülü Bilgi Grafı Üretim Motoru: Hadis İsnad Zincirleri Üzerine Bir Uygulama |
| **Danışmanın Adı Soyadı** | Arş. Gör. Dr. Taha Yiğit Alkan |
| **Araştırmanın Yürütüleceği Kurum/Kuruluş** | Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü (alan uzmanı desteği: Akdeniz Üniversitesi İlahiyat Fakültesi ve iki hadis uzmanı) |

# ÖZET

Büyük dil modelleri (BDM), metin işleyen yapay zekâ modelleridir. Metindeki kişiler ve ilişkilerden bilgi grafı, yani bağlantılı bir bilgi ağı oluşturabilirler. Ancak kaynağın desteklemediği olgular üretebilir ve izin verilen bilgi türlerini belirleyen şemadan sapabilirler. Sınayacağımız motorda model öneri üretir; kontroller ve insan kararları hangi önerilerin grafa gireceğini belirler. Kontrol katmanlarını tek tek ekleyerek grafın doğruluğunun ve güvenilirliğinin nasıl değiştiğini, hangi katmanın hangi hatayı azalttığını ölçeceğiz. Kararları yeniden kullanmanın emeğe ve fark edilmeyen hataya etkisini sınayacağız.

Çalışmayı hadislerin başındaki aktarıcı (ravi) zinciri, yani isnad üzerinde yürüteceğiz. Motor ve ilk ölçümler hazırdır. Ön çalışmada, çıkarılan adın modelin kendi alıntısında geçip geçmediğini denetleyen kontrol, 300 hadiste etiketle eşleşmeyen 145 önerinin 122'sini işaretledi. Bu ölçümler insan etiketlerine veya gerçek inceleyici kararlarına dayanmamaktadır. İki ekip üyesi 300 hadisi bağımsız etiketleyecektir. Üç hadis uzmanı kılavuzu gözden geçirecek, anlaşmazlıklarda bağımsız karar verecek ve ortak hataları aramak için üzerinde uzlaşılan 10 rastgele hadisi de değerlendirecektir. Kontrolleri en az üç modelle ölçecek, inceleme süresini ve saklanan kararların yeniden kullanımını sınayacağız.

Üç kişilik ekibimiz altı ayda dört iş paketini tamamlayacaktır.

**Anahtar Kelimeler:** büyük dil modelleri, bilgi grafı, insan-döngülü sistem, kaynağa dayandırma, karar kaydı, hadis isnad zinciri

# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

Modeller metinden bilgi grafı kurabilir [@ye2022generative; @pan2024unifying]. Kaynağın desteklemediği üretim "halüsinasyon" olarak incelenir [@ji2023survey]. Hadis alanında etiketli veri [@mghari2022sanadset; @mahmoud2022arsanad] ve bilgi grafları bulunmaktadır [@kamran2023semantichadith; @kamran2026semantic]. Bir alan derlemesi, uzman doğrulamasının seyrekliğini açık sorunlar arasında sayar [@haque2026hadith]. Hadis bilgi grafı, ontoloji, ravi çıkarımı, varlık eşleştirme ve insan incelemesi [@tsaneva2025validation] ayrı ayrı çalışılmıştır; ilk hadis bilgi grafını kurduğumuzu veya model çıktısını ilk kez doğruladığımızı iddia etmiyoruz. Farkımız, şema kontrolünü, kaynak/kanıt kontrolünü, gerektiğinde insan incelemesini, karar kaydını ve kabul edilen bilginin kanonik grafa yazılmasını aynı boru hattında birleştirip her aşamanın katkısını ölçmektir. Literatür taramamız sistematik değildir.

Ön çalışmada altı kitaptan 300 hadisi platform kaynaklı ravi etiketlerine karşı puanladık. Değer-alıntıda kontrolü, çıkarılan adın modelin kendi alıntısında bulunup bulunmadığını denetler. Bu kontrol, yalnız şema verilen modelin önerilerinin %9,2'sini işaretledi ve etiketle eşleşmeyen 145 önerinin 122'sini yakaladı. Modelin güven skoru, 0,85 eşiğiyle önerilerin %16,3'ünü incelemeye gönderdiğinde bile bunların 50'sini buldu. Alıntı-kaynakta kontrolü, yani alıntının kaynak metinde bulunması denetimi hiçbirini işaretlemedi. Biyomedikal derlemde [@li2016bc5cdr] aynı model ve yalnız şema içeren istemle kontrol 303 eşleşmeyen önerinin 53'ünü, güven skoru 58'ini buldu. Kontrolün hadis dışında aynı sonucu verdiği gösterilmemiştir. İlk ölçümler platform etiketlerine dayanmaktadır; kullanılabilir sonuçlar tek modelden gelmiştir ve insan inceleyici yoktur.

- **K-1. İnsan etiketli isnad referans kümesi.** İki kodlayıcı, kılavuzla ve sistem çıktısını görmeden altı kitaptan 300 hadisin ravi geçişlerini ve sırasını etiketleyecektir. Üç hadis uzmanı anlaşmazlıkları bağımsız değerlendirecektir. Kodlayıcı ve uzman uyumunu, hadis başına süreyi raporlayacağız.
- **K-2. Kontrol katmanlarının insan etiketine karşı ölçümü.** Kural tabanlı ayrıştırıcıyı taban çizgisi alıp yalnız modeli, şema kontrolünü, kanıt kontrollerini ve insan incelemesini sırayla eklediğimiz koşulları karşılaştıracağız. İnceleme gerektirmeyen model koşullarını en az biri açık ağırlıklı en az üç modelle ikişer kez çalıştıracak, insan incelemesini tek modelin bir koşusunda ölçecek ve sonuçları hata türüne göre raporlayacağız.
- **K-3. İnceleyicinin döngüde ölçümü.** Hadisin etiketini üretmemiş kişi inceleme kuyruğunda karar verecektir. İnceleme sonrası precision (önerilerde doğruluk payı), recall (referanstaki bilgiyi bulma payı), gerekçe koduna göre ret oranı ve karar süresini raporlayacağız.
- **K-4. Motorda kimlik karar defteri.** Kararı aday kimliğine değil içeriğe bağlayıp saklayacağız. Ravi kuşağı (tabaka) ve vefat yılı kuralı çelişki bulduğunda kararın kullanım kapsamı daralacaktır. Benzetimi gerçek kararlarla tekrarlayacağız.

Kontrol katmanlarını tek tek eklediğimizde daha doğru ve güvenilir bir bilgi grafı elde ediyor muyuz, hangi katman hangi tür hatayı azaltıyor? Kararların yeniden kullanımı emeği ve fark edilmeyen hatayı nasıl değiştirir? Hipotez eşiklerini, insan etiketine dayanmayan ön çalışma ölçümlerinin altında seçtik.

- **H1.** Yalnız şema verilen modelde değer-alıntıda kontrolü, insan etiketiyle eşleşmeyen önerilerin en az %60'ını işaretler ve aynı inceleme payında güven skorundan fazlasını bulur. (Ön çalışma: %84; kontrol %9,2'lik payla 122, güven skoru %16,3'lük payla 50.)
- **H2.** İncelemesiz kabul edilen önerilerde hata oranı (1 − precision), ham önerilere göre en az %50 düşer. (Ön çalışma: 0,086'dan 0,015'e.)
- **H3.** Ret veya düzeltme olasılığı, işaretlenen adaylarda işaretlenmeyenlere göre anlamlı biçimde daha yüksektir (aday düzeyinde lojistik model, hadis düzeyinde kümelenmiş, p < 0,05).
- **H4.** Gerçek kararlarla kapsamı daralan defter, öğrenciye (zincirde addan önceki raviye) ve ada sabitlenmiş defterden en az %20 az soru sorar. Geçiş başına sessiz hata farkı 0,02'yi aşmaz. (Benzetimde soru azalması %32 ile %48, hata farkı 0,003 ile 0,008 arasındadır.)

## 1.2. Amaç ve Hedefler

Amacımız, kontrollerin ve insan kararlarının belirlediği graf üretimini değerlendirmek ve kararları yeniden kullanmanın inceleme emeğine etkisini ölçmektir.

- **Hedef 1 (referans kümesi).** İki kodlayıcı 300 hadisi bağımsız etiketleyecektir. Karşılıklı F1 (precision ve recall'u birleştiren ölçü), gevşek eşleştirmede en az 0,85 olacaktır. Altında kalırsa kılavuzu düzeltecek, turu tekrarlayacağız. Üç uzmanın kararlarıyla referansı oluşturup uyumlarını ve ortalama etiketleme süresini raporlayacağız.
- **Hedef 2 (ölçüm).** İnsan incelemesi dışındaki dört katman koşulunda, en az biri açık ağırlıklı en az üç modeli ikişer kez çalıştırıp precision, recall ve F1'i katı ve gevşek eşleştirmede, hata türüne göre raporlayacağız. Hadisleri yeniden örnekleyerek belirsizliği hesaplayan bootstrap güven aralıklarını verecek, H1 ve H2'yi sınayacağız.
- **Hedef 3 (inceleyici).** Bir inceleyici 300 hadisin tüm inceleme öğelerinde karar verecektir. İnceleme sonrası precision ve recall'u, ret oranını ve medyan karar süresini raporlayıp H3'ü sınayacağız.
- **Hedef 4 (karar defteri).** Defteri motora ekleyip testlerini gerçek veritabanlarında geçireceğiz. Gerçek kimlik kararlarıyla soru sayısını ve sessiz hatayı ölçüp H4'ü sınayacağız.
- **Hedef 5 (yaygın etki ve açık bilim).** Motoru, betikleri ve referans etiketlerini açık lisansla yayımlayacak; en az bir hakemli etkinlikte bildiri sunup ön baskı paylaşacağız.

# 2. YÖNTEM

Tasarım bilimi yaklaşımıyla motoru geliştirecek [@hevner2004design; @wieringa2014design], kontrollü deneylerle değerlendireceğiz.

## 2.1. Mevcut Motor ve Bu Projede Eklenecekler

Modelin grafa yazma yetkisi yoktur; yalnızca alıntılı öneriler üretir. İnceleyici öneriyi kabul edebilir, reddedebilir veya düzeltebilir. Kabul kaydıyla bilgi grafa girer; her olgunun kaynağını ve kararı kimin verdiğini saklarız; kararlar silinmez ve üzerlerine yazılmaz. İnceleme kuyruğu ve ölçüm betikleri hazırdır.

E-1 ile kararı aday kimliği yerine hadis ve standartlaştırılmış ada bağlayacağız. E-2 ile kimlik kararını komşu ravilerle birlikte saklayacağız. E-3, tabaka ve vefat yılı çelişkisinde inceleyiciye soru soracak ve kullanım kapsamını daraltacaktır. E-4, yalnız hâl eki değişen adları otomatik kabul edecek ve kuralı kaydedecektir.

## 2.2. Değişkenler ve Ölçütler

Çıkarım koşulunu, modeli, kontrolleri ve defter politikasını değiştireceğiz. Politikalar yalnız ada, öğrenci ve ada veya kuralla daralan kapsama dayanacaktır. Katı eşleştirmede standartlaştırılmış adlar eşittir; gevşek eşleştirmede eşitlik, alt dizi veya sözcük düzeyinde F1 ≥ 0,60 aranır. Ölçütü deneyden önce sabitleyeceğiz. İşaretlenen önerilerin payını, ret ve düzeltme oranlarını, süreyi ve geçiş başına soru sayısını ölçeceğiz. Sessiz hata, yeniden kullanılan cevabın inceleyici kararıyla çelişmesidir. Analiz birimi hadistir.

## 2.3. Veri ve Referans Kümesinin Oluşturulması

Altı kitaptan tabakalı örneklenen 300 Arapça hadis, ön çalışmadaki test kümesidir. Telifsiz ve tam isnadlı Türkçe kaynak bulamadığımız için Türkçe metin kapsam dışındadır; kılavuz ve arayüz Türkçedir.

CSE 491 bitirme projesinde iki ekip üyesi 50 hadisi bağımsız etiketler, anlaşmazlıkları hadis uzmanları karara bağlar ve prototip uçtan uca çalışır; TÜBİTAK projesinde insan etiketli kümeyi 300 hadise genişletecek, deneyleri en az üç modelle tekrarlayacak, ravi kimliği ve karar defterini ekleyeceğiz.

Dr. Öğr. Üyesi Tunahan Erdoğan (Akdeniz Üniversitesi İlahiyat Fakültesi, Temel İslam Bilimleri Bölümü, Arap Dili ve Belagatı Anabilim Dalı) ve ilk ay belirlenecek iki hadis uzmanı, 300 hadislik küme için kılavuzu gözden geçirecektir. İki ekip üyesi sistem çıktısını görmeden bağımsız etiketleyecek; kontrolleri yazan kişi etiketlemeyecektir. Bitirme projesindeki ilk 50 hadisin uyum ve süre ölçümlerine göre kılavuzu düzelteceğiz.

Kodlayıcıların anlaşamadığı her öğeyi üç uzman birbirinden bağımsız değerlendirecektir. Çoğunluk kararı referansa girecektir. Üç cevap da farklıysa öğeyi "tartışmalı" işaretleyip ana puandan çıkaracak ve ayrı raporlayacağız. Kodlayıcıların uzlaştığı rastgele 10 hadisi de ortak hataları aramak için uzmanlara göndereceğiz. Kodlayıcıların karşılıklı F1 değerinin yanında uzmanların uyumunu Fleiss' kappa ile, yani rastlantısal uzlaşmayı hesaba katan ölçüyle raporlayacağız.

Uzmanlar sistem çıktısını görmeyecek ve inceleme kuyruğunda karar vermeyecektir. İnceleyici, hadisin etiketini üretmemiş ekip üyesidir; referansı belirleyen kişi sistemi de yargılamayacaktır. Yayımlanan küme yalnız etiketleri ve kaynak kimliklerini içerecektir.

## 2.4. Deney Tasarımı ve İstatistiksel Yöntem

Beş koşulu karşılaştıracağız: kural tabanlı ayrıştırıcı (taban çizgisi); yalnız model; model + şema kontrolü; model + şema kontrolü + kanıt kontrolleri (alıntı-kaynakta ve değer-alıntıda); model + bütün kontroller + insan incelemesi. İnceleme gerektirmeyen model koşullarını en az biri açık ağırlıklı en az üç modelle, ikişer kez ve 300 hadiste çalıştıracağız. İnsan incelemesi koşulunda inceleyici, tek modelin bir koşusundaki inceleme öğelerine bir kez karar verecektir (Hedef 3). Kaynakta olmayan ravi, adı değiştirilen ravi, şema dışı öneri ve sıra hatası gibi hata türlerini ayrı raporlayarak her katmanın katkısını ölçeceğiz. Yanıtları saklayacak, koşul farklarını hadis düzeyinde eşli bootstrap aralıklarıyla vereceğiz. H1 ve H2'de insan etiketleriyle eşleşmeyi, güven skoruyla aynı inceleme payında karşılaştıracağız. H3'te gerekçe kodları ve güven skoruyla ret veya düzeltme olasılığını lojistik regresyon adlı istatistiksel yöntemle hesaplayıp standart hataları hadis düzeyinde kümeleyeceğiz. H4'te aynı kimlik kararlarını üç politikadan geçirecek, hadis sırasını karıştırarak belirsizliği ölçeceğiz.

## 2.5. Ön Çalışma ve Bu Projenin Sınırı

Motor ve ilk ölçümler tamamlanmıştır. Destek, insan etiketleri, gerçek inceleyiciyle değerlendirme ve karar defterinin eklenip sınanması içindir.

# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

| Tarih Aralığı | Faaliyetler | Kim(ler) Tarafından Gerçekleştirileceği | Başarı Ölçütü ve Araştırmanın Başarısına Katkısı |
|---|---|---|---|
| 1.-2. Ay | İP1: Bitirme projesindeki 50 hadisin uyum ve süre ölçümlerine göre kılavuzu düzeltecek; E-1'i ekleyeceğiz. | Tüm ekip; üç uzman kılavuzu gözden geçirecektir. | Kılavuz v2 ve etiketler hazırlanacak; karşılıklı F1 ve süre raporlanacak, E-1 testleri geçecektir. Katkısı %20'dir. |
| 2.-4. Ay | İP2: Kalan 250 hadisi etiketleyecek, inceleme gerektirmeyen katman koşullarını en az üç modelle ikişer kez çalıştıracağız. | Tüm ekip; üç uzman bağımsız değerlendirecektir. | 300 hadislik referans ve sonuç tablosu hazırlanacak; F1 ≥ 0,85 olacak, H1 ve H2 sınanacaktır. Katkısı %30'dur. |
| 3.-5. Ay | İP3: E-2, E-3, E-4'ü ekleyip 300 hadisi inceleyeceğiz. | Tüm ekip çalışacaktır. | Defterli motor ve kayıtlar hazırlanacak; gerçek veritabanı testleri geçecek, H3 ve H4 sınanacak, süre raporlanacaktır. Katkısı %30'dur. |
| 5.-6. Ay | İP4: Kodu ve veriyi yayımlayacak; rapor, bildiri ve ön baskı hazırlayacağız. | Tüm ekip çalışacaktır. | Açık kod, veri, rapor ve bildiri taslağı hazırlanacak; sonuçlar temiz klondan yeniden üretilecektir. Katkısı %20'dir. |

## 3.2. Risk Yönetimi

| En Önemli Riskler | Alınacak Tedbirler (B Planı) |
|---|---|
| R1: Derlem veya ravi kataloğu lisansı doğrulanamaz. | Açık lisanslı metinleri ve kendi etiketlerimizi kullanacağız; diğer derlemleri dağıtmadan ölçeceğiz. |
| R2: Kodlayıcı uyumu düşük kalır. | Kılavuzu düzeltip kalibrasyonu tekrarlayacağız; gerekirse 300 hadisi 200'e indireceğiz. |
| R3: Etiketleme ve inceleme uzar. | İlk 50 hadisin süresine göre planlayacak; incelemeyi işaretlenen öğelerle sınırlayabileceğiz. |
| R4: Model erişimi, maliyeti veya çıktı biçimi sorun olur. | Açık ağırlıklı model kullanıp hadis sayısını azaltacağız; başarısız koşuyu raporlayacağız. |
| R5: Akademik yoğunluk takvimi kaydırır. | Her pakette %15 zaman payı vardır; tekrarları ikiden bire indirebiliriz. |
| R6: Projenin çoğu tamamlanmış görünebilir. | Desteği insan etiketi, inceleyici ölçümü ve karar defteri için kullanacağız. |
| R7: Yapay zekâ kodunun davranışı anlaşılmayabilir. | Kodu testlerle kabul edecek, paket başında modülü inceleyecek, sayıları betikle üreteceğiz. |
| R8: Bir uzman katılamaz veya gecikir. | İki uzmanla çalışacağız; anlaşamadıkları öğeyi "tartışmalı" işaretleyeceğiz. |

## 3.3. Araştırma Olanakları

| Kuruluşta Bulunan Altyapı/Ekipman Türü, Modeli | Projede Kullanım Amacı |
|---|---|
| Akdeniz Üniversitesi Bilgisayar Mühendisliği yazılım geliştirme laboratuvarı | Geliştirme, kod inceleme ve etiketleme oturumlarında kullanacağız. |
| Bölüm sunucuları ve kampüs ağı | PostgreSQL ve Neo4j veritabanlarını barındıracağız. |
| Dr. Öğr. Üyesi Tunahan Erdoğan (Akdeniz Üniversitesi İlahiyat Fakültesi, Temel İslam Bilimleri Bölümü, Arap Dili ve Belagatı Anabilim Dalı) ve ilk ay belirlenecek iki hadis uzmanı | Kılavuz incelemesi, bağımsız kararlar ve ravi kaynaklarına erişim desteği alacağız. |
| GiraffeGraph Core, betikler ve ön çalışma sonuçları | Motoru geliştirecek, depoyu geliştirme süresince özel tutacağız. |

# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Çıktı, Etki ve Kazanımlar | Öngörülen Çıktı(lar), Etki(ler) ve Kazanım(lar) |
|---|---|
| **Bilimsel/Akademik Çıktılar** | En az bir hakemli etkinlikte bildiri sunacak, ön baskı yayımlayacak ve bitirme tezi hazırlayacağız. |
| **Ekonomik/Ticari/Sosyal Çıktılar** | Motoru ve betikleri açık kaynak, uyumu raporlanmış 300 hadislik etiket kümesini metinsiz açık veri olarak yayımlayacak; bölümde seminer düzenleyeceğiz. |
| **Yeni Proje(ler) Oluşturmasına Yönelik Çıktılar** | Ravi adlarını otorite listesine bağlama ve grafla soru cevaplama çalışmaları yapacağız. İlahiyat ile iş birliğini sürdüreceğiz. |

# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

Ön çalışma beyanı: Motoru ve ilk ölçümleri finansman almadan tamamladık.

Yapay zekâ kullanımı beyanı: Literatür aramasında, kodun büyük kısmında, betiklerde, deneylerde ve form taslağında üretken yapay zekâ kullandık [@tubitak2024uyz]. Kaynakça kayıtlarını dizinlerden alıyor, sayıları betikle üretip saklıyor, kodu testlerle kabul ediyoruz. İçeriğin sorumluluğu ekibimizdedir.

Veri ve açık bilim: Üçüncü taraf hadis metinlerini değerlendirmede kullanıp dağıtmayacağız. Bu metinlerle aynı depodaki kodu geliştirme süresince özel tutup proje sonunda açacağız.

Alan uzmanı desteği: Dr. Öğr. Üyesi Tunahan Erdoğan ve ilk ay belirlenecek iki hadis uzmanı kılavuzu gözden geçirecek ve anlaşmazlıklarda bağımsız karar verecektir. Sistem çıktısını görmeyecek, inceleme kuyruğunda karar vermeyeceklerdir.

# 6. EKLER

## EK-1: KAYNAKLAR

<!-- references -->

# Göndermeden önce (başvuru metnine girmez)

1. **Başvuru dönemi ve form şablonu.** Bu metin 2026 yılı I. dönem formunun başlıklarını izler. Güncel dönemin şablonu ve sayfa sınırı başvuru sisteminden kontrol edilir.
2. **Başvuru sahipleri.** Liste bitirme projesi ekibidir. Sıra ve yürütücü, başvuru sistemindeki role göre yazılır.
3. **Çerçeve.** Kapsam, ekibin 25 Ekim proje özetini (Alperen Ulukaya) izler; danışman onaylamamıştır.
4. **Alan uzmanlarının desteği.** Üç hadis uzmanının destek beyanları alınmalıdır. Beyanlar, kılavuzu gözden geçirme ve anlaşmazlıklarda bağımsız karar verme rollerini kapsamalı; uzmanların inceleme kuyruğunda karar vermeyeceğini belirtmelidir.
5. **Eşikler.** H1 (%60), H2 (%50), H4 (%20 ve 0,02) ve Hedef 1 (karşılıklı F1 ≥ 0,85) öneridir. Verilen söz bağlar; ekip ve danışman onaylar.
6. **Metin kaynağı ve lisans.** 300 hadislik test kümesinin metin ve etiket kaynaklarının lisansı teyit edilmemiştir (`data/README.md`). R1'deki B planı buna göre yazılmıştır.
7. **Kalkınma planı ve program öncelikleri.** Önceki taslaktaki "12. Kalkınma Planı ile doğrudan ilişkilidir" cümlesi buraya alınmamıştır, çünkü plan metni okunmamıştır. Eklenecekse planı okuyan biri yazar.
8. **Bütçe.** Bu formda bütçe bölümü yoktur; başvuru sisteminde girilir. Model kullanım bedeli ve varsa etiketleme giderleri orada yazılır.
