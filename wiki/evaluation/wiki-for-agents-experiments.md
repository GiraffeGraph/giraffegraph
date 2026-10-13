# LLM'in tuttuğu wiki ajana ne kazandırır: deneyler

## Purpose

"Bir LLM ajanı için neyi saklamak gerekir?" sorusunun ölçülmüş cevabını tutmak. 30 Eylül paketinin
hiç koşulmamış iki öngörüsünü (kod vakası: niyet soruları yalnız karar varken cevaplanır; karar defteri
ve arama, belgeli wiki'den kötü değildir) ve bu gece denenen "tanıklı wiki" fikrini sınayan deneylerin
sonucudur.

## Scope

- In: ajan soru-cevap deneyi (belge türü × düzen × araç bütçesi), belge-kod atıflarının git geçmişindeki
  ömrü, wiki'nin kendi sayılarının izlenebilirliği, okuma anında doldurulan çerçeveler, beş ajanla
  yapılan fikir turu, emsal taraması
- Out: hadis çıkarımı ve kimlik deneyleri (`wiki/evaluation/engine-experiments.md`,
  `wiki/evaluation/decision-ledger-experiments.md`), denemenin metni (`cache-and-ledger/README.md`)

## Statü

Keşif aşaması (2026-10-13). Tek gecede, ajanın kendi kararlarıyla yürüttüğü bir oturumda üretildi; ekip
ve danışman görmedi. Betikler ve çıktılar `cache-and-ledger/data/` altındadır; o klasörün bir kopyası
`data/cache-and-ledger-backup/` altında özel veri reposundadır. Yorumlar öneridir.

## BLUF

1. **Karar, saklanması gereken tek şeydir.** Kodda yazmayan "neden" soruları belgesiz %0–4, karar
   defteriyle %88–100 doğru cevaplandı.
2. **Yeterince arama hakkı olan ajan, yapıyı koddan okur.** 14 araç çağrısıyla yapısal sorular belgesiz
   %94–98 doğru; taze, bayat, tanıklı, haritalı hiçbir belge doğruluğu değiştirmedi. Belgeyi bağlama
   koymak istem token'ını 2–4 katına çıkardı.
3. **Belge ancak arama kıtken işe yarar.** 2 araç çağrısında belgesiz %31, taze belgeyle %88
   (+0,56 [0,38 – 0,75]); 4 çağrıda fark +0,23'e iner; 14 çağrıda sıfırdır.
4. **Bayat belge, değişen olguda yarı yarıya yanıltır ama yalan söyletmez.** 2 çağrıda değişen sorularda
   taze %96, bayat %50. Bayat cevabı kesin diye sunma oranı %0–4; "belge böyle diyor, doğrulayamadım"
   diye aktarma %21–33.
5. **Tanık notu işe yaramadı.** Bayat bölümlerin üstüne makinenin koyduğu "dayandığı kod değişti" notu
   hiçbir kolda ölçülebilir fark yaratmadı; her bölüme konan sıradan bir uyarıdan da ayrışmadı. Bu
   gecenin ana fikri bu ölçekte tutmadı.
6. **Dosya düzeyinde tanık bir ayda ölür.** Sekiz açık repoda belgenin atıf verdiği dosyaların %54'ü
   bir ay sonra bayt bayt aynı; 24 ayda %10. Sembol bloğu düzeyinde %98 ve %62.
7. **"Cevabı değil sorguyu sakla" fikri tutmadı.** Olguları koddan okuma anında doldurulan boşluklu
   cümleler, 2 çağrıda değişen sorularda 0,625 verdi; aynı cümlelerin eski koddan doldurulmuş hâli
   0,667, bayat sayfa 0,500, baştan yazılmış sayfa 0,958. Sorgu bilinen bir olgunun değerini
   tazeler; yazıldığında var olmayan davranışı bulamaz.
8. **Beş ajana aynı soru üç sırayla soruldu; fikri sıra değil model belirledi.** On beş oturumun on
   biri "çalıştırılabilir bir şey sakla" ailesine düştü. Sonnet, Codex ve Antigravity üç sırada da
   kendi fikrini tekrarladı.

Deneme (`cache-and-ledger/README.md`) haklı çıktı: türetilebilen şeyi saklama, kararı sakla. Eklenen
iki şey var. Bir sınır koşulu: türetmek pahalıysa (arama hakkı azsa) saklanan türetim değer kazanır.
Bir de olumsuz sonuç: eski bir sayfayı betikle tazelemenin denenen dört yolu da (tanık notu, yalnız
işaret, okuma anında doldurma, eklenenlerin listesi) güncel kodu okuyan bir ajanın baştan yazdığı
sayfaya yaklaşmadı; türetilmiş sayfa yamanmaz, yeniden üretilir.

## Tasarım: ajan soru-cevap deneyi

Claude Haiku 5.5 (effort `low`), üç salt-okunur araç (`list_dir`, `read_file`, `grep`),
`giraffegraph-core` backend kaynağı (141 dosya, 16.923 satır, commit `bfb0f9c`). 36 soru, sınıf başına
12: **değişmeyen** (cevabı 2026-04-05 commit'i ile bugün aynı yapısal olgu), **değişen** (cevabı Ekim
yeniden yazımında değişen yapısal olgu), **karar** (cevabı ADR ve kural gerekçelerinde olan, kodda
olmayan "neden"). Soruları ve anahtarı, sınanan belge sayfalarını görmeyen ayrı bir ajan koda bakarak
yazdı.

Koşullar yalnız `docs/` klasörünün içeriğiyle ayrılır; talimat ve araçlar aynıdır:

| Koşul | `docs/` içeriği |
|---|---|
| belgesiz | "belge yok" notu |
| karar | 30 kararlık defter (gerekçe ve reddedilen seçenek; türetilebilir olgu yok) |
| taze | karar + güncel koddan yazılmış davranış sayfası (1.754 kelime) |
| bayat | karar + nisan commit'inden aynı talimat ve aynı başlıklarla yazılmış sayfa (1.981 kelime) |
| bayat + tanık | bayat sayfa; her bölümün altında dayandığı kod dilimlerinin değişip değişmediği |
| bayat + sıradan uyarı | bayat sayfa; her bölümün altında aynı "bayat olabilir, doğrula" cümlesi |
| harita | karar + `ast` ile üretilmiş dosya → sınıf / işlev listesi |
| yalnız işaret | karar + sayfanın başlıkları ve kod dilimleri; hiçbir iddia yok (216 kelime) |

İki düzen: **çekme** (ajan `docs/` klasörünü kendisi açar) ve **itme** (belgeler sistem istemine de
konur; ajan bağlam dosyalarının yüklenme biçimi). Kollar: talimatta "belge bayat olabilir" cümlesi var /
yok; araç bütçesi 14 / 4 / 2. Hücre başına 2 tekrar, toplam 2.880 koşu. Puanlama aynı modelle, yazılı
anahtara karşı ve koşulu görmeden yapıldı; analiz birimi sorudur, aralıklar sorular üzerinde
bootstrap'tir.

Tanık kontrolü: bir kod dilimi, sayfanın yazıldığı ağaçtaki metni güncel ağaçta aynı dosyada birebir
geçiyorsa "değişmemiş" sayılır. Bayat sayfanın 10 bölümünün 9'unda en az bir dilim değişmiştir.

## Sonuç 1: tam araç bütçesi (14 çağrı)

| `docs/` | Yapısal, çekme | Yapısal, itme | Karar, çekme | Karar, itme | Yapısal soru başına istem token'ı, itme |
|---|---|---|---|---|---|
| belgesiz | 0,979 [0,94 – 1,00] | 0,938 [0,85 – 1,00] | 0,042 | 0,000 | 21.843 |
| karar | 0,938 | 0,979 | 1,000 | 0,958 | 45.343 |
| karar + taze | 0,979 | 0,958 | 1,000 | 0,917 | 57.825 |
| karar + bayat | 0,896 | 1,000 | 0,875 | 0,958 | 75.443 |
| bayat + tanık | 0,938 | 0,938 | 0,958 | 0,958 | 90.303 |
| bayat + sıradan uyarı | 0,979 | 0,979 | 0,958 | 0,958 | 76.700 |

Çekme düzeninde ajan 432 yapısal koşunun hiçbirinde `docs/` klasörüne bakmadı; doğrudan `grep` ile
koda gitti. Karar sorularında soru başına 2,0–2,5 kez belgeye baktı. Talimattan "bayat olabilir"
cümlesi çıkarıldığında yapısal sonuç değişmedi (0,94 – 0,98).

Yapısal sorulardaki 36 yanlışın 26'sı iki sorudandır; anahtar o sorularda doğru cevapların çoğunun
yazmadığı bir ayrıntıyı (HTTP durum kodu, "inceleme öğesi" ifadesi) şart koşar. Koşullar arası farklar
bu gürültünün içindedir.

## Sonuç 2: kıt araç bütçesi (itme düzeni, yapısal sorular)

| `docs/` | 2 çağrı: hepsi | değişmeyen | değişen | 4 çağrı: hepsi | değişmeyen | değişen |
|---|---|---|---|---|---|---|
| belgesiz | 0,312 [0,15 – 0,48] | 0,375 | 0,250 | 0,750 [0,60 – 0,88] | 0,708 | 0,792 |
| taze sayfa | 0,875 [0,75 – 0,98] | 0,792 | 0,958 | 0,979 [0,94 – 1,00] | 0,958 | 1,000 |
| taze, yalnız işaret | 0,604 [0,44 – 0,75] | 0,542 | 0,667 | 0,833 | 0,833 | 0,833 |
| bayat sayfa | 0,688 [0,50 – 0,85] | 0,875 | 0,500 | 0,812 | 0,917 | 0,708 |
| bayat + tanık | 0,708 [0,58 – 0,83] | 0,833 | 0,583 | 0,792 | 0,875 | 0,708 |
| bayat + sıradan uyarı | 0,667 [0,48 – 0,83] | 0,917 | 0,417 | 0,833 | 0,917 | 0,750 |
| bayat, yalnız işaret | 0,500 [0,33 – 0,67] | 0,500 | 0,500 | 0,792 | 0,750 | 0,833 |

Belgesize göre eşli fark, 2 çağrı: taze +0,56 [0,38 – 0,75], bayat +0,38 [0,13 – 0,63]. 4 çağrı:
taze +0,23 [0,10 – 0,38], bayat +0,06 [−0,10 – 0,23].

Okuma:

- Bayat sayfa toplamda yine de belgesizden iyidir, çünkü olguların yarısı değişmemiştir ve sayfa
  ajanı doğru dosyaya götürür. Değişen olgularda taze sayfanın yarısı kadar doğrudur.
- Tanık notu ile sıradan uyarı ve notsuz bayat sayfa arasındaki farklar (0,58 / 0,42 / 0,50; 12 soru)
  birbirinin aralığı içindedir.
- İddiasız "yalnız işaret" sayfası tam sayfanın kazancının yaklaşık yarısını verir (dokuzda bir boyutla)
  ve bayat cevabı aktarma davranışını neredeyse hiç üretmez (%0–8).
- Kod yolları ajanın yazıldığı gibi açamayacağı biçimde verildiğinde (çalışma klasörüne göre değil,
  `src/app/` altına göre) bayat sayfa 2 çağrıda değişen sorularda 0,083'e düştü; belgesiz 0,292'dir.
  Bu karşılaştırma planlı değildi: iki kol arasında yol biçimi düzeltilirken ortaya çıktı.

## Sonuç 3: tanıkların ömrü (açık repolar)

Sekiz açık GitHub reposu (bevy, wasmtime, zulip, transformers, argo-cd, tektoncd/pipeline, desktop,
playwright), 24 ay önceki commit'te Markdown belgelerinin atıf verdiği 1.804 kod yolu (367 belge
dosyası); bunların 122'sinde aynı satırda dosyada geçen bir sembol vardır. Yüzde olarak sağ kalan:

| Ay | Yol hâlâ var | Dosya bayt bayt aynı | Sembol bloğu aynı |
|---|---|---|---|
| 1 | 97,9 | 54,2 | 98,4 |
| 3 | 96,8 | 44,1 | 96,7 |
| 6 | 90,6 | 25,6 | 84,4 |
| 12 | 87,6 | 18,0 | 77,9 |
| 24 | 82,8 | 10,4 | 61,5 |

12 ayda atıfların %63,2'sinde dosya değişti ama belge cümlesi birebir aynı kaldı (sembol bloğunda
%17,2). Bu, sessiz bayatlığın üst sınırıdır: dosya değişikliklerinin çoğu cümleyi yanlış yapmaz.
Sembol sütunu 122 atıfa dayanır ve kaba bir blok kuralı kullanır; repo başına sonuçlar anekdottur.

Sonuç: dosya özeti düzeyinde bir tanık neredeyse her şeyi bayat gösterir, bilgi taşımaz. İşaretin
kendisi (yol) içeriğinden çok uzun yaşar.

## Sonuç 4: wiki'nin kendi sayıları izlenebiliyor mu

Bu wiki'nin sayı içeren 14 yaşayan sayfasındaki 968 sayı (bu sayfa yazılmadan önceki durum), sayfanın
atıf verdiği dosyalardaki sayılarla karşılaştırıldı (sayfanın hassasiyetinde yuvarlayarak). 888'i (%91,7) atıf verilen bir dosyada bulundu.
Bulunmayan 80 sayı iki türdür: sayfayı yazan modelin yaptığı dönüşümler (işaret çevirme, fark ve oran
hesabı) ve dosyası çalışma alanında olmayan makale sayıları. Bulunmayan sayılar arasında elle bakılan
örneklerde yanlış çıkmadı; tamamı elle denetlenmedi. Büyük kaynak dosyalarında rastlantısal eşleşme
olabileceği için %91,7 üst sınırdır.

## Sonuç 5: okuma anında doldurulan çerçeveler

Fikir: cümleyi sakla, içindeki olguyu saklama. Cümlede isim, sayı ya da değer bulunamaz; her olgu bir
boşluktur ve boşluk `yol.py::Sınıf.metot` biçiminde bir seçici ile `ast` üzerinde çalışan bir
indirgeyiciden oluşur (`cache-and-ledger/data/agent-qa/cloze.py`). Yalnız `4279c98` ağacını ve on
bölüm başlığını gören, soruları görmeyen bir ajan 58 cümle ve 95 boşluk yazdı. `bfb0f9c` ağacında 95
boşluğun 92'si çözüldü (biri başka dosyada bulundu), 3 cümle geri çekildi.

İtme düzeni, kök yollu, yapısal 24 soru, ikişer tekrar (384 koşu):

| `docs/` | 2 çağrı: hepsi | değişmeyen | değişen | 4 çağrı: hepsi | değişmeyen | değişen |
|---|---|---|---|---|---|---|
| bayat sayfa (Sonuç 2) | 0,688 | 0,875 | 0,500 | 0,812 | 0,917 | 0,708 |
| bayat sayfa + eklenen semboller | 0,771 [0,58 – 0,92] | 0,958 | 0,583 | 0,875 | 0,875 | 0,875 |
| çerçeveler, eski koddan dolu | 0,708 [0,54 – 0,85] | 0,750 | 0,667 | 0,854 | 0,875 | 0,833 |
| çerçeveler, güncel koddan dolu | 0,792 [0,65 – 0,92] | 0,958 | 0,625 | 0,896 | 0,958 | 0,833 |
| çerçeveler, güncel + eklenen semboller | 0,750 [0,60 – 0,88] | 0,917 | 0,583 | 0,917 | 0,917 | 0,917 |
| taze sayfa (Sonuç 2) | 0,875 | 0,792 | 0,958 | 0,979 | 0,958 | 1,000 |

"Eklenen semboller": `4279c98`'de olmayıp `bfb0f9c`'de olan 201 sınıf, fonksiyon ve metodun dosya
başına ad:satır listesi (320 kelime), betikle üretilir (`added_symbols.py`).

Değişen 12 soruda, 2 çağrıda eşli farklar: güncel dolu çerçeve − bayat sayfa +0,13 [−0,13 – 0,42];
güncel dolu − eski dolu −0,04 [−0,25 – 0,17]; taze sayfa − güncel dolu +0,33 [0,08 – 0,63].

Okuma:

- Öldürme ölçütleri koşudan önce yazıldı: değişen sorularda 0,667 ya da altı (yalnız işaret sayfasının
  düzeyi), ya da bayat sayfaya karşı aralığın sıfırı içermesi. İkisi de gerçekleşti.
- Boşluğu güncel koddan doldurmak, eski koddan doldurmaya göre değişen sorularda fark yaratmadı.
  Kaçırılan sorular (C01, C09, C12; kısmen C03, C07, C10) çerçeveler yazıldıktan sonra eklenen
  denetim ve dalları sorar; hiçbir boşluk oraya bakmaz.
- Eklenenlerin adını vermek 2 çağrıda açığı kapatmadı; 4 çağrıda bayat sayfaya eklendiğinde değişen
  sorularda 0,875'e karşı 0,708 (+0,17 [0,00 – 0,38]), aralık sıfıra değiyor.
- Taze sayfaya uzaklık ölçülmüştür; bayat sayfayla eşitlik ölçülmemiştir (12 soru, geniş aralık).

## Sonuç 6: beş ajan, üç sıra

Çerçeve fikri bir fikir turundan çıktı. Beş ajana (Claude Sonnet, Claude Opus, Codex `gpt-6.1-sol`,
Pi `gpt-5.6-sol`, Antigravity `gemini-3.8-flash-high`; üç model ailesi) aynı görev metni verildi:
bilgi grafiği ve markdown wiki dışında bir saklama biçimi öner, on ölçülmüş olguya uy, yasak listeye
girme. Sonra her ajana aynı metin, olguların ve yasak listenin sırası tohumlu karıştırmayla
değiştirilerek iki ayrı oturumda daha verildi. On beş oturumun tablosu ve tam cevaplar:
`cache-and-ledger/data/idea-sessions/README.md`.

- "Çalıştırılabilir" ölçütü (ana fikir, okuma anında güncel kaynağa karşı çalışan bir program, sorgu
  ya da test saklar) karıştırılmış oturumlar okunmadan önce yazıldı. On karıştırılmış oturumun yedisi
  bu aileye düştü (okumadan yazılan tahmin: en az yedi); özgün sırayla birlikte on beşte on bir, biri
  kısmen.
- Sıra neredeyse hiçbir şeyi değiştirmedi. Sonnet üç kez sonda/tarif, Codex üç kez karşıolgusal deney,
  Antigravity üç kez hash'li iddia defteri önerdi. Yalnız Opus üç farklı fikir verdi.
- Karıştırma yalnız sırayı değiştirir; olguların ve yasak listenin içeriği sabitti.
- Sınanmayan iki fikir ölçümlere dayanıyor: bilgiyi ajanın zaten grep attığı ağacın içine tek satır
  olarak koymak (Sonuç 1: ajan `docs/` klasörünü 432 koşuda hiç açmadı) ve yalnız "yalnızca / hiç /
  tam N" iddialarını sorgu olarak saklayıp taban kümeye göre farkı vermek.

## Emsal

Bir alt ajan 2026-10-13'te birincil kaynaklardan çekti; künyeler ayrıca doğrulanmadı.

| Konu | En yakın iş | Buradaki fark |
|---|---|---|
| Bağlam dosyası ajana yarar mı | Gloaguen vd. 2026, arXiv:2602.11988: LLM üretimi AGENTS.md başarıyı artırmıyor, maliyeti %20 artırıyor | Aynı yön. Bilerek bayat belge ve yalnız karar defteri koşulu için kontrollü çalışma bulunmadı |
| Deterministik olmayan görevde izle doğrulama | Mokhov, Mitchell, Peyton Jones 2018, DOI 10.1145/3236774 (§6.3) | Denemenin "LLM deterministik değil, önbellek olmaz" itirazı erken kesme için geçerli, girdi izini doğrulamak için değil |
| İddiaya içerik özeti bağlamak | Hsu vd. 2026 (EA-Graph), arXiv:2608.04278; GitHub Copilot Memory (2026) | Mekanizma var. Buradaki ölçüm, bölüm düzeyinde notun ajan davranışını değiştirmediğini gösteriyor |
| Belgedeki eski kod atıfları | Tan, Wagner, Treude 2024, DOI 10.1007/s10664-023-10397-6: projelerin %28,9'unda güncel olmayan atıf | Onlar silinmiş atıfı sayar; Sonuç 3 içeriği değişmiş atıfı sayar |
| İstem önbelleği ve eklemeli bağlam | Manus bağlam mühendisliği yazısı (2025); Lumer vd. 2026, arXiv:2601.06007 | Biliniyor; burada ölçülmedi |

## Sınırlar

- Tek repo (17 bin satır), tek model, sınıf başına 12 soru, hücre başına 2 tekrar. Büyük bir kod
  tabanında arama pahalılaşır; "kıt bütçe" kolu bunu taklit eder, yerini tutmaz.
- Puanlayıcı aynı model ailesidir; elle yalnız yanlış sayılan yapısal cevaplar incelendi.
- Tanık notu bölüm düzeyindedir. İddia düzeyinde tanık sınanmadı.
- Taze ve bayat sayfayı ajanlar yazdı; insan yazımı belge sınanmadı.
- Soruların hepsi en çok beş dosya okuyarak cevaplanabilir türdendir.

## Rules

- MUST: "belge ajanı yanıltır" ya da "belge işe yaramaz" cümlesi koşulsuz yazılmaz; araç bütçesi ve
  olgunun değişip değişmediği belirtilir. Gerekçe: sonuç bütçeye göre işaret değiştirir (Sonuç 1 ve 2).
- MUST: tanık notu "işe yarıyor" diye sunulmaz. Gerekçe: bölüm düzeyinde ölçülebilir etkisi çıkmadı.
- MUST: "sorguyu sakla" ya da "okuma anında doldur" bir çözüm diye sunulmaz. Gerekçe: Sonuç 5'te kendi
  ölçütünü geçemedi; sınır, yazıldığında var olmayan davranışı kapsayamamasıdır.
- SHOULD: bu çalışma alanında ajan için yazılan belge karar ve gerekçe taşır; kodun ne yaptığını
  anlatan cümle yazılmaz, yol çapası yazılır. Gerekçe: Sonuç 1, 2 ve 3.
- SHOULD: yol çapaları ajanın çalıştığı köke göre yazılır (`wiki/architecture/context-quality.md`
  kuralı); Sonuç 2'deki yol biçimi gözlemi bu kuralın ölçülmüş gerekçesidir.

## Source anchors

- `cache-and-ledger/data/agent-qa/README.md` — deneyin İngilizce özeti ve yeniden üretim komutları
- `cache-and-ledger/data/agent-qa/analysis.json` — hücre başına doğruluk, aralık, eşli fark, tutum payları
- `cache-and-ledger/data/agent-qa/results.json`, `build.json`, `questions.json`, `decisions.md`, `inputs/`
- `cache-and-ledger/data/agent-qa/run_agent_qa.py`, `analyse.py`; ham koşular `runs.tar.gz`
- `cache-and-ledger/data/agent-qa/cloze.py`, `added_symbols.py`, `inputs/frames-earlier-commit.json` — Sonuç 5
- `cache-and-ledger/data/idea-sessions/README.md`, `brief.md`, `shuffle_brief.py`, `outputs/` — Sonuç 6
- `cache-and-ledger/data/witness-survival/REPORT.md`, `results.json`, `witness_survival.py` — Sonuç 3
- `cache-and-ledger/data/explore-number-check.py`, `number-check-wiki.json` — Sonuç 4
- `wiki/sources/claude-science-context/12_synthesis_hypothesis_source_ledger_views.md` §5 (T4) ve
  `wiki/sources/claude-science-results/02_tasarim_uzayi_ve_optimum_mimari.md` §4 (Ç4) — sınanan öngörüler

## Verification checklist

- [ ] `python3 -I cache-and-ledger/data/agent-qa/analyse.py <koşu klasörü> cache-and-ledger/data/agent-qa/questions.json out.json` çıktısı Sonuç 1 ve 2 tablolarıyla aynı (koşu klasörü `runs.tar.gz` açılarak kurulur)
- [ ] Sonuç 3 tablosu `cache-and-ledger/data/witness-survival/results.json:pooled` ile aynı
- [ ] `python3 -I cache-and-ledger/data/explore-number-check.py . wiki --skip wiki/sources/claude-science --skip wiki/literature --skip wiki/thesis --skip wiki/_templates` özet satırı Sonuç 4 ile aynı

## Related docs

- `wiki/evaluation/decision-ledger-experiments.md`
- `wiki/architecture/context-quality.md`
- `wiki/project/open-decisions.md`
- `wiki/sources/README.md`

## Last updated

2026-10-13
