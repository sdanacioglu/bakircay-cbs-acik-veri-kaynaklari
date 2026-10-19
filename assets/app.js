/* Bakırçay CBS Açık Veri Kaynakları — arama ve filtreleme */
(async function () {
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const TR = new Set(["Türkiye", "İzmir", "İstanbul", "Ordu"]);
  const SAYFA = 60;
  const trLower = s => String(s || "").toLocaleLowerCase("tr");
  const fold = s => trLower(s).normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ı/g, "i");

  let veri;
  try {
    veri = await (await fetch("data/kaynaklar.json", { cache: "no-cache" })).json();
  } catch (e) {
    $("liste").innerHTML = `<div class="card empty">Liste yüklenemedi. <a href="data/kaynaklar.csv">CSV dosyasını</a> indirebilirsin.</div>`;
    return;
  }
  const kayitlar = veri.kaynaklar.map(k => ({ ...k, _ara: fold([k.ad, k.aciklama, k.konu, k.kapsam, k.tur, k.url].join(" ")) }));
  const m = veri.meta;

  $("stats").innerHTML = `
    <div><strong>${m.toplam}</strong><span>kayıt</span></div>
    <div><strong>${m.aktif}</strong><span>etkin bağlantı</span></div>
    <div><strong>${m.turkiye}</strong><span>Türkiye kaynağı</span></div>
    <div><strong>${esc(m.son_baglanti_kontrolu)}</strong><span>son bağlantı kontrolü</span></div>`;
  $("guncelleme").textContent = `Liste güncellemesi: ${m.uretim_tarihi}`;

  /* Select options */
  const say = alan => { const c = new Map(); kayitlar.forEach(k => { if (k.durum !== "erişilemiyor" && k[alan]) c.set(k[alan], (c.get(k[alan]) || 0) + 1); }); return c; };
  const doldur = (sel, alan, ozel = []) => {
    const c = say(alan);
    const sirali = [...c.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "tr"));
    $(sel).innerHTML = `<option value="">Tümü</option>` + ozel.map(([v, l]) => `<option value="${esc(v)}">${esc(l)}</option>`).join("")
      + sirali.map(([v, n]) => `<option value="${esc(v)}">${esc(v)} (${n})</option>`).join("");
  };
  doldur("kapsam", "kapsam", [["@tr", "🇹🇷 Türkiye (tümü)"], ["@yabanci", "🌍 Türkiye dışı (tümü)"]]);
  doldur("konu", "konu");
  doldur("tur", "tur");

  /* URL state */
  const alanlar = ["q", "kapsam", "konu", "tur", "indir"], kutular = ["girissiz", "erisilemeyen"];
  const params = new URLSearchParams(location.search);
  alanlar.forEach(a => { if (params.has(a)) $(a).value = params.get(a); });
  kutular.forEach(a => { $(a).checked = params.get(a) === "1"; });

  let gosterilen = SAYFA, sonuc = [];

  const filtrele = () => {
    const q = fold($("q").value.trim()).split(/\s+/).filter(Boolean);
    const kap = $("kapsam").value, konu = $("konu").value, tur = $("tur").value, ind = $("indir").value;
    sonuc = kayitlar.filter(k =>
      ($("erisilemeyen").checked || k.durum !== "erişilemiyor") &&
      (!kap || (kap === "@tr" ? TR.has(k.kapsam) : kap === "@yabanci" ? !TR.has(k.kapsam) : k.kapsam === kap)) &&
      (!konu || k.konu === konu) && (!tur || k.tur === tur) && (!ind || k.indirilebilir === ind) &&
      (!$("girissiz").checked || k.giris_gerekli !== "Evet") &&
      q.every(t => k._ara.includes(t)));
    gosterilen = SAYFA;
    ciz();
    const p = new URLSearchParams();
    alanlar.forEach(a => { if ($(a).value) p.set(a, $(a).value); });
    kutular.forEach(a => { if ($(a).checked) p.set(a, "1"); });
    history.replaceState(null, "", p.toString() ? `?${p}` : location.pathname);
  };

  const rozet = k => {
    if (k.durum === "erişilemiyor") return `<span class="badge bad">erişilemiyor</span>`;
    if (k.durum === "kontrol edilemedi") return `<span class="badge warn" title="Son otomatik kontrolde yanıt alınamadı">kontrol edilemedi</span>`;
    if (k.durum === "arşiv") return `<span class="badge warn">arşiv</span>`;
    return "";
  };

  const ciz = () => {
    $("sayac").textContent = `${sonuc.length} kaynak`;
    $("liste").innerHTML = sonuc.length ? sonuc.slice(0, gosterilen).map(k => `
      <article class="card kaynak${TR.has(k.kapsam) ? " tr" : ""}">
        <div class="ust">
          <h2><a href="${esc(k.url)}" target="_blank" rel="noopener">${esc(k.ad)}</a>${k.onerilen === "Evet" ? ' <span title="Öne çıkan">⭐</span>' : ""}</h2>
          ${rozet(k)}
        </div>
        ${k.aciklama ? `<p>${esc(k.aciklama)}</p>` : ""}
        <div class="etiketler">
          <span class="et kapsam">${TR.has(k.kapsam) ? "🇹🇷 " : ""}${esc(k.kapsam)}</span>
          <span class="et">${esc(k.konu)}</span>
          <span class="et">${esc(k.tur)}</span>
          ${k.veri_turu ? `<span class="et">${esc(k.veri_turu)}</span>` : ""}
          ${k.indirilebilir ? `<span class="et">İndirme: ${esc(k.indirilebilir)}</span>` : ""}
          ${k.giris_gerekli === "Evet" ? `<span class="et">Üyelik gerekir</span>` : ""}
        </div>
        <div class="alt"><span class="url">${esc(k.url.replace(/^https?:\/\//, "").replace(/\/$/, ""))}</span><span>${esc(k.kaynak_listesi)}</span></div>
      </article>`).join("") : `<div class="card empty">Bu filtrelerle kaynak bulunamadı. Filtreleri temizlemeyi dene.</div>`;
    $("dahafazla").hidden = gosterilen >= sonuc.length;
  };

  $("filters").addEventListener("input", filtrele);
  $("filters").addEventListener("change", filtrele);
  $("dahafazla").addEventListener("click", () => { gosterilen += SAYFA; ciz(); });
  $("temizle").addEventListener("click", () => { alanlar.forEach(a => $(a).value = ""); kutular.forEach(a => $(a).checked = false); filtrele(); });
  $("paylas").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(location.href); $("paylas").textContent = "✅ Bağlantı kopyalandı"; }
    catch { prompt("Bağlantıyı kopyala:", location.href); }
    setTimeout(() => { $("paylas").textContent = "🔗 Bu listeyi paylaş"; }, 2000);
  });
  filtrele();
})();
