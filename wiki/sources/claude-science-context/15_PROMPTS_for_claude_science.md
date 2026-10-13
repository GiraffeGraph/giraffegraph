# 15 — Claude Science için promptlar

## A. "What do you work on?" kutusu (onboarding)

```
Bilgisayar mühendisliği lisans öğrencisiyim (Akdeniz Üniversitesi). Bitirme projem ve TÜBİTAK 2209-A başvurum GiraffeGraph: LLM'lerin yalnızca aday bilgi önerdiği; deterministik doğrulama ve insan onayının (human-in-the-loop) araya girdiği açık kaynak bir bilgi grafı motoru (Python/FastAPI, PostgreSQL + Neo4j). İlk vaka çalışması hadis isnad (ravi) zincirleri; alan uzmanı İlahiyat'tan. Asıl araştırma sorum daha genel: ham veriden (kod tabanı, hadis metni, Kur'an meali) halüsinasyona ve drift'e dayanıklı, insan tarafından doğrulanabilir bir bilgi katmanı ("wiki") kurmanın optimum yolu ne — KG, markdown veya başka bir temsil zorunlu değil. Yöntemler: LLM tabanlı bilgi çıkarımı, entity resolution, şema doğrulama, deney tasarımı (precision/recall, ablation, karışık etkili modeller). Ekteki dosyalar: TÜBİTAK formu, kod, web sitesi, önceki araştırma notlarım.
```

(Attach files: `claude-science-context/` klasöründeki tüm dosyalar. Önce `00_README_START_HERE.md`.)

## B. İlk görev: "Describe your own first task" kutusu veya ilk mesaj

```
Ekteki dosyalar projemin tüm bağlamı. Önce 00_README_START_HERE.md'yi, sonra numara sırasıyla hepsini oku. Önem sırası: (1) TÜBİTAK formu 02a/02b, (2) giraffegraph.com içeriği 03, (3) Cache & Ledger çalışmam 06a/06b, (4) kod ve boşluk denetimi 04a/05/14.

ASIL SORU: Ham veriden LLM destekli, halüsinasyon ve drift'e dayanıklı, insanca doğrulanabilir bir bilgi katmanı kurup güncel tutmanın OPTİMUM yolu nedir? Knowledge graph, markdown, mevcut mimari — hiçbiri zorunlu değil. Hadis isnad vakası (TÜBİTAK taahhütleri bağlayıcı) birincil kanıt; kod tabanı wiki'si ve Kur'an uygulaması transfer vakaları (01).

Senden derin, şüpheci, kanıta dayalı bir analiz istiyorum. Aşamalar:

1) DURUM TESPİTİ — Paketteki iddiaları kendin doğrula. 05'teki kod bulgularını 14'teki kaynakla çapraz kontrol et; yanlış olan varsa söyle. TÜBİTAK formundaki kaynakçayı birincil kaynaklardan doğrula (02b'de şüpheli işaretlenenler öncelikli): her referans için VAR/YOK/HATALI-KÜNYE + doğru künye.

2) TASARIM UZAYI — Temsil (KG / tipli md wiki / event-sourced ledger + türetilmiş görünüm / yalnız RAG / GraphRAG / bi-temporal KG / nanopublication) × doğrulama (deterministik kural / quote-grounding / NLI / LLM-judge / insan) × güncelleme (full rebuild / memoize / artımlı delta) matrisini çıkar. Her seçenek için 01'deki 9 optimumluk ekseninde literatür kanıtı ve maliyet ver. Literatür için 10'daki listeyi başlangıç al ama HER atfı doğrula; doğrulayamadığını açıkça belirt, asla uydurma.

3) SENTEZ HİPOTEZİNİ ÇÜRÜTMEYE ÇALIŞ — 12'deki "Kaynak + Karar Defteri + Türetilmiş Görünümler / dört olgu sınıfı" hipotezini en güçlü alternatiflere karşı sına. Tutuyorsa neden, tutmuyorsa neyle değiştirilmeli? Sonunda net bir OPTİMUM MİMARİ önerisi: alan-bağımsız çekirdek + alan-özgü eklentiler + bir kod tabanına ve Kur'an verisine nasıl aktarıldığı.

4) HADİS DENEY PLANI — TÜBİTAK hipotezlerini (H1–H4) ve taahhütlerini (K-1..K-5) koruyarak; 02b ve 11'deki metodoloji eleştirilerini değerlendir ve revize bir deney protokolü yaz: ablation merdiveni, metrik tanımları (eşleşme kriterleri dahil), altın standart ve kör protokol, istatistik (karışık etkili modeller, bootstrap, güç analizi/simülasyonu ile 500 hadisin yeterliliği), veri kaynağı ve dil kararı (Türkçe meallerde isnad kısaltılmış mı? Sanadset/SemanticHadith/ravi veri setlerinin varlığını, lisansını, uygunluğunu kontrol et), veri sızıntısı (modellerin isnad ezberi) kontrolü.

5) YOL HARİTASI — 05'teki boşlukları önceliklendir; 6 aylık, 2-3 kişilik lisans ekibine gerçekçi bir iş planı (iş paketi → çıktı → başarı ölçütü). Minimum uygulanabilir sürüm vs ideal sürüm ayrımı. Site ve form arasındaki tutarsızlıklar için düzeltme önerisi.

6) YAYIN — Katkıların hangileri özgün, hangileri değil; gerçekçi venue önerileri (lisans ekibi için), makale iskeleti.

Mümkünse KÜÇÜK BİR PİLOT çalıştır: erişilebilir açık bir hadis veri setinden ~20-50 hadis al; (a) deterministik isnad ayrıştırıcı (sîga lafızları + isim bölme) ile (b) bir LLM çıkarımını karşılaştır; ravi mention çıkarımında precision/recall ve tipik hata türlerini raporla. Pilot yapamıyorsan nedenini yaz ve protokolünü ver.

Kurallar: Türkçe yaz, teknik terimler İngilizce kalabilir. Doğrulanmamış her sayıyı/atfı [UNVERIFIED] ile işaretle. Emin görünen uydurma yerine dürüst boşluk tercih et. Bana hak verme eğiliminden kaçın; zayıf noktaları sert söyle. Çıktıları ayrı dosyalar olarak üret: (1) yönetici özeti (1 sayfa), (2) tasarım uzayı ve optimum mimari raporu, (3) revize deney protokolü, (4) doğrulanmış kaynakça (BibTeX), (5) önceliklendirilmiş kod değişiklik listesi, (6) 6 aylık iş planı, (7) açık sorular (13) için önerilerin.
```

## C. Takip promptları (sırayla, ihtiyaç halinde)

1. **Derinleştirme (mimari):**
```
Önerdiğin optimum mimari için GiraffeGraph Core'a (14) somut veri modeli değişikliğini yaz: decision_events ve extraction_records tabloları (alanlar, anahtarlar, indeksler), içerik-adresli hedef (content-addressed target) tanımı ve yeni bir model/prompt ile yeniden çıkarımda eski insan kararlarının nasıl yeniden uygulanacağının algoritması (bulanık span eşleme dahil) ve rebuild(S, D, P) prosedürü. Neo4j isnad modeli (Transmission reifikasyonu vs hadis-kapsamlı kenar) için karşılaştırma ve Cypher örnekleri.
```

2. **Derinleştirme (ER):**
```
Hadis ravi entity resolution'ı için otorite-linking tasarımı yap: aday üretimi (blocking), özellikler (isim bileşenleri — ism/nesep/künye/nisbe, transliterasyon düzlemleri, zincir komşuluğu, tabaka), skorlayıcı (kural + Fellegi-Sunter + LLM), eşik ve HITL yönlendirme; over-merge'i asimetrik cezalandıran metrik ve eşik seçimi. H4'ün (≥%50 duplicate azalma) mevcut baz çizgiye (05 #7) göre sınanma protokolü.
```

3. **Transfer deneyi (kod):**
```
Aynı mimariyi açık kaynak bir kod tabanında sınamak için hafif bir deney tasarla (07, 11 §5): repo seçimi kriterleri, soru seti (yapısal vs niyet/karar soruları), koşullar (grep-only ajan / LLM-üretimli wiki / anchor+linter wiki / ledger+türetilmiş görünüm), git geçmişinden drift ölçümü, maliyet. Bitirme süresine sığacak minimum versiyon.
```

4. **Kırmızı takım:**
```
Bir TÜBİTAK hakemi ve bir EMNLP workshop hakemi gözüyle projeyi ve senin önerini acımasızca eleştir. Reddettirecek en olası 10 sebep ve her biri için önlem.
```
