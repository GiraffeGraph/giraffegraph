# Ek A Sonuçları yeniden üretme

Bir yol aksi yönde belirtmedikçe bütün komutlar proje deposundaki `giraffegraph-core/` dizininden çalıştırılır. Depo geliştirme sırasında özeldir; motor proje sonunda yayımlanacaktır. Değerlendirme verileri `data/README.md` içinde açıklanmıştır ve yeniden dağıtılmamaktadır.

Veritabanı ya da ağ gerektirmeyen arka uç testleri:

```
cd backend
uv sync --extra dev
uv run pytest -q
```

Gerçek veritabanları üzerindeki testler, bir PostgreSQL 16 ve bir Neo4j 5 örneği ile üç ortam değişkeni gerektirir:

```
GG_TEST_POSTGRES_DSN=... GG_TEST_NEO4J_URI=... GG_TEST_NEO4J_PASSWORD=... uv run pytest -q -m real_db
```

Bir değerlendirme koşusu ve analizi:

```
cd backend
uv run python scripts/run_isnad_experiment.py --input <hadiths.json> --out-dir <run-dir> \
    --condition llm_isnad_whole --model claude-haiku-5-5 --effort low --max-cost-usd 0.85
cd ..
python evaluation/analyze_experiment.py --run <run-dir> --reference <reference.jsonl> --out <run-dir>/analysis
python evaluation/compare_runs.py --runs <run-dir> <run-dir> ... --reference <reference.jsonl> --out compare.md
python evaluation/extra_tables.py --runs <run-dir> ... --reference <reference.jsonl> \
    --reference-chains <reference_chains.jsonl> --out extra-tables.json
python evaluation/classify_value_flags.py --run <run-dir> --hadiths <hadiths.json> \
    --reference <reference.jsonl> --out value-flag-classes.json
python evaluation/identity_baseline.py --reference-chains <reference_chains.jsonl> --out identity.json
```

Model yanıtları `backend/var/llm-cache/` altında önbelleğe alınır. Önbellek bulunduğunda koşu hiçbir API çağrısı yapmaz ve aynı çıktıyı yeniden üretir.

Bölüm 8'in destek çalışmaları. Defter benzetimi ve yeniden çıkarımdaki örtüşme, `evaluation/README.md` içinde açıklandığı biçimde çalıştırılır (`identity_ledger.py`, `decision_reapplication.py`). Ajan deneyi, proje deposundaki `data/cache-and-ledger/data/agent-qa/` dizininden çalıştırılır; README'si komutları, soruları, cevap anahtarını ve her deney kolunun maliyetini verir.

# Ek B Sonuç dosyaları

| İçerik | `giraffegraph-core/evaluation/results/` altındaki yol |
|---|---|
| Altı kitap test kümesi, dört koşul | `2026-10-12-sixbooks300/` (`compare-ifta.md`, `extra-tables-ifta.json`, koşu başına bir klasör; `haiku-llm_schema_whole/value-flag-classes.json`) |
| Pilot küme, dört koşul | `2026-10-12-pilot50/` (`compare-sanadset.md`) |
| İkinci model alt kümesi | `2026-10-12-subset36/` (`compare-ifta.md`) |
| Ravi kimliği taban çizgisi | `2026-10-12-identity-baseline/sixbooks300.json` |
| İlk uçtan uca koşunun kural tabanlı taban çizgisi | `2026-10-12-rule-based-baseline/` |
| Kimlik defteri benzetimi ve yeniden çıkarım örtüşmesi (Bölüm 8.1) | `2026-10-13-identity-ledger/` (`identity-ledger.json`, `decision-reapplication.json`) |

Ajan deneyinin koşuları ve analizi (Bölüm 8.2), bu klasörün dışında, `data/cache-and-ledger/data/agent-qa/` içindedir (`analysis.json`, `runs.tar.gz`).

Her koşu klasörü, puanlayıcının biçimindeki sistem çıktısını, durum ve gerekçe kodlarıyla aday başına bir satırı, belirteç ve gecikmeyle sağlayıcı çağrısı başına bir satırı, koşu raporunu ve analizi tutar.

# Ek C Yapay zekâ araçlarının kullanımı

Bu proje boyunca yapay zekâ asistanları kullanıldı: literatür taramasında, 30 Eylül 2026'daki tasarım analizinde ve pilotta, değerlendirilen dalda yazılan kodun çoğunda, analiz betiklerinde ve bu raporun taslağını hazırlarken. Çıkarım deneylerinin kendisi de sınanan sistem olarak bir dil modeli kullanır.

Bu çalışma biçiminin risklerini sınırlamak için aşağıdaki kuralları uyguladık. Bibliyografik kayıtlar Crossref, arXiv, ACL Anthology ya da yayıncının ilk sayfasından alındı; hiçbir zaman bellekten yazılmadı. Önceki bir proje belgesindeki üç kaynak hiçbir dizinde bulunamadı ve burada kullanılmadı. Bu rapordaki her ölçülmüş sayı bir betik tarafından üretildi ve bir sonuç dosyasında saklanıyor; veri kümelerinin istatistikleri veri manifestosundan alındı. Kod yalnız testlerle kabul edildi; gerçek veritabanları için işaretlenen testler PostgreSQL ve Neo4j üzerinde çalıştırıldı. Bu raporun bir taslağı, bağımsız bir yapay zekâ inceleyicisi tarafından sonuç dosyalarına karşı kontrol edildi; rapor, dosyaların gösterdiğinden fazlasını iddia ettiği yerlerde düzeltildi. Diğer çalışmalar hakkındaki ifadeler, atıf verilen kaynakta okunanlarla sınırlıdır.

Yazarlar bu raporun içeriğinden sorumludur.
