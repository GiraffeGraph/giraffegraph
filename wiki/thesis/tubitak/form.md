# TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı: Araştırma Önerisi Formu

> **Taslak, gönderilmedi (2026-11-05).** Bu sürüm ekibin 25 Ekim proje özetini izler; danışmanın 5 Kasım geri bildirimi ve gönderdiği belgeyle yeniden yazıldı, danışmanın okuması içindir. Göndermeden önce karara bağlanacak noktalar en sondaki "Göndermeden önce" bölümündedir; o bölüm ve bu kutu başvuru metnine girmez.

# A. GENEL BİLGİLER

| | |
|---|---|
| **Başvuru Sahibinin Adı Soyadı** | Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya |
| **Araştırma Önerisinin Başlığı** | Büyük Dil Modelleriyle Bilgi Grafı Üretiminde Doğrulama Denetimlerinin ve İnsan İncelemesinin Etkisi: Hadis İsnad Zincirleri Üzerine Bir Uygulama |
| **Danışmanın Adı Soyadı** | Arş. Gör. Dr. Taha Yiğit Alkan |
| **Araştırmanın Yürütüleceği Kurum/Kuruluş** | Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü (alan uzmanı desteği: Akdeniz Üniversitesi İlahiyat Fakültesi ve iki hadis uzmanı) |

# ÖZET

Hadis isnadlarının bilgi grafına dönüştürülmesinde ravi adlarının doğru çıkarılması ve aktarım sırasının korunması gerekir. Büyük dil modelleri (BDM), kaynak metinde bulunmayan raviler önerebilir veya tanımlanan şemadan sapabilir. Şemaya uygun bir önerinin kaynak tarafından desteklenip desteklenmediği de ayrıca sınanmalıdır. Bu projede şema denetiminin, kanıt denetimlerinin ve insan incelemesinin bilgi çıkarma başarısına etkisi karşılaştırılacaktır. Ravi kimliği kararlarının yeniden kullanılmasının inceleme yükünü ve sessiz hatayı nasıl değiştirdiği araştırılacaktır.

Motor ve ilk ölçümler hazırdır. Ön çalışmada adın alıntıda bulunması denetimi, altı hadis kitabından seçilen 300 hadiste platform etiketleriyle eşleşmeyen 145 önerinin 122'sini işaretledi. Bu sonuç insan etiketlerine dayanmamaktadır; ön çalışmada gerçek inceleyici kararları da kullanılmadı. Projede iki ekip üyesi aynı 300 hadisin ravi geçişlerini ve isnad sırasını sistem çıktısını görmeden bağımsız etiketleyecektir. Üç alan uzmanının bağımsız kararlarıyla anlaşmazlıklar çözülecek, üzerinde uzlaşılan rastgele 10 hadis ortak hatalar açısından değerlendirilecektir.

Kural tabanlı ayrıştırıcı ile model, şema denetimi, kanıt denetimleri ve insan incelemesinin aşamalı olarak eklendiği koşullar karşılaştırılacaktır. İncelemesiz model koşulları, en az biri açık ağırlıklı olmak üzere en az üç modelle ikişer kez yürütülecektir. İnsan incelemesi tek modelin bir koşusunda, bir kez uygulanacaktır. Kesinlik (precision), duyarlılık (recall) ve F1 ile hata türleri raporlanacak; inceleme kararları, süreler ve karar defterinin yeniden kullanımından doğan sessiz hatalar ölçülecektir. Koşullar arasındaki farklar hadis düzeyinde eşli bootstrap güven aralıklarıyla değerlendirilecektir.

Araştırma, üç kişilik ekip tarafından altı ayda dört iş paketinde yürütülecektir. İş paketleri kılavuz ve karar kayıtlarının hazırlanmasını, referans kümesi ve model deneylerini, karar defteri ve insan incelemesini, analiz ve tekrarlanabilirliği kapsar. Motor, deney betikleri ve kaynak kimlikleriyle birlikte referans etiketleri açık lisanslarla yayımlanacaktır. Üçüncü taraf hadis metinleri dağıtılmayacaktır. Sonuçların en az bir hakemli bilimsel etkinliğe bildiri olarak gönderilmesi ve ön baskı olarak paylaşılması hedeflenmektedir.

**Anahtar Kelimeler:** büyük dil modelleri, bilgi grafı, insan-döngülü sistem, kaynağa dayandırma, karar kaydı, hadis isnad zinciri

# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

Hadis isnadı, bir rivayeti aktaran kişileri belirli bir sırayla gösterir. İsnadın bilgi grafına dönüştürülmesi, ravi adlarının çıkarılmasını, aynı kişiye ait farklı adların eşleştirilmesini ve aktarım ilişkilerinin korunmasını gerektirir. Bir adın kaynakta geçmesi, o adın doğru ravi kimliğiyle eşleştirildiğini göstermez. Ad, kimlik ve sıra hataları bu nedenle ayrı değerlendirilecektir.

Modellerin metinden bilgi grafı üretmesine yönelik çalışmalar bulunmaktadır [@ye2022generative; @pan2024unifying]. Kaynağın desteklemediği üretim, halüsinasyon başlığı altında incelenir [@ji2023survey]. Hadis alanında etiketli veri kümeleri [@mghari2022sanadset; @mahmoud2022arsanad] ve bilgi grafları geliştirilmiştir [@kamran2023semantichadith; @kamran2026semantic]. Bir alan derlemesi, uzman doğrulamasının seyrekliğini açık sorunlar arasında sayar [@haque2026hadith]. İnsan incelemesine dayalı doğrulama da araştırılmıştır [@tsaneva2025validation]. Projenin özgün katkısı, şema ve kanıt denetimleriyle insan incelemesini aynı boru hattında karşılaştırmak ve kimlik kararlarının yeniden kullanımının doğruluk ile inceleme yükü üzerindeki etkisini ölçmektir. Literatür taraması sistematik değildir.

Ön çalışmada altı kitaptan 300 hadis, platform kaynaklı ravi etiketlerine karşı puanlandı. Adın alıntıda bulunması denetimi, yalnız şema verilen modelin önerilerinin %9,2'sini işaretledi ve etiketle eşleşmeyen 145 önerinin 122'sini buldu. Modelin güven skoru, 0,85 eşiğinde önerilerin %16,3'ünü incelemeye ayırırken eşleşmeyen önerilerin 50'sini buldu. Alıntının kaynakta bulunması denetimi hiçbir öneriyi işaretlemedi. Biyomedikal derlemde [@li2016bc5cdr] aynı model ve yalnız şema içeren istemle adın alıntıda bulunması denetimi 303 eşleşmeyen önerinin 53'ünü, güven skoru ise 58'ini buldu. Kullanılabilir sonuçlar tek modelden elde edildi; insan incelemesi yapılmadı. Denetimin hadis dışındaki verilerde aynı sonucu verdiği gösterilmedi.

Araştırmanın katkıları dört başlıkta toplanmaktadır:

- **K-1. İnsan etiketli isnad referans kümesi.** Altı kitaptan 300 hadisin ravi geçişleri ve sırası, kılavuza göre ve sistem çıktısı görülmeden iki kodlayıcı tarafından etiketlenecektir. Anlaşmazlıklar üç alan uzmanının bağımsız kararlarıyla değerlendirilecek; kodlayıcı ve uzman uyumu ile hadis başına etiketleme süresi raporlanacaktır.
- **K-2. Denetim katmanlarının insan etiketine karşı ölçümü.** Kural tabanlı ayrıştırıcı taban çizgisi alınarak model, şema denetimi, kanıt denetimleri ve insan incelemesinin etkileri karşılaştırılacaktır. İncelemesiz model koşulları en az biri açık ağırlıklı en az üç modelle ikişer kez yürütülecek; insan incelemesi tek modelin bir koşusunda, bir kez ölçülecektir.
- **K-3. İnceleyicinin döngüde ölçümü.** İlgili hadisin referans etiketini üretmemiş bir ekip üyesinin kararlarıyla inceleme sonrası kesinlik ve duyarlılık, gerekçe koduna göre ret oranı ve karar süresi hesaplanacaktır.
- **K-4. Motorda kimlik karar defteri.** Kararlar aday kimliği yerine içeriğe bağlanarak saklanacak; ravi tabakası veya vefat yılıyla çelişen eşleştirmelerde kararın kullanım kapsamı daraltılacaktır. Benzetimdeki bulgular gerçek kimlik kararlarıyla sınanacaktır.

Araştırma, doğrulama katmanlarının hangi hata türlerini ne ölçüde azalttığına ve önceki kimlik kararlarının yeniden kullanımının inceleme emeği ile sessiz hatayı nasıl değiştirdiğine odaklanır. Hipotez eşikleri, insan etiketine dayanmayan ön çalışma ölçümlerinin altında seçildi.

- **H1.** Yalnız şema verilen modelde adın alıntıda bulunması denetimi, insan etiketiyle eşleşmeyen önerilerin en az %60'ını işaretler ve aynı model içinde eşit inceleme payında güven skorundan daha fazlasını bulur. Ön çalışmada denetim %9,2'lik payla 122 öneriyi (%84), güven skoru %16,3'lük payla 50 öneriyi buldu; bu ilk karşılaştırmada inceleme payları eşit değildi.
- **H2.** İncelemesiz kabul edilen önerilerin hata oranı, ham önerilere göre en az %50 düşer. Hata oranı, 1 eksi kesinlik olarak hesaplanacaktır. Ön çalışmada bu oran 0,086'dan 0,015'e düştü; hata azalması duyarlılık kaybıyla birlikte raporlanacaktır.
- **H3.** Ret veya düzeltme olasılığı, işaretlenen adaylarda işaretlenmeyenlere göre anlamlı biçimde daha yüksektir. Aday düzeyinde lojistik model kullanılacak, standart hatalar hadis düzeyinde kümelenecek ve p < 0,05 ölçütü uygulanacaktır.
- **H4.** Gerçek kararlarla kapsamı daralan defter, öğrenci ve ada sabitlenmiş defterden en az %20 az soru sorar; geçiş başına sessiz hata farkı 0,02'yi aşmaz. Benzetimde soru azalması %32 ile %48, hata farkı 0,003 ile 0,008 arasında bulundu. Gerçek kararlarda aynı soru azalması garanti değildir.

Proje, yapay zekâ alanındaki temel teknolojilerin geliştirilmesini öngören 12. Kalkınma Planı'nın 591. maddesiyle ilişkilidir. Model çıktısını kaynak metin ve insan kararıyla doğrulayan açık bir yazılım ile insan etiketli bir veri kümesi üretecektir. Bu çıktılar, başka araştırmacıların doğrulama yöntemlerini aynı veri üzerinde karşılaştırmasına imkân verecektir.

## 1.2. Amaç ve Hedefler

Projenin amacı, hadis isnadlarından bilgi grafı üretilirken uygulanan denetimlerin ve insan incelemesinin bilgi çıkarma başarısına etkisini, kimlik kararlarının yeniden kullanımının ise inceleme yükünü nasıl değiştirdiğini ölçmektir.

- **Hedef 1 (referans kümesi).** İki kodlayıcının 300 hadisi bağımsız etiketlemesi ve gevşek eşleştirmede en az 0,85 karşılıklı F1 uyumu sağlaması hedeflenmektedir. Uyum bu değerin altında kalırsa kılavuz gözden geçirilerek kalibrasyon turu tekrarlanacaktır. Üç uzmanın kararlarıyla referans kümesi oluşturulacak; uyum ve ortalama etiketleme süresi raporlanacaktır.
- **Hedef 2 (ölçüm).** Kural tabanlı ayrıştırıcı ile incelemesiz model koşulları karşılaştırılacaktır. Model koşulları, en az biri açık ağırlıklı en az üç modelle ikişer kez yürütülecek; kesinlik, duyarlılık ve F1 katı ve gevşek eşleştirmede, hata türlerine göre raporlanacaktır. Hadis düzeyinde bootstrap güven aralıkları hesaplanarak H1 ve H2 sınanacaktır.
- **Hedef 3 (inceleyici).** Tek modelin bir koşusunda, bir inceleyici 300 hadisin tüm inceleme öğelerine, işaretlenmeyen öneriler de dahil olmak üzere, bir kez karar verecektir. İnceleme sonrası kesinlik ve duyarlılık, ret ve düzeltme oranları ile medyan karar süresi raporlanacak; H3 sınanacaktır.
- **Hedef 4 (karar defteri).** Karar defteri motora eklenecek ve gerçek veritabanlarında test edilecektir. Gerçek kimlik kararlarıyla soru sayısı ve sessiz hata ölçülerek H4 sınanacaktır.
- **Hedef 5 (yaygın etki ve açık bilim).** Motor, betikler ve referans etiketleri açık lisanslarla yayımlanacaktır. Sonuçların en az bir hakemli bilimsel etkinliğe bildiri olarak gönderilmesi ve ön baskı olarak paylaşılması hedeflenmektedir.

# 2. YÖNTEM

## 2.1. Araştırma Yaklaşımı

Tasarım bilimi yaklaşımıyla GiraffeGraph motoru geliştirilecek [@hevner2004design; @wieringa2014design] ve kontrollü deneylerle değerlendirilecektir. Araştırmada çıkarım koşulu, model, denetim katmanları ve karar defteri politikası değiştirilecektir. Yazılımın çalışması ile üretilen bilgi grafının doğruluğu ayrı değerlendirilecektir.

## 2.2. Veri ve Referans Etiketleme

Ön çalışmanın test kümesini oluşturan, altı kitaptan tabakalı örneklenmiş 300 Arapça hadis kullanılacaktır. Telifsiz ve tam isnadlı Türkçe kaynak bulunamadığı için Türkçe metin kapsam dışındadır; kılavuz ve arayüz Türkçe hazırlanacaktır.

Dr. Öğr. Üyesi Tunahan Erdoğan (Akdeniz Üniversitesi İlahiyat Fakültesi, Temel İslam Bilimleri Bölümü, Arap Dili ve Belagatı Anabilim Dalı) ve ilk ay belirlenecek iki hadis uzmanının görüşleriyle kılavuz gözden geçirilecektir. İki ekip üyesi sistem çıktısını görmeden bağımsız etiketleme yapacak; denetim kurallarını geliştiren kişi etiketleme görevinde yer almayacaktır. İlk 50 hadisin uyum ölçümlerine göre kılavuz düzeltilecek, etiketleme süreleri ve anlaşmazlık sayısından uzman iş yükü hesaplanacaktır.

Karar birimi, ad yazımı ve zincir konumuyla tanımlanan ravi geçişidir. Kodlayıcıların anlaşamadığı her geçiş üç uzman tarafından bağımsız değerlendirilecektir. Her uzman iki kodlayıcının etiketinden birini seçebilecek veya kendi etiketini yazabilecektir. Çoğunluk kararı referansa alınacak; üç cevap farklıysa öğe "tartışmalı" işaretlenerek ana puandan çıkarılacak ve ayrı raporlanacaktır. Kodlayıcıların uzlaştığı rastgele 10 hadis de ortak hataları aramak için uzmanlarca değerlendirilecektir. Kodlayıcı uyumu karşılıklı F1, uzman uyumu Fleiss' kappa ile raporlanacaktır.

Uzmanlar sistem çıktısını görmeyecek ve inceleme kuyruğunda karar vermeyecektir. İnceleyici, ilgili hadisin referans etiketini üretmemiş ekip üyesi olacaktır. Paylaşılacak küme, etiketleri ve kaynak kimliklerini içerecektir.

## 2.3. Bilgi Grafı Üretimi ve Doğrulama

Mevcut motorda modelin grafa yazma yetkisi yoktur; model, kaynak alıntılarıyla birlikte öneriler üretir. Şema denetimi, önerilerin tanımlanan düğüm, ilişki ve özelliklere uygunluğunu sınar. Alıntının kaynakta bulunması denetimi, sunulan alıntının özgün metinde yer alıp almadığını; adın alıntıda bulunması denetimi ise önerilen ravi adının bu alıntıda geçip geçmediğini sınar. Bu iki işlem birlikte kanıt denetimleri olarak adlandırılacaktır.

İnceleyici öneriyi kabul edebilir, reddedebilir veya düzeltebilir. Kabul edilen bilgi, kaynak ve kabul kaydıyla kanonik grafa yazılır. Kararlar silinmez ve üzerlerine yazılmaz. İnceleme kuyruğu ve ölçüm betikleri hazırdır. Kanıt denetimleri metinsel tutarlılığı ölçer, ravi kimliğinin doğruluğunu tek başına garanti etmez; aktarım ilişkileri ve isnad sırası referans etiketlerle ayrıca değerlendirilecektir.

Puanlamada ravi adlarına Unicode NFKC normalizasyonu uygulanacak, hareke ve tatvil kaldırılacaktır. Elif biçimleri (`أ إ آ ٱ`) `ا` biçimine; `ى` → `ي`, `ة` → `ه`, `ؤ` → `و`, `ئ` → `ي` biçiminde dönüştürülecektir. Noktalama işaretleri ile dua ve unvan kalıpları atılacak, ad başındaki `و`, `ف`, `ثم`, `قال` gibi bağlaç ve söz fiilleri en çok üç kez temizlenecektir. Motorun kanıt denetimindeki normalizasyon ise kaynak konumlarını korur, dua kalıplarını ve parçacıkları atmaz. Yüzey eşleşmesi kimlik eşitliği sayılmayacaktır.

## 2.4. Ravi Kimliği Karar Defteri

Karar kaydı aday kimliği yerine hadis ve standartlaştırılmış ravi adına bağlanacak; kimlik kararı komşu ravilerle birlikte saklanacaktır. Ravi tabakası ve vefat yılı kurallarıyla çelişen eşleştirmeler yeniden incelemeye açılacak, önceki kararın kullanım kapsamı daraltılacaktır. Yalnız hâl eki bakımından farklılaşan adların otomatik kabulüne ilişkin kural ve bu kuralla verilen kararlar kaydedilecektir.

Aynı kimlik kararları üç politika altında yeniden yürütülecektir:

- P1: Karar yalnız ravi adına göre yeniden kullanılacaktır.
- P2: Her öğrenci ve ad çifti için ayrı soru sorulacak; karar bu çifte bağlı olarak yeniden kullanılacaktır. Öğrenci, zincirde addan önceki ravidir.
- P3: Karar başlangıçta yalnız ada göre yeniden kullanılacaktır. İnceleyici veya tabaka ve vefat yılı kuralları çelişki belirlediğinde kapsam önce öğrenciye, ardından hocaya göre daraltılacaktır. Hoca, zincirde addan sonraki ravidir.

P3'te her öğrenci ve ad çifti için baştan soru sorulmadığından P2'ye göre daha az soru beklenmektedir. Buna karşılık, henüz çelişki belirlenmemiş bir karar yanlış kimlik eşleştirmesini sürdürebilir. Sessiz hata, yeniden kullanılan kararın ilgili geçiş için verilmiş inceleyici kararıyla çelişmesidir. H4'te soru azalması ve geçiş başına sessiz hata farkı birlikte sınanacaktır.

## 2.5. Deney Tasarımı

Aynı 300 hadis üzerinde beş koşul karşılaştırılacaktır. K0'da model kullanılmayacak; K1, K2 ve K3 en az biri açık ağırlıklı en az üç modelle ikişer kez yürütülecektir. K4, tek modelin bir koşusunda, bir kez insan incelemesiyle uygulanacaktır.

| Koşul | Uygulama | Değerlendirilen katkı ve tekrar düzeni |
|---|---|---|
| K0 | Kural tabanlı isnad ayrıştırıcı | Taban çizgisi; model kullanılmaz. |
| K1 | Yalnız model | Ham çıkarım başarısı; en az üç model, ikişer tekrar. |
| K2 | Model ve şema denetimi | Şema denetiminin etkisi; en az üç model, ikişer tekrar. |
| K3 | Model, şema ve iki kanıt denetimi | Kanıt denetimlerinin etkisi; en az üç model, ikişer tekrar. |
| K4 | Model, bütün denetimler ve insan incelemesi | İnsan incelemesinin etkisi; tek modelin bir koşusunda, bir kez. |

Model yanıtları, istemler, yazılım sürümleri ve denetim sonuçları saklanacaktır. İki kanıt denetiminin işaretlediği öneriler ayrı raporlanacaktır. K4'te işaretlenen ve işaretlenmeyen öneriler için inceleme kararı elde edilerek H3 sınanacaktır.

## 2.6. Ölçütler ve Hipotezlerin Sınanması

Bilgi çıkarma başarısı kesinlik, duyarlılık ve F1 ile ölçülecektir. Katı eşleştirmede standartlaştırılmış adların eşitliği aranacaktır. Gevşek eşleştirmede eşitlik, bir adın diğerinin alt dizisi olması veya sözcük düzeyinde F1 ≥ 0,60 yeterli sayılacaktır. Eşleştirme kuralları deneylerden önce sabitlenecektir. Kaynakta bulunmayan ravi, değiştirilmiş ad, şema dışı öneri ve isnad sırası hataları ayrı raporlanacaktır.

H1'de adın alıntıda bulunması denetimi ile güven skoru, her model içinde aynı sayıda öneriyi incelemeye ayırdıkları durumda karşılaştırılacaktır. Güven skoru, modelin yapılandırılmış yanıtta her öneri için verdiği öz değerlendirme değeridir; kalibre edilmiş bir olasılık değildir. Ön çalışmada model yalnız 7 farklı değer kullandı. Bu nedenle çok sayıda öneri aynı puanı alır; eşit puanlı önerilerin incelemeye ayrılma kuralı deneylerden önce sabitlenecektir.

H2'de ham öneriler ile incelemesiz kabul edilen önerilerin hata oranları karşılaştırılacaktır. Doğru önerilerin de incelemeye yönlendirilmesinden doğan duyarlılık kaybı birlikte raporlanacaktır. Ön çalışmada kesinlik 0,914'ten 0,985'e çıkarken duyarlılık 0,868'den 0,849'a düştü.

H3'te işaretlenme durumu, gerekçe kodları ve güven skoruyla ret veya düzeltme olasılığı lojistik regresyonla incelenecek; standart hatalar hadis düzeyinde kümelenecektir. İşaretlenmeyen önerilerin kararları da analize katılacaktır. R3'teki örnekleme planına başvurulursa örnekleme olasılıkları kaydedilecek ve analizde dikkate alınacaktır. İşaretlenen önerilerin payı, kabul, ret ve düzeltme oranları ile karar süreleri raporlanacaktır.

H4 için aynı gerçek kimlik kararları P1, P2 ve P3 politikaları altında yeniden yürütülecek; hadis sırası değiştirilerek soru sayısı ve sessiz hata oranındaki belirsizlik hesaplanacaktır. Koşullar arasındaki performans farkları, temel analiz birimi hadis alınarak eşli bootstrap güven aralıklarıyla verilecektir. Hipotezleri desteklemeyen sonuçlar da raporlanacaktır.

## 2.7. Ön Çalışma ve Bu Projenin Sınırı

Motor ve ilk ölçümler finansman alınmadan tamamlandı. CSE 491 bitirme projesinde iki ekip üyesi 50 hadisi bağımsız etiketler, anlaşmazlıkları hadis uzmanları karara bağlar ve prototip 100 hadiste uçtan uca çalışır. TÜBİTAK projesinde insan etiketli küme 300 hadise genişletilecek, deneyler en az üç modelle tekrarlanacak, ravi kimliği karar defteri motora eklenerek gerçek inceleyici kararlarıyla sınanacaktır.

Motor şema tabanlıdır ve başka alanlara uyarlanabilir; bu projenin değerlendirmesi hadis isnadlarıyla sınırlıdır. Hadislerin sıhhatine ilişkin hüküm verilmesi kapsam dışındadır.

# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

| Tarih Aralığı | Faaliyetler | Kim(ler) Tarafından Gerçekleştirileceği | Başarı Ölçütü ve Araştırmanın Başarısına Katkısı |
|---|---|---|---|
| 1.-2. Ay | İP1: İlk 50 hadisin uyum ve süre ölçümlerine göre etiketleme kılavuzunun gözden geçirilmesi; kararların hadis ve standartlaştırılmış ada bağlanması. | Tüm ekip; üç uzman tarafından kılavuz değerlendirmesi. | Kılavuz v2 ve etiketler hazırlanacak; karşılıklı F1 ve süre raporlanacak, içerik tabanlı karar kaydının testleri geçecektir. Katkısı %20'dir. |
| 2.-4. Ay | İP2: Kalan 250 hadisin etiketlenmesi, incelemesiz model koşullarının en az üç modelle ikişer kez yürütülmesi. | Tüm ekip; üç uzman tarafından bağımsız değerlendirme. | 300 hadislik referans ve sonuç tablosu hazırlanacak; F1 ≥ 0,85 uyumu sağlanacak, H1 ve H2 için ölçümler tamamlanacaktır. Katkısı %30'dur. |
| 3.-5. Ay | İP3: Kararlara komşu ravi bilgilerinin eklenmesi, çelişkide kapsam daraltma ve hâl eki kurallarının uygulanması; 300 hadisin incelenmesi. | Tüm ekip. | Defterli motor ve inceleme kayıtları hazırlanacak; gerçek veritabanı testleri geçecek, H3 ve H4 için kararlar ve süre ölçümleri tamamlanacaktır. Katkısı %30'dur. |
| 5.-6. Ay | İP4: Analiz ve tekrarlanabilirlik: hipotez sınamaları, bootstrap aralıkları, hata türü tabloları, sonuçların temiz kurulumdan yeniden üretilmesi. | Tüm ekip. | H1, H2, H3 ve H4 analizleri, güven aralıkları ve hata türü tabloları tamamlanacak; sonuçlar temiz kurulumdan yeniden üretilecektir. Katkısı %20'dir. |

## 3.2. Risk Yönetimi

| En Önemli Riskler | Alınacak Tedbirler (B Planı) |
|---|---|
| R1: Derlem veya ravi kataloğu lisansı doğrulanamaz. | Açık lisanslı metinler ve ekibin ürettiği etiketler kullanılacak; dağıtım izni olmayan derlemler paylaşılmadan değerlendirilecektir. |
| R2: Kodlayıcı uyumu düşük kalır. | Kılavuz uzman görüşüyle düzeltilecek ve ek kalibrasyon turu uygulanacaktır. 300 hadislik hedef korunacaktır. |
| R3: Etiketleme ve inceleme uzar. | İlk 50 hadisin sürelerine göre iş yükü planlanacaktır. Gerekirse işaretlenen öğelerin tamamı ve işaretlenmeyenlerden önceden belirlenmiş rastgele örnek incelenecek; örnekleme olasılıkları kaydedilerek H3 sınanacaktır. |
| R4: Model erişimi, maliyeti veya çıktı biçimi sorun olur. | Açık ağırlıklı model bölüm sunucusunda yerel çalıştırılacak; çıktı biçimi şema denetimleriyle sınanacaktır. Hadis sayısı, model sayısı ve tekrar hedefleri korunacaktır. |
| R5: Akademik yoğunluk takvimi kaydırır. | Her iş paketindeki %15 zaman payı kullanılacak ve bağımsız işler paralel yürütülecektir. |
| R6: Yazılım hataları ölçüm sonuçlarını bozabilir. | Otomatik testler uygulanacak, sayılar betikle üretilecek ve sonuçlar temiz kurulumdan yeniden üretilecektir. |
| R7: Bir uzman katılamaz veya gecikir. | Kalan iki uzmanın bağımsız kararlarıyla çalışılacak; anlaşamadıkları geçişler "tartışmalı" işaretlenip ana puandan çıkarılarak ayrı raporlanacaktır. |

## 3.3. Araştırma Olanakları

| Kuruluşta Bulunan Altyapı/Ekipman Türü, Modeli | Projede Kullanım Amacı |
|---|---|
| Akdeniz Üniversitesi Bilgisayar Mühendisliği yazılım geliştirme laboratuvarı | Geliştirme, kod inceleme ve etiketleme oturumlarında kullanılacaktır. |
| Bölüm sunucuları ve kampüs ağı | PostgreSQL ve Neo4j veritabanlarının barındırılmasında ve açık ağırlıklı modelin yerel çalıştırılmasında kullanılacaktır. |
| Dr. Öğr. Üyesi Tunahan Erdoğan (Akdeniz Üniversitesi İlahiyat Fakültesi, Temel İslam Bilimleri Bölümü, Arap Dili ve Belagatı Anabilim Dalı) ve ilk ay belirlenecek iki hadis uzmanı | Kılavuz değerlendirmesi, bağımsız kararlar ve ravi kaynaklarına erişim desteği sağlanacaktır. |
| GiraffeGraph Core, betikler ve ön çalışma sonuçları | Motorun geliştirilmesinde ve deneylerin yürütülmesinde kullanılacak; depo geliştirme süresince özel tutulacaktır. |

# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Çıktı, Etki ve Kazanımlar | Öngörülen Çıktı(lar), Etki(ler) ve Kazanım(lar) |
|---|---|
| **Bilimsel/Akademik Çıktılar** | Sonuçların en az bir hakemli bilimsel etkinliğe bildiri olarak gönderilmesi ve ön baskı olarak paylaşılması hedeflenmektedir. Araştırma bulgularıyla bitirme tezi hazırlanacaktır. |
| **Ekonomik/Ticari/Sosyal Çıktılar** | Motor ve betikler açık kaynak, uyumu raporlanmış 300 hadislik etiket kümesi kaynak metinleri içermeyen açık veri olarak yayımlanacaktır. Bölümde seminer düzenlenecektir. |
| **Yeni Proje(ler) Oluşturmasına Yönelik Çıktılar** | Ravi adlarının otorite listesine bağlanması ve grafla soru cevaplama üzerine sonraki çalışmalar için deney kayıtları kullanılacak; İlahiyat ile iş birliği sürdürülecektir. |

# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

Ön çalışma beyanı: Motor ve ilk ölçümler finansman alınmadan tamamlandı.

Veri ve açık bilim: Üçüncü taraf hadis metinleri değerlendirmede kullanılacak, dağıtılmayacaktır. Bu metinlerle aynı depodaki kod geliştirme süresince özel tutulacak; proje sonunda metinler dağıtım dışında bırakılarak motor, betikler ve referans etiketleri uygun açık lisanslarla yayımlanacaktır.

Alan uzmanı desteği: Dr. Öğr. Üyesi Tunahan Erdoğan ve ilk ay belirlenecek iki hadis uzmanı kılavuzu gözden geçirecek ve anlaşmazlıklarda bağımsız karar verecektir. Uzmanlar sistem çıktısını görmeyecek, inceleme kuyruğunda karar vermeyecektir. İlk 50 hadisin süre ve anlaşmazlık ölçümlerinden uzman iş yükü hesaplanacaktır.

# 6. EKLER

## EK-1: KAYNAKLAR

<!-- references -->

# Göndermeden önce (başvuru metnine girmez)

1. **Form TYBS'de oluşur.** 2026 çağrısında yüklenecek bir form dosyası yoktur; metin TYBS'deki kutulara girilir, sayfa sınırı yoktur. Özet 25–450 kelimedir (bu metinde 274); 1.1, 1.2 ve 2. bölüm en az 350 karakterdir. Kaynakça ayrı adımda girilir; DOI'si olan kaynağa DOI eklenir. Takvimde literatür taraması, rapor yazımı ve sonuç paylaşımı ayrı iş adımı olamaz; B planları temel hedeften sapamaz (2026 Başvuru İçeriği Bilgi Notu, <https://tubitak.gov.tr/sites/default/files/2026-10/2209-A_Basvuru_Icerigi_Bilgi_Notu.pdf>). Öneride ticari ürün ya da marka öne çıkarılmaz; model adları bu yüzden yazılmadı (çağrı duyurusu madde 4.1.8, <https://tubitak.gov.tr/sites/default/files/2026-10/2209-A_2026_Yili_Cagri_Duyurusu.pdf>).
2. **Başvuru sahipleri.** Liste bitirme projesi ekibidir. Sıra ve yürütücü, başvuru sistemindeki role göre yazılır.
3. **Çerçeve ve danışman.** Kapsam, ekibin 25 Ekim proje özetini (Alperen Ulukaya) izler. Danışman 5 Kasım'da metnin yapay zekâ koktuğunu söyleyip `giraffe.docx` belgesini gönderdi; bu sürüm o belgenin üslubunu, bu formun sayılarını ve atıflarını izler. Danışmana bildirilecek değişiklikler: başlık artık sınanacak etkiyi sonuç gibi sunmuyor; Hedef 5'te bildiri "sunma" yerine "gönderme" (danışman belgesindeki gibi); R2, R4 ve R5'teki hedef küçülten B planları ve yayın/rapor iş paketi (İP4) 2209-A kuralı yüzünden değişti. Danışman son metni okumadı.
4. **Alan uzmanlarının desteği.** Üç hadis uzmanının destek beyanları alınmalıdır. Beyanlar, kılavuzu gözden geçirme ve anlaşmazlıklarda bağımsız karar verme rollerini kapsamalı; uzmanların inceleme kuyruğunda karar vermeyeceğini belirtmelidir.
5. **Eşikler.** H1 (%60), H2 (%50), H4 (%20 ve 0,02) ve Hedef 1 (karşılıklı F1 ≥ 0,85) öneridir. Verilen söz bağlar; ekip ve danışman onaylar.
6. **Metin kaynağı ve lisans.** 300 hadislik test kümesinin metin ve etiket kaynaklarının lisansı teyit edilmemiştir (`data/README.md`). R1'deki B planı buna göre yazılmıştır.
7. **Kalkınma Planı ve strateji belgeleri.** 1.1'deki cümle 12. Kalkınma Planı'nın 591. maddesine dayanır; madde plan metninde doğrulandı (<https://www.sbb.gov.tr/wp-content/uploads/2023/12/On-Ikinci-Kalkinma-Plani_2024-2028_11122023.pdf>). Planda "büyük dil modeli" ve "üretken yapay zekâ" geçmez. 2030 Sanayi ve Teknoloji Stratejisi (Amaç 1, Strateji 6) Türkçe büyük dil modeli geliştirmeyi anar; proje model geliştirmediği için oraya bağlanmadı ve resmî PDF okunmadı. TÜBİTAK öncelikli alanlar listesi (<https://tubitak.gov.tr/sites/default/files/2025-07/Oncelikli_Alanlar_2025-2.pdf>) okunmadı.
8. **Bütçe.** Bu formda bütçe bölümü yoktur; başvuru sisteminde girilir. Model kullanım bedeli ve varsa etiketleme giderleri orada yazılır.
9. **Üretken yapay zekâ beyanı.** Beyan form metnine değil, TYBS'deki ayrı bölüme girilir: aracın adı ve sürümü, kullanıldığı bölüm ve kullanımın niteliği (ör. ilk taslak, kod, veri analizi). TÜBİTAK ÜYZ Rehberi (Ocak 2026, madde 1.2.2, <https://tubitak.gov.tr/sites/default/files/2026-01/UYZ_Rehberi_v04_TR.pdf>). Rehberin 1.5.3. maddesi yayımlanmamış araştırma verisini ÜYZ araçlarına girmeyi yasaklar; ön çalışma verisi ve bu taslak yapay zekâ araçlarıyla işlendi. Bunun nasıl beyan edileceği danışmanla konuşulmalıdır; çağrının 8.5. maddesine göre ÜYZ ile üretilen içeriğin doğruluğundan danışman sorumludur.
