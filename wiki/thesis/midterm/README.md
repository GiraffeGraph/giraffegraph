# CSE 491 ara rapor

## Purpose

Grup 10 için 8 Kasım 2026 teslim tarihli, ders şablonuna uygun ara raporun kaynaklarını ve teslim dosyasını aynı yerde tutmak.

## Scope

- Teslim: `wiki/thesis/midterm/10_MidtermReport.docx`, İngilizce, 10 sayfa.
- Kaynak: `build_midterm.py`; bunun ürettiği okunabilir metin `report.md`.
- Tasarım otoritesi: dersin `template.docx` dosyası. Aslı değiştirilmez; çıktı ayrı dosyadır.
- Geçici sayfa görselleri ve kontrol PDF'i teslim dosyası değildir; `/tmp/giraffe-midterm/render-final/` içinde tutulmuştur.
- Herkese açık web kopyası teslim raporuyla aynı içerik ve sayfa düzenini taşır; öğrenci numaraları kullanıcı isteğiyle yer alır, TÜBİTAK başvuru numarası çıkarılmıştır. Eski bağlantılar için `landing/public/downloads/midterm-report.pdf` kopyası da tutulur.
- Güncel kart ve ayrıntı sayfası, önbellekteki eski sabit adresi kullanmamak için `landing/public/downloads/midterm-report-2026-11-08-7fe35d5178.pdf` dosyasına bağlanır. Yeni PDF içeriği üretildiğinde dosya adındaki hash ve iki sayfadaki bağlantı birlikte değiştirilir.
- Yayın: <https://giraffegraph.com/reports/> ve <https://giraffegraph.com/downloads/midterm-report.pdf>. Landing commit `3c37b8b`, GitHub Pages koşusu `42527849790` başarılıdır. Canlı kartın etkinliği, PDF'in 10 sayfa olması ve yayımlanan dosyanın kontrol edilen kopyayla bayt düzeyinde eşitliği 9 Kasım 2026 tarihinde doğrulandı.

## Güncel durum

Teslim tarihi kullanıcının düzeltmesiyle 8 Kasım 2026 olarak yazılır. Repo bağlantısında private ibaresi bulunmaz; repo public durumdadır. Gerçek test ve erişim tarihleri ayrıca korunur.

Son PDF düzeltmesi landing commit `2fb915f`, başarılı GitHub Pages koşusu `42529918924` ile yayımlandı. Canlı PDF'in yerel kontrol edilmiş kopyayla eşitliği doğrulandı; çıktı yine 10 sayfadır. İndirilenler klasöründeki Word dosyası aynı düzeltmeleri taşır.

Proje sahibi 9 Kasım 2026 tarihinde grup numarasının 10 olduğunu, çift etiketleme ve uzman değerlendirmesinin henüz başlamadığını doğruladı. Raporda bu işler tamamlanmış gösterilmez. Yeni ödev yönergesine göre ayrı ara sunum yoktur; rapor Supervisor Meeting 4 sırasında konuşulacaktır.

Prototip ve hazırlık kodu, dönem sonu kabulünden ayrılır. 50 insan etiketli hadis ve 100 hadislik uçtan uca çalışma CSE 491 hedefidir. TÜBİTAK'ın 300 insan etiketli hadis, üç model, tekrarlar ve gerçek kararlarla kimlik defteri taahhütleri sonraki araştırma aşamalarında korunur.

## Yeniden üretme

Çalışma alanı kökünden `python wiki/thesis/midterm/build_midterm.py` çalıştırılır. Python ortamında `python-docx`, `lxml` ve `Pillow` gerekir. Bu oturumda Codex'in Python 3.12 çalışma zamanı kullanıldı:

`/Users/efe/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python`

Betik şablonun ZIP parçalarını korur; yalnız gövdeyi, yeni şekiller için ilişkileri ve içerik türlerini değiştirir. Özgün 26 diğer parça bayt düzeyinde korunur; sayfa geometrisi aynı kalır. Görsel düzen ve 10 sayfa sınırı her içerik değişikliğinden sonra yeniden kontrol edilir.

## Source anchors

- `wiki/thesis/proposal/proposal.md` — CSE 491 kapsamı, FR/NFR, S1–S5 ve WP1–WP6.
- `wiki/thesis/tubitak/form.md` — son araştırma önerisi; kullanıcının verdiği başvuru 1919B012619516 PDF'i ile birlikte okundu.
- `giraffegraph-core/README.md` ve `backend/src/app/` — prototip davranışı ve eksikler.
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md` ve `wiki/evaluation/engine-experiments.md` — insan altın standardı olmayan ön ölçümler.
- `giraffegraph-core/frontend/docs/screens/08-incele.png` — rapordaki mevcut ekran örneği; araştırma katılımcısı verisi değildir.

## Verification checklist

- [x] Grup 10 ve henüz başlanmayan insan çalışmaları kullanıcıdan doğrulandı.
- [x] Backend testi: `uv run pytest -q`, 9 Kasım 2026, 273 geçti / 12 gerçek veritabanı testi atlandı, 3,98 saniye.
- [x] Şablon yönergeleri kaldırıldı; danışman değerlendirme alanı boş bırakıldı.
- [x] Mimari diyagramı eklendi; tarayıcıdan doğrudan veritabanı erişimi gösterilmedi.
- [x] Kaynak şablon hash'i: `a584a9ec55559d44cab167bc1f71b447bc171fa6917435accea5ca4838a05ad0`.
- [x] Son DOCX render edildi; sayfa sınırı ve sayfa görselleri kontrol edildi.

## Related docs

- `wiki/thesis/README.md`
- `wiki/project/tubitak-commitments.md`
- `wiki/project/roadmap.md`

## Last updated

2026-11-09
