# Büyük Dil Modellerinde Halüsinasyon ve Şema Sapmasını Önleyen İnsan-Döngülü Bilgi Grafı Üretim Motoru: Hadis İsnad Zincirleri Üzerine Bir Uygulama

**Bitirme Projesi Raporu**

Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya

Danışman: Dr. Taha Yiğit Alkan

Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü

CSE 491 Bitirme Projesi I, Güz 2026–2027

13 Ekim 2026 taslağı

# Özet

Büyük dil modelleri (BDM) metni bilgi grafı olgularına dönüştürebilir; ancak kaynakta olmayan olgular ekler ve kendilerine verilen şemadan sapar. Bu raporda, modelin yalnızca öneride bulunduğu GiraffeGraph Core motorunu sunuyoruz. Önerilen her olgu kaynaktan bir alıntı taşır. Deterministik kontroller, bir insanın olguyu incelemesi gerekip gerekmediğini belirler. Olgu, ancak bir inceleyicinin kararı ya da adı kayıtlı bir otomatik politika aracılığıyla kabulü kaydedildiğinde grafa girer. Vaka çalışmamız, hadisin başında yer alan ravi zinciri, yani isnaddır. Tasarım tek bir iddiaya dayanır: bir dil modeliyle kurulan bilgi katmanının saklaması gereken şey insanın verdiği karardır; kaynaktan türetilebilen her şey yeniden türetilir.

Motoru, altı temel hadis kitabından 300 hadis üzerinde değerlendirdik. Mevcut bir platform kaynaklı derlemin ravi etiketlerini referans olarak kullandık; eşleştirme protokolünü sabit tuttuk ve hadis düzeyinde bootstrap aralıkları hesapladık. Gevşek eşleştirmede kural tabanlı ayrıştırıcı F1 0,923'e, yalnız şema verilen model 0,890'a, tip açıklamaları ve alan ipuçları eklenen aynı model ise 0,956'ya ulaştı. Katı eşleştirmede her iki model koşulu da ayrıştırıcının üzerindeydi. Çıkarılan adın modelin kendi alıntısında geçip geçmediğine bakan kontrol, yalnız şema verilen modelin önerilerinin %9'unu işaretledi. İşaretlenen önerilerin %79'u referansla eşleşmiyordu ve bunlar modelin etiketle eşleşmeyen tüm önerilerinin %84'ünü oluşturuyordu. Çoğu, modelin çevriyazıya çevirdiği, başka bir ad hâlinde yazdığı ya da bir akrabalık ifadesinden çıkarsadığı adlardı. İncelemesiz kabul edilen adaylarda precision 0,914'ten 0,985'e çıktı. Alıntının kaynakta geçip geçmediğine bakan kontrol hiçbirini bulamadı; çünkü model doğru alıntı yapıp adı değiştiriyordu. Modelin bildirdiği güven skoru, etiketle eşleşen ve eşleşmeyen önerileri zayıf ayırdı (AUC 0,634). Raviyi yazılı adıyla tanımlamak, her on zincir konumundan birini birden çok kişinin paylaştığı bir ad altında topladı.

İki destekleyici çalışmada iddianın saklamayla ilgili tarafını sınadık. Etiketli 27.056 zincir üzerinde yapılan bir benzetimde, anahtarı yalnızca yazılı ad olan kimlik kararı her on geçişten birinde yanlış yeniden kullanıldı. Kararın kapsamını deterministik bir kuralın saptadığı çelişkilerden türetmek, sabit ve dar bir anahtarın gerektirdiği inceleyici sorularının yaklaşık yarısıyla sessiz hatayı geçiş başına 0,014'e indirdi. Sonuç, ikinci bir etiket kümesinde ve dışarıda bırakılan kitaplarda tekrarlandı. İkinci bir alanda, kod ajanı motorun kodunun neden o şekilde yazıldığına ilişkin soruları yalnız koddan %0 ile %4 arasında, karar defteriyle %88 ile %100 arasında doğru yanıtladı. Yeterli araç çağrısı hakkı olduğunda ise yapısal olguları hiçbir belge olmadan koddan okuyabildi.

Referans etiketleri insan altın standardı değildir; koşuları hiçbir insan incelememiştir. Motorun değerlendirmesinde kullanılabilir sonuç üreten tek bir model vardır. Defter çalışmasındaki inceleyici etiketlerden benzetilmiştir ve deneyler motorun bellekte çalışan arka ucunda yürütülmüştür. Yazılımda 285 otomatik arka uç testi vardır; bunların on ikisi boru hattını PostgreSQL ve Neo4j üzerinde sınar. Yazılım ayrıca, bir zincirin her bağlantısına ait kaynak alıntısı ve kabul kaydıyla birlikte okunabildiği bir panel içerir.

**Anahtar kelimeler:** bilgi grafı, büyük dil modelleri, insan-döngülü sistem, kaynağa dayandırma, karar kaydı, şema sapması, hadis, isnad
