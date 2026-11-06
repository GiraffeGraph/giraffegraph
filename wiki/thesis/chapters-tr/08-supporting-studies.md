# 8 Destek çalışmaları: neyin saklanması gerekir

Bölüm 7'de motorun denetimleri ölçülmüştür. Bu bölümde ise tasarımın diğer yarısını oluşturan karar kaydına ilişkin iki küçük çalışma raporlanmaktadır. Projenin dayandığı iddia Bölüm 2.6'da belirtilmiştir: bir kaynaktan türetilebilen olgu yeniden türetilmelidir; bir kişinin verdiği karar ise türetilemediğinden bir kez saklanmalıdır. İlk çalışmada, etiketli isnad zincirlerinde kimlik kararını saklamanın sağladığı kazanım ele alınmaktadır. İkinci çalışmada aynı soru farklı bir alanda, motorun kendi kaynak kodunu okuyan bir kod ajanı üzerinden incelenmektedir.

Her iki çalışma da keşif amaçlıdır ve 13 Ekim 2026'da gerçekleştirilmiştir. İlk çalışma, veri kümesinin etiketlerinin inceleyicinin yerine geçtiği bir benzetimdir. İkinci çalışmada ise okuyucu olarak bir dil modeli kullanılmıştır. Çalışmaların hiçbirine kişi katılmamıştır; bu durumun sonuçları Bölüm 8.3'te belirtilmektedir.

## 8.1 Etiketli isnad zincirlerinde kimlik kararının yeniden kullanımı

Bölüm 7.10'da, yazılı bir adın ravinin kimliği olmadığı gösterilmiştir. Bu sorunu çözen "bu ad, burada, şu kişidir" kararı, motorun kaydettiği türden bir karardır. Çalışmada böyle bir kararın ne sıklıkta yeniden kullanılabildiği ve bu kullanımın maliyeti incelenmiştir.

**Benzetim.** Defter, etiketli zincirleri her seferinde bir geçiş okuyarak işlemektedir. Daha önce karşılaşmadığı bir anahtar için inceleyiciye başvurulmakta ve yanıt olarak veri kümesinin etiketi alınmaktadır. Sonrasında aynı anahtar için bu yanıt yeniden kullanılmaktadır. İnceleyiciye yönlendirilen her şey bir *soru*, etiketle uyuşmayan ve hiçbir inceleyicinin görmediği, yeniden kullanılmış yanıt ise *sessiz hata* sayılmaktadır. Her iki ölçüt de geçiş başına raporlanmaktadır. Kullanılan modül `evaluation/identity_ledger.py`'dır; zincirlerin sırası rastgeledir ve değerler beş sıra üzerinden alınan ortalamalardır.

**Veriler.** AR-Sanad 280K test zincirleri [@mahmoud2022arsanad], 27.056 zincir, 150.904 geçiş, 6.378 kişi ve 15.301 farklı yazılı ad içermektedir; bu adların 815'i birden fazla kişiyi temsil etmektedir. Tekrar çalışmasında altı Ifta kitabının ravi kimliği içeren hadisleri kullanılmıştır: 34.681 hadis, 205.514 geçiş ve 6.891 kişi. İki etiket kümesi farklı kaynaklardan gelmektedir [@internal-data-manifest]. Zincirde bir geçişten önce adı verilen ravi onun *öğrencisi*, sonra adı verilen ravi ise *hocası* olarak adlandırılmaktadır.

**Kararın kapsamı.** Defter, her yanıtı tam bağlamıyla (öğrenci, ad, hoca) saklamaktadır. Kararın kapsamı, yanıtın yeniden kullanılabilmesi için sonraki bir geçişin bu bağlamın hangi kısmını paylaşması gerektiğini belirtmektedir. Yalnız ad kapsamı, en fazla yeniden kullanımı ve en fazla hatayı vermektedir. Tablo 8.1'de iki sabit kapsam ve üç daraltma biçimi sunulmaktadır.

Daraltma politikalarında kapsam önceden seçilmemektedir. Her ad yalnız ad kapsamıyla başlamakta, ancak o ad için bir çelişki görüldükten sonra öğrencisine bağlanmaktadır. Çelişki algılayıcısı, ravi kataloğu üzerinde çalışan deterministik bir kuraldır: defterin önerdiği kişiyle komşu ravi arasındaki tabaka farkı beşten büyük ya da eksi birden küçükse veya vefat yılları arasındaki fark 85 yıldan büyük ya da eksi 20'den küçükse inceleyiciye sorulmaktadır. Sınırlar AR-Sanad zincirlerinde seçilmiş ve bu zincirlerde etiketli komşu çiftlerin %0,8'i işaretlenmiştir. Aynı sınırlar Ifta verilerine değiştirilmeden uygulanmış ve burada çiftlerin %3,4'ü işaretlenmiştir.

**Tablo 8.1** İki etiket kümesinde beş politika için geçiş başına soru ve sessiz hata (beş rastgele sıra üzerinden ortalamalar). "Sonradan bilme", belirsiz olduğu bilinen adları dar kapsamda başlatmaktadır; etiketleri önceden gerektirmekte ve bir üst sınır oluşturmaktadır.

| Politika | AR-Sanad: sorular | AR-Sanad: sessiz hatalar | Ifta: sorular | Ifta: sessiz hatalar |
|---|---|---|---|---|
| Sabit kapsam: ad | 0,101 | 0,100 | 0,077 | 0,102 |
| Sabit kapsam: ad; kural yalnız işaretlenen geçişi sorar | 0,204 | 0,054 | 0,229 | 0,049 |
| Kuralla daralan kapsam | 0,178 | 0,014 | 0,199 | 0,010 |
| Sabit kapsam: öğrenci ve ad | 0,340 | 0,006 | 0,292 | 0,007 |
| Sonradan bilme | 0,187 | 0,006 | 0,157 | 0,007 |

Yalnız adla anahtarlanan kararın her on geçişten birinde yanlış yeniden kullanıldığı gözlemlenmiştir. Öğrenci ve adla anahtarlama, bu hataların neredeyse tamamını kaldırmış; ancak yaklaşık üç katı soru gerektirmiştir. Kapsamın yalnız kuralın çelişki gördüğü yerlerde daraltılmasıyla dar anahtarın hatasına yaklaşılmıştır (AR-Sanad'da 0,006'ya karşı 0,014, Ifta'da 0,007'ye karşı 0,010); soru sayısı ise dar anahtardaki sayının yaklaşık yarısı ile üçte ikisi arasında kalmıştır.

Aynı kural iki biçimde kullanılmıştır. Yalnız işaretlenen geçiş inceleyiciye gönderildiğinde hata 0,05 yakınında kalmıştır. İşaretlemenin aynı zamanda o adın kapsamını daralttığı durumda ise bir çelişki adın sonraki bütün geçişlerini korumuş ve hata 0,014 ile 0,010'a düşmüştür.

**Defterin görmediği bir kitap.** Defter, altı Ifta kitabının beşinden doldurulmuş ve altıncısında sayım yapılmıştır; bu işlem her kitap için sırayla tekrarlanmıştır. Kuralla daralan kapsamda geçiş başına sessiz hata 0,004 ile 0,016, soru sayısı ise 0,138 ile 0,249 arasında bulunmuştur. Öğrenci ve adın sabit kapsamında hata 0,007 ile 0,023, soru sayısı 0,151 ile 0,307 arasında bulunmuş; daraltma politikası her kitapta daha az soru gerektirmiştir. Yalnız ad kapsamında hata 0,091 ile 0,151 arasında bulunmuştur: başka bir kitaptan taşınan yanıt, aynı adı taşıyan başka bir kişiye ait olabilmektedir.

**Hata yapan bir inceleyici.** Benzetimdeki inceleyicinin belirsiz adların %5'i için yanlış yanıt verdiği durumda (AR-Sanad), daraltma politikasında geçiş başına 0,219 soru ve 0,018 sessiz hata; öğrenci ve adın sabit kapsamında ise 0,340 ve 0,019 elde edilmiştir. Yanlış yanıtlar sahte çelişkiler ve dolayısıyla daha fazla soru üretmiş; politikaların sıralaması değişmemiştir.

**Karar, yeniden çıkarımdan sonra da kullanılabilir mi?** Saklanan bir karar, ancak metinden ikinci kez çıkarım yapıldığında yeniden bulunabiliyorsa yararlıdır. Motor, kararı bir adaya bağlamaktadır. Bu kapsamda Bölüm 7'deki dört koşunun ravi adayları karşılaştırılmış; hedef hadis ve normalize ad çifti olduğunda bir koşunun adaylarının ne kadarının başka bir koşuda karşılığı olduğu incelenmiştir (`evaluation/decision_reapplication.py`). Aynı modelin iki istemi arasında bu pay, altı yönde 0,857 ile 0,977 arasında bulunmuştur. Ayrıştırıcının metin aralıkları uzun kaldığı için kural tabanlı ayrıştırıcı ile bir model koşusu arasında ise 0,561 ile 0,634 arasında bulunmuştur. Karar aday kimliğine bağlandığında pay, yapı gereği sıfırdır. Hiçbir karar verilmediğinden bu ölçüm, kararların değil hedeflerin örtüşmesini ölçmektedir.

## 8.2 İkinci bir alan: kod ajanı için neyin saklanması gerekir

İkinci çalışma hadis alanının dışında yürütülmüştür. Bu çalışmada, türetilebilir olgular ile kararlar arasındaki ayrımın başka bir okuyucu ve başka tür bir kaynak için de geçerli olup olmadığı, bir kod tabanı hakkındaki soruları yanıtlayan kod ajanı üzerinden incelenmiştir. Kod tabanı, motorun kendi arka ucudur (141 dosya, 16.923 satır); tasarım, sorular ve koşular deneyle birlikte belgelenmiştir [@internal-agent-experiment].

**Düzenek.** Düşük çaba ayarında Claude Haiku 5.5 ajanı kullanılmış ve ajana salt okunur üç araç sağlanmıştır: dizin listeleme, dosya okuma ve arama. Ajana üç sınıfın her birinde on iki olmak üzere 36 soru yöneltilmiştir. *Değişmeyen* sorular, 5 Nisan 2026 kodunda ve güncel kodda aynı olan yapısal bir olguya ilişkindir. *Değişen* sorular, Ekim'deki yeniden yazımın değiştirdiği yapısal bir olguya ilişkindir. *Karar* sorularında ise bir şeyin neden o biçimde olduğu sorulmaktadır; yanıtlar kodda değil, projenin karar kayıtlarında bulunmaktadır. Sorular ve cevap anahtarı, sınanan belgeleri görmeyen ayrı bir ajan tarafından hazırlanmıştır; yapısal sorular için kod, karar soruları için projenin karar kayıtları kullanılmıştır.

Koşullar yalnız bir `docs/` klasörünün içeriği bakımından farklılaşmaktadır: hiçbir şey; her biri gerekçesini ve reddedilen alternatifi içeren, türetilebilir hiçbir olgu içermeyen 30 kararlık bir defter; defterle birlikte güncel koddan yazılmış, kodu açıklayan bir sayfa (taze sayfa); defterle birlikte aynı talimatlarla 5 Nisan kodundan yazılmış bir sayfa (bayat sayfa). Bir düzende ajanın `docs/` klasörünü kendisinin açması gerekmekte, diğerinde belgeler isteme de yerleştirilmektedir. Araç çağrısı hakkı 14, 4 ya da 2'dir. Her hücre iki kez çalıştırılmıştır. Yanıtlar, koşulu görmeyen aynı model tarafından yazılı anahtara göre puanlanmıştır. Analiz birimi sorudur; aralıklar sorular üzerinden bootstrap aralıklarıdır. Temel tasarımda 2.880 koşu yer almaktadır; aşağıda açıklanan sonraki deney kollarıyla birlikte deney 5.520 koşu içermektedir.

**Tablo 8.2** 14 araç çağrısı hakkıyla doğru yanıtların payı (24 yapısal soru ve 12 karar sorusu, her biri için iki koşu).

| `docs/` içeriği | Yapısal, ajan `docs/` klasörünü açar | Yapısal, belgeler istemde | Karar, ajan `docs/` klasörünü açar | Karar, belgeler istemde |
|---|---|---|---|---|
| Hiçbir şey | 0,979 | 0,938 | 0,042 | 0,000 |
| Karar defteri | 0,938 | 0,979 | 1,000 | 0,958 |
| Defter ve taze sayfa | 0,979 | 0,958 | 1,000 | 0,917 |
| Defter ve bayat sayfa | 0,896 | 1,000 | 0,875 | 0,958 |

Yeterli araç çağrısı sağlandığında ajan yapıyı koddan okumuştur. Belge olmadan yapısal soruların %94 ile %98'i yanıtlanmış ve hiçbir belge türü bu sonucu değiştirmemiştir. `docs/` klasörünü ajanın kendisinin açması gereken 432 yapısal koşuda klasör bir kez bile açılmamıştır. Belgelerin isteme yerleştirilmesiyle yapısal soru başına istem belirteçleri 21.843'ten 45.343 ile 75.443 arasına çıkmıştır. Karar sorularında ise ters bir durum gözlemlenmiştir: defter olmadan bu soruların neredeyse hiçbiri yanıtlanamamış, defterle neredeyse tamamı yanıtlanmıştır.

**Tablo 8.3** Belgeler istemdeyken ve araç çağrısı hakkı azken yapısal sorular.

| `docs/` içeriği | 2 çağrı: tamamı | 2 çağrı: değişmeyen | 2 çağrı: değişen | 4 çağrı: tamamı |
|---|---|---|---|---|
| Hiçbir şey | 0,312 | 0,375 | 0,250 | 0,750 |
| Taze sayfa | 0,875 | 0,792 | 0,958 | 0,979 |
| Bayat sayfa | 0,688 | 0,875 | 0,500 | 0,812 |

Kodun saklanan açıklaması, yalnız kodu okumanın pahalı olduğu durumda yarar sağlamaktadır. Taze sayfayla, belgesiz koşula göre doğru yanıt payı iki araç çağrısında 0,56 (aralık 0,38 ile 0,75 arasında), dört çağrıda 0,23 (0,10 ile 0,38 arasında) artmış; on dört çağrıda ise artmamıştır. Değişen olgularda bayat sayfanın doğru olduğu durumların sıklığı, taze sayfanın yaklaşık yarısı düzeyinde kalmıştır.

Saklanan açıklamayı yeniden yazmadan geçerli tutmak için üç yol denenmiştir: her bölümün altına, yazıldığı kodun değişip değişmediğini belirten makine üretimi bir not eklenmesi; olguları saklanan seçiciler aracılığıyla güncel koddan doldurulan cümleler kullanılması; sayfanın yazılmasından sonra eklenen sembollerin listelenmesi. Bu yolların hiçbiri, güncel koddan yeniden yazılmış sayfanın sonucuna yaklaşmamıştır. İki çağrıda değişen olgular için doldurulan cümlelerle 0,625, bayat sayfayla 0,500, taze sayfayla 0,958 elde edilmiştir.

Bir ifadenin konumu, ajana ulaşıp ulaşmadığını belirlemektedir. Taze sayfanın tek satırlık notlara bölünüp kaynak ağacına yerleştirilmesi, yalnız arama aracının eşleşen notları koddan önce döndürdüğü durumda yardımcı olmuştur: iki çağrıda yapısal sorulardaki kazanım, Claude Haiku 5.5 ve Claude Sonnet 5.5 modellerinde 0,15 ile 0,31 arasında bulunmuştur; dosyalar karıştırılmış sırada arandığında ise 0,04 elde edilmiştir (aralık −0,15 ile 0,23 arasında). Bu kazanımların en küçüğünün aralığı sıfıra ulaşmaktadır. Sonnet koşularında notsuz deney kolunda, 48 koşunun 5'inde boş yanıt döndürülmüştür. Bu oran, güvenilir karşılaştırmanın sınırı olarak önceden belirlenen %10'un üzerinde olduğundan söz konusu iki kazanım bu çekinceyle raporlanmaktadır.

## 8.3 İki çalışmanın ekledikleri ve göstermedikleri

İki çalışma, iddianın ilk yarısı bakımından Bölüm 2.6 ile uyumludur. Ajan tarafından bir karar koddan elde edilememiş; ravinin kimliği de yazılı addan elde edilememiştir. Her iki durumda da yanıtın bir kez bir kişiden gelmesi ve saklanması gerekmektedir.

İki çalışma, iddianın ikinci yarısını ise sınırlandırmaktadır. Türetilebilir bir olgunun kullanım anında türetilmesi ucuzsa saklanması gerekmemekte; ucuz değilse saklanan kopya yarar sağlamaktadır. Ajan için iki araç çağrısında ve çıkarımın bir model çağrısı ile inceleme gerektirdiği her yerde bu durum geçerlidir. Yeniden üretilmeyen saklanmış kopya, tam da değişen olgularda yanıltmaktadır.

İki çalışma ayrıca bir değişken daha eklemektedir. Saklanan kararın bir kapsamı bulunmaktadır; ancak kapsamın saklanması gerekmemiş, algılayıcı olarak deterministik bir alan kuralı kullanılarak çelişkilerden türetilmiştir. Mekanizmanın yeni olduğu iddia edilmemektedir. Bir düzeltmenin önceki yanıtın başarısız olduğu bağlama bağlanması, bilgi ediniminde ripple-down rules adıyla bilinmektedir; kaynağın tamamı okunmadan bibliyografik kaydından atıf yapılmaktadır [@compton1990philosophical].

Çalışmaların sınırları, benzetimlerin sınırlarıdır. Defter çalışmasında inceleyici veri kümesinin etiketidir; dolayısıyla ilk yanıt ücretsizdir ve %5 varyantı dışında daima doğrudur. Bir soru, kişiden ne kadar zaman isteyeceğine bakılmadan bir birim sayılmaktadır. AR-Sanad kişi etiketlerinin nasıl atandığı belgelenmemiştir; altı kitap ravilerinin çoğunu paylaştığı için uzak bir kitap sınanmamıştır. Ajan çalışmasında 17 bin satırlık bir kod tabanı, sınıf başına on iki soru ve hücre başına iki koşu bulunmaktadır; puanlayıcı ajanla aynı modeldir ve sayfalar kişiler yerine ajanlar tarafından yazılmıştır. Ayrıca ikinci model yalnız iki karşılaştırmada çalıştırılmıştır ve aynı model ailesindendir. Her iki çalışma da motoru ölçmemekte ve Bölüm 10.1'de planlanan inceleyici deneyinin yerini tutmamaktadır.