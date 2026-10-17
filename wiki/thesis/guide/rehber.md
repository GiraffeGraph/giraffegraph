# GiraffeGraph: ne yapıyoruz, neden ve nerede farklıyız

*CSE 491 ekibi, TÜBİTAK 2209-A başvurusunu hazırlayanlar ve projeyi ilk kez okuyacaklar için, 16 Ekim 2026.*

## 0. Kısa özet

GiraffeGraph ile metinden çıkarılan bilgilerin, insanların başvuracağı bir bilgi grafına hangi koşullarda girebileceğini araştırıyoruz. Bilgi grafı, kişiler gibi varlıkları ve aralarındaki ilişkileri ayrı kayıtlarla tutar. Çalışma alanımız hadislerdeki aktarım zincirleri: model bir metinden ravi adlarını öneriyor, yazılım önerinin biçimini ve dayanağını kontrol ediyor, sorun görülen öneriyi insan incelemesine gönderiyor. Modelin grafı doğrudan değiştirmesine izin vermiyoruz. İlk ölçümümüzde, platform etiketlerine göre uyuşmayan 145 adın 122 tanesini, önerilen adın modelin kendi alıntısında bulunmasını isteyen kontrolle işaretledik. Ancak bu etiketler insan eliyle hazırlanmış bir altın standart değil; hiçbir koşuda insan karar vermedi. Bu nedenle ölçtüğümüz şey uzman doğruluğu veya insan emeğinden sağlanan tasarruf değil. Araştırma iddiamız, kaynaktan yeniden çıkarılabilen öneriyi kontrol etmek, insanın kabul, ret, düzeltme ve kimlik kararını ise kim verdiği ve ne zaman verdiğiyle saklamak. Bu iddia proje sahibinin 13 Ekim 2026 tarihli tercihidir; danışman tarafından henüz onaylanmadı. İnsan etiketleri, gerçek inceleme kararları ve farklı modellerle yapılacak tekrarlar, mevcut sonuçların ne kadarını koruyabildiğimizi gösterecek.

## 1. Problem: metinden kayıt üretmek ve kaydı kabul etmek

Bir dil modeli, kendisine verilen metni okuyup kişi adları ve ilişkiler gibi düzenli kayıt önerileri üretebilir. Örneğin bir aktarım cümlesini, kimin kimden rivayet ettiğini gösteren bir kayda çevirmesini isteyebiliriz. Böylece metinleri tek tek elle aktarmanın yerine, düşük maliyetle öneri üretme olanağımız olur. Burada ucuz olan işlemin doğru olduğu sonucunu çıkarmıyoruz. Asıl sorumuz, önerilerden hangisinin insanların güvenerek başvuracağı depoya alınacağıdır.

Bir metni düzenli kayda çevirdiğimizde farklı hatalar aynı düzgün görünüşün arkasına saklanabilir. Kaynakta hiç bulunmayan bir kişi eklenebilir. Kaynakta bulunan bir ad sessizce daha uzun bir ada çevrilebilir. Yazılımın tanımadığı bir kayıt türü üretilebilir. Sonunda doğru görünen bir bilgi saklansa bile, onu kimin kabul ettiği kaybolabilir. Bunların her biri farklı bir sorun olduğu için hepsini modelin tek bir güven puanıyla açıklamaya çalışmıyoruz.

Temsilî örnek olarak, kaynakta yalnızca `سفيان` yazdığını düşünelim. Model `سفيان بن عيينة` önerirse kaynakta görünen biçime bilgi eklemiştir. Bu kişinin gerçekten o kişi olup olmadığı ayrı bir araştırma sorusudur. Metinden aynen ad çıkarma görevinde ise eklenen bölümün kaynağı gösterilmemiştir. Bilinen bir kimliği tahmin etmek ile metinde görünen adı kaydetmek aynı iş değildir.

Başka bir temsilî örnekte model, tanımlı kişi türü yerine kendisinin uydurduğu bir tür adı döndürebilir. Bu durumda ad doğru olsa da öneri yazılımın beklediği biçime uymaz. Bir insan öneriyi düzeltmişse yalnızca son değeri tutmak da eksiktir. Düzeltmeden önce ne yazdığını, kim tarafından değiştirildiğini ve değişikliğin hangi öneriye ait olduğunu bilmek isteriz.

GiraffeGraph bu ayrımları depoya giriş sırasında görünür kılmayı amaçlıyor. Bir kaydın kaynakla ilişkisi, biçimsel uygunluğu ve kabul kararı birbirinin yerine geçmiyor. Kaynakta geçen bir ad yanlış kişiye bağlanabilir; biçimi uygun bir öneri kaynaksız olabilir; insanın kabul ettiği bir kayıt da sonradan yeniden incelenebilir. Tasarladığımız kayıt düzeni, bu durumları tek bir doğruluk damgasına indirmemeli.

## 2. Hadis ve isnad

### Metin ve aktarım zinciri

Hadis çalışmasında burada kullandığımız ayrım, aktarım zinciri ile aktarılan metin arasındadır. İsnad, rivayetin kimlerden geçerek aktarıldığını gösteren zincirdir. Matn, bu zincirin taşıdığı metindir. Ravi ise zincirde aktarımı yapan kişidir. Bu rehberde hadislerin dinî hükmünü veya sıhhatini belirlemiyoruz; metinde yazılan aktarım zincirini düzenli kayda çevirme ve kaydın kabulünü izleme sorununu ele alıyoruz.

Etiketleme yönergemizdeki gerçek örnek, Buhârî 1'in başlangıcıdır:

`حدثنا الحميدي عبد الله بن الزبير قال حدثنا سفيان قال حدثنا يحيى بن سعيد الأنصاري قال أخبرني محمد بن إبراهيم التيمي أنه سمع علقمة بن وقاص الليثي يقول سمعت عمر بن الخطاب رضي الله عنه على المنبر قال سمعت رسول الله ...`

Bu parçada yönergenin ravi adı olarak yazdığı ifadeler sırasıyla şöyledir:

`الحميدي عبد الله بن الزبير | سفيان | يحيى بن سعيد الأنصاري | محمد بن إبراهيم التيمي | علقمة بن وقاص الليثي | عمر بن الخطاب`

`حدثنا`, "bize anlattı" anlamında bir aktarım ifadesidir. `أخبرني`, `سمعت`, `عن` ve `قال` da aktarımı anlatan sözcüklerdir; adın parçası sayılmazlar. Ad çıkarırken bu sözcüklerle kişi adını ayırmamız gerekir. Yönergemiz `رسول الله` ifadesini ravi olarak etiketlemiyor. Dolayısıyla metinde bu ifadenin bulunması, görevimiz açısından yeni bir ravi etiketi üretmemiz gerektiği anlamına gelmiyor.

Yönergenin başka bir kuralı da kaynakta `سفيان` varsa `سفيان` yazmaktır. Bunun `سفيان بن عيينة` olduğunu bildiğimizi düşünsek bile metindeki adın yerine o bilgiyi koymuyoruz. Önce görünen ifadeyi kaydediyoruz. İfadenin hangi kişiyi gösterdiğine karar vermek, daha sonra açıklayacağımız kimlik çözümleme işidir.

### Bir ad neden zinciri değiştirir?

Zincirde bir adı yanlış yazmak, yalnızca yazım hatası olarak kalmayabilir. Temsilî örnekte aynı kısa adla anılan farklı kişileri birleştirirsek, aktarımı yanlış kişiye bağlarız. Aynı kişinin farklı yazılışlarını ayrı kişiler sayarsak bu kez tek kişiyi parçalarız. Metindeki ifadeyi doğru çıkarmak ile doğru kişiyi bulmak bu yüzden ayrı ayrı ölçülmelidir.

Bir zinciri bilgi grafı olarak gösterirken her ravi bir düğüm, yani ayrı bir varlık kaydı olur. Komşu ravileri yönlü ilişkilerle bağlarız. Buhârî 1 için yönergede yer alan sırayı, el-Humeydî → Süfyân → Yahyâ b. Saîd el-Ensârî → Muhammed b. İbrâhîm et-Teymî → Alkame b. Vakkâs el-Leysî → Ömer b. el-Hattâb biçiminde gösterebiliriz. Her ok "ondan rivayet etti" anlamını taşır. Her ilişki üzerinde hadis referansı, zincir numarası ve zincirdeki konum bulunur; böylece aynı kişiler arasındaki başka bir aktarımı bununla karıştırmayız.

<!-- sekil:graf -->
*Şekil 1. Buhârî 1 zinciri: el-Humeydî → Süfyân → Yahyâ b. Saîd el-Ensârî → Muhammed b. İbrâhîm et-Teymî → Alkame b. Vakkâs el-Leysî → Ömer b. el-Hattâb; her ok "ondan rivayet etti" anlamındadır ve hadis referansı, zincir numarası ve konum taşır.*

Hadis isnadı araştırma sorumuza uygun bir örnektir: zincirin kendisi graf olarak yazılabilir, ad ve sıra hatalarının sonucu görünürdür, karşılaştırma yapabileceğimiz etiketli veriler vardır. Son gerekçe, etiketleri tartışmasız doğru saydığımız anlamına gelmiyor. Uzmanların isnadın nerede bittiğinde bile anlaşamayabildiğini ilgili çalışmalarda göreceğiz. Veri bulunması, insan değerlendirmesi ihtiyacını ortadan kaldırmıyor.

## 3. Temel kavramlar

### Model, kayıt ve dayanak

Büyük dil modeli, metin girdisinden metin çıktısı üreten modeldir. Bizim görevimizde girdiye hadis parçası ve istenen kayıt biçimi, çıktıya ise ravi önerileri koyuyoruz. Temsilî örnekte modelden `سفيان` ifadesini bir kişi adı olarak döndürmesini istemek, onun metni düzenli bir öneriye çevirmesidir; bu çıktı henüz kabul edilmiş bilgi değildir.

Bilgi grafı, varlıkları düğümlerle, aralarındaki bağları ilişki veya kenarlarla gösterir. Düğümü bir kişi kartı, kenarı kartlar arasındaki anlamlı bağlantı gibi düşünebiliriz. Temsilî örnekte Süfyân bir düğüm, onun başka bir raviden aktarımı bir kenardır. Kenarın yönü de anlamın parçasıdır.

Şema, hangi düğüm ve ilişki türlerinin, hangi özelliklerle yazılabileceğini belirleyen tanımdır. `Narrator` adlı ravi düğümü ve `NARRATED_FROM` adlı aktarım ilişkisi bir şema örneğidir. Özellik, bir kaydın ad veya hadis referansı gibi alanıdır. Şema, metnin ne söylediğini doğrulamaz; yazılabilecek kayıt biçimini sınırlar.

Aday veya öneri, henüz kabul edilmemiş model çıktısıdır. Temsilî örnekte modelin `سفيان` için ürettiği kişi kaydı adaydır. Kontrolleri geçmesi ya da insan tarafından kabul edilmesi, adayın iş akışındaki durumunu değiştirir. "Model yazdı" ile "sisteme kabul edildi" ifadelerini bu nedenle ayırıyoruz.

Alıntı, öneriye dayanak olarak gösterilen kaynak parçasıdır. Aday, alıntının hangi bölütten geldiğini de taşır; bölüt, kaynak metnin işleme için ayrılmış parçasıdır. Temsilî örnekte `قال حدثنا سفيان` alıntısı `سفيان` önerisine dayanak olabilir. Alıntının gerçekten kaynakta bulunması ile önerilen adın o alıntıda bulunması farklı kontrollerdir.

Kaynağın desteklemediği olguya burada halüsinasyon diyoruz. Kaynakta olmayan bir kişiyi eklemek bunun temsilî örneğidir. Buna karşılık kaynaktaki adı Latin harfleriyle yazmak, yönergeye aykırı bir dönüşüm olabilir ama tek başına hayalî bir kişi uydurulduğunu göstermez. Hata sınıflarını ayırma gerekçemiz budur.

Şema sapması, önerinin tanımlanan kayıt düzeninden çıkmasıdır. Temsilî örnekte izin verilen `Narrator` yerine tanımlanmamış bir tür döndürmek veya tanımsız bir özellik eklemek sapmadır. Bunun çözümüyle yanlış kişiyi bulmanın çözümü aynı değildir; biri biçim, diğeri içerik sorunudur.

### Kontrol ve insan kararı

Deterministik kontrol, aynı girdi ve kuralla aynı sonucu veren yazılım kontrolüdür. Temsilî örnekte "önerilen ad alıntıda geçiyor mu" sorusunu metin karşılaştırmasıyla yanıtlarız. Modelden yeniden görüş istemeyiz. Böyle bir kontrol belirli bir koşulu sınar; bütün yanlışları yakaladığı iddiasını taşımaz.

Gerekçe kodu, önerinin neden incelemeye gönderildiğini makinenin kaydedebileceği kısa sınıftır. Örneğin değerin alıntıda bulunmaması bir gerekçedir. Kod, inceleyen kişinin sorunun nerede çıktığını görmesini sağlar; insanın vereceği kabul veya ret kararının yerine geçmez.

İnceleme kuyruğu, kararı bekleyen önerilerin tutulduğu yerdir. Temsilî örnekte alıntıda bulunmayan uzun ad burada bekler. Kuyrukta bulunmak, önerinin yanlışlığının kanıtlandığını göstermez. Kontrolün karar vermeye yetmediğini ve insan değerlendirmesi gerektiğini gösterir.

İnsan-döngülü sistem, bazı aşamalarda insanın karar verdiği iş akışıdır. Temsilî örnekte model ad önerir, kontrol işaretler, inceleyen kişi kaynakla karşılaştırıp kabul eder, reddeder veya düzeltir. Mevcut ölçümlerimizde bu insan aşaması uygulanmadı; terim, kurduğumuz ve sınayacağımız düzeni anlatıyor.

Kabul kaydı, bir olgunun hangi insan kararıyla veya adı belirtilen otomatik politikayla kabul edildiğini gösterir. Karar kaydı daha geniştir; ret ve düzeltme de karardır. Temsilî örnekte kısa adın korunmasına karar veren kişinin adı, karar zamanı ve düzeltme varsa önceki ve sonraki değer birlikte tutulur.

Güven skoru, modelin önerisi için verdiği sayısal güven ifadesidir. Temsilî örnekte iki öneriden birine daha yüksek skor vermesi, onun dışarıdan doğrulandığı anlamına gelmez. Skoru doğru ve yanlış önerileri ayırma yeteneği bakımından ölçmek gerekir. Biz bunu kontrolün bulduklarıyla da karşılaştırıyoruz.

### Ölçümün dili

Referans etiketleri, çıktıyı karşılaştırdığımız cevap kayıtlarıdır. İnsanlarca hazırlanıp uzlaşıyla sonuçlandırılmış bir cevap anahtarına altın standart diyoruz. Otomatik veya dolaylı yolla elde edilen etiketler gümüş standart olarak kullanılabilir. Platform etiketlerimiz karşılaştırma sağlıyor, fakat insan altın standardı olduklarını söylemiyoruz.

Precision, doğru önerilerin bütün öneriler içindeki payıdır. Recall, bulunması gerekenlerin ne kadarını bulduğumuzdur. F1 bu ikisini birlikte değerlendiren, ikisinin çarpımının iki katını toplamlarına bölen ölçüdür. Aşağıdaki sayılar ölçüm sonucu değildir; uydurulmuş bir öğretim örneğidir: gerçekte 10 ravi olsun, model 9 ravi önersin, bunların 8 tanesi doğru olsun. Precision 8/9, yaklaşık 0,889; recall 8/10, yani 0,800; F1 ise 16/19, yaklaşık 0,842 olur. Bu temsilî örnek, doğru öneri oranı yüksekken bazı ravilerin yine de bulunamayabileceğini gösterir. Mikro F1, örneklerin kararlarını birlikte sayarak bu ölçüyü hesaplar; tek tek hadis puanlarını ortalamakla aynı işlem değildir.

Katı eşleştirmede, harekeler ve harf varyantları ayıklandıktan sonra önerilen ad ile referanstaki ad birebir aynı olmalıdır. Gevşek eşleştirmede birebir aynılık, birinin ötekinin içinde geçmesi ya da sözcük düzeyinde F1 değerinin en az 0,60 olması yeter. Sistemin adları referans adlarla, toplam benzerliği en yüksek tutan eşleme ile birer birer eşlenir. Temsilî örnekte `الحميدي عبد الله بن الزبير` yerine yalnız `الحميدي` yazan bir çıktı katı eşleştirmede yanlış, gevşek eşleştirmede doğru sayılır.

Bootstrap güven aralığı, elimizdeki örnekleri yeniden seçerek ölçümü tekrarlamak ve sonucun ne kadar değiştiğini görmek için kullanılan yöntemdir. Biz hadisleri yeniden seçerek bunu 2.000 kez tekrarladık. Örneğin yalnız şema verilen modelin gevşek F1 değeri 0,890, %95 aralığı ise 0,865 ile 0,914 arasıdır: başka 300 hadisle ölçseydik değerin büyük olasılıkla bu aralıkta kalmasını bekleriz.

Ablation, bir parçanın katkısını görmek için o parçayı çıkararak veya aşama aşama ekleyerek karşılaştırma yapmaktır. Temsilî örnekte aynı önerilere önce şema, sonra alıntı, sonra değer kontrolü uygularız. Değişen sonuç, hangi kontrolün ne eklediğini gösterir; başka bir modelin önerileriyle karıştırılmaz.

### Ad, kimlik ve kararın kapsamı

Ravi kimliği veya varlık çözümleme, metindeki adın hangi gerçek kişiyi gösterdiğini belirleme işidir. `سفيان` ifadesini doğru kopyalamak bu işi tek başına çözmez. Aynı ad farklı kişiler için kullanılabilir; bir kişi de farklı yazılışlarla anılabilir. Adın yüzey biçimi, metinde görünen yazılışıdır; kişi kimliği bundan ayrı kayıttır.

Sessiz hata, sistem soru sormadan bir kararı uyguladığında oluşan yanlış sonuçtur. Temsilî örnekte kısa ada daha önce verilmiş bir kimlik kararını başka bağlamda kullanıp yanlış kişiye bağlamak böyle bir hatadır. Kullanıcıya soru çıkmaması, işlemin doğru olduğu anlamına gelmez.

Karar defteri, yeniden kullanılması gereken insan kararlarının tutulduğu kayıttır. Kararın kapsamı, eski kararın hangi durumlarda geçerli sayılacağını belirler. Temsilî örnekte "bu ad her yerde bu kişidir" geniş, "bu öğrencinin aktardığı yerde bu ad bu kişidir" daha dar kapsamdır. Öğrenci burada eğitim alan kişi değil, zincirde adı geçen raviden aktarım yapan önceki ravidir.

Tabaka, ravileri kuşaklar üzerinden değerlendirmede kullandığımız sınıftır. Vefat yılı kuralı da kişi kimliği kararının zaman bilgisiyle çelişip çelişmediğini sınayan kuraldır. Temsilî örnekte yeniden kullanılan kimlik kararı kuşak veya vefat bilgisiyle çelişirse kapsamı daraltıp yeni soru sormayı deneyebiliriz. Bu alan kuralları ve kimlik defteri henüz motorun içinde değildir; sonuçlarını benzetimde ölçtük.

## 4. Sistem nasıl çalışıyor?

### Motorun parçaları

GiraffeGraph Core, metinden gelen önerilerle kabul edilmiş grafı ayıran motordur. FastAPI arka ucu, uygulamanın işlem isteklerini karşılayan yazılım katmanıdır. PostgreSQL, üst veriyi, yani işlenen kaynak ve iş akışıyla ilgili kayıtları tutar. Neo4j kabul edilerek işlenmiş bilgi grafını tutar. Next.js ile hazırlanan web paneli de sistemin tarayıcıdan kullanılan yüzüdür.

Bir proje, kullanacağı düğüm türlerini, ilişki türlerini ve özellikleri tanımlar. İsnad şablonunda 2 düğüm türü ve 2 ilişki türü vardır. Bu sayı bütün alanların aynı şemayı kullanacağı anlamına gelmez. Motorun proje tanımı, hangi önerinin o iş için izin verilen biçimde olduğunu belirler.

Kaynak birimi, işlenecek metin kaydıdır; bölütleyici bu birimi daha küçük parçalara ayırır. Hadis için isnadı matndan ayırır, tahvîl işareti `ح` geldiğinde yeni bölüt başlatır. Tahvîl işaretini burada yeni bir bölüt sınırı olarak kullanıyoruz. Model veya kurallı program olan sağlayıcı, bölütlerden aday üretir. Sağlayıcı sözcüğü, öneriyi hangi bileşenin hazırladığını anlatır.

Adayın yanında bir veya daha fazla alıntı ve bunların bölüt referansları bulunur. Kontroller öneri üzerinde çalışır; inceleme gerektiren durumlar kuyruğa gider. Motorun incelemeye yönlendiren on gerekçe kodu, bilinmeyen tür ve özellikleri kaydeden iki kodu vardır. Bunlar, sorunları sonradan açıklayabilmek için ayrı tutulur.

<!-- sekil:akis -->
*Şekil 2. İşleyiş: hadis metni → bölütleme → modelin önerisi → kontroller → inceleme kuyruğu → karar kaydı → bilgi grafı.*

### Buhârî 1'in adım adım izlediği yol

İlk adımda Buhârî 1 kaynak birimi olarak gelir. Bölütleyici zinciri aktarılan metinden ayırır. Kaynakta görülen ravi ifadelerinin hangi parçada olduğunu kaybetmemek gerekir. Sonraki alıntı kontrolü, bütün metinde gelişigüzel arama yapmak yerine adayın gösterdiği bölütü kullanır.

Sonra sağlayıcı adları ve aktarım önerilerini hazırlar. Temsilî işlem örneğinde el-Humeydî ifadesinin geçtiği alıntı onun adayına, `قال حدثنا سفيان` alıntısı Süfyân adayına eşlik eder. Burada bu hadise ait gerçek bir model çalıştırmasının çıktısını sunmuyoruz; verilen gerçek metin üzerinden motorun nasıl işleyeceğini anlatıyoruz.

Şema kontrolünde adayın türü proje tanımında aranır. Tür tanınmıyorsa yalnızca o aday düşürülür; aynı çağrıdaki diğer adaylar yaşamaya devam eder. Bilinmeyen tür ayrıca inceleme öğesi olarak kaydedilir. Tanımlanmamış özellik anahtarları kaldırılır ve kayda geçirilir. Böylece tek bir uygunsuz aday yüzünden çağrıdaki bütün önerileri kaybetmeyiz.

Alıntının kaynakta bulunması kontrolünde gösterilen parça, belirtilen bölütte aranır. Model gerçek bir ifadeyi yanlış bölüte bağladıysa bu da dayanak sorunudur. Değerin alıntıda bulunması kontrolü ise düğüm kimliğini oluşturan dizeyi, örneğin ravi adını, adayın alıntılarından en az birinde arar. Dize, yazılımın karşılaştırdığı metin değeridir. Karşılaştırma Arapça harekeleri ve harf varyantlarını göz ardı eder.

Bu iki kontrolün ayrılığı Süfyân üzerinden görülebilir. Temsilî örnekte alıntı gerçekten `قال حدثنا سفيان` olsun, önerilen ad ise `سفيان بن عيينة` olsun. Alıntı kaynak kontrolünü geçer; uzatılmış ad değer kontrolünü geçmez. Model, alıntıyı doğru kopyaladığı hâlde önerdiği değeri değiştirmiştir. Gerçek ölçümde bütün alıntıların bulunmuş olması, çıkarılan bütün adların aynı nedenle desteklendiğini göstermedi.

Ölçülen koşudaki gerçek örneklerden birinde `هشام بن عروة عن أبيه` ifadesindeki `أبيه` yerine `عروة` yazıldı. Bir başkasında metindeki `عثمان`, `عثمان بن عفان` biçimine genişletildi; eklenen bölüm metnin hiçbir yerinde bulunmuyordu. İlkinde akrabalık ifadesi ada çevriliyor, ikincisinde ad tamamlanıyor. İki işlem de kaynakta yazan biçimi koruma görevi açısından izlenmesi gereken dönüşümdür. Bu örneklerden kişilerin tarihsel kimliği hakkında yeni hüküm çıkarmıyoruz.

Alıntı veya değer kontrolünü geçemeyen aday, güveni ne kadar yüksek olursa olsun incelemeye gider. Onu silmiyoruz; çünkü kontrolün başarısızlığı olgunun yanlışlığını kanıtlamaz. İnceleyen kişinin dönüşümü uygun bulması, kaynak biçimine dönmesi veya öneriyi reddetmesi gerekebilir. İncelemeye ayrılan doğru adaylar da bu yüzden kaybolmadan bekler.

Karar verildiğinde inceleyenin adı, zaman, harcanan süre ve düzeltme varsa önceki ve sonraki değer tutulur. Kararlar eski kaydın üzerine yazılmaz, eklenir. Böylece son değerin yanında o değere nasıl gelindiği de kalır. Her kabul edilmiş olgu için insan kararını veya onu kabul eden adı belirtilmiş otomatik politikayı gösterebiliriz.

Bir koşunun graf kaydı, o koşuda inceleme bekleyen aday kalmadığında yapılır. Koşu, aynı işleme ait öneri ve kontrol sürecidir. Zincir ilişkisini yalnızca iki ravi adıyla tanımlamıyoruz: kimliği hadis referansı, zincir numarası ve konumdan oluşur. Aynı raviler başka hadiste de komşuysa ayrı bir kenar kaydedilir. Model bu son yazma işlemini yapamaz; grafın kapısında motorun iş akışı vardır.

## 5. Ana fikir: saklanan şey insanın kararıdır

### Yeniden çıkarılabilen bilgi ve karar

Proje sahibinin 13 Ekim 2026'da benimsediği ana iddia şu: dil modeliyle kurulan bilgi katmanında kalıcı olarak saklamamız gereken şey insanın kararıdır; kaynaktan yeniden türetilebileni yeniden türetiriz. Bu tercih danışman tarafından henüz onaylanmadı. Dolayısıyla bunu tamamlanmış ortak değerlendirme veya kanıtlanmış genel sonuç olarak sunmuyoruz.

Türetilmiş bilgi, eldeki asıl kaynaktan yeniden üretilebilen bilgidir. Hadisten çıkarılan ravi adayı böyledir: metin duruyorsa çıkarım tekrar denenebilir. Kabul, ret, düzeltme veya "buradaki ad şu kişiyi gösteriyor" kararı ise metnin içinde yazılı değildir. Onu veren kişinin değerlendirmesini yeniden üretilebilir kaynak bilgisiyle karıştırmamak gerekir.

Bu ayrım projenin iç yazısı "The Cache and the Ledger"dan geliyor. Cache, burada kaynaktan yeniden üretilebilen ara kayıt anlamındadır. Ledger ise karar defteridir. Kaynağın doğrusu değiştiğinde türetilmiş kaydı yeniden hazırlamak isteriz. Geçmişte verilmiş bir kararı ise sırf yeniden üretim yaptık diye kaybetmek istemeyiz.

Yazıdaki belge sayfası örneği ayrımı somutlaştırır. "Denetleyici bu dosyada bulunuyor" ifadesi koddan yeniden bulunabilir. "Başka bir tasarımı değerlendirdik ve reddettik" ifadesi koddan çıkarılamaz. İlkini güncel kodla yeniden kurabiliriz; ikincisi gerekçeyi bilen insanların geçmiş kararını gerektirir. Denetleyici, bu örnekte kod içindeki bir yazılım bileşenidir; dosyası hakkındaki bilgiyle tasarım tercihi farklı türde kayıttır.

### Ayrımı destekleyen gözlemler

İç yazıdaki Python Enhancement Proposal sayımı, yeniden üretilebilir bağlantıların saklandıkça uyumsuzlaşmasına örnektir. Python Enhancement Proposal, burada incelediğimiz Python öneri belgelerinin adıdır; PEP kısaltmasını bunun için kullanıyoruz. 733 PEP içinde ileriye doğru "replaces" bağlantılarının 42 tanesinden 27 tanesi geri bağlantıyla karşılanıyordu: %64. Başlıkları denetleyen bir linter, yani biçim kontrol programı bulunması bu karşılıklılığı sağlamamıştı.

Bu sayım, bütün belgelendirme kayıtlarının aynı oranda bozulduğunu söylemez. Gösterdiği şey daha sınırlı: birbirinden türetilebilir iki bağlantıyı ayrı ayrı saklamak, aralarında tutarsızlık bırakabilir. Böyle bir örnekte daha çok denetim eklemek kadar, hangi bilginin asıl kaynak olduğunu seçmek de araştırma konusudur.

Diğer destekleyici çalışma, motorun kendi kodu hakkında soru yanıtlayan kodlama ajanı deneyidir. Ajan, araç çağrılarıyla kodu inceleyebilen model tabanlı programdır. Koda neden o biçimin verildiğini soran sorular, koddan bulunabilen yapısal sorulardan farklı sonuç verdi. Karar defteri neden sorularına yardım etti; güncellenmemiş açıklamalar ise değişen yapı hakkında yanıltabildi. Bu gözlem de kendi deney koşullarıyla sınırlıdır.

Motor açısından bu fikir, öneriyi yeniden üretebilmek ile kararı yeniden kullanabilmek arasında ayrım koyar. Yeni çıkarım yapılması, geçmiş kararın her yeni bağlamda otomatik geçerli olması demek değildir. Ad aynı kalsa bile kişi farklı olabilir. Bu nedenle kararın kimin tarafından verildiği kadar hangi kapsamda geçerli olduğu da kayıt tasarımının parçasıdır.

## 6. Ne ölçtük?

### Veri, referans ve çıkarım koşulları

12 Ekim 2026 ölçümünde 300 hadis kullandık. Altı koleksiyonun her birinden 50 hadis vardı; referans toplam 1.778 ravi anılışı içeriyordu. Anılış, bir kişinin metindeki görünümüdür; aynı kişi farklı yerlerde anılabilir. Referans, İfta Sunnah platformunun üçüncü tarafça yeniden düzenlenen etiketleriydi. Bunlar insan altın standardı değil. Bu bölümde "doğru" ve "uyuşmayan" dediğimiz sonuçlar, aksi açıkça söylenmedikçe bu etiketlerle karşılaştırmayı anlatıyor.

Model koşullarında Claude Haiku 5.5 kullandık. Birden fazla model ailesini karşılaştırmadık. Kurallı ayrıştırıcı, dil modeli yerine yazılı kurallarla ravi çıkarmaya çalışan programdır. Model koşullarında ise yalnızca şemayı vermekle, tür açıklamaları ve alan ipuçları eklemek arasındaki farkı araştırdık. "İsnad-aware" ifadesi, isnadı gözeten bu ikinci istem biçiminin adıdır; istem, modele verdiğimiz talimat metnidir.

| Koşul, aynı 300 hadis | Gevşek P / R | Gevşek F1 | Eksiksiz zincir payı |
| --- | --- | --- | --- |
| Kurallı ayrıştırıcı | 0,968 / 0,881 | 0,923 | 0,490 |
| Yalnızca şema verilen model | 0,914 / 0,868 | 0,890 | 0,567 |
| Tür açıklamaları ve alan ipuçları | 0,997 / 0,919 | 0,956 | 0,690 |
| Aynı istem, zincir başına çağrı | 0,998 / 0,903 | 0,948 | 0,650 |

Tabloda P precision, R recall anlamındadır. Eksiksiz zincir payı, bütün anılışların doğru sırayla bulunduğu ve fazladan anılış eklenmediği zincirlerin payıdır. Birçok adı doğru çıkarmakla bütün zinciri doğru çıkarmanın farkını bu sütun gösterir.

Aynı testte katı eşleştirme F1 değeri kurallı yöntem için 0,633, yalnızca şema verilen model için 0,826 oldu. Gevşek ölçümdeki sıralama ve farklar bu nedenle her değerlendirme tanımına aynen taşınamaz. "Başarı" sözcüğünü tek bir sayıyla kullanmak yerine, ad sınırlarının ne kadar sıkı değerlendirildiğini ve zincirin tamamının istenip istenmediğini söylemek gerekiyor.

Daha erken pilotu da ayrı tutuyoruz. 30 Eylül 2026'da, motor dışında başka bir modelle ve Sanadset'in kurallarla üretilmiş etiketleriyle 50 hadis üzerinde çalıştık. Kurallı ayrıştırıcı F1 değeri 0,879, yalnızca şema istemi 0,865, isnadı gözeten istem 0,935 oldu. 605 alıntının 605 tanesi kelimesi kelimesine kaynakta bulundu; değer kontrolü 318 adayın 32 tanesini işaretledi. Doğru öneriyi yanlışın üzerinde sıralama yeteneğini ölçen AUC değeri, güven skoru için 0,626 idi. Bu pilotla sonraki deneyin farklarını, tek bir büyüyen test kümesinin sonuçları gibi birleştirmiyoruz.

### Değer kontrolü ve güven skoru

Yalnızca şema verilen model 1.688 ravi anılışı önerdi; bunların 145 tanesi referans etiketleriyle uyuşmadı. Değerin alıntıda bulunması kontrolü 155 öneriyi, yani %9,2'sini işaretledi. Bu kümede uyuşmayanların 122 tanesi vardı: 145 uyuşmazlığın %84'ü. Etiketlere göre 33 yanlış alarm oluştu ve 23 uyuşmazlık kaçtı. Yanlış alarm, kontrolün işaretlediği fakat referansla uyuşan öneridir; kişinin kararını henüz ölçmediğimiz için buna insanın gereksiz bulduğu işlem demiyoruz.

Alıntının kaynakta bulunması kontrolü hiçbir öneriyi işaretlemedi. Bütün alıntılar gösterilen kaynakta bulunuyordu. Bu sonuç kontrolün gereksiz olduğunu kanıtlamaz; bu koşuda ayırıcı bir katkı vermediğini gösterir. Değer kontrolünün katkısı da tam burada ortaya çıktı: alıntı doğruyken alıntıdan çıkarıldığı söylenen ad farklı olabiliyordu.

| Sinyal, şema koşulu | İncelemeye giden | İçerdiği uyuşmazlık |
| --- | --- | --- |
| Değer alıntıda yok | 155, %9,2 | 145 içinde 122 |
| Güven < 0,80 | 65, %3,9 | 145 içinde 16 |
| Güven < 0,85 | 275, %16,3 | 145 içinde 50 |
| Güven < 0,90 | 1.018, %60,3 | 145 içinde 110 |

Güven eşiklerini değiştirince kuyruğun boyutu da değişiyor. Kontrolün gönderdiği 155 öneriye en yakın eşik 0,85'tir: bu eşik daha fazla öneri gönderiyor (275) ama daha az uyuşmazlık buluyor (50, kontrolün 122'sine karşı). Yine de tablodaki eşikleri tam eşit iş yükü karşılaştırması saymıyoruz. Araştırma hedefimiz aynı inceleme payında kontrol ile güven skorunu karşılaştırmak. Buradaki eşik sayıları, güveni azaltarak daha çok öneri göndermenin hangi uyuşmazlıkları bulduğunu gösteriyor.

Model 7 farklı güven değeri kullandı. Güvenin AUC değeri 0,634 oldu. AUC burada rastgele seçilmiş doğru önerinin, rastgele seçilmiş yanlış öneriden daha yüksek puan alma olasılığını anlatır. 0,5 yazı tura düzeyini, 1 kusursuz ayrımı gösterir. Bu ölçüm, modelin verdiği güvenin bu veri ve görevde dışarıdan sınanması gerektiğini gösteriyor; bütün güven skorlarının her görevde aynı işleyeceğini söylemiyor.

İnceleme bekleyenleri dışarıda tuttuğumuzda, incelemesiz kabul edilen bölümün precision değeri 0,914'ten 0,985'e çıktı. Recall 0,868'den 0,849'a indi; F1 0,912 oldu. Düşen recall, doğru önerilerin bir kısmının kuyrukta beklediği durumun ölçümüdür. Onları reddetmedik. İnsan bu önerileri incelemediği için son kabul edilmiş bütünün F1 değerini bildiremiyoruz.

### İşaretlenen adlar neydi?

| Dönüşüm, 155 ad içinde | Sayı | Referansla uyuşmayan |
| --- | --- | --- |
| Latin harflerine aktarım | 79 | 79 |
| Dilbilgisel biçim değişimi | 34 | 21 |
| Akrabalık ifadesini ada çevirme | 25 | 18 |
| Başka yerde geçen ad | 7 | 3 |
| Metinde bulunmayan diğer ad | 10 | 1 |

Latin harfleriyle yazılan 79 ad, 14 hadiste toplandı ve hepsi etiketlerle uyuşmadı. Dilbilgisel biçim değişimine `أبي` yerine `أبو` yazılması örnektir. Akrabalık ifadesini ada çevirmeye ise `هشام بن عروة عن أبيه` içindeki `أبيه` için `عروة` yazılması örnektir. Bu dönüşümleri tek tek incelemek, "uyuşmuyor" etiketinin her zaman aynı hatayı anlatmadığını gösteriyor.

İşaretlenen bir ad, metnin hiçbir yerinde bulunmayan ekleme içeriyordu: `عثمان` yerine `عثمان بن عفان`. Dolayısıyla yalnızca şema koşulunda referansa göre gördüğümüz hataların çoğu, hayalî ravilerden çok doğru bir ad üzerinde kaydedilmeden yapılan dönüşümlerdi. Bu saptama bütün uyuşmazlıkların zararsız olduğu anlamına gelmez. Metinde görünen biçimi isteyen işte dönüşümü açıkça kaydetmek gerekir.

Peygamber'in ravi olarak yazılması ayrı bir sınıftı. Referansla uyuşmayan öneriler içinde 10 kez görüldü. Değer kontrolü bunların 2 tanesini yakaladı. Bu kategoriye özel kontrol henüz yok; planlanan "Peygamber ravi değildir" kuralı kalan 8 tanesini yakalayacaktı. Böylece kaynakta geçen bir ifadenin yine de görev tanımına aykırı olabileceğini görüyoruz.

### Parçaların ayrı katkısı ve alan dışındaki sonuç

Aşağıdaki ablation tablosunu mevcut koşulardan, aynı 300 hadisin yalnızca şema koşulundaki önerileri üzerinden hazırladık. İnsan incelemesi satırını boş bir başarı varsayımıyla doldurmuyoruz. İleride bu satır, kuyruğa gönderilenlerin ne kadarının düzeltildiğini veya kabul edildiğini gösterecek.

| Eklenen aşama | P / R / F1 | İncelemeye giden |
| --- | --- | --- |
| Model | 0,914 / 0,868 / 0,890 | Bu satırda yok |
| Şema kontrolü | 0,914 / 0,868 / 0,890 | Tür hatası görülmedi |
| Alıntı kaynakta kontrolü | 0,914 / 0,868 / 0,890 | İşaretleme yok |
| Değer alıntıda kontrolü | 0,985 / 0,849 / 0,912 | 155 öneri |
| İnsan incelemesi | Ölçülmedi | İnsan karar vermedi |

Haiku koşularındaki 910 çağrıda bilinmeyen tür görülmedi, bir bilinmeyen özellik görüldü. Şema kontrolü bu yüzden ad çıkarım puanlarını değiştirmedi. Değer kontrolü satırındaki değerler ise incelemesiz kabul edilen bölümündür. Tablonun son satırına kadar aynı türde tamamlanmış sonuç varmış gibi okumamak gerekir.

Hadis dışındaki karşı sonuç, iddiamızın sınırını gösteriyor. İnsan etiketli biyomedikal BC5CDR derleminde, aynı model ve yalnızca şema istemiyle değer kontrolü 303 uyuşmazlığın 53 tanesini işaretledi. Aynı inceleme payında güven skoru 58 tanesini buldu. Derlem, değerlendirme için kullanılan metin kümesidir. Bu sonuçta kontrol güven skorundan daha iyi değildi; hadis verisindeki yararı her alana genellemiyoruz.

### Adın kimlikten ayrıldığı ölçüm

Aynı 300 hadisteki kimlik incelemesinde 2.150 zincir konumu 740 kişiyi gösteriyordu. Konumların %10,0'ı birden fazla kişiyi kapsayan yazılışlarla ifade ediliyordu. Kişilerin %25,8'i ise birden fazla yazılışa bölünmüştü. Bunlar ad çıkarmanın ardından kalan iki ayrı güçlüğü sayısallaştırıyor: ad ortaklığı ve aynı kişinin farklı adlarla görünmesi.

Bu bulgulara dayanarak adın kendisini her durumda kimlik anahtarı saymıyoruz. Anahtar, eski kararın bulunmasını sağlayan kayıt bileşimidir. Aynı adı görünce eski kararı uygulamak az soru çıkarabilir, fakat bağlam değişmişse yanlış kişiyi sessizce seçebilir. Daha dar anahtar daha çok soru üretebilir. Benzetimde bu dengeyi araştırdık.

### Kimlik karar defteri benzetimi

AR-Sanad üzerindeki benzetim 27.056 gerçek test zinciri ve 150.904 anılış kullandı. Veri kümesinin etiketi, inceleyen insanın yerine geçti. Yani sonuç, insanların ne kadar sürede veya hangi doğrulukla karar verdiğinin ölçümü değil. Farklı kapsamlarla eski kararı yeniden kullanınca oluşan soru ve sessiz hata miktarını ölçtük.

| Kararın anahtarı | Anılış başına sessiz hata | Anılış başına soru |
| --- | --- | --- |
| Yalnızca ad | 0,100 | 0,101 |
| Öğrenci ve ad | 0,006 | 0,340 |
| Çelişkide kapsamı daraltma | 0,014 | 0,178 |

Son koşulda, tabaka ve vefat yıllarına dayanan deterministik kural çelişki gördüğünde kapsam daraltıldı. Sabit dar anahtara göre %48 daha az soru çıktı; sessiz hata farkı 0,008 oldu. Bu farkı bedelsiz iyileşme gibi sunmuyoruz. Soru sayısındaki azalmayla hatadaki değişimi birlikte veriyoruz.

İkinci etiket kümesi olan İfta'da 34.681 hadis ve 205.514 anılış vardı. Burada %32 daha az soru ve 0,003 sessiz hata farkı bulundu. Sonuç, defterin önceden görmediği koleksiyonlarda da korundu. Yine de etiketin insan yerine geçtiği koşul değişmedi; gerçek inceleme davranışını gösteren sonuç henüz yok.

### Kodlama ajanı deneyi

İkinci alan deneyinde motorun kendi kaynak kodunu kullandık: yaklaşık 17 bin satırlık tek kod tabanı, toplam 5.520 çalıştırma ve aynı model ailesinden iki model. Kodun neden öyle yazıldığını soran 12 soru, her biri iki çalıştırmayla değerlendirildi. Kod tek başınayken doğru yanıt oranı %0 ile %4, karar defteriyle %88 ile %100 oldu.

Yapısal sorular, yeterli araç çağrısı olduğunda belgesiz %94 ile %98 doğru yanıtlandı. Araç çağrısı ikiyle sınırlanınca açıklama gerekiyordu. Yeniden üretilmemiş açıklama ise değişen olgular konusunda ajanı yanılttı. Bu, karar bilgisini saklama ve türetilebilir açıklamayı yenileme ayrımını destekliyor. Ancak değerlendiren model aynı modeldi ve sayfaları ajanlar yazmıştı; deney bu sınırlardan bağımsız insan doğrulaması sayılmaz.

## 7. Başkaları ne yapmış?

Literatür okumalarımız 8 ve 15 Ekim tarihlerindeki incelemelere dayanıyor. Arama sistematik değildi. "Bulmadık" dediğimizde bütün alanı tarayıp yokluğunu kanıtladığımızı söylemiyoruz; okuduğumuz çalışmalar içinde görmediğimizi söylüyoruz. Hadis çalışmalarında veri ve görevler farklı olduğundan, aşağıdaki sayılar doğrudan bir yarışma tablosu değildir.

### Hadis ve ad çözümleme çalışmaları

SemanticHadith 2.0.1, Kamran, Butt ve Basharat'ın 2026 çalışmasıdır. Altı koleksiyondaki 34.458 hadisi ve 303.869 varlığı grafa dönüştürür; dil modeli yerine özel eğitilmiş tanıyıcı kullanır, varlık tanıyıcısı için mikro F1 %97 bildirir. Her koleksiyondan rastgele 100 örneği üç uzman kontrol etmiş, ancak uyum istatistiği verilmemiştir. Olgu başına karar ve kaynak alıntısı kontrolü yoktur; aynı adlı kişiler işaretlenmiş veya dışarıda bırakılmış, belirsiz adları aday listesiyle uzmana sunmak gelecek işe bırakılmıştır.

Oumer'in 2025 çalışması, önceden eğitilmiş modelleri görev için yeniden eğitir; buna ince ayar denir. Yazarın model deposundaki değerler, platform etiketlerine karşı ravi F1 için 0,98, ilişki F1 için 0,95'tir; kullanılan büyük etiketli eğitim verisi 223.478 hadistir. Bizim sorumuz bu sayıları geçmek değil, çıkarılan önerinin dayanağını ve kabul kararını izlemektir.

Mahmoud ve arkadaşlarının 2022 tarihli AR-Sanad 280K çalışması, 27.056 gerçek zincir ve 18.298 raviyle kimlik çözümlemeyi ele alır. Mikro F1 83,5'tir; zincirlerin %60,6'sında en az bir yanlış ravi bulunur, doğru ravi adayların ilk üçünde %95,3 oranında yer alır. Muhammad ve Abdullah gibi ortak adlarda doğruluk yalnızca %26'dır. Bu sonuçlar kimliği ayrıca ele almamızla ilişkilidir, fakat kararın kapsamını insan kaydı olarak yeniden kullanma deneyimizle aynı görev değildir.

AR-Sanad v2, 2024 çalışmasında yapay zincirlerde %94,6 doğruluk bildirir. Burada yalnızca özeti okuduk. Gerçek zincirdeki belirsizlik veya insan kararlarının kaydı hakkında özetin ötesinde sonuç çıkarmıyoruz.

Mosa'nın 2025 çalışması da yapay zincirlerde %97,8 doğruluk bildirir. Bunun için de yalnızca özet bilgimiz var. Bu sayıyı gerçek zincirlerdeki önceki sonuçlarla aynı koşulun gelişimi gibi göstermiyoruz.

Rezwan'ın 2025 çalışmasında altı uzman 1.213 rivayeti 0 ile 10 arası puanlamıştır. Uzman uyum istatistiği verilmemiştir. Uzman değerlendirmesi içermesi bizim planımızla ilişkilidir; ancak bu bilgi, metin önerilerinin her biri için kabul kaydı tutulduğunu göstermiyor.

Çinici'nin 2026 çalışması, 271 âlimin biyografisi için Gemini ve getirim kullanır. Getirim, yanıt üretirken ilgili kaynak parçalarını bulup modele sunma işlemidir; yazar ilk 100 kaydı kontrol etmiş, sayısal sonuç vermemiştir. Bu yüzden çalışmayı bizim kaynak ve değer kontrolümüzle aynı ölçekte karşılaştırmıyoruz.

Muther ve Smith'in 2020 çalışması, uzmanların isnadın bitişinde tam uyuşmasının %53 olduğunu gösterir. Aynı çıktı katı değerlendirmede 0,254, kısmi değerlendirmede 0,835 F1 alır. Bu çalışma kabul motorumuzla aynı işi yapmaz; etiketleme yönergesiyle eşleştirme kuralının sonuçları ne kadar değiştirebildiğini gösterir.

Text2KGBench 2023'te özne halüsinasyonu 0,17 iken precision 0,38'dir. Özne, bir ilişkinin başlangıcındaki varlıktır; temsilî örnekte aktarımı yapan ravi olabilir. Bu karşılaştırma, metinde bulunmanın doğru ilişki kurulduğunu göstermediğini hatırlatır; değer kontrolümüzün bütün doğruluğu çözmediği sınırla örtüşür.

### Genel bilgi grafı çalışmaları

Genel bilgi grafı tarafında ekibin 27 makalelik listesine ODKE+ ve KARMA eklenince 29 çalışma oldu. Bunların hiçbirinde çıkarılan değerin modelin kendi alıntısında bulunup bulunmadığını kontrol eden bir aşama görmedik. Bu, okuduğumuz küme hakkındaki bulgudur; evrensel bir ilk olma iddiası değildir.

Tsaneva ve arkadaşlarının 2025 çalışması, bize en yakın çalışmadır. Bilimsel bilgi grafı için dil modeli doğrulayıcılarını ve insanları dokuz iş akışında birleştirir; insanlar bütün üçlüleri, desteği düşük olanları veya model doğrulayıcıyla hattın anlaşamadıklarını görür. Üçlü, bir başlangıç varlığı, ilişki ve bitiş varlığından oluşan kayıttır; yalnızca anlaşmazlıkları göndermek F1'i 75'ten 77 ile 79 arasına çıkarmış, 61 ile 75 insan yargısı gerektirmiştir. Modüller ayrı değerlendirilmemiştir ve önceki otomatik doğrulayıcının attığı üçlülerin %34'ü doğrudur; bizim kontrolleri ayrı ölçme ve işaretleneni silmeme tercihimizle karşılaştırdığımız nokta budur.

KARMA 2025, birden fazla dil modeli ajanıyla çıkarım ve doğrulama yapar. Doğrulama ajanlarını sırayla kaldırarak ablation uygular, sonucu dil modeli hakemi puanlar. Bizim karşılaştırmamızdaki fark, deterministik kontrolü aynı önerilerde dış referansa göre ölçmek; kendi insan altın standardımızın henüz bulunmadığını da saklamamaktır.

Apple'ın ODKE+ 2025 çalışmasında ikinci bir dil modeli, bağlamın her olguyu destekleyip desteklemediğine karar verir. %35 daha az halüsinasyon bildirir ve precision değerinin %91'den %98,8'e çıktığını söyler; ölçüm yöntemi verilmemiştir. Yüzey biçimiyle normalleştirilmiş yanıtı ayrı alanlarda tutar, fakat değerin alıntıda bulunmasını kontrol etmez. Normalleştirme, ifadeyi ortak bir yazıma dönüştürmektir; bizim sorumuz bu dönüşümün dayanakla ilişkisinin nasıl denetleneceğidir.

Google'ın Knowledge Vault 2014 çalışmasında kararı kalibre edilmiş güven belirler. Kalibrasyon, skorun doğrulukla ilişkisini ayarlamaktır; AUC otomatik etiketlere karşı 0,959, insan etiketlerine karşı 0,869'dur. Bizim güven skorunu dışarıdan sınamamızla ilişkilidir, fakat modelin kendi alıntısına karşı değer kontrolüyle aynı mekanizma değildir.

HoloClean 2017, düşük güvenli düzeltmeleri kullanıcılara sormayı önerir. Bu öneri sınanmamıştır. Dolayısıyla belirsizliği insana gönderme fikrini kendimize ait saymıyoruz; hangi kontrolün hangi öneriyi gönderdiğini ve gerçek karar yükünü ölçmek istiyoruz.

Zep 2025, yeni olguyla çelişen eski olguyu dil modeliyle geçersiz kılar. Kararı insan vermez. Karar defteri ve çelişkide kapsamı değiştirme yönünden en yakın karşılaştırmamız budur; insanın verdiği kararı saklama ayrımı burada ortaya çıkar.

GoLLIE 2024, şema dışı etiketleri düşürür ve bunları ayrı hata sınıfı sayar. Bu nedenle şema dışı çıktıyı ele alma fikrini yeni sunmuyoruz. Kendi motorumuzda bu davranışın diğer adayları nasıl koruduğunu ve ölçümde ne katkı verdiğini açıklıyoruz.

Extract, Define, Canonicalize 2024, bütün şema istemde bulunsa bile başka sistemlerin şema dışı ilişkiler ürettiğini gösterir. Böylece modele şemayı söylemenin yeterli olmadığını ortaya koyar. Biz de şemayı talimatta bırakmayıp yazılımla kontrol ediyoruz; bu gereksinimi ilk fark eden biz değiliz.

GraphRAG 2024, tasarımı gereği metinde kelimesi kelimesine bulunmayan çıktıları kabul eder. Bu tercih onun göreviyle ilişkilidir. Bizim metindeki ravi biçimini koruma görevimizde uyguladığımız değer kontrolünü bütün graf sistemleri için zorunlu kural saymıyoruz.

Carriero ve arkadaşlarının 2024 çalışması da metinde aynen bulunmayan çıktıları tasarım gereği kabul eder. Bu bakımdan bizim yüzey biçimine dayalı görevimizden ayrılır. Bir kontrolün yararı, sistemin ne üretmeyi amaçladığına göre değerlendirilmelidir.

Sikos ve Philp 2020, her ifadeye ajan ve zaman bağlamak için standart yollar bulunduğunu gösterir. Adlandırılmış graflar ve nanopublication yapıları, ifadeleri köken bilgisiyle ilişkilendirme yollarıdır. Köken bilgisi, kaydın kaynağını ve oluşumunu açıklayan bilgidir; bunu temsil etmenin yeni yolunu icat ettiğimizi söylemiyoruz.

## 8. Nerede farklıyız?

### İddia etmediklerimiz

Yeni bir şema, daha yüksek çıkarım doğruluğu veya belirsiz olguları insanlara gönderme fikri ileri sürmüyoruz. Köken bilgisini temsil etmenin yeni yolunu veya kimlik mekanizmasının yeni olduğunu da iddia etmiyoruz. Şema ve kabul kayıtları motorun parçalarıdır; araştırma katkısını bütün parçaların ilk kez yapılmış olmasına bağlamıyoruz.

Bir farkın araştırma sonucu olabilmesi için tanım kadar ölçüm de gerekir. Mevcut sayılar bize sınanabilir başlangıç veriyor. İnsan etiketleri ve gerçek inceleme olmadan sonuçları uzmanlarca doğrulanmış kazanıma çeviremeyiz. D1 ile D4 adlarını, bu ayrımları takip etmek için kullanıyoruz.

### D1: değerin kendi alıntısında bulunması

D1, modelin önerdiği kimlik değerinin kendi gösterdiği alıntıda bulunmamasını ayrı hata sınıfı yapmaktır. Süfyân örneğinde alıntının doğru olması, eklenmiş ad bölümünü desteklemiyordu. Yalnızca şema koşulunda 145 referans uyuşmazlığının 122 tanesini bu kontrol yakaladı; 33 yanlış alarm ve 23 kaçan uyuşmazlık vardı.

İnsan verisinde bu sınıfın neye karşılık geldiğini göstereceğiz. Bağımsız etiketlenen hadislerde hangi adın korunması gerektiğini belirledikten sonra kontrolün işaretlediklerini karşılaştıracağız. Kuyruk kararlarında bu önerilerin ne kadarının reddedildiğini veya düzeltildiğini ayrıca ölçeceğiz. Böylece etiket uyuşmazlığıyla gerçek inceleme kararını ayırabileceğiz.

### D2: her kontrolün ayrı katkısı

D2, aynı öneriler üzerinde her deterministik kontrolün katkısını ayrı göstermektir. Mevcut ablation'da şema ve alıntı kontrolü F1'i değiştirmedi; değer kontrolü incelemesiz bölümün F1'ini 0,890'dan 0,912'ye taşıdı. Dış referans kullandık, dil modeli hakemi kullanmadık; fakat bu dış referans henüz insan altın standardı değil.

İnsan etiketleriyle aynı ayrımı yeniden ölçeceğiz. Bir kontrolün katkısı yoksa onu tablodan saklamayacağız. İnsan incelemesi eklendiğinde sonuca ne kattığını da aynı adayların devamı olarak izleyeceğiz. Böylece farklı girdilerin yarattığı farkı kontrol başarısı diye sunmaktan kaçınabiliriz.

### D3: kontrol ve güveni eşit inceleme payında karşılaştırmak

D3, kontrolü modelin kendi güveniyle aynı inceleme payında karşılaştırma sorusudur. Hadis koşulunda kontrol 155 öneriyi işaretledi ve 122 uyuşmazlık içerdi. Güven skoru 0,85 eşiğiyle bundan fazla öneri gönderdiği hâlde (275) yalnız 50 uyuşmazlık buldu. BC5CDR'de ise eşit inceleme payında kontrol 53, güven 58 uyuşmazlık buldu; karşı sonuç iddiamızın parçasıdır.

İnsan etiketlerinde eşit pay karşılaştırmasını tekrar yapacağız. Kuyruğa giden öneri miktarını eşitlemek, bir yönteme daha çok soru sorma hakkı vererek üstünlük üretmeyi önler. Gerçek incelemede karar süresini de tutacağız; aynı sayıda önerinin aynı insan süresi olduğu henüz gösterilmiş değil.

### D4: insan kararını saklamak ve kapsamıyla yeniden kullanmak

D4, her olgu için kabulün izini tutmak ve kimlik kararını kapsamıyla yeniden kullanmaktır. AR-Sanad benzetiminde çelişkide daralan kapsam, sabit dar anahtara göre %48 daha az soru ve 0,008 sessiz hata farkı verdi. İfta tekrarında değerler %32 ve 0,003 oldu. Bu sonuçlar insan kararı tasarımını gerekçelendiriyor; motor içinde tamamlanmış insan deneyi değiller.

İnsan verisinde karar veren kişiyi, süreyi ve düzeltmeyi kaydedeceğiz. Kimlik defterini motora aldıktan sonra yeniden kullanılan kararların nerede yeni soru gerektirdiğini izlemek gerekecek. En yakın karşılaştırma Zep'tir; orada kararı model verir. Bizim yaklaşımımızda saklanacak kararın insan kaynağı ve geçerli olduğu kapsam açık olmalıdır.

### Ne olursa haksız çıkarız?

İnsan etiketlerine karşı değer kontrolü az hata yakalarsa, mevcut etiketler üzerinde gördüğümüz yarar iddiamızı desteklemeyebilir. Aynı inceleme payında güven skoru aynı sayıda hata yakalarsa, kontrolün bu karşılaştırmadaki üstünlüğünü savunamayız. Biyomedikal sonuç bunun soyut bir olasılık olmadığını zaten gösteriyor. Yeni ölçümde sonuç değişirse açıklamayı değişen veriye göre daraltmamız gerekir.

## 9. Henüz bilmediklerimiz

İnsan altın standardımız yok. Hiçbir koşuda insan karar vermedi. Bu nedenle inceleme ekranının gerçek kullanımını, insanların kontrol gerekçelerini nasıl yorumlayacağını ve kuyruk kararlarının dağılımını mevcut sayılardan bilmiyoruz. İncelemeye gönderilen önerilerden ne kadarının sonunda kabul edileceği de ölçülmedi.

Çıkarım deneyinde tek model kullandık. Alan ipuçları eklendiğinde sonuçların değişmesi, yalnızca şema koşulundaki hata dağılımının bütün istemler için sabit sayılamayacağını gösteriyor. Referansların platform etiketleri olması da sınırdır. Etiketle uyuşmayan dönüşümün uzman açısından nasıl değerlendirileceğini ayrı ölçmek gerekiyor.

Kimlik karar defteri ve alan kuralları motor içinde değil, benzetimde çalıştı. Veri kümesi etiketi insan gibi yanıt verdiğinde soru sayısını hesaplayabiliriz, fakat gerçek kişinin kararsızlığını ve harcadığı zamanı bundan çıkaramayız. Sessiz hata miktarının insanla kurulacak defterde aynı kalacağını da bilmiyoruz.

Kodlama ajanı çalışması tek kod tabanındaydı; aynı model değerlendirici olarak kullanıldı ve sayfalar ajanlarca yazıldı. Karar defteri sonuçlarını başka alanlara taşıyan kanıt olarak tek başına yeterli saymıyoruz. Literatür aramamız da sistematik değildi. Okuduğumuz 29 çalışmada bir kontrolü bulamamamız, başka yerde hiç yapılmadığını kanıtlamıyor.

## 10. Sırada ne var?

Önce cevap anahtarının nasıl hazırlanacağını netleştireceğiz. Üç hadis uzmanının tamamı 6. haftada, etiketleme başlamadan önce yönergeyi gözden geçirip açık soruları yanıtlayacak. Hadis uzmanları kendi aralarında da ayrışabilir; danışmanımız bu yüzden birden fazla uzmanla çalışmamızı önerdi. Özellikle metindeki adı koruma ve zincir sınırları gibi kararların etiketleyenlerce aynı şekilde anlaşılması gerekiyor. Sistemin çıktısını görmeden yapılacak çalışma, insan referansının model önerisine göre şekillenmesini önlemeyi amaçlıyor.

| Zaman | Yapılacak iş | Tutulacak kayıt |
| --- | --- | --- |
| 6. hafta | Üç uzmanın yönerge incelemesi | Açık soruların yanıtları |
| 7. hafta | Bağımsız 50 hadis etiketi | Hadis başına süre |
| 8. hafta | Uyuşmazlıklara üç uzmanın bağımsız kararı | Sonuçlandırılmış etiketler |
| TÜBİTAK planı | Çalışmayı 300 hadise taşıma | Yeni değerlendirme verisi |

Deniz ve Alperen 50 hadisi bağımsız etiketleyecek. Birbirlerine karşı F1 hesaplayarak uyumu değerlendireceğiz; buna karşılıklı F1 diyoruz. Anlaşamadıkları her madde 8. haftada üç uzmana gidecek. Uzmanlar birbirlerinin yanıtlarını görmeden bağımsız karar verecek; çoğunluğun yanıtı referansa girecek. Üç yanıt da farklıysa madde "tartışmalı" olarak işaretlenecek, ana puanın dışında tutulacak ve ayrı raporlanacak. İki etiketleyicinin de yaptığı hataları yakalamak için anlaştıkları hadislerden rastgele seçilen 10 hadis de uzmanlara gidecek. Uzmanlar arasındaki uyumu, rastlantıyla oluşacak uyumu hesaba katan bir uyum ölçüsü olan Fleiss' kappa ile hesaplayıp etiketleyicilerin karşılıklı F1 değeriyle birlikte raporlayacağız. Böylece ölçüm referansının hangi kurallarla ve hangi anlaşmazlıklardan geçerek oluştuğu görülebilecek.

Kuyruğu, ilgili hadisi etiketlememiş bir ekip üyesi değerlendirecek. Karar başına süreyi ve ret oranını kaydedeceğiz; işaretlenen önerilerin daha sık reddedilip reddedilmediğine bakacağız. Uzmanlar kuyruk kararlarını vermeyecek. Böylece cevap anahtarını belirleyen kişilerle sistemin önerilerini değerlendiren kişiyi ayıracağız.

Teknik işlerde Peygamber kuralını eklemek, kimlik karar defterini motora taşımak ve daha çok modelle tekrar yapmak var. Bu işler tamamlanmış sonuçlar değil, plan. CSE 491 önerisinin teslimi 18 Ekim 2026, ara rapor 8. hafta, final 15. haftadır. TÜBİTAK 2209-A formu ise taslak hâlinde ve henüz gönderilmedi.

## 11. Ekip, belgeler ve nerede bulunur?

Ekip Yahya Efe Kuruçay, Deniz Büyükşahin ve Alperen Ulukaya'dan oluşuyor. Danışmanımız Arş. Gör. Dr. Taha Yiğit Alkan. Üç hadis uzmanıyla çalışacağız: Akdeniz Üniversitesi İlahiyat Fakültesinden Prof. Dr. Rifat Atay ve 6. haftaya kadar belirlenecek iki hadis uzmanı. Aşağıdaki iş paylaşımı öneri belgesindeki önerilen rollerdir; bütün görevlerin tamamlandığı anlamına gelmez.

Efe mimariyi, kontrolleri, karar kaydını ve puanlama betiğini üstleniyor. Puanlama betiği, çıktıyı referansla karşılaştırıp ölçüleri hesaplayan programdır. Deniz etiketleme yönergesini, ilk etiketleyici görevini ve inceleme ekranını üstleniyor. Alperen isnad bölütleyicisini, ikinci etiketleyici görevini ve zincir görünümünü üstleniyor.

Belgeler özel `GiraffeGraph/giraffegraph` deposunda bulunuyor. Aşağıdaki yollar depo köküne göredir. Ölçüm sayfaları deneylerin ve okuma karşılaştırmalarının izini taşırken, yönerge insan etiketlemesinde hangi kararların verileceğini tanımlar. Taslak belgeleri gönderilmiş başvuru veya onaylanmış sonuç belgesi olarak göstermiyoruz.

| Belge | Durum veya içerik | Depo yolu |
| --- | --- | --- |
| Tez taslağı | 55 sayfa, İngilizce ve Türkçe | `wiki/thesis/build/thesis.pdf`, `wiki/thesis/build/thesis-tr.pdf` |
| Makale taslağı | 11 sayfa, "Alıntı doğru, çıkarılan değer farklı" | `wiki/thesis/paper/build/` |
| TÜBİTAK formu | Taslak, gönderilmedi | `wiki/thesis/tubitak/build/form.pdf` |
| CSE 491 önerisi | Proje önerisi | `wiki/thesis/proposal/build/proposal.pdf` |
| Danışman toplantısı notları | 16 Ekim 2026 materyalleri | `wiki/thesis/meeting/2026-10-16/build/` |
| Uzman belgeleri ve yönerge | Etiketleme hazırlığı | `giraffegraph-core/evaluation/annotation/expert/build/` |
| Motor deneyleri | Ölçüm sayfası | `wiki/evaluation/engine-experiments.md` |
| İlgili çalışmalar | Okuma ve karşılaştırma sayfası | `wiki/evaluation/related-work.md` |

Ortak Zotero grup kütüphanesinin adı "giraffegraph". Zotero burada kaynakları birlikte tuttuğumuz kütüphanedir. Belgeler arasındaki ayrım, bir önerinin kaynağı ile o öneri hakkında verdiğimiz kararın kaynağını ayrı izlememize de yardım eder.

## Ek: Kavramlar sözlüğü

| Terim | Kısa anlamı | Örnek |
| --- | --- | --- |
| Hadis | Aktarım zinciriyle ele aldığımız rivayet | Buhârî 1 |
| İsnad | Aktaran kişilerin zinciri | El-Humeydî'den başlayan sıra |
| Matn | Zincirin taşıdığı metin | İsnaddan ayrılan bölüm |
| Ravi | Zincirde aktarım yapan kişi | Süfyân |
| Aktarım sözcüğü | Adın dışında aktarımı bildiren ifade | `حدثنا` |
| Tahvîl işareti | Yeni bölüt açtığımız işaret | `ح` |
| Büyük dil modeli | Metinden metin çıktısı üreten model | Claude Haiku 5.5 |
| İstem | Modele verilen görev talimatı | Şema ve tür açıklamaları |
| İnce ayar | Modeli görev verisiyle yeniden eğitme | Oumer'in model yaklaşımı |
| Sağlayıcı | Adayı üreten bileşen | Model veya kurallı program |
| Kurallı ayrıştırıcı | Yazılı kurallarla metni çözen program | Ravi çıkarım karşılaştırması |
| Bilgi grafı | Varlık ve ilişkilerin kayıt düzeni | Ravi aktarım grafı |
| Düğüm | Graftaki varlık kaydı | `Narrator` |
| Kenar veya ilişki | Düğümleri bağlayan anlamlı bağ | `NARRATED_FROM` |
| Üçlü | Başlangıç, ilişki ve bitiş kaydı | Raviler arasındaki aktarım |
| Şema | İzin verilen tür ve alanların tanımı | Ravi ve aktarım türleri |
| Özellik | Kaydın bir alanı | Hadis referansı |
| Şema sapması | Tanımın dışına çıkan çıktı | Bilinmeyen tür |
| Kaynak birimi | İşlenecek kaynak metin kaydı | Bir hadis |
| Bölüt | Kaynağın ayrılmış parçası | İsnad parçası |
| Bölütleyici | Metni parçalara ayıran bileşen | İsnadı ayıran program |
| Aday veya öneri | Henüz kabul edilmemiş çıktı | Modelin önerdiği ad |
| Alıntı | Öneriye dayanak gösterilen parça | `قال حدثنا سفيان` |
| Dize | Yazılımın işlediği metin değeri | `سفيان` |
| Halüsinasyon | Kaynağın desteklemediği olgu | Kaynaksız kişi ekleme |
| Deterministik kontrol | Aynı girdiyle aynı sonucu veren kural | Değeri alıntıda arama |
| Gerekçe kodu | İşaretleme nedeninin kayıt sınıfı | Değer alıntıda bulunmadı |
| İnceleme kuyruğu | Kararı bekleyen öneriler | İşaretlenen ad adayı |
| İnsan-döngülü sistem | İnsanın karar verdiği iş akışı | İnceleyenin düzeltmesi |
| Kabul kaydı | Kabulün dayanağını gösteren kayıt | İnsan veya politika kabulü |
| Karar kaydı | Kabul, ret veya düzeltmenin izi | Önceki ve sonraki değer |
| Otomatik politika | Adıyla belirtilen kabul kuralı | İnsan dışındaki kabul dayanağı |
| Güven skoru | Modelin verdiği güven ifadesi | Eşik altında kalan skor |
| Referans etiketi | Karşılaştırılan cevap kaydı | İfta Sunnah etiketi |
| Altın standart | İnsan uzlaşısıyla hazırlanmış anahtar | Üç uzmanın çoğunluk kararı |
| Gümüş standart | Otomatik veya dolaylı etiketler | Kuralla üretilen pilot etiketleri |
| Precision | Önerilerin doğru olan payı | Öğretim örneğinde 8/9 |
| Recall | Gerekenlerin bulunan payı | Öğretim örneğinde 8/10 |
| F1 | Precision ve recall ortak ölçüsü | Öğretim örneğinde 16/19 |
| Mikro F1 | Kararları birlikte sayarak F1 ölçümü | SemanticHadith sonucu |
| Katı eşleştirme | İfadede daha sıkı uyuşma arama | Katı F1 raporu |
| Gevşek eşleştirme | İzin verilen farklara tolerans | Gevşek F1 raporu |
| Kısmi eşleştirme | Tam olmayan örtüşmeyi değerlendirme | Muther ve Smith ölçümü |
| Bootstrap güven aralığı | Yeniden örneklemeyle değişimi gösterme | Hadisleri yeniden seçme |
| Ablation | Parçaları ayırarak katkıyı ölçme | Kontrolleri sırayla ekleme |
| AUC | Skorun doğruyu üstte sıralama ölçüsü | Güven için 0,634 |
| Kalibrasyon | Skorun doğrulukla ilişkisini ayarlama | Knowledge Vault güveni |
| Yanlış alarm | İşaretlenen fakat referansla uyuşan aday | Ölçümde 33 öneri |
| Derlem | Değerlendirmede kullanılan metin kümesi | BC5CDR |
| Anılış | Kişinin metindeki görünümü | Referanstaki ravi ifadesi |
| Yüzey biçimi | Metinde görünen yazılış | `سفيان` |
| Normalleştirme | İfadeyi ortak biçime dönüştürme | Ayrı normalleştirilmiş alan |
| Ravi kimliği | İfadenin gösterdiği kişi | Kısa adın hangi kişi olduğu |
| Varlık çözümleme | Adı kişi kimliğine bağlama | Aynı adlı kişileri ayırma |
| Sessiz hata | Soru sormadan verilen yanlış sonuç | Yanlış kimliği yeniden kullanma |
| Karar defteri | Yeniden kullanılacak kararların kaydı | Kimlik kararı defteri |
| Kararın kapsamı | Kararın uygulanacağı durumlar | Öğrenci ve ad birlikteliği |
| Anahtar | Eski kararı bulduran bileşim | Öğrenci ve ad |
| Öğrenci | Zincirde sonraki raviden aktaran kişi | Adın önündeki ravi |
| Tabaka | Kuşak değerlendirmesi için sınıf | Kimlik çelişkisi kontrolü |
| Vefat yılı kuralı | Zaman bilgisiyle çelişkiyi sınama | Kapsam daraltma gerekçesi |
| Benzetim | İnsan yerine veri etiketiyle deneme | AR-Sanad karar deneyi |
| Koşu | Bir işleme ait öneri ve kontrol süreci | İnceleme bekleyen koşu |
| İlişki kimliği | Kenarı diğerinden ayıran bileşim | Hadis, zincir ve konum |
| Üst veri | Kaynak ve işlem hakkındaki kayıt | PostgreSQL kayıtları |
| Arka uç | Uygulamanın istek işleyen katmanı | FastAPI |
| Web paneli | Tarayıcıdan kullanılan uygulama yüzü | Next.js paneli |
| Cache | Kaynaktan yeniden üretilebilir kayıt | Koddan bulunan dosya bilgisi |
| Ledger | Saklanan karar defteri | Reddedilen tasarımın kaydı |
| Denetleyici | Örnekteki yazılım bileşeni | Dosyası koddan bulunan parça |
| PEP | Python öneri belgesinin kısaltması | "Replaces" bağlantısı |
| Linter | Biçim kurallarını denetleyen program | PEP başlık denetimi |
| Kodlama ajanı | Araçlarla kod inceleyen model programı | Motor hakkında soru yanıtlama |
| Getirim | İlgili kaynak parçalarını bulma | Biyografi kaynaklarını sunma |
| Köken bilgisi | Kaydın kaynağı ve oluşumunun izi | Ajan ve zaman |
| Adlandırılmış graf | İfadeleri ayrı adla ilişkilendirme yolu | Köken bilgisi temsili |
| Nanopublication | İfadeyi kökenle sunan kayıt yapısı | Sikos ve Philp karşılaştırması |
| Karşılıklı F1 | Etiketleyicileri birbirine karşı ölçme | Deniz ve Alperen'in etiketleri |
| Puanlama betiği | Çıktıyı referansla ölçen program | Efe'nin önerilen görevi |
| Zotero | Ortak kaynak kütüphanesi | "giraffegraph" grubu |

