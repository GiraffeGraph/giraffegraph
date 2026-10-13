# 1 Giriş

## 1.1 Problem

Metinden kurulan bir bilgi grafı, ancak içerdiği her olguya güvenilebiliyorsa ve her olgu izlenebiliyorsa yararlıdır. Büyük dil modelleri (BDM) çıkarımı ucuzlatır: bir metin parçası ve bir şema verildiğinde model, saniyeler içinde düğüm ve ilişkiler döndürür. Aynı modeller, sonradan fark edilmesi zor iki tür hata yapar. Metin parçasının desteklemediği olgular döndürür ve kimsenin tanımlamadığı bir tip ya da özellik kullanarak şemadan sapar. Böyle bir çıktı grafa yazıldığında doğru çıktıdan ayırt edilemez.

Yaygın çözüm, modelden bir alıntı ve güven skoru istemektir. Alıntı, olgunun nereden geldiğini gösterir; skor ise hangi olguların kontrol edileceğine işaret eder. Biz de aynı düşünceden yola çıktık. Kendi kodumuzda, bir pilot çalışmada ve bu raporun deneylerinde, denediğimiz modellerle ikisinin de varsayıldığı gibi çalışmadığını gördük. Model, kaynağı doğru alıntılıyor, sonra alıntıda olmayan bir değer yazıyordu. Referansla eşleşen ve eşleşmeyen çıktılara verdiği güven skoru neredeyse aynıydı.

## 1.2 Vaka çalışması

Problemi, hadisin başında yer alan ravi zinciri, yani isnad üzerinde inceliyoruz: "A bize anlattı, o B'den, o C'den". Bu görev, sorumuza üç nedenle uygundur. Zincir, doğası gereği bir graftır. Hatalar sonucu etkiler; çünkü âlimler hadisi zincirindeki kişilere göre değerlendirir ve tek bir yanlış ad hükmü değiştirir. Son olarak, etiketli veri vardır; dolayısıyla çıktıyı gözle incelemek yerine puanlayabiliriz.

Bu görev çözümsüz değildir. Büyük etiketli eğitim kümeleri bulunduğunda ince ayar yapılmış modeller ravileri ve aralarındaki bağlantıları doğru biçimde çıkarır [@oumer2025relation]. Altı temel hadis kitabının ontolojisi ve bilgi grafı yayımlanmıştır [@kamran2023semantichadith; @kamran2026semantic]; ravi adları da biyografik veritabanlarına bağlanmıştır [@wirahman2026linking]. Bölüm 3'te bu çalışmaları inceliyoruz. Bulamadığımız şey, genel amaçlı bir model ile graf arasındaki adımı inceleyen bir çalışmadır: bu adımda hangi kontroller yer almalı, her biri neyi yakalar ve bir olgunun kabulü nasıl kaydedilir?

## 1.3 Amaç ve yaklaşım

Amacımız, dil modelinin graf olguları önerdiği, deterministik kontrollerin ve insan incelemesinin hangilerinin kabul edileceğini belirlediği, kabul edilen her olgunun da kaynak alıntısını ve nasıl kabul edildiğine ilişkin kaydı koruduğu bir motordur. İkinci amacımız, kontrollerin katkısını ölçmektir.

Her iki amacın arkasında, Bölüm 2.6'da bütünüyle ifade ettiğimiz tek bir iddia vardır. Ayrıştırıcının ya da modelin metinden çıkardığı bir olgu yeniden çıkarılabilir; bu yüzden saklanması gerekmez. Bir insanın kabulü, reddi ya da düzeltmesi ise hiçbir şeyden türetilemez ve bir kez saklanmalıdır. Motoru bu ayrım üzerine kurduk. Üçüncü amacımız da bu ayrımı motorun kendi görevinde ve başka bir alanda sınamaktır.

GiraffeGraph Core motoru, modeli güvenilmeyen bir öneri üreticisi olarak ele alır. Bir kontrolden geçemeyen aday sessizce reddedilmez; gerekçe koduyla inceleme kuyruğuna gider. İnceleyicinin kararı, inceleyicinin adı, zaman ve süreyle birlikte saklanır; sonraki işlemler bu kararı geçersiz kılamaz. İnsan müdahalesi olmadan kabul edilen adaylar, adı kayıtlı bir politika tarafından kabul edilmiş olarak kaydedilir. Hadise özgü davranışlar eklentilerle eklenir: bir bölütleme stratejisi, bir şema şablonu ve bir kural tabanlı sağlayıcı.

## 1.4 Katkılar

1. **Çalışan bir motor.** Motor, kaynağa dayandırılmış adaylar, adayı incelemeye yönlendiren on gerekçe kodu ve tanımsız tip ve özellikleri kaydeden iki gerekçe kodu içerir. Aynı iki ravi arasındaki ayrı aktarımları ayrı tutan ilişki kimliği, yalnızca yeni kayıt eklenen bir karar kaydı, zincir görünümü ve gerçek PostgreSQL ve Neo4j örnekleri üzerinde de çalışan bir test paketi vardır (Bölüm 5 ve 6).
2. **Motor içindeki kontrollerin ölçümü.** Daha önce görülmemiş 300 hadiste, değer-alıntıda kontrolü, yalnız şema verilen modelin referansla eşleşmeyen 145 önerisinin 122'sini, henüz hiçbiri kabul edilmeden işaretler. Alıntı-kaynakta kontrolü ise hiçbirini işaretlemez (Bölüm 7).
3. **Çıkarım koşullarının tek bir boru hattında karşılaştırılması.** Kurallar, yalnız şema verilen model, tip açıklamaları ve alan ipuçları eklenen model ve girdisi zincir metin aralığıyla sınırlandırılan aynı model, eşli bootstrap aralıklarıyla karşılaştırılır. Yalnız şema içeren isteme açıklama ve ipucu eklemek F1'i 0,066 artırır; girdiyi zincir metin aralığıyla sınırlandırmak yarar sağlamaz.
4. **Bir değerlendirme kiti ve veri kümeleri.** Sabit eşleştirme protokolü kullanan bir puanlayıcı, kontrollerin, güven skorunun ve maliyetin analizi, mevcut etiketli bir derlemden oluşturulmuş ve kökeni belirtilmiş 300 hadislik test kümesi ve gelecekte hazırlanacak insan etiketli küme için kılavuz içeren bir etiketleme formu sunuyoruz.
5. **Ravi kimliği için bir taban çizgisi.** Bu taban çizgisi, referans etiketlerinde yazılı bir adın ne sıklıkla birden çok kişiyi temsil ettiğini sayısallaştırır.
6. **İki etiketli derlem üzerinde ravi kimliği karar defteri benzetimi.** Anahtarı yalnızca ad olan bir karar, her on geçişten birinde yanlış yeniden kullanılır. Kararın kapsamını deterministik bir kuralın saptadığı çelişkilerden türetmek, sabit ve dar bir anahtarın hata düzeyine, onun gerektirdiği inceleyici sorularının yaklaşık yarısı ile üçte ikisi arasında kalan bir soru sayısıyla yaklaşır. Bu sonuç, defterin görmediği kitaplarda da elde edilir (Bölüm 8.1).
7. **İkinci bir alanda deney.** Bu deneyde bir kod ajanı, motorun kaynak kodu hakkındaki soruları yanıtlar. Kararlara ilişkin soruları yalnız koddan neredeyse hiç yanıtlayamazken karar defteriyle neredeyse her zaman yanıtlar. Kodu okuyabilecek kadar kaynak ayırabildiğinde, kodun saklanmış bir açıklamasına ihtiyaç duymaz (Bölüm 8.2).

## 1.5 Kapsam ve sınırlar

Rapor bir prototipi anlatır. Ravi kimlik çözümleme, biyografik tarihler gerektiren kurallar, graf üzerinden soru yanıtlama ve kimlik doğrulama motorun kapsamı dışındadır (Bölüm 4). Kimlik kararları ve tarih kuralı yalnızca Bölüm 8.1'deki benzetimde yer alır. Referans etiketleri mevcut derlemlerden gelir; bağımsız etiketleyicilerin ürettiği bir altın standart değildir. Değerlendirme koşularını hiçbir insan incelememiştir; dolayısıyla döngünün insan tarafı uygulanmış ve test edilmiş, ancak ölçülmemiştir. Motorun değerlendirme sonuçları, bellekte çalışan arka uç üzerinde tek bir modelden elde edilmiştir. İki destekleyici çalışma keşif niteliğindedir: biri inceleyiciyi etiketlerden benzetir, diğeri okuyucu olarak bir model kullanır. Bölüm 7'de ölçülmeyenleri listeliyor, Bölüm 9'da sonuçlara ne ölçüde güvenilebileceğini tartışıyoruz.

## 1.6 Yapı

Bölüm 2'de hadis zincirlerine ve dil modelleriyle çıkarıma ilişkin arka planı veriyoruz. Bölüm 3'te ilgili çalışmaları inceliyoruz. Bölüm 4, gereksinimleri ve kapsamı belirler. Bölüm 5 ve 6, tasarımı ve gerçekleştirimini anlatır. Bölüm 7, motorun değerlendirmesini raporlar. Bölüm 8'de nelerin saklanması gerektiğine ilişkin iki destekleyici çalışmayı sunuyoruz. Bölüm 9'da sonuçları tartışıyor, Bölüm 10'da ikinci dönem planıyla raporu tamamlıyoruz.
