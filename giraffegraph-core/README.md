# GiraffeGraph Core

GiraffeGraph Core, ham ve dağınık verileri adım adım işlenebilir, doğrulanabilir ve büyütülebilir bir bilgi grafiğine dönüştüren genel amaçlı bir platform.

İlk alan şablonumuz `Story / Series / Film` olacak. Ancak çekirdek sistem doğrudan dizi ya da filme bağlı değil; şema tabanlı, yapay zeka destekli ve panelden yönetilebilir bir platform olarak kurgulanıyor.

Bu repo yalnızca ürünün iç panelini ve çekirdek motorunu kapsar. SaaS landing page bu reponun dışındadır.

## Ürün Tanımı

Ürünün amacı:

- Ham veriyi normalleştirmek
- Veriyi şemaya göre varlık, ilişki ve olay adaylarına çevirmek
- Aday veriyi doğrulamak
- Doğrulanan veriyi kalıcı grafik katmanına yazmak
- Her yeni kaynak birimi ile bilgi grafiğini yinelemeli olarak büyütmek

Zihinsel model:

`Grafik(t) + KaynakBirimi(t+1) -> Grafik(t+1)`

Bu yüzden ürün tek seferlik bir içe aktarma aracı değil, zaman içinde büyüyen bir grafik oluşturma platformudur.

## Temel İlkeler

- Alana özel kavramları çekirdeğe gömme; ayrı şablon olarak tut
- Şemayı kod olarak değil, veri olarak yönet
- Yapay zeka önerir, sistem karar verir
- Aday → Doğrulama → Kesinleşme
- Güven skoru düşükse insan incelemesi zorunlu
- Temiz mimari + önce tekli modüler yapı

## Repository Layout

- [`docs/README.md`](docs/README.md): Dokuman giris noktasi
- [`docs/architecture/system-overview.md`](docs/architecture/system-overview.md): Mimari omurga
- [`docs/architecture/development-environment.md`](docs/architecture/development-environment.md): Docker ve lokal gelistirme ortami
- [`docs/glossary/domain-language.md`](docs/glossary/domain-language.md): Ortak dil
- [`docs/adr/`](docs/adr): Architecture Decision Record'lar
- [`backend/README.md`](backend/README.md): Backend klasor yapisi ve amaci
- [`frontend/README.md`](frontend/README.md): Frontend klasor yapisi ve amaci

## Documentation Order

Projede yeni bir karar alinacagi zaman once su sirayla ilerlenir:

1. Problem ve kapsam yazilir.
2. Gerekirse deep research prompt hazirlanir.
3. Sonuc dokumante edilir.
4. ADR yazilir.
5. Kod iskeleti ve kontratlar guncellenir.

## Deep Research Workflow

Kullanici talebine gore, guncel ve kolay degisebilecek teknik konularda ek dis arastirma gerektiginde once bir `deep research prompt` hazirlanir. Kullanici o prompt ile arastirma yaptirip sonucu geri yollar; mimari ve implementasyon kararlarinda bu sonuc temel alinir.

Hazir reusable prompt burada tutulur:

- [`docs/research/deep-research-prompts.md`](docs/research/deep-research-prompts.md)

## Mevcut Kapsam

Bu aşamada odak:

- Genel çekirdek mimariyi kurmak
- Şema yönetimini tasarlamak
- Veri alımı → çıkarım → doğrulama → grafik kayıt hattını netleştirmek
- Story şablonunu ayrı bir alan paketi olarak tanımlamak

Bu aşamada odak değil:

- Ajan simülasyonu
- Sorgulama ürünü
- Gelişmiş GraphRAG arayüzü
- Çok alanlı şablon marketi

Notlar:

- Tüm metadata (proje, şema, kaynak birim, çalıştırma, iş, segment, aday, doğrulama, inceleme, grafik deltası) artık Postgres üzerinde tutuluyor.
- Postgres şeması Alembic migration'ları ile yönetiliyor.
- Testler ve izole çalıştırmalar için varsayılan backend `memory` olarak kalır.
- İşlem kuyruğu (extract_candidates, validate_run, commit_run) altyapısı mevcut; worker servisi bekleyen işleri otomatik tüketir.
- Panel içinde proje bazlı iş görünürlüğü eklendi; kuyruk durumu operatör panelinden izlenebilir.
- Şema versiyonu bazında pipeline tanımları tutulur; yeni şema oluşturulduğunda varsayılan v1 pipeline otomatik oluşturulur.
- Bir çalıştırma başlatmak için seçilen pipeline versiyonunun ilgili şema versiyonunda tanımlı olması zorunlu.
- Grafik yazım adımı; delta kaydı, düğüm/ilişki birleştirme ve köken bağlantılarını içeriyor.
- İnceleme kararı akışı açık: tekrar tespit, düşük güven skorlu adaylar karar altına alınabiliyor.
- Düzenleme kararları şema kurallarına göre yeniden doğrulanıyor; geçersiz düzenleme grafik yazım adımına geçemiyor.
- Kesinleşmiş grafik için temel okuma endpoint'leri hazır: genel bakış, düğüm listesi, ilişki listesi.

## Sonraki Adım

- Pipeline tanım editörü / panel görünürlüğü
- Varlık çözümleme ve tekrar tespit katmanını ilerletmek
- Kesinleşmiş grafik okuma modelleri

## Local Development

Docker Compose tabanli hot reload gelistirme ortami icin:

1. `.env.example` dosyasini `.env` olarak kopyalayin.
2. `docker compose up --build` calistirin.

Migration komutlari:

- `docker compose exec backend alembic upgrade head`
- `docker compose exec backend alembic current`
- `docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once --job-type extract_candidates`
- `docker compose exec backend python -m app.interfaces.cli.processing_jobs_worker --once --run-id <run_id>`

Servisler:

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000`
- Worker: `docker compose logs -f worker`
- Neo4j Browser: `http://localhost:7474`
- Postgres: `localhost:5432`

---

gitingest . \
  -e "*.lock" \
  -e "tests/" \
  -e "docs/" \
  -e "**/migrations/versions/" \
  -e ".gitkeep" \
  -e "alembic.ini" \
  -e "script.py.mako" \
  -e "next-env.d.ts" \
  -e ".dockerignore" \
  -e "__init__.py"