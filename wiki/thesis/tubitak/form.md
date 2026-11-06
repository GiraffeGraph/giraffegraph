# TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı: Araştırma Önerisi Formu

> **TYBS'ye girildi, danışman onayı bekliyor (2026-11-06).** Bu dosya başvuru no 1919B012619516'nın TYBS'deki araştırma önerisi metninin kopyasıdır; TYBS önizleme PDF'i `wiki/thesis/tubitak/tybs/arastirma-onerisi.pdf`. Metin ekibin ve danışmanın son düzeltmelerini taşır. En sondaki "Göndermeden önce" bölümü ve bu kutu başvuru metnine girmez.

# A. GENEL BİLGİLER

| | |
|---|---|
| **Başvuru Sahibinin Adı Soyadı** | Yahya Efe Kuruçay (proje ortakları: Deniz Büyükşahin, Alperen Ulukaya) |
| **Araştırma Önerisinin Başlığı** | Büyük Dil Modelleriyle Bilgi Grafı Üretiminde Doğrulama Denetimlerinin ve İnsan İncelemesinin Etkisi: Hadis İsnad Zincirleri Üzerine Bir Uygulama |
| **Akademik Danışmanın Adı Soyadı** | Arş. Gör. Dr. Taha Yiğit Alkan |
| **Araştırmanın Yürütüleceği Kurum/Kuruluş** | Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü |

# ÖZET

Hadis isnad zincirlerinin bilgi grafına dönüştürülmesi, ravi adlarının ve kimliklerinin doğru belirlenmesini, aktarım ilişkilerinin korunmasını gerektirmektedir. Büyük dil modelleri bu süreçte yapılandırılmış bilgi çıkarımını desteklemekle birlikte, kaynak metinle uyuşmayan veya tanımlanan şemaya uygun olmayan öneriler üretebilmektedir. Ayrıca bir ravi adının kaynakta bulunması, doğru kişiyle eşleştirildiğini tek başına göstermemektedir. Bu araştırmada, şema ve kanıt denetimleri ile insan incelemesinin bilgi çıkarma başarısına etkilerinin karşılaştırılması amaçlanmaktadır. Bunun yanında, önceki ravi kimliği kararlarının yeniden kullanılmasının inceleme yükü ve hata riski üzerindeki etkileri değerlendirilecektir.

Ön çalışma kapsamında geliştirilen GiraffeGraph motoru, altı hadis kitabından seçilen 300 Arapça hadis üzerinde değerlendirilmiştir. Elde edilen bulgularda, ravi adının kaynak alıntısında bulunmasını kontrol eden denetimin, mevcut kaynak etiketleriyle uyuşmayan önerilerin belirlenmesinde etkili olduğu gözlemlenmiştir. Ancak bu sonuçlar insan tarafından oluşturulmuş referans etiketlerine dayanmamaktadır. Bu nedenle doğrulama mekanizmalarının insan etiketleri üzerinden yeniden değerlendirilmesi planlanmaktadır.

Araştırmada, iki ekip üyesinin bağımsız etiketlemeleri ve alan uzmanlarının değerlendirmeleriyle bir referans veri kümesi oluşturulacaktır. Kural tabanlı ayrıştırıcı ve farklı büyük dil modelleri, doğrulama katmanlarının aşamalı olarak eklendiği deney koşullarında karşılaştırılacaktır. İnsan incelemesi seçilen bir modelin deney çıktısı üzerinde uygulanacaktır. Bilgi çıkarma başarısı kesinlik, duyarlılık, F1 ve hata türleri üzerinden değerlendirilecektir. Ayrıca ravi kimliği kararlarının yeniden kullanımına yönelik farklı politikalar, inceleme gereksinimi ve sessiz hata oranları açısından incelenecektir.

Araştırma sonucunda, doğrulama mekanizmalarının bilgi çıkarma başarısı üzerindeki etkilerine ilişkin karşılaştırmalı bulgular elde edilmesi beklenmektedir. Geliştirilen yazılımın, deney betiklerinin ve insan etiketli referans kümesinin, kaynakların paylaşım hakları gözetilerek araştırmacıların kullanımına sunulması hedeflenmektedir. Bu çıktıların, doğrulanabilir bilgi grafı üretimine yönelik sonraki çalışmalara katkı sağlaması öngörülmektedir.

**Anahtar Kelimeler:** Büyük dil modelleri, bilgi grafı, bilgi çıkarımı, insan-döngülü sistemler, hadis isnadı

# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

Hadis isnad zincirleri, bir rivayetin hangi kişiler aracılığıyla aktarıldığını ve bu kişilerin aktarım sırasını göstermektedir. Bu zincirlerin bilgi grafına dönüştürülmesi, ravi adlarının doğru çıkarılmasını, aynı kişiye ait farklı adların eşleştirilmesini ve raviler arasındaki ilişkilerin korunmasını gerektirmektedir. Ancak aynı ravinin farklı adlarla anılması veya benzer adların farklı kişilere ait olması, bilgi çıkarma sürecinde hatalara yol açabilmektedir. Bu nedenle yalnızca metinde geçen adların belirlenmesi yeterli değildir. Ravi kimliklerinin ve aktarım ilişkilerinin de doğrulanması önem taşımaktadır.

Metinlerden yapılandırılmış bilgi çıkarma ve bilgi grafiği oluşturma süreçlerinde büyük dil modellerinin kullanımı, literatürde ele alınan bir konudur [@ye2022generative; @pan2024unifying]. Bununla birlikte, bu modellerin kaynak metin tarafından desteklenmeyen bilgiler üretmesi önemli bir güvenilirlik sorunudur [@ji2023survey]. Hadis alanında ise ravi bilgilerinin işlenmesine yönelik veri kümeleri [@mghari2022sanadset; @mahmoud2022arsanad] ve bilgi grafı çalışmaları geliştirilmiştir [@kamran2023semantichadith; @kamran2026semantic]. Bu çalışmalar hadis metinlerinin bilgisayar ortamında işlenmesine önemli katkılar sağlamaktadır.

Bilgi çıkarma süreçlerinde doğrulama mekanizmalarının ve insan incelemesinin kullanımı da araştırılmaktadır [@tsaneva2025validation]. Hadis alanındaki güncel literatürde uzman doğrulamasının geliştirilmesi gereken konular arasında değerlendirildiği görülmektedir [@haque2026hadith]. Bununla birlikte, mevcut literatür ışığında; şema denetimi, kaynak metne dayalı kanıt doğrulaması ve insan denetiminin aynı deneysel çerçevede aşamalı olarak mukayese edilmesine yönelik kapsamlı değerlendirmelere ihtiyaç duyulmaktadır. Öte yandan, önceden teyit edilmiş ravi kimliği kararlarının yeniden kullanımının inceleme iş yüküne ve hata oranına etkisi de önem arz eden bir diğer araştırma alanıdır.

Bu araştırma, söz konusu doğrulama yaklaşımlarını GiraffeGraph üzerinde karşılaştırmalı olarak değerlendirmeyi amaçlamaktadır. Projenin özgün katkısı, farklı doğrulama katmanlarının bilgi çıkarma başarısına etkisini ortak bir referans kümesi üzerinden incelemek ve ravi kimliği kararlarının yeniden kullanımını doğruluk ile inceleme yükü açısından değerlendirmektir. Bu kapsamda insan tarafından etiketlenmiş bir referans kümesi oluşturulması, doğrulama katmanlarının karşılaştırılması ve önceki kararların kontrollü biçimde yeniden kullanılmasını sağlayan bir karar defterinin geliştirilmesi planlanmaktadır.

Araştırmanın ön çalışmasında, altı hadis kitabından seçilen 300 hadis üzerinde mevcut bilgi çıkarma motoru değerlendirilmiştir. Elde edilen bulgular, önerilen ravi adının kaynak alıntıda bulunup bulunmadığını kontrol eden denetimin, modelin güven skoruna kıyasla daha düşük inceleme yüküyle daha fazla uyumsuz öneriyi işaretleyebildiğini göstermiştir. Bununla birlikte, bu değerlendirmede insan tarafından oluşturulmuş referans etiketler yerine platform etiketleri kullanılmıştır. Bu nedenle ön çalışma bulgularının insan etiketleriyle doğrulanması ve farklı modellerle değerlendirilmesi gerekmektedir.

Ön çalışma bulguları ve araştırmanın amaçları doğrultusunda aşağıdaki hipotezler oluşturulmuştur:

- **H1.** Ravi adının kaynak alıntısında bulunmasını kontrol eden denetimin, insan etiketleriyle uyuşmayan önerilerin en az %60'ını işaretlemesi ve eşit inceleme payında modelin güven skorundan daha başarılı olması beklenmektedir.
- **H2.** Doğrulama denetimleri sonrasında incelemesiz kabul edilen önerilerin hata oranının, ham model çıktılarına göre en az %50 azalması beklenmektedir.
- **H3.** Denetimler tarafından işaretlenen önerilerin insan incelemesinde reddedilme veya düzeltilme olasılığının, işaretlenmeyen önerilere göre daha yüksek olması beklenmektedir.
- **H4.** Önceki kimlik kararlarının kontrollü biçimde yeniden kullanılmasının, her öğrenci ve ravi adı çifti için ayrı karar tutan yaklaşıma kıyasla inceleme gereksinimini en az %20 azaltması ve geçiş başına sessiz hata oranı farkının 0,02'yi aşmaması beklenmektedir.

Bu hipotezler aracılığıyla doğrulama katmanlarının hangi hata türlerinde etkili olduğu, insan incelemesine duyulan gereksinimi nasıl değiştirdiği ve önceki kararların yeniden kullanımından kaynaklanan riskler değerlendirilecektir. Ölçüm yöntemleri ve deney koşulları araştırmanın yöntem bölümünde ayrıntılandırılacaktır.

Araştırmanın beklenen çıktıları, yapay zekâ uygulamalarının güvenilirliğini ve doğrulanabilirliğini geliştirmeye yönelik çalışmalarla ilişkilidir. Bu yönüyle proje, 12. Kalkınma Planı'nın 591. maddesinde [@sbb2023kalkinma] yer alan yapay zekâ teknolojilerinin geliştirilmesine yönelik hedeflerle uyumludur. Geliştirilecek doğrulama mekanizmalarının, insan etiketli referans kümesinin ve deney sonuçlarının, bilgi grafı üretimine yönelik sonraki araştırmalara katkı sağlaması hedeflenmektedir.

## 1.2. Amaç ve Hedefler

Bu projenin temel amacı, büyük dil modelleri kullanılarak hadis isnad zincirlerinden bilgi grafı oluşturulması sürecinde uygulanan doğrulama mekanizmalarının bilgi çıkarma başarısına etkisini araştırmaktır. Bu kapsamda şema denetimi, kaynak metne dayalı kanıt denetimleri ve insan incelemesinin doğruluk üzerindeki katkıları karşılaştırılacaktır. Ayrıca, daha önce doğrulanmış ravi kimliği kararlarının yeniden kullanılmasının inceleme yükü ve hata riski üzerindeki etkileri değerlendirilecektir.

Bu amaç doğrultusunda aşağıdaki hedeflere ulaşılması planlanmaktadır.

**Hedef 1. İnsan Etiketli Referans Veri Kümesinin Oluşturulması**

Altı hadis kitabından seçilen 300 hadisin ravi geçişleri ve aktarım sırası, iki ekip üyesi tarafından bağımsız olarak etiketlenecektir. Kodlayıcılar arasında en az 0,85 karşılıklı F1 uyumuna ulaşılması hedeflenmektedir. Anlaşmazlıkların üç alan uzmanının değerlendirmeleriyle ele alınması ve etiketleme sürecinin güvenilirliğinin raporlanması planlanmaktadır.

**Hedef 2. Doğrulama Mekanizmalarının Karşılaştırılması**

Kural tabanlı ayrıştırıcı ve büyük dil modellerinin bilgi çıkarma başarıları karşılaştırılacaktır. En az biri açık ağırlıklı olmak üzere üç farklı modelin ikişer kez çalıştırılması planlanmaktadır. Şema ve kanıt denetimlerinin etkileri kesinlik, duyarlılık, F1 ve hata türleri üzerinden değerlendirilecektir. Elde edilen sonuçlarla H1 ve H2 hipotezleri sınanacaktır.

**Hedef 3. İnsan İncelemesinin Etkisinin Ölçülmesi**

Seçilen bir modelin deney koşulunda, işaretlenen ve işaretlenmeyen önerilerin insan tarafından değerlendirilmesi planlanmaktadır. İnceleme sonrasında doğruluk ölçütlerindeki değişim, kabul, ret ve düzeltme oranları ile karar süreleri analiz edilecektir. Bu değerlendirmeyle H3 hipotezinin sınanması hedeflenmektedir.

**Hedef 4. Ravi Kimliği Karar Defterinin Geliştirilmesi**

Önceki ravi kimliği kararlarının yeniden kullanılmasını sağlayan karar defteri mevcut sisteme eklenecektir. Farklı karar yeniden kullanım politikaları, gerekli inceleme sayısı ve fark edilmeden sürdürülen hatalar açısından karşılaştırılacaktır. Böylece H4 hipotezinin gerçek inceleyici kararları üzerinden değerlendirilmesi amaçlanmaktadır.

**Hedef 5. Araştırma Sonuçlarının Paylaşılması**

Geliştirilen yazılımın, deney betiklerinin ve insan tarafından oluşturulan referans etiketlerinin uygun açık lisanslarla paylaşılması hedeflenmektedir. Üçüncü taraf hadis metinleri, dağıtım izinleri doğrultusunda açık veri kapsamı dışında tutulacaktır. Araştırma sonuçlarının en az bir hakemli bilimsel etkinliğe bildiri olarak gönderilmesi ve ön baskı olarak paylaşılması planlanmaktadır.

# 2. YÖNTEM

## 2.1. Araştırma Yaklaşımı

Araştırma, tasarım bilimi yaklaşımı temelinde yürütülecek ve kontrollü deneylerle değerlendirilecektir [@hevner2004design; @wieringa2014design]. Ön çalışma kapsamında geliştirilen GiraffeGraph motoru, bu projede doğrulama mekanizmaları ve ravi kimliği kararlarının yeniden kullanımını destekleyecek şekilde genişletilecektir.

Araştırmada farklı büyük dil modellerinin, doğrulama katmanlarının ve insan incelemesinin bilgi çıkarma başarısına etkileri karşılaştırılacaktır. Ayrıca, önceki ravi kimliği kararlarının farklı politikalarla yeniden kullanılmasının inceleme yükü ve hata riski üzerindeki etkileri ölçülecektir. Bu süreçte yazılımın işlevsel doğruluğu ile üretilen bilgi grafının içerik doğruluğu ayrı değerlendirilecektir.

## 2.2. Veri Kümesi ve Referans Etiketleme

Araştırmada, ön çalışma kapsamında altı hadis kitabından tabakalı örnekleme yöntemiyle seçilen 300 Arapça hadis kullanılacaktır. Türkçe metinlerin kapsam dışında tutulması, tam isnad zincirleri içeren ve kullanım koşulları uygun kaynaklara erişimdeki sınırlılıklara dayanmaktadır. Etiketleme kılavuzu ve inceleme arayüzü ise Türkçe hazırlanacaktır.

Güvenilir bir değerlendirme yapılabilmesi amacıyla ravi adları, kimlikleri ve aktarım sıralarını içeren insan etiketli bir referans kümesi oluşturulacaktır. Etiketleme kılavuzu, ilahiyat alanında görev yapan bir akademisyen ve proje kapsamında belirlenecek iki hadis uzmanının görüşleri doğrultusunda değerlendirilecektir.

İki ekip üyesi, sistem çıktılarını görmeden bağımsız etiketleme yapacaktır. Doğrulama kurallarını geliştiren ekip üyesi bu süreçte kodlayıcı olarak görev almayacaktır. İlk 50 hadisin etiketlenmesinden sonra kodlayıcı uyumu ölçülecek ve gerekli görüldüğünde kılavuz güncellenecektir.

Değerlendirmenin temel birimi, ravi adı ve zincirdeki konumuyla tanımlanan ravi geçişidir. Kodlayıcıların anlaşamadığı geçişler üç alan uzmanı tarafından bağımsız olarak incelenecektir. Uzmanların çoğunluk kararı referans kabul edilecektir. Üç farklı kararın ortaya çıktığı öğeler tartışmalı olarak işaretlenecek, ana değerlendirme dışında tutularak ayrıca raporlanacaktır. Kodlayıcıların uzlaştığı rastgele seçilen 10 hadis de ortak hataların belirlenmesi amacıyla uzmanlar tarafından kontrol edilecektir.

Kodlayıcılar arasındaki uyum karşılıklı F1, uzmanlar arasındaki uyum ise Fleiss' kappa ölçütüyle değerlendirilecektir. Etiketleme süreleri ve anlaşmazlık sayıları kaydedilerek uzman iş yükü de incelenecektir. Referans etiketleri oluşturan uzmanlar sistem çıktılarını görmeyecek ve sonraki insan incelemesi aşamasına katılmayacaktır.

## 2.3. Bilgi Grafı Üretimi ve Doğrulama

GiraffeGraph motorunda büyük dil modeli, kaynak metinden ravi ve aktarım ilişkilerine yönelik öneriler üretmektedir. Modelin bilgi grafına doğrudan yazma yetkisi bulunmamaktadır. Üretilen öneriler, kanonik bilgi grafına aktarılmadan önce doğrulama aşamalarından geçirilecektir.

İlk aşamada **şema denetimi** uygulanacaktır. Bu denetim, önerilen düğümlerin, ilişkilerin ve özelliklerin önceden tanımlanan bilgi grafı şemasına uygunluğunu değerlendirecektir.

İkinci aşamada **kanıt denetimleri** kullanılacaktır. Bu kapsamda alıntının kaynakta bulunması denetimi, modelin sunduğu alıntının özgün metinde yer alıp almadığını kontrol edecektir. Adın alıntıda bulunması denetimi ise önerilen ravi adının ilgili kaynak alıntısında geçip geçmediğini inceleyecektir.

Denetimler sonucunda oluşturulan öneriler insan incelemesine sunulabilecektir. İnceleyici öneriyi kabul edebilecek, reddedebilecek veya düzeltebilecektir. Kabul edilen bilgiler, kaynak bağlantıları ve karar kayıtlarıyla birlikte kanonik bilgi grafına aktarılacaktır. Önceki kararlar silinmeden korunacak ve değişikliklerin izlenebilirliği sağlanacaktır.

Metinsel eşleştirmede Arapça yazım farklılıklarını azaltmak amacıyla Unicode NFKC normalizasyonu uygulanacaktır. Hareke, tatvil, belirlenen noktalama işaretleri ve bazı unvan kalıpları temizlenecektir. Elif ve diğer harflerin önceden belirlenen yazım dönüşümleri kullanılacaktır. Kaynak alıntılarının doğrulanmasında ise metin konumlarını koruyan ayrı bir normalizasyon uygulanacaktır.

Bu denetimler, önerilerin kaynak metinle ve tanımlanan şemayla tutarlılığını değerlendirmeyi amaçlamaktadır. Ancak bir adın kaynakta bulunması, doğru ravi kimliğiyle eşleştirildiğini tek başına göstermemektedir. Bu nedenle kimlik eşleştirmeleri ve isnad sırası, insan etiketli referans kümesiyle ayrıca karşılaştırılacaktır.

## 2.4. Ravi Kimliği Karar Defteri

Hadis isnadlarında aynı ravinin farklı adlarla anılması veya benzer adların farklı kişilere ait olması, kimlik eşleştirmesini zorlaştırabilmektedir. Bu sorunun değerlendirilmesi amacıyla GiraffeGraph motoruna önceki ravi kimliği kararlarının yeniden kullanılmasını sağlayan bir karar defteri eklenecektir.

Kararlar, geçici aday kimlikleri yerine hadis ve standartlaştırılmış ravi adıyla ilişkilendirilecektir. Ayrıca, ilgili ravinin zincirdeki komşularına ait bilgiler saklanacaktır. Ravi tabakası ve vefat yılı gibi bilgilerle çelişen eşleştirmeler yeniden incelemeye açılabilecektir. Yalnızca hâl eki bakımından farklılaşan adlara yönelik otomatik kabul kuralları da karar kayıtlarıyla birlikte izlenecektir.

Kararların yeniden kullanılması üç farklı politika altında karşılaştırılacaktır.

- **P1. Ada dayalı yeniden kullanım:** Önceki kimlik kararları yalnızca standartlaştırılmış ravi adına göre kullanılacaktır.
- **P2. Bağlama dayalı yeniden kullanım:** Kararlar, zincirde ilgili addan önce yer alan ravi (öğrenci) ve ravi adı çiftine göre saklanacaktır. Her farklı çift için ayrı değerlendirme yapılacaktır.
- **P3. Uyarlanabilir yeniden kullanım:** Kararlar başlangıçta ravi adına göre kullanılacaktır. Bir çelişki belirlenmesi durumunda kararın kullanım kapsamı önce öğrenciye, ardından zincirde ilgili addan sonra yer alan raviye (hoca) göre daraltılacaktır.

Bu politikalar, gerekli inceleme sayısı ve sessiz hata oranı açısından değerlendirilecektir. Sessiz hata, yeniden kullanılan bir kimlik kararının ilgili geçiş için verilmiş gerçek inceleyici kararıyla uyuşmaması olarak tanımlanmaktadır.

Böylece kararların yeniden kullanımından sağlanan inceleme tasarrufu ile yanlış eşleştirmelerin sürdürülme riski birlikte araştırılacaktır.

## 2.5. Deney Tasarımı

Araştırmada aynı 300 hadis üzerinde beş deney koşulu karşılaştırılacaktır. İlk koşulda kural tabanlı bir isnad ayrıştırıcı kullanılacaktır. Diğer koşullarda büyük dil modeli çıktıları farklı doğrulama aşamalarından geçirilecektir.

| Koşul | Uygulama | Değerlendirilen etki |
|---|---|---|
| K0 | Kural tabanlı isnad ayrıştırıcı | Başlangıç performansı |
| K1 | Yalnızca büyük dil modeli | Ham bilgi çıkarma başarısı |
| K2 | Model ve şema denetimi | Şema doğrulamasının katkısı |
| K3 | Model, şema ve kanıt denetimleri | Kaynak doğrulamasının katkısı |
| K4 | Model, tüm denetimler ve insan incelemesi | İnsan incelemesinin katkısı |

K1, K2 ve K3 koşullarının, en az biri açık ağırlıklı olmak üzere üç farklı modelle ikişer kez yürütülmesi planlanmaktadır. K4 koşulunda ise seçilen bir modelin tek deney çıktısı üzerinde bir kez insan incelemesi gerçekleştirilecektir.

İnsan incelemesi, ilgili hadisin referans etiketlerini oluşturmamış bir ekip üyesi tarafından yapılacaktır. İşaretlenen ve işaretlenmeyen önerilerin tamamı değerlendirmeye alınacaktır.

Deneylerde kullanılan istemler, model yanıtları, yazılım sürümleri ve denetim sonuçları kaydedilecektir. Böylece koşullar arasındaki farkların incelenmesi ve deneylerin yeniden yürütülmesi mümkün olacaktır.

## 2.6. Değerlendirme Ölçütleri ve Hipotezlerin Sınanması

Bilgi çıkarma başarısı kesinlik (precision), duyarlılık (recall) ve F1 ölçütleriyle değerlendirilecektir. Önerilen ravi geçişleri insan etiketli referans kümesiyle karşılaştırılacaktır.

Eşleştirmede katı ve gevşek olmak üzere iki yaklaşım kullanılacaktır. Katı eşleştirmede standartlaştırılmış adların aynı olması aranacaktır. Gevşek eşleştirmede ise alt dizi ilişkisi veya sözcük düzeyinde en az 0,60 F1 benzerliği yeterli kabul edilecektir. Eşleştirme kuralları deneylerden önce belirlenecektir.

Kaynakta bulunmayan ravi önerileri, değiştirilmiş adlar, şemaya aykırı çıktılar ve isnad sırasındaki hatalar ayrı kategoriler altında raporlanacaktır.

**H1 kapsamında**, adın alıntıda bulunması denetimi ile modelin güven skoru karşılaştırılacaktır. Her iki yaklaşımın eşit sayıda öneriyi incelemeye ayırdığı durumlar esas alınacaktır. Modelin ürettiği güven skorları, doğrulanmış olasılıklar olarak kabul edilmeyecektir. Ön çalışmada sınırlı sayıda farklı güven skoru gözlemlendiğinden, eşit skorlu önerilerin seçim kuralı deneylerden önce belirlenecektir.

**H2 kapsamında**, ham model önerilerinin hata oranı ile doğrulama sonrasında incelemesiz kabul edilen önerilerin hata oranı karşılaştırılacaktır. Hata oranındaki değişim değerlendirilirken doğru önerilerin de elenmesinden kaynaklanabilecek duyarlılık kaybı dikkate alınacaktır.

**H3 kapsamında**, denetimler tarafından işaretlenen önerilerin insan tarafından reddedilme veya düzeltilme olasılığı incelenecektir. Bu amaçla işaretlenme durumu, gerekçe kodları ve modelin güven skorları kullanılarak lojistik regresyon analizi yapılacaktır. Standart hatalar hadis düzeyinde kümelenecektir. İnceleme kararları ve karar süreleri de raporlanacaktır.

**H4 kapsamında**, aynı gerçek ravi kimliği kararları P1, P2 ve P3 politikaları altında yeniden yürütülecektir. Politikalar arasındaki inceleme sayısı ve sessiz hata oranı farkları karşılaştırılacaktır. Hadislerin işlenme sırasının sonuçlara etkisi de değerlendirilecektir.

Deney koşulları arasındaki performans farklarının belirsizliği, hadis düzeyinde eşli bootstrap yöntemiyle hesaplanan güven aralıkları üzerinden incelenecektir. Hipotezleri desteklemeyen sonuçlar da araştırma bulguları arasında raporlanacaktır.

## 2.7. Ön Çalışma ve Araştırmanın Kapsamı

GiraffeGraph motorunun temel bilgi çıkarma ve doğrulama bileşenleri, TÜBİTAK desteği öncesinde yürütülen çalışmalar kapsamında geliştirilmiştir. Ön çalışma sonuçları araştırmanın deneysel tasarımına temel oluşturmuştur.

Bitirme projesi kapsamında iki ekip üyesinin 50 hadisi bağımsız olarak etiketlemesi, uzman değerlendirmelerinin gerçekleştirilmesi ve prototipin 100 hadis üzerinde uçtan uca çalıştırılması hedeflenmektedir.

TÜBİTAK projesinde ise insan etiketli referans kümesinin 300 hadise genişletilmesi, deneylerin farklı büyük dil modelleriyle tekrarlanması ve ravi kimliği karar defterinin gerçek inceleyici kararları üzerinden değerlendirilmesi planlanmaktadır.

GiraffeGraph, farklı alanlara uyarlanabilecek şema tabanlı bir bilgi grafı üretim altyapısı olarak tasarlanmıştır. Bununla birlikte, bu araştırmanın deneysel değerlendirmesi hadis isnad zincirleriyle sınırlandırılmıştır. Hadislerin dinî açıdan sıhhatine ilişkin hüküm verilmesi araştırmanın kapsamı dışındadır.

# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

| Proje Süresi (Ay) | Faaliyetler | Kim(ler) Tarafından Gerçekleştirileceği | Başarı Ölçütü ve Araştırmanın Başarısına Katkısı |
|---|---|---|---|
| 2 | (1.–2. ay) İP1: Etiketleme kılavuzunun hazırlanması ve ilk 50 hadis üzerinden değerlendirilmesi. Karar kayıtlarının geliştirilmesi. | Tüm proje ekibi ve alan uzmanları | Etiketleme kılavuzunun oluşturulması, kodlayıcı uyumunun ölçülmesi ve karar kayıtlarının test edilmesi. Katkı: %20 |
| 3 | (2.–4. ay) İP2: Referans veri kümesinin 300 hadise tamamlanması ve model deneylerinin yürütülmesi. | Alperen Ulukaya, Deniz Büyükşahin ve alan uzmanları | En az 0,85 karşılıklı F1 uyumunun hedeflenmesi, üç modelle ikişer deney yapılması ve H1 ile H2 ölçümlerinin tamamlanması. Katkı: %30 |
| 3 | (3.–5. ay) İP3: Ravi kimliği karar defterinin genişletilmesi, insan incelemesinin gerçekleştirilmesi ve karar politikalarının karşılaştırılması. | Yahya Efe Kuruçay, Alperen Ulukaya | Karar defterinin test edilmesi, inceleme kayıtlarının oluşturulması ve H3 ile H4 değerlendirmeleri için gerekli verilerin elde edilmesi. Katkı: %30 |
| 2 | (5.–6. ay) İP4: Deney sonuçlarının analiz edilmesi, hipotezlerin değerlendirilmesi ve araştırmanın raporlanması. | Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya | Performans karşılaştırmalarının, güven aralıklarının ve hata analizlerinin tamamlanması. Deney sonuçlarının yeniden üretilebilirliğinin kontrol edilmesi. Katkı: %20 |

## 3.2. Risk Yönetimi

| En Önemli Riskler | Alınacak Tedbirler (B Planı) |
|---|---|
| R1. Veri kaynaklarının kullanım ve paylaşım izinlerinde sorun yaşanması. | Kullanım koşulları uygun kaynaklar tercih edilecektir. Dağıtım izni bulunmayan metinler yayımlanmayacak, paylaşım yalnızca izin verilen içerikler ve üretilen etiketlerle sınırlandırılacaktır. |
| R2. Kodlayıcılar arasında hedeflenen uyumun sağlanamaması. | Etiketleme kılavuzu uzman görüşleriyle yeniden değerlendirilecek ve gerektiğinde ek kalibrasyon çalışması yapılacaktır. |
| R3. Etiketleme ve insan incelemesinin planlanandan uzun sürmesi. | İlk 50 hadisin süre ölçümleriyle iş yükü yeniden değerlendirilecektir. Gerekirse işaretlenmeyen önerilerden rastgele örnekleme yapılacak ve örnekleme yöntemi analizlerde dikkate alınacaktır. |
| R4. Modellerin erişiminde, maliyetinde veya çıktı biçiminde sorun yaşanması. | Açık ağırlıklı modellerin yerel çalıştırılması değerlendirilecek ve çıktıların şemaya uygunluğu otomatik olarak kontrol edilecektir. |
| R5. Akademik yoğunluk nedeniyle iş takviminin aksaması. | Bağımsız faaliyetler mümkün olduğunca paralel yürütülecek ve iş paketlerindeki zaman payları kullanılacaktır. |
| R6. Yazılım hatalarının deney sonuçlarını etkilemesi. | Otomatik testler uygulanacak, ölçümler betiklerle hesaplanacak ve sonuçların yeniden üretilebilirliği kontrol edilecektir. |
| R7. Alan uzmanlarından birinin değerlendirme sürecine katılamaması. | Kalan iki uzmanın bağımsız değerlendirmeleri kullanılacaktır. Uzlaşma sağlanamayan öğeler tartışmalı olarak işaretlenecek ve ana analiz dışında ayrıca raporlanacaktır. |

## 3.3. Araştırma Olanakları

| Kuruluşta Bulunan Altyapı/Ekipman Türü, Modeli (Laboratuvar, Araç, Makine-Teçhizat, vb.) | Projede Kullanım Amacı |
|---|---|
| Akdeniz Üniversitesi Bilgisayar Mühendisliği Bölümü yazılım geliştirme laboratuvarı | Yazılım geliştirme, test ve etiketleme çalışmalarında kullanılacaktır. |
| Akdeniz Üniversitesi Bilgisayar Mühendisliği Bölümü sunucuları ve kampüs ağı | Veritabanlarının barındırılması ve uygun modellerin yerel ortamda çalıştırılması için değerlendirilecektir. |
| İlahiyat alanında görev yapan bir akademisyen ve iki hadis alan uzmanının desteği | Etiketleme kılavuzunun değerlendirilmesi, anlaşmazlıkların incelenmesi ve alan bilgisi desteğinin sağlanması amaçlanmaktadır. |
| GiraffeGraph motoru, deney betikleri ve ön çalışma çıktıları | Mevcut sistemin geliştirilmesinde ve deneylerin yürütülmesinde temel altyapı olarak kullanılacaktır. |

# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Çıktı, Etki ve Kazanımlar | Öngörülen Çıktı(lar), Etki(ler) ve Kazanım(lar) |
|---|---|
| **Bilimsel/Akademik Çıktılar** | Araştırma bulgularının en az bir uluslararası kongreye bildiri olarak gönderilmesi ve ön baskı olarak paylaşılması hedeflenmektedir. Elde edilen sonuçların bitirme tezinde değerlendirilmesi planlanmaktadır. |
| **Ekonomik/Ticari/Sosyal Çıktılar** | GiraffeGraph motorunun ve deney betiklerinin açık kaynak olarak yayımlanması planlanmaktadır. İnsan etiketli 300 hadislik referans kümesinin, kaynak metinlerin paylaşım hakları gözetilerek araştırmacıların kullanımına sunulması hedeflenmektedir. Ayrıca, araştırma sonuçlarının üniversite bünyesinde düzenlenecek bir seminerle paylaşılması öngörülmektedir. |
| **Yeni Proje(ler) Oluşturmasına Yönelik Çıktılar** | Elde edilen bulguların ravi kimliklerinin otorite listeleriyle eşleştirilmesi ve bilgi grafı üzerinden soru cevaplama gibi sonraki çalışmalara temel oluşturması beklenmektedir. İlahiyat ve bilgisayar mühendisliği alanları arasındaki akademik iş birliğinin sürdürülmesi hedeflenmektedir. |

# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

Araştırmanın ön çalışması kapsamında GiraffeGraph motorunun temel bileşenleri geliştirilmiş ve ilk deneysel ölçümler TÜBİTAK desteği öncesinde gerçekleştirilmiştir. Bu çalışmalar, proje kapsamında yürütülmesi planlanan deneysel araştırmanın başlangıç altyapısını oluşturmaktadır.

Araştırmada kullanılacak üçüncü taraf hadis metinlerinin erişim ve paylaşım koşulları dikkate alınacaktır. Dağıtım izni bulunmayan kaynak metinler yayımlanmayacaktır. Geliştirilen yazılım, deney betikleri, kaynak kimlikleri ve araştırma kapsamında oluşturulan referans etiketleri uygun açık lisanslarla paylaşılacaktır.

# 6. EKLER

## EK-1: KAYNAKLAR

<!-- references -->

# Göndermeden önce (başvuru metnine girmez)

1. **TYBS'deki girişler.** Bilimsel alan: Teknik Bilimler > Bilgisayar Bilimleri > Yapay Zeka, Bilgisayarda Öğrenme ve Örüntü Tanıma. Öncelikli alan: Evet, Yapay Zeka. Bütçe: Hizmet Alımı 12.000 TL (programın üst sınırı), Makine Teçhizat, Sarf Malzemesi ve Ulaşım 0. Üretken yapay zekâ beyanı ve taahhüdü TYBS'deki ayrı bölümde verildi. Kalan adım danışman onayıdır; ardından kurum yetkilisinin e-imzası gelir (16–23 Kasım).
2. **Kaynakçada atıfsız kaynak.** TYBS kaynakçasında [6] Li vd. 2016 (BioCreative V CDR) durur, ancak metinde bu kaynağa atıf yoktur; biyomedikal karşılaştırma cümlesi metinden çıkarılmıştır. ÜYZ taahhüdünün 1. maddesi kaynakçadaki her kaynağa metinde atıf yapıldığını beyan eder; danışman onayından önce kaynak TYBS kaynakçasından çıkarılmalıdır. Bu dosyanın derlemesi yalnız atıf yapılan kaynakları listeler.
3. **Kaynakça biçimi.** TYBS, "Kaynakçayı Numaralandır" düğmesine basılmadan kaynakçayı kaydetmez ve listeyi [1]–[n] biçiminde numaralar. Metin içi atıflar TÜBİTAK'ın yazar-yıl biçimindedir (<https://tubitak.gov.tr/tr/duyuru/bibliyografik-verilerin-duzenlenmesi>); bu dosyanın derlemesi alfabetik, numarasız liste üretir. Crossref'e göre Kamran vd. 2026 makale numarasıyla kayıtlıdır ve sayfa aralığı yoktur; kaynakçadaki "1–27" kaynak paketinden gelir. Haque ve Islam 2026 bir arXiv ön baskısıdır.
4. **Takvim kuralı.** 2209-A bilgi notu rapor yazımının ayrı iş adımı olarak gösterilmesini istemez (<https://tubitak.gov.tr/sites/default/files/2026-10/2209-A_Basvuru_Icerigi_Bilgi_Notu.pdf>); İP4 "araştırmanın raporlanması" ifadesini taşır. Proje Süresi alanı yalnız sayı kabul ettiği için ay aralıkları faaliyet metninin başına yazılmıştır.
5. **Alan uzmanlarının desteği.** Üç hadis uzmanının destek beyanları alınmalıdır. Beyanlar, kılavuzu gözden geçirme ve anlaşmazlıklarda bağımsız karar verme rollerini kapsamalı; uzmanların inceleme kuyruğunda karar vermeyeceğini belirtmelidir.
6. **Eşikler.** H1 (%60), H2 (%50), H4 (%20 ve 0,02) ve Hedef 1 (karşılıklı F1 ≥ 0,85) danışman onayıyla bağlayıcı olur.
7. **Metin kaynağı ve lisans.** 300 hadislik test kümesinin metin ve etiket kaynaklarının lisansı teyit edilmemiştir (`data/README.md`). R1'deki B planı buna göre yazılmıştır.
8. **Kalkınma Planı.** 1.1'deki cümle 12. Kalkınma Planı'nın 591. maddesine dayanır; madde plan metninde doğrulandı. Planda "büyük dil modeli" ve "üretken yapay zekâ" geçmez.
9. **Bütçe ve fatura.** Çağrının 6.2. maddesine göre harcamalar faturayla belgelenir. Yurt dışı model API hizmet faturalarının kabul edilip edilmediği doğrulanmadı; danışmana ve proje ofisine sorulmalıdır. Bütçe başvurular kapandıktan sonra değiştirilemez.
10. **Üretken yapay zekâ.** TÜBİTAK ÜYZ Rehberi'nin 1.5.3. maddesi yayımlanmamış araştırma verisini ÜYZ araçlarına girmeyi yasaklar (<https://tubitak.gov.tr/sites/default/files/2026-01/UYZ_Rehberi_v04_TR.pdf>); ön çalışma verisi ve taslak yapay zekâ araçlarıyla işlendi. Çağrının 8.5. maddesine göre ÜYZ ile üretilen içeriğin doğruluğundan danışman sorumludur.
