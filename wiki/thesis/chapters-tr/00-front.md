# Büyük dil modellerinde halüsinasyon ve şema sapmasını önleyen insan-döngülü bilgi grafı üretim motoru: hadis isnad zincirleri üzerine bir uygulama

**Bitirme Projesi Raporu**

Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya

Danışman: Dr. Taha Yiğit Alkan

Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü

CSE 491 Bitirme Projesi I, Güz 2026–2027

13 Ekim 2026 taslağı

# Özet

Büyük dil modelleri (BDM), metni bilgi grafı olgularına dönüştürebilmektedir; ancak kaynakta bulunmayan olgular eklemekte ve kendilerine verilen şemadan sapmaktadır. Bu raporda, modelin yalnızca öneri ürettiği GiraffeGraph Core motoru sunulmaktadır. Önerilen her olgu, kaynaktan bir alıntı taşımakta; deterministik denetimler ise olgunun insan incelemesi gerektirip gerektirmediğini belirlemektedir. Olgu, ancak bir inceleyicinin kararı ya da adı kayıtlı bir otomatik politika aracılığıyla kabulü kaydedildiğinde grafa girmektedir. Vaka çalışması, hadisin başında yer alan ravi zinciri olan isnaddır. Tasarım, dil modeliyle kurulan bir bilgi katmanında saklanması gerekenin insan kararı olduğu ve kaynaktan türetilebilen her şeyin yeniden türetildiği iddiasına dayanmaktadır.

Motor, altı temel hadis kitabından seçilen 300 hadis üzerinde değerlendirilmiştir. Mevcut bir platform kaynaklı derlemin ravi etiketleri referans olarak kullanılmış, eşleştirme protokolü sabit tutulmuş ve hadis düzeyinde bootstrap aralıkları hesaplanmıştır. Gevşek eşleştirmede kural tabanlı ayrıştırıcı F1 0,923'e, yalnız şema verilen model 0,890'a, tip açıklamaları ve alan ipuçları eklenen aynı model ise 0,956'ya ulaşmıştır. Katı eşleştirmede her iki model koşulunun da ayrıştırıcının üzerinde sonuç verdiği görülmüştür. Çıkarılan adın modelin kendi alıntısında bulunup bulunmadığını sınayan denetim, yalnız şema verilen modelin önerilerinin %9'unu işaretlemiştir. İşaretlenen önerilerin %79'u referansla eşleşmemiş ve bunlar modelin etiketle eşleşmeyen tüm önerilerinin %84'ünü oluşturmuştur. Bu önerilerin çoğunun, modelin çevriyazıya çevirdiği, başka bir ad hâlinde yazdığı ya da bir akrabalık ifadesinden çıkarsadığı adlar olduğu görülmüştür. İncelemesiz kabul edilen adaylarda kesinlik (precision) 0,914'ten 0,985'e yükselmiştir. Alıntının kaynakta bulunup bulunmadığını sınayan denetim hiçbirini belirleyememiştir; çünkü modelin kaynağı doğru alıntıladığı, ancak adı değiştirdiği gözlemlenmiştir. Modelin bildirdiği güven skoru, etiketle eşleşen ve eşleşmeyen öneriler arasında zayıf bir ayrım sağlamıştır (AUC 0,634). Ravinin yazılı adıyla tanımlanması, her on zincir konumundan birinin birden çok kişinin paylaştığı bir ad altında toplanmasına yol açmıştır.

İki destekleyici çalışmada, iddianın saklamayla ilgili yönü sınanmıştır. Etiketli 27.056 zincir üzerinde yapılan benzetimde, anahtarı yalnızca yazılı ad olan kimlik kararı her on geçişten birinde yanlış yeniden kullanılmıştır. Kararın kapsamının deterministik bir kuralın saptadığı çelişkilerden türetilmesi, sabit ve dar bir anahtarın gerektirdiği inceleyici sorularının yaklaşık yarısıyla sessiz hatayı geçiş başına 0,014'e indirmiştir. Bu sonuç, ikinci bir etiket kümesinde ve dışarıda bırakılan kitaplarda da elde edilmiştir. İkinci bir alanda kod ajanı, motorun kodunun neden o şekilde yazıldığına ilişkin soruları yalnız koddan %0 ile %4 arasında, karar defteriyle %88 ile %100 arasında doğru yanıtlamıştır. Yeterli araç çağrısı hakkı bulunduğunda ise yapısal olguları herhangi bir belge olmadan koddan okuyabilmiştir.

Referans etiketleri insan altın standardı değildir; koşular hiçbir insan tarafından incelenmemiştir. Motorun değerlendirmesinde kullanılabilir sonuç üreten tek bir model bulunmaktadır. Defter çalışmasındaki inceleyici etiketlerden benzetilmiş ve deneyler motorun bellekte çalışan arka ucunda yürütülmüştür. Yazılımda 285 otomatik arka uç testi bulunmaktadır; bunların on ikisi boru hattını PostgreSQL ve Neo4j üzerinde sınamaktadır. Ayrıca yazılım, bir zincirin her bağlantısına ait kaynak alıntısı ve kabul kaydıyla birlikte okunabildiği bir panel içermektedir.

**Anahtar kelimeler:** bilgi grafı, büyük dil modelleri, insan-döngülü sistem, kaynağa dayandırma, karar kaydı, şema sapması, hadis, isnad
