"""data/kaynaklar.csv dosyasından data/kaynaklar.json ve README.md üretir.

Kullanım:  python scripts/build.py
Hata varsa (eksik zorunlu alan, tekrar eden id/URL) çıkış kodu 1 olur ve hiçbir dosya yazılmaz.
"""
import datetime as dt
import json
import sys
from collections import Counter

from ortak import KOK, SUTUNLAR, ZORUNLU, oku

SITE = "https://sdanacioglu.github.io/bakircay-cbs-acik-veri-kaynaklari/"
DEPO = "https://github.com/sdanacioglu/bakircay-cbs-acik-veri-kaynaklari"
TR_KAPSAM = {"Türkiye", "İzmir", "İstanbul", "Ordu"}
YIL = "2026"
ATIF = (f"Danacıoğlu, Ş. ({YIL}). *Bakırçay CBS Açık Veri Kaynakları* [Veri seti]. "
        f"İzmir Bakırçay Üniversitesi Coğrafi Bilgi Sistemleri Topluluğu. {DEPO}")


def norm_url(u):
    u = u.lower().strip()
    for p in ("https://", "http://"):
        if u.startswith(p):
            u = u[len(p):]
    if u.startswith("www."):
        u = u[4:]
    return u.rstrip("/")


def dogrula(satirlar):
    hatalar = []
    for i, s in enumerate(satirlar, start=2):
        for k in ZORUNLU:
            if not s[k]:
                hatalar.append(f"{i}. satır: '{k}' boş ({s['ad'] or s['url']})")
    for alan, f in (("id", lambda s: s["id"]), ("url", lambda s: norm_url(s["url"]))):
        c = Counter(f(s) for s in satirlar if s[alan])
        hatalar += [f"Tekrar eden {alan}: {k}" for k, n in c.items() if n > 1]
    return hatalar


def md(t):
    return t.replace("|", "\\|").replace("\n", " ")


def tablo(satirlar, aciklama=True):
    bas = "| Ad | Kapsam | Konu | Veri | İndirilebilir |" + (" Açıklama |" if aciklama else "")
    ayr = "|---|---|---|---|---|" + ("---|" if aciklama else "")
    sat = [f"| [{md(s['ad'])}]({s['url']}) | {md(s['kapsam'])} | {md(s['konu'])} | {md(s['veri_turu'])} | {md(s['indirilebilir'])} |"
           + (f" {md(s['aciklama'])} |" if aciklama else "") for s in satirlar]
    return "\n".join([bas, ayr, *sat])


def main():
    satirlar = oku()
    hatalar = dogrula(satirlar)
    if hatalar:
        print("❌ Doğrulama hataları:\n  " + "\n  ".join(hatalar))
        sys.exit(1)

    tr_once = lambda s: (0 if s["kapsam"] in TR_KAPSAM else 1, s["kapsam"] != "Türkiye", s["ad"].lower())
    satirlar.sort(key=tr_once)
    bugun = dt.date.today().isoformat()
    gorunen = [s for s in satirlar if s["durum"] != "erişilemiyor"]
    aktif = [s for s in satirlar if s["durum"] == "aktif"]
    tr = [s for s in gorunen if s["kapsam"] in TR_KAPSAM]
    oneri = [s for s in gorunen if s["onerilen"] == "Evet" and s["kapsam"] not in TR_KAPSAM]
    son_kontrol = max((s["son_kontrol"] for s in satirlar if s["son_kontrol"]), default="—")

    meta = {
        "baslik": "Bakırçay CBS Açık Veri Kaynakları",
        "uretim_tarihi": bugun,
        "son_baglanti_kontrolu": son_kontrol,
        "toplam": len(satirlar),
        "aktif": len(aktif),
        "turkiye": len(tr),
        "durumlar": dict(Counter(s["durum"] or "kontrol edilmedi" for s in satirlar)),
        "sutunlar": SUTUNLAR,
    }
    (KOK / "data" / "kaynaklar.json").write_text(
        json.dumps({"meta": meta, "kaynaklar": satirlar}, ensure_ascii=False, indent=1), encoding="utf-8")

    readme = f"""# Bakırçay CBS Açık Veri Kaynakları

**Hazırlayan:** Dr. Şevki Danacıoğlu · İzmir Bakırçay Üniversitesi Coğrafi Bilgi Sistemleri Topluluğu (BakırçayCBS), {YIL}

Sürekli güncellenen açık coğrafi veri kaynakları arşivi.
Türkiye'den kaynaklar ve dünyadan seçilmiş veri depoları, CBS platformları ve kataloglar tek listede.

### 🔎 [Arşivde ara ve filtrele →]({SITE})

| | |
|---|---|
| Toplam kayıt | **{len(satirlar)}** |
| Etkin bağlantı | **{len(aktif)}** |
| Türkiye kaynakları | **{len(tr)}** |
| Son bağlantı kontrolü | {son_kontrol} |

**Veriyi indir:** [CSV](data/kaynaklar.csv) · [JSON](data/kaynaklar.json) · [Bağlantı raporu](reports/baglanti_raporu.md)

## 🇹🇷 Türkiye kaynakları

{tablo(tr)}

## ⭐ Öne çıkan küresel kaynaklar

{tablo(oneri)}

Diğer {len(gorunen) - len(tr) - len(oneri)} kaynak için [arama sayfasını]({SITE}) ya da [CSV dosyasını](data/kaynaklar.csv) kullanın.

## Teşekkür ve kaynakça

- Küresel kayıtların büyük bölümü, **Sven Schmitz-Leuffen**'in UN Environment Programme (UNEP) için derlediği *GIS Data Repositories* listesinden (2019) alınmıştır. O liste de **Robin Wilson** ([Free GIS Data](https://freegisdata.rtwilson.com/)) ve **Karen Payne** (University of Georgia) derlemelerine dayanır. Bu kayıtlar `kaynak_listesi = UNEP 2019` ile işaretlidir.
- Bazı kayıtlar [#30DayMapChallenge kaynaklar sayfasından](https://30daymapchallenge.com/resources/) alınmıştır (`kaynak_listesi = 30DayMapChallenge`).
- Türkiye kaynakları ve diğer eklemeler BakırçayCBS tarafından derlenmiştir.

Her veri kaynağının kendi kullanım koşulları geçerlidir; kullanmadan önce ilgili sitedeki lisansı kontrol edin.
"""
    (KOK / "README.md").write_text(readme, encoding="utf-8")
    print(f"✅ {len(satirlar)} kayıt · aktif {len(aktif)} · Türkiye {len(tr)} · öne çıkan {len(oneri)}")


if __name__ == "__main__":
    main()
