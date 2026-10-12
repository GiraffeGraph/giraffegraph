# Ravi etiketleme kılavuzu

> **v0 taslak — ekip ve alan uzmanı onayı bekliyor.** Kurallar onaydan sonra değişebilir.
> Etiketlerken kararsız kaldığınız her yeri `notes` sütununa yazın; v1 bu notlardan çıkacak.

## Görev

`hadiths_to_label.tsv` dosyasında 50 hadis var. Her satırda `text` sütunundaki Arapça metni okuyup
isnadda geçen ravi anmalarını, metindeki sırayla `narrators` sütununa yazacaksınız. Anmalar ` | `
ile, zincirler ` || ` ile ayrılır. İki kişi aynı 50 hadisi birbirinden bağımsız etiketliyor; amaç
iki etiketin ne kadar örtüştüğünü ölçmek.

## Çalışma kuralları

- Hiçbir sistem çıktısına bakmayın: program çıktısı, Sanadset etiketleri, hazır ravi listeleri,
  yapay zekâ araçları ve diğer etiketleyicinin dosyası buna dahil. Etiketleme bitene kadar bu
  hadisleri birbirinizle konuşmayın.
- Yalnızca `narrators`, `notes` ve `seconds_spent` sütunlarını doldurun. `hadith_id` ve `text`
  sütunlarına dokunmayın.
- Her hadis için kronometre tutun. Okumaya başladığınız andan satırı bitirdiğiniz ana kadar geçen
  süreyi saniye olarak `seconds_spent` sütununa yazın (örnek: `75`).
- Dosyayı Google E-Tablolar ya da LibreOffice ile UTF-8, sekmeyle ayrılmış olarak açın ve yine
  `.tsv` olarak kaydedin.

## Ravi anması nedir

Hadisi birinden alıp bir başkasına aktaran kişinin metinde geçtiği her yer bir ravi anmasıdır.

- Aynı kişi metinde iki kez geçiyorsa iki kez yazılır.
- Hz. Peygamber ravi olarak etiketlenmez (`رسول الله`, `النبي`).
- Hadisin metninde (olayın anlatıldığı kısımda) adı geçen kişiler ravi değildir.
- Musannifin hadisten sonraki değerlendirmesinde geçen isimler etiketlenmez
  (örnek: `قال أبو عيسى: هذا حديث حسن`).

## Anma nerede başlar, nerede biter

- Anmayı metinde yazıldığı gibi kopyalayın. Harekeleri ve i‘rab durumunu düzeltmeyin, ismi
  tamamlamayın, kısaltmayın. Metinde `سفيان` yazıyorsa `سفيان` yazın; kim olduğunu biliyor
  olsanız bile `سفيان بن عيينة` yazmayın.
- Rivayet lafızları anmaya girmez: `حدثنا`, `حدثني`, `أخبرنا`, `أنبأنا`, `سمعت`, `عن`, `أن`,
  `قال`, `يقول`. Pilot ayrıştırıcı `قال` kelimesini isme yapıştırmıştı (`الحميدي قال`);
  doğrusu `الحميدي`.
- Baştaki bağlaç `و` yazılmaz: `وهشام` yerine `هشام`. İsmin kendi harfi olan `و` kalır
  (`وكيع`, `وهب`).
- Dua ve saygı ifadeleri anmaya girmez (`رضي الله عنه`).
- `و` ile bağlanan raviler ayrı anmalardır: `حدثنا شعبة وهشام` → `شعبة | هشام`.

Örnek (Buhârî 1; etiketlenecek 50 hadis arasında değildir, kılavuzdaki diğer örnekler kurgudur):

`حدثنا الحميدي عبد الله بن الزبير قال حدثنا سفيان قال حدثنا يحيى بن سعيد الأنصاري قال أخبرني محمد بن إبراهيم التيمي أنه سمع علقمة بن وقاص الليثي يقول سمعت عمر بن الخطاب رضي الله عنه على المنبر قال سمعت رسول الله ...`

`narrators`: `الحميدي عبد الله بن الزبير | سفيان | يحيى بن سعيد الأنصاري | محمد بن إبراهيم التيمي | علقمة بن وقاص الليثي | عمر بن الخطاب`

## Niteleyiciler (künye, nisbe, lakap, mevlâ)

İsme bitişik yazılan niteleyici aynı anmanın parçasıdır, ayrı anma yapılmaz.
`عن نافع مولى ابن عمر` → tek anma: `نافع مولى ابن عمر`. Buradaki `ابن عمر` ayrı ravi değildir.
Araya giren açıklama da anmanın içinde kalır: `سفيان يعني ابن عيينة`.

## İsimsiz anmalar

`عن أبيه`, `عن جده`, `عن رجل`, `عن عمه` gibi ifadelerde kişi adı yoktur. Metindeki kelimeyi aynen
yazın (`أبيه`, `جده`, `رجل`) ve `notes` sütununa `isimsiz` yazın. Kim olduğunu biliyor olsanız da
ismini yazmayın. Metin ismi kendisi veriyorsa (`عن أبيه عروة`) ifadeyi olduğu gibi yazın
(`أبيه عروة`); bu durumda `isimsiz` notu gerekmez.

## Paralel zincirler (`ح`)

Tahvîl işareti `ح` yeni bir zincirin başladığını gösterir. Her zincirin ravilerini kendi sırasıyla
yazın, zincirleri ` || ` ile ayırın. Zincirlerin birleştiği ortak kısım metinde bir kez geçer; siz
de bir kez, geçtiği yerde yazın. Metinden sonra başlayan yeni bir isnad varsa (`وحدثني ...`) o da
` || ` ile ayrılmış ayrı bir zincirdir.

Kurgu örnek: `حدثنا آدم حدثنا شعبة ح وحدثنا مسدد حدثنا يحيى عن شعبة عن قتادة عن أنس ...`
→ `آدم | شعبة || مسدد | يحيى | شعبة | قتادة | أنس`

İsnadı olmayan bir satırda `narrators` boş kalır ve `notes` sütununa `isnad yok` yazılır.

## Açık sorular (alan uzmanına)

- Mevlâ gibi niteleyicide adı geçen kişi (`ابن عمر`) ayrıca işaretlenmeli mi?
- `عن أبيه عروة` tek anma mı (`أبيه عروة`), yoksa yalnızca `عروة` mi?
- Musannifin değerlendirmesinde geçen rivayet yolları (`ورواه فلان عن فلان`) etiketlenmeli mi?
- Ravinin şüphesi (`فلان أو فلان`) iki ayrı anma olarak mı yazılmalı?
