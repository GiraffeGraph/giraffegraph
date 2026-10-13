# Çalışma alanı haritası

## Purpose

`/Users/efe/projects/GiraffeGraph` altındaki her klasörün ne olduğunu, hangi repoda durduğunu ve
bitirme projesiyle ilişkisini tek yerde tutmak. Çalışma alanının başka bir makinede nasıl kurulacağını
söyler.

## Scope

- In: üst düzey klasörler, sahiplik, git durumu, proje ilgisi, çalışma alanının kurulumu
- Out: klasörlerin iç mimarisi (her birinin kendi belgesine bağlanır)

## Harita

Boyut bilgisi 2026-10-08'de `du -sh` ile okundu; `data/` satırı 2026-10-12'de; git durumu 2026-10-13'te
`git log` ve `gh repo view` ile.

| Klasör | Ne | Proje ilgisi | Git |
|---|---|---|---|
| `giraffegraph-core/` | KG üretim motoru: FastAPI backend, Postgres + Neo4j, Next.js iç panel. Aday → doğrulama → canonical graf hattı | **Çekirdek.** Deney bu kodun üzerinde koşar | `github.com/GiraffeGraph/giraffegraph-core` (herkese açık), `main`; LICENSE dosyası yok |
| `data/` | 2026-10-12'de indirilen dış etiketli hadis verisi (`raw/`: İfta ailesinin altı kitabı ve ravi kataloğu, AR-Sanad, Sanadset; hadis dışı iki biyomedikal derlem, MedMentions ve BC5CDR, 2026-10-13'te eklendi; 99 dosya), kurulum betikleri (`scripts/`) ve bunlardan kurulan değerlendirme kümeleri (`eval/`: `sixbooks-fresh`, `pilot50`, `ar-sanad-identity`). `core-backup/`, Core'un izlemediği iki klasörün kopyasıdır: deney koşularının tam çıktısı ve model yanıt önbelleği. Manifest: `data/README.md` | **Aktif, yalnız değerlendirme.** Motor deneylerinin girdisi ve referansı. Veri yeniden dağıtılmaz; `raw/` altındaki dosyalar güvenilmeyen indirmedir, çalıştırılmaz | `github.com/GiraffeGraph/giraffegraph-eval-data` (özel), ilk commit 2026-10-13. `raw/` ve `work/` izlenmez; diskte 4,5 GB, repoda yaklaşık 35 MB |
| `wiki/` | Projenin kod dışındaki bütün bağlamı: yaşayan sayfalar, literatür taraması, tarihli kaynak paketleri, tez ve makale taslakları (`wiki/thesis/`) | **Aktif.** Her oturumun ilk okuduğu yer | `github.com/GiraffeGraph/giraffegraph-wiki` (özel), ilk commit 2026-10-13 |
| `wiki/literature/` | Efe'nin literatür taraması: 38 makale, LLM başarı ölçüm metrikleri | **Aktif.** Danışman toplantısı aksiyonu | wiki reposunun parçası |
| `wiki/sources/claude-science-results/` | 2026-09-30 Claude Science çıktısı: mimari analizi, revize deney protokolü, pilot kodu ve sayıları, iş planı, yayın planı | **Referans (donmuş).** Ölçüm ve protokol önerilerinin kaynağı | wiki reposunun parçası |
| `wiki/sources/claude-science-context/` | Aynı çalışmaya girdi olarak hazırlanan bağlam paketi: TÜBİTAK formu, kod bundle'ı, alan özeti, açık sorular | **Referans (donmuş).** | wiki reposunun parçası |
| `data/cache-and-ledger/` | "The Cache and the Ledger" denemesi, arXiv taslağı, karar defteri, bash araçları (`bin/ledger`, `bin/anchor-check`); `data/` altında denemenin sayılarını üreten betikler ve 2026-10-13 keşif deneyleri (`explore-*.py` ve çıktıları) | **Projenin iddiasının kaynağı ve destek deneyleri.** "Türetilebilen saklanmaz, karar saklanır" tezi; etiketli veride ve canlı ajanla sınanması `wiki/evaluation/decision-ledger-experiments.md`, `wiki/evaluation/wiki-for-agents-experiments.md`; özet `data/cache-and-ledger/MEASUREMENTS.md` | özel veri reposunun parçası |
| `landing/` | giraffegraph.com tanıtım sayfası (Next.js, statik export) | **İkincil.** Kamuya verilen iddiaların kaynağı; kodla tutarlılığı izlenir | `github.com/GiraffeGraph/landing` (herkese açık), `main`; `main`e push siteyi yayınlar (`landing/.github/workflows/deploy.yml`) |

## Rules

- MUST: çalışma alanında yalnız bitirme projesinin dört klasörü durur. Aynı GitHub organizasyonundaki
  `giraffle` (not ve planlama uygulaması) ve `giraffe-code` (çok-ajanlı kodlama aracı) repoları
  projenin parçası değildir ve çalışma alanına klonlanmaz; yalnızca ad benzerliği taşırlar, bilgi
  grafı, hadis ya da RAG ile ortak kodları yoktur.
- MUST: `wiki/sources/claude-science-context/` ve `wiki/sources/claude-science-results/` düzenlenmez. Dosya adlarındaki numaralar
  iki pakette bağımsızdır (`wiki/sources/claude-science-context/05_…` denetim, `wiki/sources/claude-science-results/05_…`
  değişiklik listesi); atıf yaparken klasör adı yazılır.
- MUST: literatür dosyalarının canlı kopyası `wiki/literature/` klasörüdür.
  `wiki/sources/claude-science-context/09_literature/` aynı dosyaların 2026-09-30 kopyasıdır (2026-10-08'de `cmp`
  ile bayt düzeyinde eşit).
- MUST: `wiki/sources/` ya da `wiki/literature/` altındaki bir dosyanın yolu değişirse ona dayanan
  üç yer aynı görevde güncellenir: Core testleri
  (`giraffegraph-core/evaluation/tests/conftest.py`, `backend/tests/unit/test_hadith_segmenter.py`,
  `backend/tests/unit/test_hadith_normalization.py`), `data/README.md` ve tez derleme betiği
  (`wiki/thesis/build.py`, `BIB_FILES`). Gerekçe: pilot regresyon testleri dosyayı bulamazsa
  hata vermez, atlanır; kırılma fark edilmez.
- SHOULD: Core'da kod değişikliği `giraffegraph-core/` reposunun kendi commit'leriyle yapılır; wiki
  değişikliği `wiki/` reposunda commit edilir.

## Çalışma alanını kurmak

Kök dizin bir repo değildir; yan yana klonlanan repolardan oluşur. Yol çapaları ve Core testleri bu
yerleşimi varsayar.

```
mkdir GiraffeGraph && cd GiraffeGraph
git clone git@github.com:GiraffeGraph/giraffegraph-wiki.git wiki
git clone git@github.com:GiraffeGraph/giraffegraph-core.git
git clone git@github.com:GiraffeGraph/giraffegraph-eval-data.git data
git clone git@github.com:GiraffeGraph/landing.git
printf '@wiki/CLAUDE.md\n' > CLAUDE.md
```

Hiçbir repoda durmayan iki şey: kökteki `CLAUDE.md` (tek işi `wiki/CLAUDE.md` dosyasını içe
aktarmaktır) ve `data/raw/` altındaki 4,5 GB indirilmiş veri (yeniden
indirme kaynakları ve sha256 değerleri `data/raw_manifest.json` ve `data/README.md` içinde).

## Çalışma alanı dışındaki ilgili varlıklar

| Varlık | Yer | İlgi |
|---|---|---|
| CSE 491 ders reposu | `/Users/efe/cse/CSE-491-Senior-Design-Project-I` | İzlence, haftalık plan, imzalı toplantı formları. Ders reposunun kendi klonudur; proje klasörü o repoda izlenmez. Proje klasörü `assignments/2026-2027-fall-efe-kurucay/giraffegraph/`: proje önerisi taslağı `proposal.md`, imzalı toplantı formu, TÜBİTAK formunun kopyası. Aynı klasördeki `thesis`, `wiki/thesis/` klasörüne sembolik bağdır; tezin ve makalenin tek kopyası wiki reposundadır |
| Kur'an uygulaması | `/Users/efe/projects/rtndigital/QuranApp` | Genelleme vakası C: provenance ve bayat embedding olayı (`wiki/sources/claude-science-context/07_case_codebase_wiki_and_quran.md`) |
| Makale kütüphanesi | Zotero: kişisel "My Library" ve "giraffegraph" grup kütüphanesi (groupID 6601142) | `LLM-Eval-Metrics` koleksiyonu iki kütüphanede de var: 38 makalenin künyesi, PDF'i ve NotebookLM review notu. `KG-Hadith-Design` koleksiyonu yalnız kişisel kütüphanede: `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` içinden 49 kayıt (tema etiketli) ve `wiki/literature/extraction_eval_precedents.bib` içinden 6 kayıt (`eval-precedent` etiketli; Oumer 2025 tezi Zotero'da yok). Zotero API anahtarının grup kütüphanesine yazma izni yoktur (2026-10-08: 403) |
| Sanadset 650K | Hugging Face `freococo/650k_sanadset`; yerel kopya `data/raw/sanadset-hf/` | Arapça tam isnad korpusu; pilotun veri kaynağı. Lisans beyanları çelişiyor: Hugging Face kartı `cc0-1.0`, özgün Mendeley Data kaydı "CC BY 4.0" (`data/README.md`) |
| İfta Sünnet veri ailesi | Kaggle `jehadoumer/ifta-hadith-*` (üç sürüm), GitHub `JehadOumer/Ifta-Sunnah-Hadith-and-Narrators-Dataset`; yerel kopya `data/raw/ifta-kaggle/`, `data/raw/ifta-github/` (altı kitap ve ravi kataloğu) | Ravi span'i, aktarım ilişkisi ve ravi kimliği taşıyan 276.347 hadis; 300 hadislik test kümesinin referansı. Lisans beyanları sürüme göre değişir (`wiki/evaluation/related-work.md`, "Hazır referans veri adayları") |
| AR-Sanad 280K | GitHub `somaia02/Narrator-Disambiguation`; yerel kopya `data/raw/ar-sanad/` | Ravi kimlikli 27.056 gerçek sened ve 18.298 ravilik tablo; L2 için aday referans, üzerinde ölçüm yapılmadı. Depoda LICENSE yok |

## Bilinen durum notları

- Kök dizin git reposu değildir. Dört reponun her birinde yalnız `main` dalı vardır; çalışma `main`
  üzerinde yürür (proje sahibi kararı, 2026-10-13).
- Core'un `main` dalı isnad prototipini taşır (2026-10-13); GitHub Actions'ta `backend` ve `frontend`
  işleri geçer. `evaluation/results/` altından yalnız özet tablolar izlenir; hadis metni ve alıntı
  içeren koşu dosyaları ile `backend/var/llm-cache/` Core'da izlenmez, kopyaları özel
  `giraffegraph-eval-data` reposunda `core-backup/` altındadır (yenileme komutu `data/README.md`).
  `wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md` içindeki C1–C14 değişikliklerinden
  `main` dalında duranlar: C1 (alıntı ve değer kapıları), C2 (aday bazında red, şema önerisi inceleme öğesi olarak),
  C4 (ASCII ad doğrulaması), C5 (ilişki `merge_keys`), C7 (isnad bölütleyici), C8 (zincir başına çağrı),
  C10'un bir kısmı (tanımsız özellik, izinli değer listesi), C11'in lisans dışındaki kısmı (README, CI,
  kilit dosyası, kırık test), C12'nin tek işlem kısmı (koşu başına tek Neo4j işlemi; outbox yok) ve
  C3'ün asgari hâli (`review_decisions`: kim, ne zaman, süre; içerik adresli hedef yok). C6, C9, C13, C14
  yoktur. Değişiklik listesinde olmayıp kodda duranlar: `anthropic` sağlayıcısı, proje oluştururken şablon
  şemasının uygulanması, toplu yükleme ve işleme uçları, zincir okuma uçları ve paneldeki "Zincirler"
  sekmesi, deney koşucusu ve yanıt önbelleği. Davranış: `wiki/domains/hadith/isnad-pipeline.md`.
- Core testleri (2026-10-13): `backend` içinde 285 test toplanır; bellek içi depoyla 273'ü geçer, `real_db`
  işaretli 12'si atlanır. `evaluation` testleri numpy ve scipy ile 72 geçer; onlarsız 1'i atlanır. `real_db`
  testleri 2026-10-12'de yerel konteynerlerde PostgreSQL 16 ve Neo4j 5.26'ya karşı koşuldu ve 12'si de
  geçti; o koşunun çıktısı dosya olarak kayıtlı değil. Komutlar: `giraffegraph-core/README.md`,
  "Run the backend tests".
- Ölçüm çıktıları `giraffegraph-core/evaluation/results/2026-10-12-*/` altındadır (beş klasör); okuma
  kılavuzu `wiki/evaluation/engine-experiments.md`. LLM yanıt önbelleği
  `giraffegraph-core/backend/var/llm-cache/` altındadır ve depoda yok sayılır.
- İndirilen her dosyanın boyutu ve sha256 değeri `data/raw_manifest.json` içindedir; `data/eval/`
  altındaki kümeler `data/README.md` içindeki kurulum zinciriyle bayt düzeyinde yeniden üretilir.
- Tez ve makale taslakları `wiki/thesis/` altındadır (özel wiki reposu). Proje önerisi taslağı
  (`proposal.md`) ders reposunun çalışma ağacındadır ve hiçbir uzak repoda durmaz.
- Sitedeki cümleler Core `main`in yaptığına göre yazılıdır (`landing` commit `b92fc4b`, 2026-10-13, 6 dosya).
- Core `main`, kimlik karar defteri benzetimini (`evaluation/identity_ledger.py`), yeniden uygulama
  ölçümünü (`evaluation/decision_reapplication.py`), testlerini ve iki sonuç dosyasını taşır
  (2026-10-13). Bunlar ölçüm betikleridir; motor koduna dokunmaz.
- Core için lisans seçilmemiştir; LICENSE dosyası yoktur.

## Verification checklist

- [ ] `ls /Users/efe/projects/GiraffeGraph` çıktısındaki her klasör tabloda var
- [ ] Çalışma alanı kökünde `giraffegraph-core/`, `data/`, `landing/`, `wiki/` ve `CLAUDE.md` dışında bir şey yok
- [ ] Core durumu notu `git -C giraffegraph-core log -1` ile uyumlu
- [ ] Test sayıları `cd giraffegraph-core/backend && uv run pytest -q` çıktısıyla aynı
- [ ] `du -sh data` çıktısı tablodaki boyutla uyumlu
- [ ] `gh repo view GiraffeGraph/giraffegraph-wiki --json visibility` çıktısı `PRIVATE`
- [ ] Pilot dosyalarına dayanan testler atlanmıyor: `uv run --no-project --python 3.12 --with pytest --with numpy --with scipy python -m pytest -q giraffegraph-core/evaluation/tests` çıktısında atlanan test yok

## Related docs

- `wiki/project/overview.md`
- `wiki/project/roadmap.md`
- `wiki/evaluation/engine-experiments.md`
- `wiki/evaluation/decision-ledger-experiments.md`
- `wiki/evaluation/wiki-for-agents-experiments.md`
- `wiki/sources/README.md`
- `data/README.md`
- `wiki/sources/claude-science-context/00_README_START_HERE.md`
- `wiki/sources/claude-science-context/04a_giraffegraph_core_architecture.md`

## Last updated

2026-10-13
