# Katkı rehberi

## Kaynak önermek (GitHub hesabı yeterli)
[Kaynak öner](https://github.com/sdanacioglu/bakircay-cbs-acik-veri-kaynaklari/issues/new?template=kaynak-oner.yml) formunu doldurun. Öneriler kontrol edildikten sonra listeye eklenir.

## Listeyi doğrudan güncellemek (bakımcılar)
1. Tek doğruluk kaynağı **`data/kaynaklar.csv`** dosyasıdır (UTF-8, virgülle ayrılmış). GitHub'da dosyayı açıp ✏️ ile düzenleyebilir ya da Excel'de açabilirsiniz (Excel'de **UTF-8 CSV** olarak kaydedin).
2. Yeni satırda en az şu alanları doldurun: `id`, `ad`, `url`, `kapsam`, `konu`, `tur`. Önerilen diğer alanlar: `aciklama`, `veri_turu`, `giris_gerekli`, `indirilebilir`, `kaynak_listesi`, `eklenme_tarihi`.
3. `son_kontrol`, `durum`, `http_kodu` ve `hata_sayisi` alanlarını **boş bırakın**; bunlar otomatik doldurulur.
4. Değişikliği kaydettiğinizde GitHub Actions README'yi, JSON'u ve arama sayfasını yeniden üretir. `id` ya da URL tekrar ederse işlem durur ve hata Actions sekmesinde görünür.

## Alan değerleri
| Alan | Değerler |
|---|---|
| `kapsam` | Türkiye, İzmir, İstanbul, Ordu, Küresel, Avrupa, ülke adı… |
| `tur` | Veri deposu · CBS platformu · Bilgi platformu · Katalog · Harita altlığı |
| `veri_turu` | Vektör · Raster · Tablo · Çoklu |
| `giris_gerekli` | Evet · Hayır |
| `indirilebilir` | Evet · Dolaylı · Hayır |
| `onerilen` | Evet (öne çıkan kaynak) ya da boş |
| `kontrol_disi` | Evet: otomatik bağlantı kontrolünden muaf (yurt dışından erişilemeyen ama çalışan siteler için) |
| `durum` | otomatik: aktif · kontrol edilemedi · erişilemiyor · arşiv (arşiv elle verilir) |

## Bağlantı kontrolü
Her ayın 1'inde otomatik çalışır. Elle çalıştırmak için: **Actions → Listeyi güncelle ve yayımla → Run workflow**.
Yerelde: `python scripts/check_links.py` ve ardından `python scripts/build.py`.
