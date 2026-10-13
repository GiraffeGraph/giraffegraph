# 10 Sonuç ve gelecek çalışma

Bir dil modeliyle bilgi grafı arasına deterministik kontroller ve kayıtlı bir kabul yerleştiren bir motor kurduk; bu yerleşimin hadis ravi zincirlerinde ne sağladığını, tek model ve platform kaynaklı etiketlerle ölçtük. Motor, böyle bir sistemin saklaması gereken şeyin bir kişinin kararı olduğu ve kaynaktan türetilebilenin yeniden türetildiği iddiasına dayanır. İki destek çalışmasıyla bu iddiayı sınadık.

Ölçümler, bu sınırlar içinde dört ifadeyi destekler. Modelin alıntısıyla çıkardığı değer arasındaki ilişkiyi kontrol etmek, talimatları zayıf verilmiş bir modelin referansla eşleşmeyen önerilerinin çoğunu ek model çağrısı olmadan işaretler; yalnız alıntıyı kontrol etmek ise hiçbirini işaretlemez. Yalnız şema içeren isteme açıklamalar ve alan talimatları eklemek, çıkarımı herhangi bir kontrolden daha fazla iyileştirir. Karşılaştırılabilir bir inceleme hakkıyla modelin güven skoru, bu önerilerin kontrolden çok daha azını bulur. Yazılı ad da ravinin kimliği değildir: her on zincir konumundan biri dizgi düzeyinde belirsizdir.

Destek çalışmaları, ikisi de benzetimlerden gelen iki ifade ekler. Kimlik kararı saklamaya değerdir ve kapsamı sonucu etkiler: yalnız adla anahtarlandığında her on geçişten birinde yanlış yeniden kullanılır. Deterministik kuralın çelişki gördüğünde daralttığı kapsam ise iki etiket kümesinde ve dışarıda bırakılan kitaplarda, yaklaşık yarısı ile üçte ikisi kadar soruyla dar anahtarın hatasına yaklaşır. İkinci bir alanda da okuyucu, kaynaktan kararları elde edememiş ama yapıyı elde edebilmiştir; bu yüzden kaynağın saklanan açıklaması, yalnız kaynağı okumak pahalı olduğunda yarar sağlamıştır.

Ölçümler, motorun ya da defterin bir inceleyiciyle nasıl sonuç verdiğini, diğer modellerle sonuçların nasıl değiştiğini, şema sapmasının ne sıklıkta oluştuğunu veya bağımsız insan etiketleyicilerin ürettiği etiketlere karşı çıktının ne kadar doğru olduğunu göstermez.

## 10.1 Bitirme Projesi II planı

1. **İnsan etiketli referans.** İki etiketleyici, mevcut form ve kılavuzla 50 pilot hadisi etiketler. Uyumu ve hadis başına süreyi ölçer, kılavuzu düzeltir, sonra altı kitap kümesinden bir örneklemi etiketleriz. Hadis sayısını ölçülen süre belirler.
2. **Döngüde inceleyici.** Hadisi etiketlememiş bir inceleyici, panelde o hadisin inceleme öğeleri hakkında karar verir. İnceleme sonrası precision ve recall'u, gerekçe kodu başına ret oranını ve karar kaydından karar başına saniyeyi raporlarız.
3. **Ravi kimliği.** Geçişleri Ifta verilerinin ravi kataloğuna bağlarız; belirsiz adlarda sıralanmış adayları inceleyiciye sunar, yanlış birleştirmeleri kaçırılan birleştirmelerden ayrı raporlarız. Kararları adaylar yerine içeriğe bağlarız; kimlik kararlarını Bölüm 8.1'deki gibi kapsamı çelişkide daralan bir defterde saklarız. Bu ölçümü, etiketler yerine gerçek bir inceleyicinin kararlarıyla tekrarlarız.
4. **Dönüşüm kuralları ve kategori kuralı.** Ad hâli değişikliklerini otomatik kabul eder ve kabul eden kuralı kaydederiz; böylece değer kontrolünün işaretlediği eşleşen 33 adın 13'ü incelemeden çıkar. Peygamber gibi ravi olmayan adlar için bir kural ekleriz.
5. **Modeller ve aktarım biçimi.** Özellik listesinin alanlarını yeniden adlandırırız; sonra en az biri açık model olmak üzere en az iki modelle daha, tekrarlı koşular yaparak değerlendirmeyi yineleriz. Ezberlemeyi sınamak için değiştirilmiş adlar da kullanırız.
6. **İlişkiler ve zincirler.** `NARRATED_FROM` bağlantılarını ve zincirlerin bütününü puanlarız; rivayet metninden sonra başlayan zincirleri bölütler, birden fazla zincirli hadislerde zincir başına çağrıları sınarız.
7. **Graf üzerinde sorular.** Küçük bir yapısal soru, yol sorusu ve karar sorusu kümesi oluşturur; graftan gelen yanıtları metin getirmeden gelen yanıtlarla karşılaştırırız.

## 10.2 Hadis dışındaki alanlar

Kontroller, inceleme kuyruğu, karar kaydı ve ilişki kimliği her şemada çalışır; hadise özgü davranışların çoğu bir bölütleme stratejisinde, bir şablonda ve bir sağlayıcıda yer alır. Motorun üç yerinde hâlâ vaka çalışmasının adı geçer (Bölüm 5.1). Aynı yapının başka bir alana hizmet ettiği iddiası motor için sınanmamıştır; bunu sınamanın yolu ikinci bir vaka çalışmasıdır. Hadis dışında elde ettiklerimiz kısmidir. Kararlar ile türetilebilir olgular arasındaki ayrım, tek kod tabanında bir kod ajanı için geçerli kaldı (Bölüm 8.2). Değer-alıntıda kontrolü, biyomedikal özetlere aynı biçimde taşınmadı (Bölüm 9.6). Komşularıyla anahtarlanan bir karar da ancak ravi zincirlerinde olduğu gibi bağlamın kendisi tekrarlandığında yeniden kullanılabilir.

Proje geliştirilirken kaynak kod özel bir depoda tutulmaktadır; çünkü aynı depo üçüncü taraflara ait hadis metinleri ve yayımlanmamış taslaklar içerir. Motoru proje sonunda açık kaynak lisansıyla yayımlamayı planlıyoruz.
