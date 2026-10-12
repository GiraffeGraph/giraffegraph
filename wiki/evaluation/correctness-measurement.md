# Doğruluk ölçümü: işlediğimiz veri doğru mu?

## Purpose

"Hadisleri ve Kur'an verisini işlediğimizde çıkan şeyin doğru olduğunu nasıl bileceğiz?" sorusuna
projenin verdiği cevabı, ölçülmüş olanı ve ölçülmemiş olanı tek yerde tutmak.

## Scope

- In: doğruluğun katmanları, her katmanın referansı ve metriği, kanıt türleri, ölçüm durumu, önkoşullar
- Out: metriklerin tam formülleri ve istatistik planı (`wiki/sources/claude-science-results/03_revize_deney_protokolu.md`),
  pilotun ayrıntılı tabloları (`wiki/sources/claude-science-results/08_pilot_raporu.md`), motor deneylerinin tasarımı
  ve tam tabloları (`wiki/evaluation/engine-experiments.md`)

Statü: katman modeli bu sayfanın sentezidir. Metrik tanımları ve protokol Claude Science önerisidir;
ekip ve danışman kararı değildir.

## BLUF

"Doğru mu?" tek bir sayıyla cevaplanmaz. Beş ayrı soru vardır ve her biri **farklı bir referansa**
karşı ölçülür. Bir sayı ancak üç şey söylendiğinde anlam taşır: hangi katman, hangi referans, hangi
eşleşme kriteri.

## Katman modeli

| Katman | Soru | Neye karşı ölçülür | Çekirdek metrikler | Durum |
|---|---|---|---|---|
| **L0 Kaynak bütünlüğü** | Elimizdeki ham metin doğru metin mi, doğru etiketli mi? | Güvenilir edisyon, lisans kaydı, içerik hash'i | Provenance doğruluğu, edisyonla karakter düzeyi fark oranı, kayıt sayısı tutarlılığı | Ölçülmedi. İndirilen dış verinin boyut ve sha256 kaydı `data/raw_manifest.json` içinde; lisans beyanları `data/README.md` içinde, Sanadset için iki beyan çelişiyor |
| **L1 Çıkarım** | Metinden çıkan ravi mention'ları, zincir sırası ve üçlüler metindekiyle aynı mı? | İnsan altın standardı, katman (a): span + sıra + sîga | P / R / F1 / F0.5 (M1 ve M2 ile), tam doğru zincir oranı, zincir düzenleme mesafesi, sıra konkordansı | İki etiket kümesine karşı ölçüldü: Sanadset kural etiketi (50 hadis) ve İfta platform etiketi (300 hadis, 2026-10-12). İnsan altın standardı yok |
| **L2 Kimlik** | Mention doğru raviye bağlandı mı? İki farklı ravi birleşti mi? | Uzman hükmü, katman (b): mention → otorite ID | Linking doğruluğu (M3), pairwise P/R/F1, B-cubed, CEAF-e, **over-merge oranı** | Sistem çıktısı ölçülmedi. Ad yazımının kimlik olarak taban çizgisi referans üzerinde ölçüldü (300 hadis, İfta ravi numaraları, 2026-10-12) |
| **L3 Graf tutarlılığı** | Graf kendi kurallarıyla çelişiyor mu? | Şema + alan kuralları (referans veri gerekmez) | Tip ve property düzeyi şema sapması, muâsara / tabaka ihlal oranı, kategori hatası, red kaynaklı recall kaybı | Tip düzeyi pilotta ölçüldü. Alıntı ve değer kapıları LLM çıktısı üzerinde motor içinde ölçüldü (300 hadis, 2026-10-12). Tarih kuralları yok |
| **L4 Tüketim** | Graf / RAG üzerinden verilen cevap doğru ve kaynağa sadık mı? | Altın cevaplı soru kümesi | Cevap doğruluğu, faithfulness, context precision / recall, atıf doğruluğu, çekimserlik; **graf vs çıplak RAG** | Ölçülmedi. Soru kümesi yok |

Katmanlar sıralıdır: L0 yanlışsa üstündeki her sayı yanlış metni ölçer. Kur'an vakasında tam bu oldu:
meal yanlış mütercime atfedilmiş ve ASCII'ye bozulmuştu, 6236 embedding bozuk metinden üretilmişti
(`wiki/sources/claude-science-context/07_case_codebase_wiki_and_quran.md` §C).

## Kanıt türleri

| Tür | Maliyet | Kapsam | Ne iddia ettirir |
|---|---|---|---|
| **Deterministik kontrol** | ~0 | Verinin %100'ü | "Kesin hatalı" ya da "kuralla çelişiyor". Doğruluğu kanıtlamaz, hatayı yakalar |
| **Gümüş standart** (Sanadset `<NAR>`) | Düşük | Büyük n | İki sistemden hangisinin daha iyi olduğu. Mutlak doğruluk değil |
| **Platform etiketi** (İfta) | Düşük | Altı kitap | Bir etiket kümesiyle uyum ve sistemler arası fark. İnsan altın standardı değil; mutlak doğruluk değil |
| **İnsan altın standardı** | Yüksek | 350–500 hadis | Mutlak P / R. Kodlayıcılar arası uyumla birlikte raporlanır |
| **Örneklemli denetim** | Orta | Rastgele tabakalı örnek | Tüm korpus için güven aralıklı doğruluk tahmini |

Sanadset `<NAR>` etiketleri düzenli ifade ve metin eşleme ile üretilmiştir; veri makalesi doğruluk
ölçümü ya da insan kontrolü raporlamaz (`related-work.md`).

Platform etiketi: İfta Sünnet platformundan türetilmiş veri ailesi ravi span'i, aktarım ilişkisi ve ravi
kimlik numarası taşır. Veri 2026-10-12'de indirildi ve 300 hadislik bir test kümesi kuruldu
(`data/README.md`, `data/eval/sixbooks-fresh/`). Etiketler platformun işaretlemesidir ve üçüncü bir kişi
tarafından yeniden yapılandırılmıştır; insan çift kodlamalı altın standart değildir ve kaynak kodlayıcılar
arası uyum raporlamaz. Gümüş standart ile insan altın standardı arasında bir basamaktır: L1 ve L2 için
hazır referans sağlar, kör protokolün ve K-5 uyum taahhüdünün yerini tutmaz. AR-Sanad 280K test kümesi
(altı kitaptan 27.056 sened, ravi kimlikleriyle) `data/eval/ar-sanad-identity/` altında hazırdır; üzerinde
ölçüm yapılmadı. Lisans beyanları: `related-work.md`, "Hazır referans veri adayları".

Altın standardın kendisi de ölçülür: katman (a) için kodlayıcılar arası karşılıklı F1, katman (b) için
sabit aday kümesinde Cohen's κ. Kör protokol şarttır: altın standardı üreten kişi sistem çıktısını
görmez, HITL kararını veren kişi o hadisin altın standardını üretmemiştir
(`wiki/sources/claude-science-results/03_revize_deney_protokolu.md` §5).

Örneklemli denetimde büyüklük: basit rastgele örneklemde %95 güven ve ±0,05 hata payı için en kötü
durumda n = 1,96² · 0,25 / 0,05² ≈ 384 üçlü. Üçlüler hadis içinde kümelendiği için güven aralığı
hadis düzeyinde cluster bootstrap ile hesaplanır (`wiki/sources/claude-science-results/pilot_isnad.py:bootstrap_ci`).

## Eşleşme kriteri (en büyük tuzak)

Aynı sistem çıktısı kritere göre çok farklı sayı verir. Pilotta deterministik ayrıştırıcının F1'i
katı eşleşmede 0,628, gevşek eşleşmede 0,879 (`wiki/sources/claude-science-results/pilot_results.csv`).

| Kriter | Tanım |
|---|---|
| M1 katı | Normalize edilmiş mention string'leri birebir eşit |
| M2 gevşek | Birebir eşit, ya da biri diğerinin substring'i, ya da içerik-token F1 ≥ 0,60 |
| M3 otorite | Aynı ravi otorite ID'sine bağlı |

Eşleştirme maksimum ağırlıklı ikili eşleştirmeyle yapılır (`wiki/sources/claude-science-results/pilot_isnad.py:align`).

## Somut örnek: bir hadiste doğru / yanlış nasıl sayılır

Üç örnek `wiki/sources/claude-science-results/pilot_sample.json` içinden; çıktı deterministik ayrıştırıcıya
(`pilot_isnad.py:rule_parse`) aittir, sayım `pilot_isnad.py:score_one` ile 2026-10-08'de yapıldı.
Referans Sanadset `<NAR>` etiketleridir (gümüş).

**1. Beklenenle karşılaştırma — Nesâî 693.** Referans 5 ravi:
`محمد بن منصور · سفيان · الزهري · سعيد · ابي هريره`. Sistem 5 ravi verdi; ilki `محمد بن منصور قال`
(sona "dedi" fiili yapışmış), diğer dördü birebir aynı.

| Kriter | Doğru (TP) | Fazla / yanlış (FP) | Kaçan (FN) | Precision | Recall |
|---|---|---|---|---|---|
| M1 katı | 4 | 1 | 1 | 0,80 | 0,80 |
| M2 gevşek | 5 | 0 | 0 | 1,00 | 1,00 |

Aynı çıktı, iki farklı not. Doğru / yanlış kararı eşleşme kriterine bağlıdır; kriter ölçümden bağımsız olarak protokolde sabitlenir.

**2. "Kelime metinde geçiyor mu" neden yetmez — Tirmizî 3144.** Referans 4 ravi. Sistem 9 parça
verdi: 4'ü doğru ravi, 5'i hadis metninden (matn) kopmuş parçalar (ör. `قتال بدر فقال غبت`).
Dokuzunun dokuzu da kaynak metinde birebir geçer (dayanaksız = 0). Recall 1,00, precision 4/9 = 0,44.
Metinde geçme kontrolü uydurmayı yakalar; yanlış yerden alınmış doğru kelimeyi yakalamaz.

**3. Metnin söyleyemediği — kimlik.** Nesâî 693'te `سفيان` ve `سعيد` tek isimdir; hangi Süfyân,
hangi Saîd olduğu metinde yazmaz. Tirmizî 3087'de zincir `عن أبيه عن جده` ("babasından, o da
dedesinden") diye biter; isim yoktur. Bu mention'lar L1'de tam puan alır, L2'de cevabı ancak ravi
otorite listesi ve uzman verir.

Sonuç: doğruluk kararı üç ayrı testten geçer — (a) çıktı kaynakta var mı (otomatik, alt eşik),
(b) insan etiketli referansla eşleşiyor mu (asıl ölçü), (c) doğru kişiye bağlandı mı (uzman).
İlişki düzeyinde bir `A → B` üçlüsü, iki ucu da doğruysa ve zincirde ardışıksa doğrudur.

## Ölçülmüş olanlar

Pilot: 50 hadis, 327 referans mention, Kütüb-i Sitte'nin 5 koleksiyonu (Buhârî yok), Sanadset 650K,
tek model, gümüş standart, 2026-09-30. Sayılar `wiki/sources/claude-science-results/pilot_summary.json` ve
`pilot_results.csv` dosyalarından.

| Bulgu | Sayı | Katman |
|---|---|---|
| Deterministik ayrıştırıcı, gevşek F1 | 0,879 | L1 |
| LLM + şema-only prompt, gevşek F1 | 0,865 | L1 |
| LLM + isnad-farkındalıklı prompt, gevşek F1 / precision | 0,935 / 1,000 | L1 |
| Zincir uzunluğu 8–14'te isnad-farkındalıklı LLM recall | 0,654 (ayrıştırıcı 0,776) | L1 |
| Alıntısı kaynakta birebir bulunan aday | 605 / 605 | L3 |
| `name` değeri kendi alıntısında geçmeyen aday (şema-only) | 32 / 318 | L3 |
| Tanımsız düğüm / ilişki tipi | 0 / 100 çağrı | L3 |
| `max_tokens` sınırında kesilen çağrı | 6 / 50, her iki LLM koşulunda | L1 |
| LLM güven skorunun doğruyu yanlıştan ayırma gücü | AUC 0,626 (n = 318) | Yönlendirme |
| Core merge key'i ile düğüm sayısı / imlâ katlamasıyla | 240 / 230 (327 mention) | L2, string düzeyi |

Pilotun gösterdiği üç şey: (1) mention çıkarımında LLM ayrıştırıcıyı geçmiyor, alan prompt'u geçiriyor;
(2) "alıntı kaynakta var mı" kontrolü hiçbir şey yakalamıyor, "değer alıntıda var mı" kontrolü %10,1
yakalıyor; (3) LLM'in kendi güven skoru insana yönlendirme için zayıf bir sinyal.

### Uçtan uca temel koşu (kural tabanlı, LLM'siz) — 2026-10-12

Aynı 50 hadis Core'un boru hattından geçirildi: isnad bölütleme, `rule_based_isnad` sağlayıcısı,
doğrulama, commit; bellek içi depo, insan kararı yok. Referans Sanadset `<NAR>` etiketleridir (gümüş,
etiket kalıntıları temizlenmiş); sayılar bu etiketlerle uyumu gösterir, doğruluğu değil. Güven
aralıkları hadis düzeyinde bootstrap (2000 örnekleme). Davranışın tanımı: `wiki/domains/hadith/isnad-pipeline.md`.

| Bulgu | Sayı | Katman |
|---|---|---|
| Commit edilen koşu | 50 / 50; 55 segment, 55 çağrı, başarısız çağrı 0 | Çalışırlık |
| Mention, katı eşleşme (M1) | P 0,684 · R 0,596 · F1 0,637 [0,573 – 0,698]; TP 195, FP 90, FN 132 | L1 |
| Mention, gevşek eşleşme (M2) | P 0,958 · R 0,835 · F1 0,892 [0,850 – 0,933]; TP 273, FP 12, FN 54 | L1 |
| Tam doğru zincir oranı | M1 0,04 · M2 0,44 | L1 |
| Grafa yazılan olgu | 515 (285 düğüm adayı, 230 ilişki); hepsinin alıntısı kaynak segmentte geçiyor ve hepsinin kabul kaydı var (`auto_validated`) | L3 |
| Ravi düğümü | 285 mention → 244 düğüm; hareke yok sayılırsa 237 ayrı yazım | L2, string düzeyi |

Bu koşu kapıların yakalama gücünü ölçmez: kural tabanlı sağlayıcı adı ve alıntıyı metinden birebir
kopyaladığı için kapılardan yapısı gereği geçer. Kapıların LLM çıktısı üzerindeki ölçümü bir sonraki
başlıktadır. Recall'un pilottaki ayrıştırıcıdan (0,890) düşük olmasının bilinen nedeni, metin
sınırından sonraki zincirlerin bölütlemede atılmasıdır.

### Motor deneyleri: LLM koşulları, kapılar, kimlik taban çizgisi — 2026-10-12

Core boru hattında dört koşul (kural tabanlı; Claude Haiku 5.5, effort `low` ile şema-only, isnad-farkındalıklı
tüm hadis, isnad-farkındalıklı zincir başına) 300 hadiste koşuldu: altı kitabın her birinden 50 hadis,
50 pilot hadisin hiçbiriyle örtüşmez, 1.778 referans mention. Referans **İfta platform etiketleridir**:
insan altın standardı değildir ve hiçbir koşuyu insan incelemedi. Sayılar bu etiketlerle uyumu gösterir.
Eşleşme M2, güven aralıkları hadis düzeyinde bootstrap (2000 örnekleme). Tasarım, tam tablolar, kırılımlar
ve sınırlar: `wiki/evaluation/engine-experiments.md`.

| Bulgu | Sayı | Katman |
|---|---|---|
| Kural tabanlı | P 0,968 · R 0,881 · F1 0,923 [0,910 – 0,935]; M1 F1 0,633 | L1 |
| Şema-only, tüm hadis | P 0,914 · R 0,868 · F1 0,890 [0,865 – 0,914]; M1 F1 0,826 | L1 |
| İsnad-farkındalıklı, tüm hadis | P 0,997 · R 0,919 · F1 0,956 [0,946 – 0,966]; M1 F1 0,904 | L1 |
| İsnad-farkındalıklı, zincir başına | P 0,998 · R 0,903 · F1 0,948 [0,936 – 0,959]; M1 F1 0,897 | L1 |
| Eşli F1 farkı: kural − şema-only | +0,032 [0,006 – 0,060] | L1 |
| Eşli F1 farkı: isnad-farkındalıklı − şema-only (tüm hadis) | +0,066 [0,041 – 0,091]; precision +0,083 [0,059 – 0,108] | L1 |
| Eşli F1 farkı: tüm hadis − zincir başına | +0,008; aralık sıfırı içerir | L1 |
| Alıntısı segmentinde bulunmayan aday (`quote_not_in_segment`) | 0; şema-only ve isnad-farkındalıklı koşullarda | L3 |
| Değer-alıntı kapısı, şema-only: 1.688 mention'ın 145'i İfta etiketiyle eşleşmiyor | 155 işaretlendi: 122 eşleşmeyen, 33 eşleşen; 23 eşleşmeyen işaretlenmedi. Eşleşmeyenlerin çoğu uydurma ravi değildir: 79'u Latin harfine çevrilmiş ad, 21'i i'râb değişikliği, 18'i akrabalık ifadesinin adla değiştirilmesi (`engine-experiments.md`, "Eşleşmeyen önerilerin bileşimi") | L3 |
| Şema-only koşulunda grafa incelemesiz yazılan çıktı (110 hadis inceleme bekliyor) | P 0,983 · R 0,582 | L3 |
| Aynı inceleme payında güven eşiği ile kapı, şema-only | Güven < 0,85: mention'ların %16,3'ü, 50 eşleşmeyen. Kapı: %9,2'si, 122 eşleşmeyen | Yönlendirme |
| Değer-alıntı kapısı, isnad-farkındalıklı (tüm hadis): 1.639 mention'ın 5'i eşleşmiyor | 3 işaretlendi; işaretlenen eşleşen mention yok | L3 |
| İncelemesiz kabul edilen çıktı, şema-only | P 0,985 · R 0,849 · F1 0,912 | L1 |
| LLM güven skorunun doğruyu yanlıştan ayırma gücü, şema-only | AUC 0,634 (n = 1.688) | Yönlendirme |
| İnceleme yükü, şema-only / isnad-farkındalıklı (tüm hadis) | 538 / 16 aday; incelemesiz commit 190 / 294 koşu (300 üzerinden) | HITL yükü |
| Maliyet, Claude Haiku 5.5 (2026-10-06 liste fiyatı), 1.000 hadis başına | 1,87 / 2,29 / 2,21 USD (şema-only / isnad tüm hadis / zincir başına) | Maliyet |
| Ad yazımı kimlik olsaydı (referans zincirleri: 2.150 mention geçişi, 740 kişi) | 964 anahtar; mention'ların %10,0'ı birden çok kişiyi kapsayan anahtarda; kişilerin %25,8'i birden çok anahtara bölünüyor; B-cubed P 0,941 · R 0,715 | L2, taban çizgisi |
| İki etiket kümesinin uyumu: Sanadset → İfta, metni eşleşen 253 hadis | M2 P 0,939 · R 0,979 · F1 0,959 [0,943 – 0,972]; M1 F1 0,931 | Referans |

"Yanlış" burada İfta etiketiyle M2'de eşleşmeyen mention demektir. Aynı dört koşul 50 pilot hadiste Sanadset
etiketlerine karşı da koşuldu (M2 F1: 0,892 / 0,828 / 0,945 / 0,919); kural tabanlı bölütleyici o 50 hadiste
ayarlandığı için bu sayılar test sonucu değildir. Claude Sonnet 5.5 ile 36 hadislik deneme bir yapılandırma
hatasını kaydeder, model karşılaştırması değildir. İkisinin ayrıntısı aynı sayfadadır.

Pilot dosyası notu: `wiki/sources/claude-science-results/pilot_sample.json` içindeki 327 `ref_nars` kaydının 17'si
`<NAR>` / `<IDF>` etiketi taşır. Pilotun raporladığı katı F1 0,628 etiketler temizlendiğinde aynen
üretilir; dosyadaki hâliyle puanlanırsa 0,595 çıkar. Gevşek F1 iki durumda da 0,879'dur
(`giraffegraph-core/evaluation/tests/test_scorer.py`, 2026-10-12).

## Ölçülmemiş olanlar

- İnsan altın standardı ve kodlayıcılar arası uyum (L1 mutlak değerleri)
- L2: sistemin ürettiği düğümlerin doğru kişiye bağlanması; ölçülen yalnız referans üzerindeki ad yazımı taban çizgisidir
- `NARRATED_FROM` ilişki düzeyi P/R; pilot ve motor deneyleri yalnız mention düzeyini ve sıra uyumunu ölçtü
- Property düzeyi şema sapması, muâsara / likâ / tabaka kural ihlalleri
- HITL: red oranı, doğrulanmış üçlü başına uzman saniyesi (kayıt altyapısı Core dalında var: `review_decisions.duration_ms`; hiçbir koşuda inceleme kararı verilmedi, veri yok)
- Model etkisi: 300 hadiste tek model ve tek effort düzeyi koşuldu (Claude Haiku 5.5, `low`); açık modeller koşulmadı
- Aynı koşulun tekrarları arasındaki oynaklık (her koşul bir kez koşuldu)
- Türkçe metin; telifsiz Türkçe tam isnad kaynağının varlığı
- Ezber kontrolü: model isnadı metinden mi çıkarıyor, eğitim verisinden mi hatırlıyor
- L4'ün tamamı: soru kümesi, graf vs RAG karşılaştırması
- L0: Sanadset ile kaynak derlemeler arasındaki fark oranı

## Önkoşullar (bunlar olmadan ölçüm yapılamaz)

| Önkoşul | Neden | Kaynak |
|---|---|---|
| Dil kararı: Arapça birincil mi | Altın standardın hangi metinden üretileceğini belirler | `wiki/sources/claude-science-results/03_revize_deney_protokolu.md` §1 |
| Etiketleme kılavuzu + iki kodlayıcı + kör atama tablosu | Altın standardın güvenilirliği | aynı belge §5 |
| İçerik-adresli karar hedefi (C3) | İnsan kararı aday UUID'sine bağlı kalırsa her yeniden çıkarımda etiketleme emeği sıfırlanır | `wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md` C3 |
| Hadis-kapsamlı kenar anahtarı (C5) | Aynı çiftin farklı hadislerdeki aktarımları tek kenara çöker; zincir düzeyi metrik ölçülemez | aynı belge C5, `giraffegraph-core/backend/src/app/infrastructure/persistence/neo4j/repositories.py` |
| Ravi otorite listesi ve lisansı | L2'nin referansı. Adaylar: İfta ravi profilleri (20.957), AR-Sanad ravi tablosu (18.298). İkisi de 2026-10-12'de indirildi; lisans beyanları kayıtlı, kaynaklardan alınmış yazılı izin kayıtlı değil | `wiki/sources/claude-science-results/03_revize_deney_protokolu.md` §1.3, `wiki/evaluation/related-work.md`, `data/README.md` |
| L4 soru kümesi (yapısal / yol-ağ / karar) | Graf katmanının RAG'a üstünlüğünün tek testi | aynı belge §3.3 |

## Kur'an verisi için

Kur'an metni sabit ve yapısaldır (114 sure, 6236 ayet); çıkarım sorusu hadisteki kadar ağır değildir.
Ağırlık L0'dadır: edisyon kimliği, mütercim atfı, karakter bütünlüğü ve kaynak onarılınca türetilmiş
artefaktların (embedding) yeniden üretilmesi. Kur'an'dan varlık ya da konu çıkarımı yapılırsa L1–L4
aynı yöntemle uygulanır.

## Rules

- MUST: raporlanan her sayı katmanını, referansını (gümüş / altın / kural) ve eşleşme kriterini taşır.
- MUST: gümüş standarda ya da platform etiketine karşı ölçülen değer "doğruluk" diye sunulmaz; o etiket
  kümesiyle uyum ve sistemler arası fark olarak sunulur.
- MUST: P, R ve F1 birlikte verilir. Özet olarak F0.5 kullanılırsa ham P/R yanında durur; pilotta
  bağlayıcı kısıt recall'dir.
- MUST: güven aralığı hadis düzeyinde hesaplanır; analiz birimi hadistir.
- MUST: "halüsinasyon oranı" tek sayı olarak verilmez; kaynakta olmayan mention, alıntıda olmayan değer
  ve kategori hatası ayrı raporlanır.
- SHOULD: L2'de birincil metrik over-merge oranıdır; iki ravinin yanlış birleşmesi zincirin hükmünü
  değiştirir, kaçan birleşme yalnız tekrar üretir.
- SHOULD: yönlendirme sinyali olarak LLM güven skoru yerine deterministik risk işaretleri kullanılır.

## Verification checklist

- [ ] Bu sayfadaki her pilot sayısı `wiki/sources/claude-science-results/pilot_summary.json` ya da `pilot_results.csv` ile eşleşiyor
- [ ] Motor deneyleri tablosundaki her sayı `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md`,
      ilgili `analysis-ifta/analysis.json` ya da `2026-10-12-identity-baseline/sixbooks300.json` ile eşleşiyor
- [ ] Yeni bir ölçüm eklendiyse katmanı, referansı, n ve tarihi yazıldı
- [ ] "Ölçülmemiş olanlar" listesinden çıkan madde "Ölçülmüş olanlar" tablosuna taşındı
- [ ] Protokolden ekipçe kabul edilen bölüm `wiki/decisions/` altında ADR'ye bağlandı

## Source anchors

- `wiki/sources/claude-science-results/03_revize_deney_protokolu.md` — metrik tanımları, ablation merdiveni, istatistik
- `wiki/sources/claude-science-results/08_pilot_raporu.md` — pilot yöntemi ve sınırları
- `wiki/sources/claude-science-results/pilot_isnad.py` — `norm`, `rule_parse`, `align`, `score_one`, `bootstrap_ci`
- `wiki/sources/claude-science-results/pilot_summary.json`, `pilot_results.csv`, `pilot_g3_crosstab.json`
- `wiki/sources/claude-science-context/11_evaluation_design_notes.md`
- `giraffegraph-core/evaluation/scorer.py`, `evaluation/README.md` — protokolün bağımsız uygulaması (M1 / M2, eşleştirme, bootstrap)
- `giraffegraph-core/evaluation/results/2026-10-12-rule-based-baseline/` — `run_report.json`, `score_proposed.json`, sistem ve referans JSONL
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/` — `compare-ifta.md`, koşu başına `run_report.json` ve `analysis-ifta/analysis.json`
- `giraffegraph-core/evaluation/results/2026-10-12-pilot50/compare-sanadset.md`, `2026-10-12-subset36/compare-ifta.md`
- `giraffegraph-core/evaluation/results/2026-10-12-identity-baseline/sixbooks300.json`
- `data/README.md` — dış etiketli veri, test kümelerinin kuruluşu, iki etiket kümesinin uyumu
- `giraffegraph-core/evaluation/annotation/` — etiketleme sayfası (50 hadis), kılavuz v0, uyum hesabı
- `giraffegraph-core/backend/src/app/application/use_cases/pipeline_management.py` — güven eşiğiyle yönlendirme
- `giraffegraph-core/backend/src/app/domain/shared/resolution.py` — merge key normalizasyonu

## Related docs

- `wiki/evaluation/engine-experiments.md`
- `wiki/evaluation/literature-map.md`
- `wiki/evaluation/related-work.md`
- `wiki/domains/hadith/isnad-pipeline.md`
- `wiki/project/overview.md`
- `wiki/sources/claude-science-context/08_hadith_domain_primer.md`

## Last updated

2026-10-12
