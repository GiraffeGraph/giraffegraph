# TÜBİTAK 2209-A taahhütleri: eldeki kanıt

## Purpose

Formdaki her katkı, hipotez ve hedef için bugün elde ne olduğunu ve neyin eksik olduğunu tek yerde
tutmak. Bir plan ya da rapor yazılırken taahhüdün karşılanıp karşılanmadığı buradan okunur.

## Scope

- In: K-1…K-5 katkıları, H1…H4 hipotezleri, Hedef 1–5; her birinin eldeki kanıtı ve eksiği; eşiklerin
  hangi ölçüme dayandığı; formun bilerek kapsamadığı işler
- Out: formun tam metni (`wiki/thesis/tubitak/form.md`), ölçümlerin ayrıntısı
  (`wiki/evaluation/engine-experiments.md`, `wiki/evaluation/decision-ledger-experiments.md`), sıradaki
  işler (`wiki/project/roadmap.md`)

## Statü

Form taslaktır ve gönderilmedi (proje sahibinin beyanı, 2026-10-13). Metin tek proje çerçevesiyle
yazılmıştır (`wiki/project/overview.md`, "Çerçeve"); ekip ve danışman okumadı. Eşikler öneridir;
gönderildiği gün bağlar. Başvuru ekibi bitirme projesi ekibidir: Yahya Efe Kuruçay, Deniz Büyükşahin,
Alperen Ulukaya.

2026 I. dönem için hazırlanmış taslak donmuş pakette durur
(`wiki/sources/claude-science-context/02a_TUBITAK_2209A_form_original.pdf`); bu sayfa onu izlemez.

Aşağıdaki "Eldeki" sütunlarında referans İfta platform etiketi, AR-Sanad etiketi ya da Sanadset kural
etiketidir; hiçbiri insan altın standardı değildir ve hiçbir koşuda bir insan karar vermedi.

## Katkılar

| Kod | Taahhüt (form) | Eldeki | Eksik |
|---|---|---|---|
| K-1 | 300 hadisin iki bağımsız kodlayıcıyla etiketlenmesi, uzman hakemliği, uyum ve süre raporu | Etiketleme kiti: kılavuz, etiketlenecek hadis tablosu, tabloyu referansa çeviren betik (`giraffegraph-core/evaluation/annotation/`). Kodlayıcılara gönderilmedi | Etiketlerin tamamı; 50 hadislik kalibrasyon turu; uyum ölçümü |
| K-2 | Dört koşul × en az üç model (biri açık ağırlıklı) × iki tekrar, insan etiketine karşı | 1 model (Claude Haiku 5.5, effort `low`) × dört koşul × 1 koşu × 300 hadis, İfta etiketine karşı. İkinci model denemesi yapılandırma hatasıyla sonuçlandı | İnsan etiketi; iki model; tekrarlar |
| K-3 | Referansı üretmemiş bir inceleyicinin kuyruğun tamamına karar vermesi; inceleme sonrası P / R, red oranı, karar başına süre | Kayıt altyapısı: `review_decisions` (kim, ne zaman, süre). Hiçbir koşuda karar verilmedi | Ölçümün tamamı |
| K-4 | Motorda kimlik karar defteri: karar içeriğe bağlanır, kapsam çelişkide daralır, tabaka ve vefat yılı kuralı | Motor dışı benzetim ve testleri (`giraffegraph-core/evaluation/identity_ledger.py`); hedef örtüşmesi ölçümü (`decision_reapplication.py`). Motorda karar aday kimliğine bağlıdır; alan kuralı kancası yoktur | E-1…E-4'ün tamamı; gerçek kararlarla ölçüm |
| K-5 | Kod ajanı deneyinin başka aileden bir modelle ve ikinci bir kod tabanıyla tekrarı | Tek kod tabanı, iki model (aynı aile), 5.520 koşu (`data/cache-and-ledger/data/agent-qa/`) | Başka aileden model; ikinci kod tabanı ve soru kümesi |

## Hipotezler

| Kod | Form metni | Ön çalışma ölçümü | Eşiğin dayanağı |
|---|---|---|---|
| H1 | Şema-only koşulda değer-alıntıda kontrolü, insan etiketiyle eşleşmeyen önerilerin en az %60'ını işaretler ve aynı inceleme payında güven skorundan fazlasını bulur | 145 eşleşmeyen önerinin 122'si (%84); güven skoru benzer payda 50 (300 hadis, İfta etiketi) | Ölçümün altında; etiket değişince pay değişebilir. Hadis dışında aynı kontrol 303'te 53 buldu (BC5CDR) |
| H2 | İncelemesiz kabul edilen önerilerde hata oranı ham öneriye göre en az %50 düşer | Precision 0,914 → 0,985; hata 0,086 → 0,015 (300 hadis, şema-only, İfta etiketi) | Göreli yazılmıştır: baz çizgi 0,914 iken mutlak artışın tavanı +0,086'dır |
| H3 | İnceleyicinin reddetme ya da düzeltme olasılığı, kontrolün işaretlediği adaylarda anlamlı biçimde yüksektir (aday düzeyinde lojistik model, hadis düzeyinde kümelenmiş, p < 0,05) | Veri yok | Aday düzeyinde yazılmıştır: model düzeyinde birkaç gözlemle korelasyon zayıf kalır |
| H4 | Kapsamı çelişkide daralan defter, öğrenci ve ada sabit deftere göre en az %20 daha az soru sorar; sessiz hata farkı geçiş başına 0,02'yi aşmaz | Benzetim: %48 daha az soru, fark 0,008 (AR-Sanad, 150.904 geçiş); %32 ve 0,003 (İfta, 205.514 geçiş) | Ölçümün altında; 300 hadiste defter soğuk başlar, yeniden kullanım daha azdır |

## Hedefler

| Hedef | Ölçüt (form) | Eldeki |
|---|---|---|
| 1 Referans kümesi | İki kodlayıcının karşılıklı F1 değeri (gevşek) ≥ 0,85; hadis başına süre | Yok. İki hazır etiket kümesi ortak hadislerinde F1 0,959 verir; insan-insan uyumu ölçülmedi |
| 2 Ölçüm | P / R / F1, katı ve gevşek, hadis düzeyinde bootstrap; H1 ve H2 | Betikler hazır ve platform etiketiyle koşuldu (`giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/`) |
| 3 İnceleyici | İnceleme sonrası P / R, red oranı, karar başına medyan süre; H3 | Yok |
| 4 Karar defteri | Testler gerçek veritabanlarında geçer; soru ve sessiz hata; H4 | Benzetim (`giraffegraph-core/evaluation/results/2026-10-13-identity-ledger/`) |
| 5 Açık bilim | Motor, betikler ve etiketler açık lisansla; en az bir bildiri ve ön baskı | Kod özel proje reposundadır; LICENSE dosyası yok. Makale taslağı `wiki/thesis/paper/` altında, gönderilmedi |

## Formun kapsamadığı işler

Form şunlara söz vermez; her biri için gerekçe ölçümdedir.

| İş | Neden kapsam dışı |
|---|---|
| En az 8 varlık ve 10 ilişki tipli hadis ontolojisi | İsnad şablonu 2 düğüm ve 2 ilişki tipiyle ölçülen işi görür (`giraffegraph-core/backend/src/app/infrastructure/template/catalog.py:ISNAD_TEMPLATE_SCHEMA`); altı kitabın ontolojisi yayımlanmıştır (`wiki/evaluation/related-work.md`) |
| Dizi benzerliğiyle (Levenshtein, fonetik) ravi birleştirme | Pilotta dizi tabanlı birleştirmenin tavanı %17,5'tir; 300 hadiste normalizasyon bölünmeyi azaltır, yanlış birleşmeyi artırır (`wiki/evaluation/engine-experiments.md`). Kimlik, saklanan kararla çözülür (K-4) |
| Türkçe hadis metni | Telifsiz, tam isnad içeren bir Türkçe kaynak bulunamadı |
| 500 hadis, 5 model, 3 tekrar | Etiketleme süresi ölçülmedi; boyut ilk 50 hadisin süresinden sonra büyütülebilir |
| Cohen kappa eşiği | Açık uçlu çıkarımda birim sayısı sabit değildir; uyum karşılıklı F1 ile ölçülür |

## Rules

- MUST: taahhüt metni aktarılırken `wiki/thesis/tubitak/form.md` esas alınır; bu sayfadaki tablo özettir.
- MUST: form gönderildikten sonra bir plan K-1…K-5, H1…H4 ya da Hedef 1–5 ile çelişmez; taahhüdü kapsar
  ya da genişletir. Gönderilene kadar eşikler ölçüme göre değiştirilebilir ve değişiklik formda ve bu
  sayfada aynı görevde yapılır.
- MUST: "Eldeki" sütununa yalnız dosyayla desteklenen şey yazılır; referans insan altın standardı
  değilse bu belirtilir.
- MUST: formun kaynakçası elle yazılmaz; `wiki/thesis/build_form.py` iki `.bib` dosyasından üretir.
  Gerekçe: 2026 I. dönem taslağındaki üç referans hiçbir dizinde bulunamadı
  (`wiki/sources/claude-science-results/04a_kaynak_dogrulama_tablosu.md`).
- MUST: bir taahhüdün durumu değiştiğinde (yeni ölçüm, yeni kod, danışman kararı) bu sayfa aynı görevde
  güncellenir.

## Source anchors

- `wiki/thesis/tubitak/form.md` — form metni; sonundaki "Göndermeden önce" bölümü karar bekleyen noktalar
- `wiki/thesis/build_form.py` — `assemble`: kaynakça numaralama, taslak kutusunun ve notların çıkarılması
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md` — koşul başına P / R / F1
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/extra-tables-ifta.json` — kontrol ve güven skoru tabloları
- `giraffegraph-core/evaluation/results/2026-10-13-identity-ledger/identity-ledger.json` — defter politikaları, iki etiket kümesi, dışarıda bırakılan kitap
- `giraffegraph-core/evaluation/results/2026-10-13-identity-ledger/decision-reapplication.json` — hedef örtüşmesi
- `giraffegraph-core/evaluation/annotation/` — etiketleme kiti
- `data/cache-and-ledger/data/agent-qa/README.md` — kod ajanı deneyi
- `wiki/sources/claude-science-context/02b_tubitak_commitments_and_critique.md` — 2026 I. dönem taslağının yöntem eleştirisi

## Verification checklist

- [ ] Tablodaki her kod ve eşik `wiki/thesis/tubitak/form.md` içinde aynı sayılarla geçiyor
- [ ] "Eldeki" ve "Ön çalışma ölçümü" sütunlarındaki her sayı çapa verilen dosyada bulunuyor
- [ ] `cd wiki/thesis && uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_form.py` hatasız biter ve "15 references" der
- [ ] Onaylanmış bir eşik varsa `wiki/decisions/` altında ADR'si var

## Related docs

- `wiki/project/overview.md`
- `wiki/project/open-decisions.md`
- `wiki/project/roadmap.md`
- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/engine-experiments.md`
- `wiki/evaluation/decision-ledger-experiments.md`
- `wiki/thesis/README.md`

## Last updated

2026-10-13
