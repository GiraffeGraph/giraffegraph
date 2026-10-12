# START HERE — Context package for Claude Science

**Kim:** Yahya Efe Kuruçay (Akdeniz Üniversitesi, Bilgisayar Mühendisliği, lisans). Bitirme projesi + TÜBİTAK 2209-A başvurusu. Ekip: Deniz Büyükşahin, İbrahim Çakır (formda), Alperen Ulukaya (sitede). Danışman: Dr. Öğr. Üyesi Taha Yiğit Alkan. Alan uzmanı: Prof. Dr. Rifat Atay (İlahiyat).

**Paketin tarihi:** 2026-09-30. Paketi Claude Code hazırladı. Repoları, canlı siteyi (giraffegraph.com), TÜBİTAK formunu ve yazarın önceki araştırma notlarını okudu, backend test paketini de çalıştırdı.

## Asıl soru (tek cümle)

> Ham veriden (kaynak kod, hadis metni, Kur'an meali, herhangi bir dağınık korpus) **LLM destekli, halüsinasyona ve sapmaya (drift) dayanıklı, insan tarafından doğrulanabilir bir bilgi katmanı** ("wiki") kurmanın ve güncel tutmanın **optimum** yolu nedir?

Knowledge graph kullanmak, markdown kullanmak ya da mevcut GiraffeGraph mimarisi **zorunlu değildir**. Hiçbir temsil peşinen kabul edilmiyor. Hadis isnad zincirleri (TÜBİTAK formu) bu genel sorunun **ilk ve kanıtlayıcı vaka çalışması**. Kod tabanı wiki'leri ve Kur'an uygulaması ikinci ve üçüncü vakalar.

## Önem sırası (yazarın kendi ifadesi)

1. **TÜBİTAK 2209-A formu** (taahhütler bağlayıcı) → `02a` (orijinal PDF), `02b` (yapılandırılmış özet + eleştiri)
2. **giraffegraph.com** (kamuya verilen iddialar) → `03`
3. **The Cache and the Ledger** (yazarın önceki araştırma sonucu, bilgi katmanı tasarımı) → `06a`, `06b`
4. GiraffeGraph Core kodu (ön çalışma) → `04a`, `04b`, `14`
5. Kod tabanı wiki pratiği (endüstriyel vaka) → `07`
6. Kur'an uygulaması → ikinci planda (`07` içinde kısa vaka)

## Dosya haritası

| Dosya | İçerik |
|---|---|
| `01_meta_research_question.md` | Asıl soru, "optimum"un tanımı, kısıtlar, beklenen çıktılar |
| `02a_TUBITAK_2209A_form_original.pdf` | Başvuru formu (orijinal) |
| `02b_tubitak_commitments_and_critique.md` | Taahhüt tablosu (K-1..K-5, H1..H4, metrikler, takvim), metodolojik zayıflıklar, referans doğrulama durumu |
| `03_website_giraffegraph_com.md` | Canlı sitenin tam içeriği ve verdiği sözler |
| `04a_giraffegraph_core_architecture.md` | Kodun gerçekte ne yaptığı (pipeline, veri modeli, kurallar) |
| `04b_giraffegraph_core_repo_docs.md` | Repo içi dokümanlar ve ADR'ler (birebir) |
| `05_claims_vs_code_gap_audit.md` | **Kritik:** Form ve site iddiaları ile kodun karşılaştırması (`file:line` anchor'lı) |
| `06a_cache_and_ledger_essay_README.md` | Yazarın "Cache and Ledger" makalesi (birebir) |
| `06b_cache_and_ledger_paper_decisions_tools.md` | Aynı çalışmanın arXiv taslağı, karar defteri, araçlar (birebir) |
| `07_case_codebase_wiki_and_quran.md` | Endüstriyel kod tabanı wiki pratiği (anonim) ve Kur'an uygulaması vakası |
| `08_hadith_domain_primer.md` | İsnad, rical, tabaka, muâsara/likâ, isim varyantları, aday veri setleri |
| `09_literature/` | Yazarın mevcut literatür taraması (38 makale, LLM değerlendirme metrikleri) + .bib |
| `10_related_work_map.md` | Asıl soruya yönelik literatür haritası (doğrulanmamış işaretli) |
| `11_evaluation_design_notes.md` | Metrik tanımları, deney tasarımı eleştirisi, genellenebilir değerlendirme önerisi |
| `12_synthesis_hypothesis_source_ledger_views.md` | Claude Code'un sentez hipotezi: *Kaynak + Karar Defteri + Türetilmiş Görünümler* (sınanacak, kabul edilmiş değil) |
| `13_open_questions.md` | Ekibin karar vermesi gereken açık sorular |
| `14_giraffegraph_core_code_bundle.md` | Ana kaynak kodu (satır numaralı) |
| `15_PROMPTS_for_claude_science.md` | Claude Science'a yapıştırılacak promptlar |

## Dürüstlük kuralları (yazarın kendi disiplini, `06a`'dan)

- Bir script ya da birincil kaynakla doğrulanmamış sayı **iddiadır, olgu değildir**. `[UNVERIFIED]` etiketi taşır.
- Boş ama dürüst bir alan, uydurma ama emin görünen bir alandan iyidir.
- Bu paketteki literatür önerilerinin bir kısmı Claude Code'un belleğinden geliyor. `10_related_work_map.md` içinde hepsi "doğrula" diye işaretli.
