# 9 Tartışma

## 9.1 Kontrolün yeri

Proje, her olguyu bir kaynak alıntısına bağlamanın kaynağın desteklemediği olguları grafın dışında tuttuğu iddiasıyla başladı. Koşularımızda modelin metinden saptığı yer alıntı değildi. Kontrole ulaşan her alıntı kendi segmentinde bulundu. Farklılaşan, alıntıyla çıkarılan değer arasındaki ilişkiydi: model "babasından" ifadesini alıntılayıp bir ad yazdı ya da Arapça bir adı alıntılayıp Latin harfleriyle yazdı.

Alıntı kontrolü, "model gerçek bir metni mi gösterdi?" sorusunu yanıtlar. Değer-alıntıda kontrolü ise "modelin yazdığı, gösterdiği metinde var mı?" sorusunu yanıtlar. Verilerimizde eşleşen önerileri eşleşmeyenlerden yalnız ikinci soru ayırdı. İki kontrolün de maliyeti bir dizgi karşılaştırmasıdır.

Kontrol, inceleyicinin kabul edeceği değerleri de işaretler. İşaretlenen 155 adın 33'ü referansla eşleşir (%21); bunların 13'ü alıntıdan yalnız ad hâli bakımından farklıdır. Motorun işaretlenen adayı reddetmek yerine incelemeye göndermesinin nedeni budur. Hâl eklerini izin verilen değişiklik olarak tanıyan bir kural, bu 13 adı otomatik kabul eder ve bunu yaptığını kaydeder; diğer 20'yi kaldırmaz.

Kontrol, uydurulmuş raviyle dönüştürülmüş raviyi ayırt etmez. İşaretlenen adların çoğu başka yazı ya da hâlde doğru kişidir; akrabalık örneklerinin çoğu da metnin desteklediği çıkarımlardır. Kontrolün ortaya koyduğu daha dardır ama yine de yararlıdır: model bir şeyi değiştirmiş ve bunu söylememiştir. Olgularının kaynak ifadesine kadar izlenebilmesi gereken bir graf için karar gerektiren olay budur.

## 9.2 Modele ne için ihtiyaç var?

Gevşek eşleştirmede, model çağrısı yapmayan kural tabanlı ayrıştırıcı F1 0,923'e, yalnız şema verilen model 0,890'a, tip açıklamaları ve alan ipuçları eklenen model 0,956'ya ulaşır.

Ayrıştırıcıyla yalnız şema verilen modelin karşılaştırması, eşleştirme kuralına bağlıdır. Ayrıştırıcı adları bulur ama uzun kalan metin aralıkları döndürür; bu yüzden gevşek eşleştirmede iyi, katı eşleştirmede kötü sonuç verir (0,633). Yalnız şema verilen model temiz adlar döndürdüğü için katı eşleştirmede daha iyidir (0,826) ve daha fazla zinciri bütünüyle doğru çıkarır; ancak ad ekler ve değiştirir. Hangisinin tercih edileceği, sonraki bir adımın metin aralıklarını kırpabilmesine ya da adları düzeltmek zorunda olmasına bağlıdır.

Şema, alan bilgisi değildir. Yalnız şema verilen model tipleri biliyordu ama yine de Peygamber'i ravi saydı ve adları çevriyazıya çevirdi. Şema şablonundaki birkaç açıklama ve talimat cümlesi, eşleşmeyen önerilerin neredeyse tamamını kaldırdı. Bu görevde talimatlar sonucu herhangi bir kontrolden daha fazla değiştirdi. Şemasız talimatları sınamadık.

İpuçları verilen model, çoğunlukla paralel zincirli hadislerdeki recall sayesinde gevşek eşleştirmede ayrıştırıcının 0,034 F1 üzerindedir; katı eşleştirmede fark çok daha fazladır. Bunun hadis başına bir model çağrısına değip değmeyeceği kullanıma bağlıdır. Büyük bir derlemde ilk geçiş için ayrıştırıcının maliyeti yoktur. Motor, aynı boru hattı üzerinden ikisini de destekler.

İstem iyi olduğunda kontroller pek az şey bulur. İstem, model ya da yapılandırma iyi olmadığında grafı koruyan kontrollerdir. İkinci modelle başarısız koşu buna örnektir: çoğu çağrının çıktısı bozuk biçimliydi ve bozuk biçimli hiçbir çıktı commit edilmedi.

## 9.3 Güven skoru

Bu model ve istemle, modelin güven skoru yönlendirme için zayıf bir temeldi. İncelemeye gönderilen geçişlerin payı karşılaştırılabilir olduğunda, kontrolün bulduğu eşleşmeyen geçişlerin yarısından azını buldu (Tablo 7.8). İlk kod, adayları yalnız güven skoru eşiğine göre incelemeye gönderiyordu. Güncel kod, eşiği korur ve kontrolleri ekler.

## 9.4 Katı commit kuralının maliyeti

Kontroller değiştirilmiş adları kabul edilen çıktının dışında tutar; commit kuralı ise adaylarından herhangi biri inceleme beklediği sürece hadisin tamamını grafın dışında tutar. Yalnız şema verilen koşulda, bir kişi karar verene kadar 300 hadisin 110'u commit edilmeden kalır ve grafın recall'u 0,582 olur. İyi bir istemle bu maliyet neredeyse kaybolur (300'ün 6'sı). Tasarım işi inceleyiciye taşır; ortadan kaldırmaz. Bu işin ne kadar sürdüğünü ölçmedik.

## 9.5 Saklanan kararlar ve türetilen olgular

Motor iki tür şeyi ayrı tutar. Adaylar türetilir: aynı metinden yeniden çıkarım yapılabilir ve Bölüm 7 bu türetimin kontrolü hakkındadır. Kararlar türetilmez: kabul, düzeltme ya da kimlik metinden elde edilemez; bu yüzden motor bunları bir kez kaydeder ve hiçbir zaman üzerine yazmaz. Bölüm 8'de ikinci türü iki yerde sınadık; ikisinde de sonuç aynıydı. Kod ajanı, kodun neden o biçimde olduğunu koddan yanıtlayamadı; karar defteriyle yanıtlayabildi. Ravinin kimliği yazılı addan okunamadı; saklanan kimlik kararı yeniden kullanılabildi.

Bundan motor için iki sonuç çıkar. Birincisi, saklanan kararın bir kapsama ihtiyacı vardır; kapsam geniş başlayıp çelişki ortaya çıktığında daralabilir. Benzetimde, tabaka ve vefat yılları üzerine tek bir deterministik kural, yaklaşık yarısı kadar soruyla sessiz hatayı dar anahtarın hatasına yaklaştırmaya yetti. Motorda böyle bir kural yoktur (biyografik tarihler gerektiren kurallar kapsam dışıdır, Bölüm 4); kararlar da ikinci çıkarımın değiştirdiği adaylara bağlıdır. Bölüm 8.1'deki ölçüm, bunun yerine içeriğe bağlansalar ne kadarının taşınacağını söyler: bir modelin iki istemi arasında çoğu, ayrıştırıcı ile model arasında üçte ikisinden azı.

İkincisi, iddianın diğer yarısını sınırlar. "Yeniden türet", türetmenin maliyetini karşılayabilen okuyucuya verilen bir öneridir. On dört araç çağrısı olan ajan, kodun açıklamasına ihtiyaç duymadı; iki çağrısı olduğunda duydu. Yeniden üretilmemiş açıklama, değişen olgularda onu yanılttı. Motordaki çıkarım pahalı durumdur; çünkü her türetim bir model çağrısı ve olası bir inceleme gerektirir. Commit edilen grafın bir depo olarak tutulmasının nedeni budur. İçindeki her olgunun nasıl kabul edildiğine ilişkin kaydı taşımasının nedeni de, ona güvenmek yerine yeni bir çıkarıma karşı kontrol edilebilmesidir.

## 9.6 Geçerlilik tehditleri

**Referans etiketleri.** Ifta etiketleri, üçüncü bir tarafın yeniden yapılandırdığı platform işaretlemeleridir; gözlemlediğimiz ve düzeltmediğimiz tutarsızlıklar içerir. Sistem, platformun işaretlemediği bir raviyi çıkardığında bazen cezalandırılır. Farklı biçimlerde üretilmiş iki etiket kümesi, ortak hadislerinde birbirine yakındır (F1 0,959); bu, etiketlerin koşulları karşılaştırmak için yeterli olduğunu düşündürür. İki kümenin ne kadar bağımsız olduğunu bilmiyoruz; mutlak değerler doğruluk olarak okunmamalıdır.

**Eşleştirme kuralı.** Gevşek eşleştirme fazladan sözcük içeren geçişi kabul eder ve aynı hâl değişikliğini adın uzunluğuna göre eşleşme ya da eşleşmeme sayar. Bir kuralda geçerli olup diğerinde olmayan sonuçları, kurallarıyla birlikte belirtiyoruz.

**"Yanlış" ne demektir?** Eşleşmeyen öneri, mutlaka hadis hakkında yanlış bir ifade değildir. Yalnız şema verilen modelin eşleşmeyen önerilerinin yarısından fazlası, doğru raviyi başka bir yazıyla adlandırır.

**Tek alan.** Değer-alıntıda kontrolünün eşleşmeyen önerilerin çoğunu (145'in 122'sini) işaretlemesi, modelin metinden başlıca sapmasının adı yeniden yazmak olduğu bu görevin ve bu istemin özelliğidir. Kontrolü hadis dışında, kimyasal madde ve hastalık geçişleri için insan etiketleri içeren BC5CDR derleminin 300 özetinde [@li2016bc5cdr], aynı model ve yalnız şema içeren bir istemle tekrarladık. Burada kontrol 2.269 önerinin %3,9'unu işaretledi; bunların içinde etiketlerle eşleşmeyen 303 önerinin 53'ü vardı. Diğer 250'si, etiketleyicilerin etiketlemediği metin aralıklarının aynen kopyalarıydı. Aynı sayıda öğe incelemeye gönderildiğinde modelin güven skoru eşleşmeyen 58 öneri, kontrol ise 53 öneri buldu. Kontrol, değerin alıntılanan metinden geldiğini ortaya koyar. Doğru metnin seçildiğini ortaya koymaz.

**Tek model, tek çaba ayarı, tek koşu.** Kullanılabilir bütün sonuçlar düşük çaba ayarındaki Claude Haiku 5.5'ten gelir; her koşul bir kez çalıştırılmıştır. İkinci model, kendi aktarım biçimimize ve çaba ayarımıza bağladığımız bir nedenle başarısız oldu; bu açıklamayı sınamadık.

**Bellek içi arka uç.** Deneyler bellek içi arka uçta çalıştı. Aynı boru hattı PostgreSQL ve Neo4j üzerinde deneylerle değil, on iki testle kapsanır.

**Ayarlama.** Kural tabanlı bölütleyici 50 pilot hadis üzerinde ayarlandı. Altı kitap kümesi bunları dışarıda bıraktığı için ana sonuçlar etkilenmez; ancak ayrıştırıcının kuralları, Bukhari'yi içermeyen pilotta görülen kitapları yansıtır.

**Ezberleme.** Hadisler iyi bilinir ve modelin eğitim verilerinde bulunmaları muhtemeldir. Metnin hiçbir biçimde içermediği işaretlenmiş bir ad bulduk; bu, modelin zincirleri hatırlayıp hatırlamadığını söylemek için çok azdır. Bunu değiştirilmiş adlarla sınamadık.

**Ölçülen döngüde insan yok.** İnceleme kuyruğu, karar kaydı ve commit korumaları testlerle kapsanır; ancak değerlendirme inceleyici olmadan çalıştı. Motorun döngüde bir kişiyle hataları azalttığı iddiasını burada ölçmedik. Aynısı Bölüm 8 için de geçerlidir: defter çalışmasının inceleyicisi veri kümesinin etiketi, ikinci çalışmanın okuyucusu ise bir dil modelidir.

**Şema sapması.** Başlık şema sapmasını içerir. Haiku 5.5'te neredeyse hiç sapma gözlemlemedik; ikinci modelde gözlemlediğimiz ise başarısız bir yapılandırmadan geldi. Motorun sapmayı ele alışını test ettik; normal kullanımdaki sıklığı belirlenmiş değildir.

**Kodun ve analizin yazarlığı.** Değerlendirilen daldaki kodun çoğu, analiz betikleri ve bu metnin ilk taslağı, yazarların yönlendirmesiyle yapay zekâ kodlama asistanları kullanılarak üretildi. Ölçümler, önbelleğe alınmış model yanıtlarından ve betiklerden yeniden üretilebilir. Yazarlar her ifadenin sorumluluğunu taşır.

## 9.7 Sistemin sınırları

Ravi düğümü, yazılı adıyla tanımlanır. Bölüm 7.10, bunun yol açtığı hatanın referans etiketlerindeki büyüklüğünü gösterir: böyle anahtarlanan graf, kısa bir adı paylaşan farklı kişileri birleştirir ve bir kişiyi farklı yazımlara böler. Güncel graf üzerine kurulan her ravi ağı analizi bunu devralır. Bölüm 8.1'deki defter, etiketleri yeniden oynatan bir değerlendirme modülüdür; motorun parçası değildir.

Rivayet metni başladıktan sonra başlayan zincirler bölütlenmez; birlikte anılan ortak raviler tek geçişte kalır. İkisi de bölütleyiciyi kullanan koşulların recall'unu düşürür.

Hiçbir kontrol, Peygamber'in ravi olarak adlandırılması gibi kategori hatalarını kapsamaz. Kontroller, elle girilen adaylara değil, çıkarım çağrısından gelen adaylara uygulanır. Kabul kayıtları, istendiğinde saklanan kararlardan ve doğrulama sonuçlarından hesaplanır. Commit edilen koşuyu geri alma gerçekleştirilmemiştir.
