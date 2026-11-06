# 9 Tartışma

## 9.1 Denetimin yeri

Proje, her olguyu bir kaynak alıntısına bağlamanın kaynağın desteklemediği olguları grafın dışında tuttuğu iddiasıyla başlamıştır. Gerçekleştirilen koşularda modelin metinden sapmasının alıntıda olmadığı gözlemlenmiştir. Denetime ulaşan her alıntı kendi segmentinde bulunmuştur. Farklılaşan unsur, alıntıyla çıkarılan değer arasındaki ilişki olmuştur: model tarafından "babasından" ifadesi alıntılanıp bir ad yazılmış ya da Arapça bir ad alıntılanıp Latin harfleriyle yazılmıştır.

Alıntının kaynakta bulunması denetimi, "model gerçek bir metni mi gösterdi?" sorusunu yanıtlamaktadır. Değerin alıntıda bulunması denetimi ise "modelin yazdığı, gösterdiği metinde var mı?" sorusunu yanıtlamaktadır. Elde edilen verilerde eşleşen önerilerin eşleşmeyenlerden yalnız ikinci soruyla ayrıldığı gözlemlenmiştir. Her iki denetimin de maliyeti bir dizgi karşılaştırmasıdır.

Denetim, inceleyicinin kabul edeceği değerleri de işaretlemektedir. İşaretlenen 155 adın 33'ü referansla eşleşmektedir (%21); bunların 13'ü alıntıdan yalnız ad hâli bakımından farklıdır. Motorun işaretlenen adayı reddetmek yerine incelemeye göndermesinin nedeni budur. Hâl eklerini izin verilen değişiklik olarak tanıyan bir kural kullanılması durumunda, bu 13 ad otomatik kabul edilecek ve bu işlem kaydedilecektir; diğer 20 ise kaldırılmayacaktır.

Denetim, uydurulmuş raviyle dönüştürülmüş raviyi ayırt etmemektedir. İşaretlenen adların çoğu başka bir yazı ya da hâlde doğru kişiyi belirtmektedir; akrabalık örneklerinin çoğu da metnin desteklediği çıkarımlardır. Denetimin ortaya koyduğu sonuç daha dar olmakla birlikte yararlıdır: model bir şeyi değiştirmiş ve bunu belirtmemiştir. Olgularının kaynak ifadesine kadar izlenebilmesi gereken bir graf için bu olay bir karar gerektirmektedir.

## 9.2 Modele ne için ihtiyaç var?

Gevşek eşleştirmede, model çağrısı yapmayan kural tabanlı ayrıştırıcıyla F1 0,923'e, yalnız şema verilen modelle 0,890'a, tip açıklamaları ve alan ipuçları eklenen modelle 0,956'ya ulaşılmıştır.

Ayrıştırıcıyla yalnız şema verilen modelin karşılaştırması, eşleştirme kuralına bağlıdır. Ayrıştırıcı adları bulmakla birlikte uzun kalan metin aralıkları döndürmektedir; bu nedenle gevşek eşleştirmede iyi, katı eşleştirmede kötü sonuç vermektedir (0,633). Yalnız şema verilen model temiz adlar döndürdüğü için katı eşleştirmede daha iyi sonuç vermekte (0,826) ve daha fazla zinciri bütünüyle doğru çıkarmaktadır; ancak ad eklemekte ve değiştirmektedir. Hangisinin tercih edileceği, sonraki bir adımda metin aralıklarının kırpılabilmesine ya da adların düzeltilmesinin gerekmesine bağlıdır.

Şema, alan bilgisi değildir. Yalnız şema verilen model tipleri bilmesine karşın Peygamber'i ravi saymış ve adları çevriyazıya çevirmiştir. Şema şablonundaki birkaç açıklama ve talimat cümlesiyle eşleşmeyen önerilerin neredeyse tamamı kaldırılmıştır. Bu görevde talimatların sonucu herhangi bir denetimden daha fazla değiştirdiği gözlemlenmiştir. Şemasız talimatlar sınanmamıştır.

İpuçları verilen modelle, çoğunlukla paralel zincirli hadislerdeki duyarlılık (recall) sayesinde gevşek eşleştirmede ayrıştırıcının 0,034 F1 üzerinde sonuç elde edilmiştir; katı eşleştirmede fark çok daha fazladır. Bunun hadis başına bir model çağrısına değip değmeyeceği kullanıma bağlıdır. Büyük bir derlemde ilk geçiş için ayrıştırıcının maliyeti bulunmamaktadır. Motor, aynı boru hattı üzerinden her iki yaklaşımı da desteklemektedir.

İstem iyi olduğunda denetimler pek az şey bulmaktadır. İstem, model ya da yapılandırmanın iyi olmadığı durumda ise grafı denetimler korumaktadır. İkinci modelle gerçekleştirilen başarısız koşu buna örnektir: çoğu çağrının çıktısı bozuk biçimli olmuş ve bozuk biçimli hiçbir çıktı commit edilmemiştir.

## 9.3 Güven skoru

Bu model ve istemle, modelin güven skorunun yönlendirme için zayıf bir temel olduğu gözlemlenmiştir. İncelemeye gönderilen geçişlerin payı karşılaştırılabilir olduğunda, denetimin bulduğu eşleşmeyen geçişlerin yarısından azı güven skoruyla bulunmuştur (Tablo 7.8). İlk kodda adaylar yalnız güven skoru eşiğine göre incelemeye gönderilmiştir. Güncel kodda ise eşik korunmakta ve denetimler eklenmektedir.

## 9.4 Katı commit kuralının maliyeti

Denetimler değiştirilmiş adları kabul edilen çıktının dışında tutmaktadır; commit kuralı ise adaylarından herhangi biri inceleme beklediği sürece hadisin tamamını grafın dışında tutmaktadır. Yalnız şema verilen koşulda, bir kişi karar verene kadar 300 hadisin 110'u commit edilmeden kalmakta ve grafın duyarlılığı 0,582 olmaktadır. İyi bir istemle bu maliyet neredeyse kaybolmaktadır (300'ün 6'sı). Tasarım, işi inceleyiciye taşımakta; ortadan kaldırmamaktadır. Bu işin ne kadar sürdüğü ölçülmemiştir.

## 9.5 Saklanan kararlar ve türetilen olgular

Motor, iki tür unsuru ayrı tutmaktadır. Adaylar türetilmektedir: aynı metinden yeniden çıkarım yapılabilmektedir ve Bölüm 7'de bu türetimin denetimi ele alınmaktadır. Kararlar ise türetilmemektedir: kabul, düzeltme ya da kimlik metinden elde edilemediği için motor bunları bir kez kaydetmekte ve hiçbir zaman üzerine yazmamaktadır. Bölüm 8'de ikinci tür iki yerde sınanmış ve her iki durumda aynı sonuç elde edilmiştir. Kod ajanı tarafından kodun neden o biçimde olduğu koddan yanıtlanamamış, karar defteriyle yanıtlanabilmiştir. Ravinin kimliği yazılı addan okunamamış, saklanan kimlik kararı yeniden kullanılabilmiştir.

Bu bulgulardan motor için iki sonuç çıkmaktadır. İlk olarak, saklanan kararın bir kapsama ihtiyacı vardır; kapsam geniş başlayıp çelişki ortaya çıktığında daralabilmektedir. Benzetimde, tabaka ve vefat yılları üzerine tek bir deterministik kuralın, yaklaşık yarısı kadar soruyla sessiz hatayı dar anahtarın hatasına yaklaştırmaya yettiği gözlemlenmiştir. Motorda böyle bir kural bulunmamaktadır (biyografik tarihler gerektiren kurallar kapsam dışıdır, Bölüm 4); kararlar da ikinci çıkarımın değiştirdiği adaylara bağlıdır. Bölüm 8.1'deki ölçüm, kararların bunun yerine içeriğe bağlanması durumunda ne kadarının taşınacağını belirtmektedir: bir modelin iki istemi arasında çoğu, ayrıştırıcı ile model arasında üçte ikisinden azı.

İkinci sonuç, iddianın diğer yarısını sınırlandırmaktadır. "Yeniden türet", türetmenin maliyetini karşılayabilen okuyucuya verilen bir öneridir. On dört araç çağrısı olan ajan için kodun açıklaması gerekmemiş; iki çağrı olduğunda ise gerekmiştir. Yeniden üretilmemiş açıklamanın, değişen olgularda ajanı yanılttığı gözlemlenmiştir. Motordaki çıkarım pahalı durumdur; çünkü her türetim bir model çağrısı ve olası bir inceleme gerektirmektedir. Bu nedenle commit edilen graf bir depo olarak tutulmaktadır. İçindeki her olgu, nasıl kabul edildiğine ilişkin kaydı taşımaktadır; böylece bu olguya güvenmek yerine yeni bir çıkarıma karşı kontrol edilmesi mümkün olmaktadır.

## 9.6 Geçerlilik tehditleri

**Referans etiketleri.** Ifta etiketleri, üçüncü bir tarafın yeniden yapılandırdığı platform işaretlemeleridir; gözlemlenen ve düzeltilmeyen tutarsızlıklar içermektedir. Sistem, platformun işaretlemediği bir raviyi çıkardığında bazen cezalandırılmaktadır. Farklı biçimlerde üretilmiş iki etiket kümesi, ortak hadislerinde birbirine yakındır (F1 0,959); bu durum, etiketlerin koşulları karşılaştırmak için yeterli olduğunu düşündürmektedir. İki kümenin ne kadar bağımsız olduğu bilinmemektedir; mutlak değerler doğruluk olarak okunmamalıdır.

**Eşleştirme kuralı.** Gevşek eşleştirme, fazladan sözcük içeren geçişi kabul etmekte ve aynı hâl değişikliğini adın uzunluğuna göre eşleşme ya da eşleşmeme saymaktadır. Bir kuralda geçerli olup diğerinde olmayan sonuçlar, ilgili kurallarla birlikte belirtilmektedir.

**"Yanlış" ne demektir?** Eşleşmeyen öneri, mutlaka hadis hakkında yanlış bir ifade değildir. Yalnız şema verilen modelin eşleşmeyen önerilerinin yarısından fazlasında, doğru ravi başka bir yazıyla adlandırılmaktadır.

**Tek alan.** Değerin alıntıda bulunması denetiminin eşleşmeyen önerilerin çoğunu (145'in 122'sini) işaretlemesi, modelin metinden başlıca sapmasının adı yeniden yazmak olduğu bu görevin ve bu istemin özelliğidir. Denetim hadis dışında, kimyasal madde ve hastalık geçişleri için insan etiketleri içeren BC5CDR derleminin 300 özetinde [@li2016bc5cdr], aynı model ve yalnız şema içeren bir istemle tekrarlanmıştır. Burada denetimle 2.269 önerinin %3,9'u işaretlenmiştir; bunların içinde etiketlerle eşleşmeyen 303 önerinin 53'ü bulunmaktadır. Diğer 250'si, etiketleyicilerin etiketlemediği metin aralıklarının aynen kopyalarıdır. Aynı sayıda öğe incelemeye gönderildiğinde modelin güven skoruyla eşleşmeyen 58 öneri, denetimle ise 53 öneri bulunmuştur. Denetim, değerin alıntılanan metinden geldiğini ortaya koymaktadır; doğru metnin seçildiğini ortaya koymamaktadır.

**Tek model, tek çaba ayarı, tek koşu.** Kullanılabilir bütün sonuçlar düşük çaba ayarındaki Claude Haiku 5.5'ten elde edilmiştir; her koşul bir kez çalıştırılmıştır. İkinci modelin başarısızlığı, çalışmada kullanılan aktarım biçimine ve çaba ayarına bağlanmıştır; bu açıklama sınanmamıştır.

**Bellek içi arka uç.** Deneyler bellek içi arka uçta çalıştırılmıştır. Aynı boru hattı PostgreSQL ve Neo4j üzerinde deneylerle değil, on iki testle kapsanmaktadır.

**Ayarlama.** Kural tabanlı bölütleyici 50 pilot hadis üzerinde ayarlanmıştır. Altı kitap kümesinde bunlar dışarıda bırakıldığı için ana sonuçlar etkilenmemektedir; ancak ayrıştırıcının kuralları, Bukhari'yi içermeyen pilotta görülen kitapları yansıtmaktadır.

**Ezberleme.** Hadisler iyi bilinmektedir ve modelin eğitim verilerinde bulunmaları muhtemeldir. Metnin hiçbir biçimde içermediği işaretlenmiş bir ad bulunmuştur; bu bulgu, modelin zincirleri hatırlayıp hatırlamadığını söylemek için çok azdır. Bu durum değiştirilmiş adlarla sınanmamıştır.

**Ölçülen döngüde insan yok.** İnceleme kuyruğu, karar kaydı ve commit korumaları testlerle kapsanmaktadır; ancak değerlendirme inceleyici olmadan çalıştırılmıştır. Motorun döngüde bir kişiyle hataları azalttığı iddiası burada ölçülmemiştir. Aynı durum Bölüm 8 için de geçerlidir: defter çalışmasının inceleyicisi veri kümesinin etiketi, ikinci çalışmanın okuyucusu ise bir dil modelidir.

**Şema sapması.** Başlık şema sapmasını içermektedir. Haiku 5.5'te neredeyse hiç sapma gözlemlenmemiştir; ikinci modelde gözlemlenen sapma ise başarısız bir yapılandırmadan kaynaklanmıştır. Motorun sapmayı ele alışı test edilmiştir; normal kullanımdaki sıklığı belirlenmiş değildir.

**Kodun ve analizin yazarlığı.** Değerlendirilen daldaki kodun çoğu, analiz betikleri ve bu metnin ilk taslağı, yazarların yönlendirmesiyle yapay zekâ kodlama asistanları kullanılarak üretilmiştir. Ölçümler, önbelleğe alınmış model yanıtlarından ve betiklerden yeniden üretilebilmektedir. Yazarlar her ifadenin sorumluluğunu taşımaktadır.

## 9.7 Sistemin sınırları

Ravi düğümü, yazılı adıyla tanımlanmaktadır. Bölüm 7.10'da, bunun yol açtığı hatanın referans etiketlerindeki büyüklüğü gösterilmektedir: bu biçimde anahtarlanan graf, kısa bir adı paylaşan farklı kişileri birleştirmekte ve bir kişiyi farklı yazımlara bölmektedir. Güncel graf üzerine kurulan her ravi ağı analizi bu hatayı devralmaktadır. Bölüm 8.1'deki defter, etiketleri yeniden oynatan bir değerlendirme modülüdür; motorun parçası değildir.

Rivayet metni başladıktan sonra başlayan zincirler bölütlenmemekte; birlikte anılan ortak raviler tek geçişte kalmaktadır. Her iki durum da bölütleyiciyi kullanan koşulların duyarlılığını düşürmektedir.

Hiçbir denetim, Peygamber'in ravi olarak adlandırılması gibi kategori hatalarını kapsamamaktadır. Denetimler, elle girilen adaylara değil, çıkarım çağrısından gelen adaylara uygulanmaktadır. Kabul kayıtları, istendiğinde saklanan kararlardan ve doğrulama sonuçlarından hesaplanmaktadır. Commit edilen koşuyu geri alma gerçekleştirilmemiştir.
