"""Bakırçay CBS Açık Veri Kaynakları — ortak CSV okuma/yazma yardımcıları."""
import csv
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
CSV_YOLU = KOK / "data" / "kaynaklar.csv"

SUTUNLAR = [
    "id",               # benzersiz kısa ad (küçük harf, tire)
    "ad",               # kaynağın adı
    "url",              # bağlantı
    "aciklama",         # kısa açıklama (Türkçe; UNEP kayıtlarında İngilizce not)
    "kapsam",           # Türkiye, İzmir, Küresel, Avrupa, ülke adı…
    "konu",             # Türkçe konu başlığı
    "cografya",         # Fiziki coğrafya / Beşerî coğrafya / Genel
    "tur",              # Veri deposu / CBS platformu / Bilgi platformu / Katalog / Harita altlığı
    "veri_turu",        # Vektör / Raster / Tablo / Çoklu
    "giris_gerekli",    # Evet / Hayır
    "indirilebilir",    # Evet / Dolaylı / Hayır
    "onerilen",         # Evet → öne çıkan kaynak
    "kaynak_listesi",   # BakırçayCBS / 30DayMapChallenge / UNEP 2019
    "eklenme_tarihi",   # YYYY-AA-GG
    "son_kontrol",      # YYYY-AA-GG (otomatik)
    "durum",            # aktif / kontrol edilemedi / erişilemiyor / arşiv (otomatik)
    "http_kodu",        # son kontrolün sonucu (otomatik)
    "hata_sayisi",      # art arda başarısız kontrol sayısı (otomatik)
    "kontrol_disi",     # Evet → otomatik bağlantı kontrolü yapılmaz (elle doğrulanmış)
]

ZORUNLU = ["id", "ad", "url", "kapsam", "konu", "tur"]


def oku(yol=CSV_YOLU):
    with open(yol, newline="", encoding="utf-8-sig") as f:
        satirlar = list(csv.DictReader(f))
    for s in satirlar:
        for k in SUTUNLAR:
            s[k] = (s.get(k) or "").strip()
    return satirlar


def yaz(satirlar, yol=CSV_YOLU):
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=SUTUNLAR, extrasaction="ignore")
        w.writeheader()
        for s in satirlar:
            w.writerow({k: s.get(k, "") for k in SUTUNLAR})
