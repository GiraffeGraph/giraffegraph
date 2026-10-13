# 8 Destek çalışmaları: neyin saklanması gerekir

Bölüm 7'de motorun kontrollerini ölçtük. Bu bölümde tasarımın diğer yarısı olan karar kaydı üzerine iki küçük çalışmayı raporluyoruz. Bölüm 2.6'da projenin dayandığı iddiayı belirtmiştik. Bir kaynaktan türetilebilen olgu yeniden türetilmelidir; bir kişinin verdiği karar ise türetilemez ve bir kez saklanmalıdır. İlk çalışma, etiketli isnad zincirlerinde kimlik kararını saklamanın ne kazandırdığını sorar. İkinci çalışma aynı soruyu farklı bir alanda, motorun kendi kaynak kodunu okuyan bir kod ajanında sorar.

İki çalışma da keşif amaçlıdır ve 13 Ekim 2026'da gerçekleştirilmiştir. İlki, veri kümesinin etiketlerinin inceleyicinin yerine geçtiği bir benzetimdir. İkincisinde okuyucu olarak bir dil modeli kullanılır. İkisine de hiçbir kişi katılmamıştır; bunun sonuçlarını Bölüm 8.3'te belirtiyoruz.

## 8.1 Etiketli isnad zincirlerinde kimlik kararının yeniden kullanımı

Bölüm 7.10, yazılı bir adın ravinin kimliği olmadığını gösterdi. Bunu çözen "bu ad, burada, şu kişidir" kararı, motorun kaydettiği türden bir karardır. Böyle bir kararın ne sıklıkta yeniden kullanılabildiğini ve bu kullanımın maliyetini sorduk.

**Benzetim.** Bir defter, etiketli zincirleri her seferinde bir geçiş okuyarak işler. Daha önce görmediği bir anahtarla karşılaşınca inceleyiciye sorar; yanıt, veri kümesinin etiketidir. Sonrasında aynı anahtar için bu yanıtı yeniden kullanır. İnceleyiciye giden her şey bir *soru* sayılır. Etiketle uyuşmayan ve hiçbir inceleyicinin görmediği, yeniden kullanılmış yanıt ise *sessiz hata* sayılır. İkisini de geçiş başına raporluyoruz. Modül `evaluation/identity_ledger.py`'dır; zincirlerin sırası rastgeledir ve değerler beş sıra üzerinden alınan ortalamalardır.

**Veriler.** AR-Sanad 280K test zincirleri [@mahmoud2022arsanad]: 27.056 zincir, 150.904 geçiş, 6.378 kişi ve 15.301 farklı yazılı ad; bu adların 815'i birden fazla kişiyi temsil eder. Tekrar çalışmasında, altı Ifta kitabının ravi kimliği içeren hadislerini kullanıyoruz: 34.681 hadis, 205.514 geçiş ve 6.891 kişi. İki etiket kümesi farklı kaynaklardan gelir [@internal-data-manifest]. Zincirde bir geçişten önce adı verilen raviyi onun *öğrencisi*, sonra adı verileni ise *hocası* olarak adlandırıyoruz.

**Kararın kapsamı.** Defter, her yanıtı tam bağlamıyla (öğrenci, ad, hoca) saklar. Yanıt yeniden kullanılmadan önce sonraki bir geçişin bu bağlamın hangi kısmını paylaşması gerektiği, kararın kapsamıdır. Yalnız ad kapsamı, en fazla yeniden kullanımı ve en fazla hatayı verir. Tablo 8.1'de iki sabit kapsamı ve üç daraltma biçimini sunuyoruz.

Daraltma politikalarında kapsam önceden seçilmez. Her ad yalnız ad kapsamıyla başlar; ancak o ad için bir çelişki görüldükten sonra öğrencisine bağlanır. Çelişki algılayıcısı, ravi kataloğu üzerinde çalışan deterministik bir kuraldır: defterin önerdiği kişiyle komşu ravi arasındaki tabaka farkı beşten büyük ya da eksi birden küçükse veya vefat yılları arasındaki fark 85 yıldan büyük ya da eksi 20'den küçükse inceleyiciye sorulur. Sınırlar AR-Sanad zincirlerinde seçilmiştir; burada etiketli komşu çiftlerin %0,8'ini işaretlerler. Ifta verilerine değiştirilmeden uygulanmışlar ve burada %3,4'ünü işaretlemişlerdir.

**Tablo 8.1** İki etiket kümesinde beş politika için geçiş başına soru ve sessiz hata (beş rastgele sıra üzerinden ortalamalar). "Sonradan bilme", belirsiz olduğu bilinen adları dar kapsamda başlatır; etiketleri önceden gerektirir ve bir üst sınırdır.

| Politika | AR-Sanad: sorular | AR-Sanad: sessiz hatalar | Ifta: sorular | Ifta: sessiz hatalar |
|---|---|---|---|---|
| Sabit kapsam: ad | 0,101 | 0,100 | 0,077 | 0,102 |
| Sabit kapsam: ad; kural yalnız işaretlenen geçişi sorar | 0,204 | 0,054 | 0,229 | 0,049 |
| Kuralla daralan kapsam | 0,178 | 0,014 | 0,199 | 0,010 |
| Sabit kapsam: öğrenci ve ad | 0,340 | 0,006 | 0,292 | 0,007 |
| Sonradan bilme | 0,187 | 0,006 | 0,157 | 0,007 |

Yalnız adla anahtarlanan karar, her on geçişten birinde yanlış yeniden kullanılır. Öğrenci ve adla anahtarlamak bu hataların neredeyse tamamını kaldırır, ancak yaklaşık üç katı soru gerektirir. Kapsamı yalnız kuralın çelişki gördüğü yerlerde daraltmak, dar anahtarın hatasına yaklaşır (AR-Sanad'da 0,006'ya karşı 0,014, Ifta'da 0,007'ye karşı 0,010); soru sayısı ise onun yaklaşık yarısı ile üçte ikisi arasındadır.

Aynı kural iki biçimde kullanıldı. Yalnız işaretlenen geçişi inceleyiciye gönderdiğinde hata 0,05 yakınında kalır. İşaretleme aynı zamanda o adın kapsamını daralttığında, bir çelişki adın sonraki bütün geçişlerini korur; hata 0,014 ve 0,010'a düşer.

**Defterin görmediği bir kitap.** Altı Ifta kitabının beşinden defteri doldurup altıncısında sayım yaptık; bunu her kitap için sırayla tekrarladık. Kuralla daralan kapsamda geçiş başına sessiz hata 0,004 ile 0,016, soru 0,138 ile 0,249 arasındaydı. Öğrenci ve adın sabit kapsamında hata 0,007 ile 0,023, soru 0,151 ile 0,307 arasındaydı; daraltma politikası her kitapta daha az soru sordu. Yalnız adla hata 0,091 ile 0,151 arasındaydı: başka bir kitaptan taşınan yanıt, aynı adı taşıyan başka bir kişiye ait olabilir.

**Hata yapan bir inceleyici.** Benzetimdeki inceleyici, belirsiz adların %5'i için yanlış yanıt verdiğinde (AR-Sanad), daraltma politikası geçiş başına 0,219 soru ve 0,018 sessiz hata; öğrenci ve adın sabit kapsamı ise 0,340 ve 0,019 verir. Yanlış yanıtlar sahte çelişkiler, dolayısıyla daha fazla soru üretir; politikaların sıralaması değişmez.

**Karar, yeniden çıkarımdan sonra da kullanılabilir mi?** Saklanan bir karar, ancak metinden ikinci kez çıkarım yapıldığında yeniden bulunabiliyorsa yararlıdır. Motor, kararı bir adaya bağlar. Bölüm 7'deki dört koşunun ravi adaylarını karşılaştırdık; hedef hadis ve normalize ad çifti olduğunda, bir koşunun adaylarının ne kadarının başka bir koşuda karşılığı olduğunu sorduk (`evaluation/decision_reapplication.py`). Aynı modelin iki istemi arasında pay, altı yönde 0,857 ile 0,977 arasındadır. Ayrıştırıcının metin aralıkları uzun kaldığı için kural tabanlı ayrıştırıcı ile bir model koşusu arasında 0,561 ile 0,634 arasındadır. Aday kimliğine bağlandığında pay, yapı gereği sıfırdır. Hiçbir karar verilmediğinden bu, kararların değil hedeflerin örtüşmesini ölçer.

## 8.2 İkinci bir alan: kod ajanı için neyin saklanması gerekir

İkinci çalışma hadis alanının dışına çıkar. Türetilebilir olgular ile kararlar arasındaki ayrımın, başka bir okuyucu ve başka tür bir kaynak için de geçerli olup olmadığını sorar: bir kod tabanı hakkında soruları yanıtlayan kod ajanı. Kod tabanı, motorun kendi arka ucudur (141 dosya, 16.923 satır); tasarım, sorular ve koşular deneyle birlikte belgelenmiştir [@internal-agent-experiment].

**Düzenek.** Ajan, düşük çaba ayarında Claude Haiku 5.5'tir ve salt okunur üç aracı vardır: dizin listeleme, dosya okuma ve arama. Üç sınıfın her birinde on iki olmak üzere 36 soruyu yanıtlar. *Değişmeyen* sorular, 5 Nisan 2026 kodunda ve güncel kodda aynı olan yapısal bir olguyu sorar. *Değişen* sorular, Ekim'deki yeniden yazımın değiştirdiği yapısal bir olguyu sorar. *Karar* soruları bir şeyin neden o biçimde olduğunu sorar; yanıtları kodda değil, projenin karar kayıtlarındadır. Sınanan belgeleri görmeyen ayrı bir ajan soruları ve cevap anahtarını yazdı: yapısal sorular için koddan, karar soruları için projenin karar kayıtlarından.

Koşullar yalnız bir `docs/` klasörünün içeriğinde farklılaşır: hiçbir şey; her biri gerekçesini ve reddedilen alternatifi içeren, türetilebilir hiçbir olgu içermeyen 30 kararlık bir defter; defterle birlikte güncel koddan yazılmış, kodu açıklayan bir sayfa (taze sayfa); defterle birlikte aynı talimatlarla 5 Nisan kodundan yazılmış bir sayfa (bayat sayfa). Bir düzende ajan `docs/` klasörünü kendisi açmak zorundadır; diğerinde belgeler isteme de yerleştirilir. Araç çağrısı hakkı 14, 4 ya da 2'dir. Her hücre iki kez çalıştırılmıştır. Yanıtlar, koşulu görmeyen aynı model tarafından yazılı anahtara göre puanlanmıştır. Analiz birimi sorudur; aralıklar sorular üzerinden bootstrap aralıklarıdır. Temel tasarımda 2.880 koşu vardır; aşağıda açıklanan sonraki deney kollarıyla birlikte deney 5.520 koşu içerir.

**Tablo 8.2** 14 araç çağrısı hakkıyla doğru yanıtların payı (24 yapısal soru ve 12 karar sorusu, her biri için iki koşu).

| `docs/` içeriği | Yapısal, ajan `docs/` klasörünü açar | Yapısal, belgeler istemde | Karar, ajan `docs/` klasörünü açar | Karar, belgeler istemde |
|---|---|---|---|---|
| Hiçbir şey | 0,979 | 0,938 | 0,042 | 0,000 |
| Karar defteri | 0,938 | 0,979 | 1,000 | 0,958 |
| Defter ve taze sayfa | 0,979 | 0,958 | 1,000 | 0,917 |
| Defter ve bayat sayfa | 0,896 | 1,000 | 0,875 | 0,958 |

Yeterli araç çağrısıyla ajan yapıyı koddan okur. Belge olmadan yapısal soruların %94 ile %98'ini yanıtlar ve hiçbir belge türü bunu değiştirmez. `docs/` klasörünü kendisinin açması gereken 432 yapısal koşuda klasörü bir kez bile açmadı. Belgeleri isteme yerleştirmek, yapısal soru başına istem belirteçlerini 21.843'ten 45.343 ile 75.443 arasına çıkardı. Karar sorularında ise durum tersidir. Defter olmadan ajan bunların neredeyse hiçbirini, defterle neredeyse tamamını yanıtlar.

**Tablo 8.3** Belgeler istemdeyken ve araç çağrısı hakkı azken yapısal sorular.

| `docs/` içeriği | 2 çağrı: tamamı | 2 çağrı: değişmeyen | 2 çağrı: değişen | 4 çağrı: tamamı |
|---|---|---|---|---|
| Hiçbir şey | 0,312 | 0,375 | 0,250 | 0,750 |
| Taze sayfa | 0,875 | 0,792 | 0,958 | 0,979 |
| Bayat sayfa | 0,688 | 0,875 | 0,500 | 0,812 |

Kodun saklanan açıklaması, yalnız kodu okumak pahalı olduğunda yarar sağlar. Taze sayfa, belgesiz koşula göre doğru yanıt payını iki araç çağrısında 0,56 (aralık 0,38 ile 0,75 arasında), dört çağrıda 0,23 (0,10 ile 0,38 arasında) artırır; on dört çağrıda ise artırmaz. Değişen olgularda bayat sayfa, taze sayfanın yaklaşık yarısı sıklıkta doğrudur.

Saklanan açıklamayı yeniden yazmadan geçerli tutmanın üç yolunu denedik: her bölümün altına, yazıldığı kodun değişip değişmediğini belirten makine üretimi bir not; olguları saklanan seçiciler aracılığıyla güncel koddan doldurulan cümleler; sayfanın yazılmasından sonra eklenen sembollerin listesi. Hiçbiri güncel koddan yeniden yazılmış sayfaya yaklaşmadı. İki çağrıda değişen olgular için doldurulan cümleler 0,625, bayat sayfa 0,500, taze sayfa 0,958 verdi.

Bir ifadenin nereye konduğu, ajana ulaşıp ulaşmadığını belirler. Taze sayfanın tek satırlık notlara bölünüp kaynak ağacına yerleştirilmesi, yalnız arama aracı eşleşen notları koddan önce döndürdüğünde yardımcı olur: iki çağrıda yapısal sorulardaki kazanım, Claude Haiku 5.5 ve Claude Sonnet 5.5 modellerinde 0,15 ile 0,31 arasındadır; dosyalar karıştırılmış sırada arandığında ise 0,04'tür (aralık −0,15 ile 0,23 arasında). Bu kazanımların en küçüğünün aralığı sıfıra ulaşır. Sonnet koşularında notsuz deney kolu, 48 koşunun 5'inde boş yanıt döndürdü. Bu, güvenilir karşılaştırmanın sınırı olarak önceden belirlediğimiz %10'un üzerinde olduğundan bu iki kazanımı bu çekinceyle raporluyoruz.

## 8.3 İki çalışmanın ekledikleri ve göstermedikleri

İki çalışma, iddianın ilk yarısında Bölüm 2.6 ile uyumludur. Ajan bir kararı koddan elde edemedi; ravinin kimliği de yazılı addan elde edilemedi. Her iki durumda da yanıtın bir kez bir kişiden gelmesi ve saklanması gerekir.

İkinci yarıyı ise sınırlarlar. Türetilebilir bir olgu, kullanım anında türetilmesi ucuzsa saklanmak zorunda değildir; ucuz değilse saklanan kopya yarar sağlar. Ajan için iki araç çağrısında, çıkarımın bir model çağrısı ve inceleme gerektirdiği her yerde durum budur. Yeniden üretilmeyen saklanmış kopya, tam da değişen olgularda yanıltır.

Bir değişken daha eklerler. Saklanan kararın bir kapsamı vardır; kapsamın saklanması gerekmemiştir: algılayıcı olarak deterministik bir alan kuralı kullanılarak çelişkilerden türetilmiştir. Mekanizmanın yeni olduğunu iddia etmiyoruz. Bir düzeltmeyi önceki yanıtın başarısız olduğu bağlama bağlamak, bilgi ediniminde ripple-down rules adıyla bilinir; kaynağın tamamını okumadan bibliyografik kaydından atıf veriyoruz [@compton1990philosophical].

Sınırlar, benzetimlerin sınırlarıdır. Defter çalışmasında inceleyici veri kümesinin etiketidir; dolayısıyla ilk yanıt ücretsizdir ve %5 varyantı dışında daima doğrudur. Bir soru, kişiden ne kadar zaman isteyeceğine bakılmadan bir birim sayılır. AR-Sanad kişi etiketlerinin nasıl atandığı belgelenmemiştir; altı kitap ravilerinin çoğunu paylaştığı için uzak bir kitap sınanmamıştır. Ajan çalışmasında 17 bin satırlık bir kod tabanı, sınıf başına on iki soru ve hücre başına iki koşu vardır; puanlayıcı ajanla aynı modeldir; sayfalar kişiler değil ajanlar tarafından yazılmıştır; ikinci model ise yalnız iki karşılaştırmada çalışmış ve aynı model ailesinden gelmiştir. İki çalışma da motoru ölçmez ve ikisi de Bölüm 10.1'de planlanan inceleyici deneyinin yerini tutmaz.
