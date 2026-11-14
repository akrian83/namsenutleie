#!/usr/bin/env python3
"""Bygger namsenutleie.no som statisk nettsted (dist/) og en én-fils forhåndsvisning (preview/index.html)."""
import os, shutil, html, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://www.namsenutleie.no"
SHOP = "https://namsen-utleie.booqableshop.com"
SHOP_VOGN = SHOP + "/products/adria-altea-522-m-3-koyer"
NB = "\u00a0"
BASE = os.environ.get("SITE_BASE", "").rstrip("/")  # f.eks. "/namsenutleie" ved test på github.io
SHOP_P = SHOP + "/products/"
WIX = "https://static.wixstatic.com/media/"
BQ = "https://content.booqablecdn.com/uploads/59647ca9ef31fb77bc74ed95fc675be5/photo/photo/"
# lokalt filnavn -> kilde. Hentes én gang av fetch-images.sh og lagres i images/.
IMAGES = {
    "snoskuter-hero.jpg": WIX + "fcca76_0763720b8c004f38adf46616ff1198a3~mv2.jpeg",
    "adria-eksterior-1.jpg": WIX + "fcca76_e4ff55a4c86b4eacba7f2e4e50ad6335~mv2.jpg",
    "adria-eksterior-2.jpg": WIX + "fcca76_637696227d964964a059dca22c9a4ce3~mv2.jpg",
    "adria-eksterior-3.jpg": WIX + "fcca76_e2e605eae9bf41de806890cb89f20763~mv2.jpg",
    "adria-eksterior-4.jpg": WIX + "fcca76_0f980ecfc2794ceaa837dad039db092b~mv2.jpg",
    "adria-interior-1.jpg": WIX + "fcca76_822f3fe4449e48af8679467504222baa~mv2.jpg",
    "adria-interior-2.jpg": WIX + "fcca76_4f264f7bc7f8478bae3b959468ee1897~mv2.jpg",
    "adria-interior-3.jpg": WIX + "fcca76_46db76e4f102430eab62807a63f9f028~mv2.jpg",
    "adria-interior-4.jpg": WIX + "fcca76_4c391daafe11426d835108dc2790c87c~mv2.jpg",
    "adria-interior-5.jpg": WIX + "fcca76_43382aaf37fb4bcd861e69f44bdc9aee~mv2.jpg",
    "adria-interior-6.jpg": WIX + "fcca76_1342e13ea0704ebebdb81e3177517f27~mv2.jpg",
    "adria-interior-7.jpg": WIX + "fcca76_d60fd7d69fff448995cfe270fd6b3cc3~mv2.jpg",
    "polaris-sks.jpg": BQ + "f45aefd1-b529-4f1c-bcc1-68490b3839df/polaris-800-sks.jpeg",
    "polaris-rmk.jpg": BQ + "80e0c6dc-03fd-4e4d-b6a6-0432120728d5/polaris-850-pro-rmk.jpeg",
    "henger-side.jpg": WIX + "fcca76_2bfe0e41809c43bdbd4d40407b36994d~mv2.jpeg",
    "henger.jpg": BQ + "fdd4f653-6222-4f94-8182-f865110a1839/henger-innside.jpeg",
}

# slug -> (hash-navn i forhåndsvisning, menynavn)
PAGES = {
    "": ("hjem", "Hjem"),
    "utleie": ("utleie", "Utleie"),
    "adria-altea-552-pk-galleri": ("campingvogn", "Campingvogn"),
    "snoskuter": ("snoskuter", "Snøskuter"),
    "henger": ("henger", "Henger"),
    "racing-simulator": ("racing-simulator", "Racing-simulator"),
    "om-oss": ("om-oss", "Om oss"),
    "kontakt": ("kontakt", "Kontakt"),
    "vilkar": ("vilkar", "Vilkår"),
}
MAIN_NAV = ["", "utleie", "om-oss", "kontakt", "vilkar"]
SUB_NAV = ["adria-altea-552-pk-galleri", "snoskuter", "henger", "racing-simulator"]

CSS = """
:root{
  /* Layout: mørk granskog-stripe øverst og nederst, lyse flater imellom, én signalfarge for booking */
  --snow:#f2f5f3; --paper:#ffffff; --ink:#10231d; --muted:#4f615a; --line:#d3dcd7;
  --brand:#17463a; --deep:#123a30; --on-deep:#eef4f1; --on-deep-muted:#b5cbc2; --signal:#c2410c;
  --display:"Archivo",system-ui,-apple-system,"Segoe UI",sans-serif;
  --body:"Source Sans 3",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark; --snow:#0d1814; --paper:#15231e; --ink:#e8efeb; --muted:#a2b5ad; --line:#2a3c35;
  --brand:#9bd3be; --deep:#0f2d25;}}
:root[data-theme="dark"]{
  color-scheme:dark; --snow:#0d1814; --paper:#15231e; --ink:#e8efeb; --muted:#a2b5ad; --line:#2a3c35;
  --brand:#9bd3be; --deep:#0f2d25;}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--snow);color:var(--ink);font:400 1.0625rem/1.6 var(--body)}
img{max-width:100%;display:block}
a{color:var(--brand)}
a:focus-visible,.btn:focus-visible{outline:3px solid var(--signal);outline-offset:3px}
h1,h2,h3{font-family:var(--display);line-height:1.15;text-wrap:balance;margin:0}
h1{font-size:clamp(1.9rem,5vw,3rem);font-weight:800;letter-spacing:-.01em}
h2{font-size:clamp(1.35rem,3vw,1.75rem);font-weight:700}
h3{font-size:1.05rem;font-weight:700}
p{margin:0;max-width:65ch}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.stack{display:flex;flex-direction:column;gap:18px}
.site-head{background:var(--deep);color:var(--on-deep)}
.site-head .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 24px;padding-top:14px;padding-bottom:14px}
.mark{font:800 1.25rem/1 var(--display);color:var(--on-deep);text-decoration:none;letter-spacing:.02em;text-transform:uppercase}
.mark span{color:#f4a261}
nav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 18px}
.site-head nav a{color:var(--on-deep);text-decoration:none;font-weight:600;padding:6px 0;display:inline-block;border-bottom:2px solid transparent}
.site-head nav a:hover,.site-head nav a[aria-current="page"]{border-bottom-color:#f4a261}
.subnav{background:var(--paper);border-bottom:1px solid var(--line)}
.subnav .wrap{padding-top:10px;padding-bottom:10px}
.subnav a{text-decoration:none;font-weight:600;color:var(--muted)}
.subnav a[aria-current="page"],.subnav a:hover{color:var(--brand)}
.hero{background:var(--deep);color:var(--on-deep)}
.hero .wrap{display:grid;grid-template-columns:1.1fr 1fr;gap:32px;align-items:center;padding-top:40px;padding-bottom:48px}
.hero p{color:var(--on-deep-muted);font-size:1.15rem}
main .wrap{padding-top:40px;padding-bottom:56px}
.lead{font-size:1.15rem;color:var(--muted)}
.btn{display:inline-block;background:var(--signal);color:#fff;font:700 1rem/1 var(--display);text-decoration:none;padding:14px 22px;border-radius:6px;align-self:flex-start}
.btn:hover{filter:brightness(1.1)}
.btn.ghost{background:transparent;color:var(--brand);border:2px solid var(--brand);padding:12px 20px}
.row{display:flex;flex-wrap:wrap;gap:12px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:20px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
.card .body{padding:18px;display:flex;flex-direction:column;gap:10px;flex:1}
.card .btn{margin-top:auto}
.price{font:700 1.1rem/1.2 var(--display);font-variant-numeric:tabular-nums;color:var(--ink)}
.tag{font:700 .78rem/1 var(--display);letter-spacing:.08em;text-transform:uppercase;color:var(--signal);max-width:none}
.price small{font:400 .95rem var(--body);color:var(--muted)}
.shot{margin:0;aspect-ratio:4/3;background:var(--line);overflow:hidden}
.shot img{width:100%;height:100%;object-fit:cover}
.shot.ph{display:flex;align-items:center;justify-content:center;padding:14px;text-align:center;color:var(--muted);font-size:.9rem;
  background:repeating-linear-gradient(135deg,var(--line) 0 12px,transparent 12px 24px)}
.hero .shot{border-radius:8px;aspect-ratio:16/10}
.hero .shot.ph{color:var(--on-deep-muted);background:repeating-linear-gradient(135deg,rgba(255,255,255,.1) 0 12px,transparent 12px 24px)}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.gallery figure{margin:0;display:flex;flex-direction:column;gap:6px}
.gallery .shot{border-radius:6px}
.gallery figcaption{font-size:.92rem;color:var(--muted)}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:20px;display:flex;flex-direction:column;gap:12px}
dl.spec{margin:0;display:grid;grid-template-columns:auto 1fr;gap:6px 18px;font-variant-numeric:tabular-nums}
dl.spec dt{color:var(--muted)} dl.spec dd{margin:0;font-weight:600;text-align:right;overflow-wrap:anywhere}
ul.tick{margin:0;padding-left:1.1em;display:flex;flex-direction:column;gap:4px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;background:var(--paper);border:1px solid var(--line);border-radius:8px;font-variant-numeric:tabular-nums}
th,td{padding:12px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-family:var(--display);font-size:.9rem;color:var(--muted)}
td.num,th.num{text-align:right;white-space:nowrap}
tr:last-child td{border-bottom:0}
.note{border-left:4px solid var(--signal);background:var(--paper);padding:14px 16px;border-radius:0 6px 6px 0}
.terms{display:flex;flex-direction:column;gap:22px;max-width:70ch}
.terms section{display:flex;flex-direction:column;gap:8px}
.site-foot{background:var(--deep);color:var(--on-deep-muted)}
.site-foot .wrap{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px;padding-top:36px;padding-bottom:36px}
.site-foot h2{font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;color:var(--on-deep)}
.site-foot a{color:var(--on-deep)}
.site-foot address{font-style:normal}
.site-foot .stack{gap:10px}
@media (max-width:720px){.hero .wrap{grid-template-columns:1fr;padding-top:28px;padding-bottom:32px}}
@media (prefers-reduced-motion:no-preference){.btn{transition:filter .15s}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">')


class Ctx:
    def __init__(self, preview):
        self.preview = preview

    def link(self, slug):
        return "#" + PAGES[slug][0] if self.preview else (BASE + "/" + slug + "/" if slug else BASE + "/")

    def img(self, fname, alt, eager=False):
        if self.preview:
            return f'<div class="shot ph" role="img" aria-label="{html.escape(alt)}"><span>Bilde: {html.escape(alt)}</span></div>'
        load = "" if eager else ' loading="lazy"'
        return f'<div class="shot"><img src="{BASE}/images/{fname}" alt="{html.escape(alt)}"{load}></div>'


def kr(n):
    return f"{n:,}".replace(",", NB) + NB + "kr"


def book(url, label="Sjekk tilgjengelighet og book"):
    return f'<a class="btn" href="{url}">{label}</a>'


# ---------- Sideinnhold ----------

def p_home(c):
    cards = [
        ("adria-altea-552-pk-galleri", "Campingvogn", "Adria Altea 552 PK med tre køyer.", f"{kr(6500)} <small>per uke</small>"),
        ("snoskuter", "Snøskuter", "To Polaris-skutere, enkeltvis eller som pakke med henger.", f"fra {kr(1990)} <small>per døgn</small>"),
        ("henger", "Henger", "Lukket henger for skuter og varer.", f"{kr(700)} <small>per døgn</small>"),
        ("racing-simulator", "Racing-simulator", "Fullskala rigg med tre skjermer.", f"{kr(5500)} <small>inntil 4 døgn</small>"),
    ]
    items = "".join(
        f'<article class="card"><div class="body"><h3>{t}</h3><p>{d}</p><p class="price">{pr}</p>'
        f'<a class="btn ghost" href="{c.link(s)}">Se {t.lower()}</a></div></article>' for s, t, d, pr in cards)
    return f"""
<section class="hero"><div class="wrap">
  <div class="stack">
    <h1>Utstyr til tur og transport – hele året</h1>
    <p>Lei campingvogn, snøskuter, henger og racing-simulator i Overhalla og Namdalen. Book på nett og hent utstyret i Overhalla.</p>
    <a class="btn" href="{c.link('utleie')}">Se utstyr</a>
  </div>
  {c.img('snoskuter-hero.jpg', 'To Polaris snøskutere i dyp snø – snøskuter til leie i Overhalla', eager=True)}
</div></section>
<main><div class="wrap stack" style="gap:24px">
  <h2>Dette kan du leie</h2>
  <div class="cards">{items}</div>
</div></main>"""


def p_utleie(c):
    rows = [
        ("adria-altea-552-pk-galleri", "adria-eksterior-1.jpg", "Adria Altea 552 PK campingvogn sett utvendig fra front og side",
         "Adria Altea 552 m/3 køyer", "Praktisk campingvogn med 3 køyer og god plass til familieferie. Egenvekt 1310 kg og bredde 230 cm – passer også bak elbil.",
         f"{kr(6500)} <small>per uke · depositum {kr(10000)}</small>"),
        ("snoskuter", "snoskuter-hero.jpg", "To Polaris snøskutere i dyp snø",
         "Snøskuter til leie", "Polaris SKS 800 og PRO RMK 850. Løypeskuter og fjellskuter – alene eller i pakke med henger.",
         f"fra {kr(1990)} <small>per døgn · depositum {kr(5000)}</small>"),
        ("henger", "henger-side.jpg", "Skuter- og varehengeren sett fra siden",
         "Henger til leie", "Skuter- og varehenger. Til snøskuter, flyttelass, hageavfall og annen frakt. Henting i Overhalla.",
         f"fra {kr(700)} <small>per døgn · depositum {kr(2000)}</small>"),
        ("racing-simulator", None, "",
         "Simulator til leie", "Fullskala rigg med tre skjermer. Til bursdagen, helgen eller firmafesten. Levering i Namdalen for bedrifter.",
         f"{kr(5500)} <small>inntil 4 døgn</small>"),
    ]
    cards = "".join(
        f'<article class="card">{c.img(f, alt) if f else ""}<div class="body"><h2>{t}</h2><p>{d}</p><p class="price">{pr}</p>'
        f'<a class="btn" href="{c.link(s)}">Se detaljer og book</a></div></article>' for s, f, alt, t, d, pr in rows)
    return f"""<main><div class="wrap stack" style="gap:24px">
  <h1>Utleie i Overhalla og Namdalen</h1>
  <p class="lead">Velg utstyr, sjekk tilgjengelighet og betal på nett. Alle priser er inkludert mva.</p>
  <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">{cards}</div>
</div></main>"""


def p_vogn(c):
    ext = [("adria-eksterior-1.jpg", "Adria Altea 552 PK campingvogn sett utvendig fra front og side", "Adria Altea 552 PK eksteriør"),
           ("adria-eksterior-2.jpg", "Adria Altea 552 PK campingvogn sett fra siden med moderne eksteriør", "Enkelt og praktisk utsveivbar markise"),
           ("adria-eksterior-3.jpg", "Adria Altea 552 PK campingvogn sett forfra", "Flott design"),
           ("adria-eksterior-4.jpg", "Adria Altea 552 PK campingvogn koblet til bil klar for tur", "Lett og smal vogn – enkel på tur med elbil")]
    inn = [("adria-interior-1.jpg", "Interiør i Adria Altea 552 PK campingvogn med lyst og moderne oppholdsrom", "Flott og moderne vogn"),
           ("adria-interior-2.jpg", "Dobbeltseng foran i Adria Altea 552 PK campingvogn", "Dobbeltseng foran"),
           ("adria-interior-3.jpg", "Tre køyesenger bak i Adria Altea 552 PK familievogn", "3 køyesenger bak"),
           ("adria-interior-4.jpg", "Kjøkken i Adria Altea 552 PK med kokeplater, vask og oppbevaring", "Fullt utstyrt kjøkken med alle nødvendigheter"),
           ("adria-interior-5.jpg", "Sittegruppe i Adria Altea 552 PK campingvogn", "Hyggelig oppholdsrom for måltider og avslapning"),
           ("adria-interior-6.jpg", "Bad og toalett i Adria Altea 552 PK campingvogn", "Kompakt og funksjonelt bad med dusjfasiliteter"),
           ("adria-interior-7.jpg", "Dusjrom i Adria Altea 552 PK campingvogn", "Eget dusjkabinett – luksus på tur")]
    g = lambda lst: "".join(f"<figure>{c.img(f, a)}<figcaption>{cap}</figcaption></figure>" for f, a, cap in lst)
    return f"""<main><div class="wrap stack" style="gap:32px">
  <div class="stack">
    <h1>Leie av Adria Altea 552 PK</h1>
    <p class="lead">Se utvendige og innvendige bilder av vogna her før du booker.</p>
    <p class="price">{kr(6500)} <small>per uke · depositum {kr(10000)} · aldersgrense 23 år</small></p>
    {book(SHOP_VOGN, 'Lei Adria Altea')}
  </div>
  <div class="stack"><h2>Utvendige bilder</h2><div class="gallery">{g(ext)}</div></div>
  <div class="stack"><h2>Innvendige fasiliteter</h2><div class="gallery">{g(inn)}</div></div>
  <div class="two">
    <div class="panel"><h3>Nøkkeldata</h3><dl class="spec">
      <dt>Modellår</dt><dd>2026</dd><dt>Lengde</dt><dd>760 cm</dd><dt>Bredde</dt><dd>230 cm</dd>
      <dt>Egenvekt</dt><dd>1310 kg</dd><dt>Totalvekt</dt><dd>1500 kg</dd><dt>Soveplasser</dt><dd>opptil 7</dd></dl></div>
    <div class="panel"><h3>Viktig utstyr</h3><ul class="tick">
      <li>Smart-TV</li><li>Elektrisk gulvvarme</li><li>Sentralvarme på strøm/gass</li><li>Markise</li>
      <li>Komplett kjøkkenutstyr</li><li>Noe campingmøbler inkludert</li></ul></div>
  </div>
  <div class="panel"><h2>Klar for tur?</h2>
    <p>Sjekk ledige uker og book direkte. Les <a href="{c.link('vilkar')}">vilkårene</a> før du bestiller.</p>
    {book(SHOP_VOGN, 'Lei Adria Altea')}</div>
</div></main>"""


def p_skuter(c):
    def sk(img, alt, tag, name, txt, motor, price, helg, slug):
        return f"""<article class="card">{c.img(img, alt)}<div class="body">
      <p class="tag">{tag}</p><h2>{name}</h2><p>{txt}</p>
      <dl class="spec"><dt>Motor</dt><dd>{motor}</dd><dt>Belte</dt><dd>155″</dd><dt>Depositum</dt><dd>{kr(5000)}</dd></dl>
      <p class="price">Fra {kr(price)} <small>per døgn · helg {kr(helg)}</small></p>{book(SHOP_P + slug, 'Book nå')}</div></article>"""
    def pk(name, txt, price, slug):
        return f"""<article class="card"><div class="body"><h3>{name}</h3><p>{txt}</p>
      <p class="price">Fra {kr(price)} <small>per døgn</small></p>{book(SHOP_P + slug, 'Book pakke')}</div></article>"""
    return f"""<main><div class="wrap stack" style="gap:32px">
  <div class="stack">
    <h1>Snøskuter til leie i Namdalen</h1>
    <p class="lead">Lei en godt vedlikeholdt Polaris for en dag på løypa, en helg på hytta eller en isfisketur. Vi har to skutere – én for trygg løypekjøring og én for deg som vil ut i dyp snø. Lei dem alene, eller som pakke med skuterhenger.</p>
  </div>
  <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">
    {sk('polaris-sks.jpg', 'Sort Polaris 800 SKS 155 snøskuter', 'Løype og tur', 'Polaris 800 SKS 155', 'Allsidig skuter med god komfort og justerbare støtdempere. Stabil på hardpakket løype – et trygt valg for deg som kjører mest i løypene.', '800 cc totakt', 1990, 3980, 'polaris-800-sks-155')}
    {sk('polaris-rmk.jpg', 'Gul Polaris 850 PRO RMK 155 snøskuter', 'Dyp snø og fjell', 'Polaris 850 PRO RMK 155', 'Lett fjellskuter bygget for løs snø og bratt terreng. Passer for erfarne førere som vil utforske.', '850 cc totakt', 2290, 4580, 'polaris-850-pro-rmk-155')}
  </div>
  <div class="stack"><h2>Pakker med skuterhenger</h2><p>Ca. 10{NB}% rimeligere enn å leie hver for seg.</p>
  <div class="cards">
    {pk('SKS 800 + henger', 'Løypeskuteren og skuterhengeren i én bestilling.', 2421, 'pakke-polaris-800-sks-henger')}
    {pk('PRO RMK 850 + henger', 'Fjellskuteren og skuterhengeren i én bestilling.', 2691, 'pakke-polaris-850-pro-rmk-henger')}
    {pk('2 snøskutere + henger', 'Begge skuterne og hengeren – ta med hele gjengen.', 4482, 'pakke-2-snoskutere-henger')}
  </div></div>
  <div class="note stack" style="gap:8px"><h3>Dette må du vite</h3><ul class="tick">
    <li>Førerkort klasse S, eller førerett i klasse B fra før 1. juli 2006. Vi sjekker førerkort ved utlevering.</li>
    <li>Kjøring kun i lovlige snøskuterløyper eller der du har tillatelse. Du er selv ansvarlig for løypekort og lokale regler.</li>
    <li>Hjelm er påbudt.</li>
    <li>Skuteren leveres med full tank og skal leveres tilbake med full tank.</li>
    <li>Se våre <a href="{c.link('vilkar')}">leievilkår</a>.</li></ul></div>
</div></main>"""


def p_henger(c):
    return f"""<main><div class="wrap stack" style="gap:32px">
  <div class="stack">
    <h1>Henger til leie i Overhalla</h1>
    <p class="lead">Vår henger er både skuterhenger og varehenger. Frakt snøskuteren til hytta om vinteren – eller bruk den til flyttelass, hageavfall, byggevarer og annet utstyr resten av året.</p>
    <div style="max-width:560px">{c.img('henger-side.jpg', 'Skuter- og varehengeren sett fra siden')}</div>
  </div>
  <div class="two">
    <article class="card">{c.img('henger.jpg', 'Lasterommet i hengeren')}<div class="body">
      <p class="tag">Hele året</p><h2>Skuter- og varehenger</h2>
      <p>Allsidig henger for snøskuter og vanlig varetransport. Henting i Overhalla.</p>
      <dl class="spec"><dt>Bruk</dt><dd>snøskuter, flytting, hageavfall, byggevarer m.m.</dd><dt>Depositum</dt><dd>{kr(2000)}</dd>
      <dt>Mål</dt><dd>5,96 × 2,01 m (total lengde og bredde)</dd><dt>Nyttelast</dt><dd>880 kg</dd><dt>Tillatt totalvekt</dt><dd>1{NB}260 kg</dd></dl>
      <p class="price">Fra {kr(700)} <small>per døgn · helg {kr(1400)}</small></p>{book(SHOP_P + 'snoskutertilhenger', 'Book henger')}</div></article>
    <article class="card"><div class="body"><p class="tag">Vinterpakke</p><h2>Henger + snøskuter</h2>
      <p>Lei hengeren sammen med én eller begge skuterne og spar ca. 10{NB}%.</p>
      <dl class="spec"><dt>SKS 800 + henger</dt><dd>fra {kr(2421)}/døgn</dd><dt>PRO RMK 850 + henger</dt><dd>fra {kr(2691)}/døgn</dd><dt>2 skutere + henger</dt><dd>fra {kr(4482)}/døgn</dd></dl>
      <a class="btn ghost" href="{c.link('snoskuter')}">Se skuterpakkene</a></div></article>
  </div>
  <div class="note stack" style="gap:8px"><h3>Dette må du vite</h3><ul class="tick">
    <li>Bilen må ha hengerfeste og tillatt tilhengervekt som dekker hengeren med last (inntil 1{NB}260 kg).</li>
    <li>Med førerkort B kan bil og henger ha samlet tillatt totalvekt på inntil 3{NB}500 kg. Over det trengs B96 (inntil 4{NB}250 kg) eller BE. Sjekk bilens vognkort.</li>
    <li>Lasten skal sikres forskriftsmessig, og hengeren leveres tilbake ryddet og uten avfall.</li>
    <li>Skader meldes umiddelbart. Se våre <a href="{c.link('vilkar')}">leievilkår</a>.</li></ul></div>
</div></main>"""


def p_sim(c):
    return f"""<main><div class="wrap stack" style="gap:32px">
  <div class="stack">
    <h1>Racing-simulator til leie</h1>
    <p class="lead">Til firmafesten, bursdagen eller helgen. Fullskala simulator med direktedrevet ratt, pedaler i klubbsportklasse og tre 32″ buede skjermer – en realistisk følelse av å sitte i en racerbil.</p>
  </div>
  <div class="two">
    <div class="panel"><p class="tag">Utstyr</p><h2>Dette får du</h2><dl class="spec">
      <dt>Cockpit</dt><dd>Trak Racer TR160 med Sparco Circuit-sete</dd>
      <dt>Ratt</dt><dd>Fanatec CSL DD 8 Nm, Formula- og Nascar-ratt</dd>
      <dt>Pedaler</dt><dd>Fanatec ClubSport V3 med performance kit</dd>
      <dt>Girspak og håndbrekk</dt><dd>Fanatec</dd>
      <dt>Skjerm</dt><dd>3 × 32″ buede gamingskjermer</dd>
      <dt>PC</dt><dd>Intel Core i9, RTX 2080 Ti, 32 GB RAM</dd></dl></div>
    <div class="panel"><p class="tag">Privat</p><h2>Lei for helgen</h2>
      <p>Perfekt for bursdag eller en helg med trening. Kort opplæring ved utlevering.</p>
      <dl class="spec"><dt>Inntil 4 døgn</dt><dd>{kr(5500)} – minstepris, helgen inkludert</dd><dt>Ekstra døgn</dt><dd>{kr(600)} per døgn</dd><dt>Depositum</dt><dd>{kr(3000)}</dd></dl>
      <p class="price">{kr(5500)} <small>inntil 4 døgn</small></p>{book(SHOP_P + 'racing-simulator', 'Book nå')}</div>
  </div>
  <div class="panel"><h2>Bedrift og arrangement</h2>
    <p>Firmafest, messe eller teambuilding – med konkurranse og resultatliste.</p>
    <p>Vi leverer, rigger opp og henter i Namdalen. Pris etter omfang, fra {kr(5500)}.</p>
    <a class="btn ghost" href="{c.link('kontakt')}">Be om tilbud</a></div>
  <p>Utstyret skal stå innendørs og tørt. Se våre <a href="{c.link('vilkar')}">leievilkår</a>.</p>
</div></main>"""


def p_om(c):
    return f"""<main><div class="wrap stack">
  <h1>Om oss</h1>
  <p class="lead">Namsen Utleie er et lokalt utleiefirma i Namdalen.</p>
  <p>Vi leier ut campingvogn, snøskuter, henger og praktisk utstyr til privatpersoner og bedrifter. Vi legger vekt på enkel utleie, god tilgjengelighet og ryddige avtaler, enten du trenger utstyret en helg eller over lengre tid.</p>
  <p>Namsen Utleie drives av Andreas K. Rian gjennom AKRI Holding AS og holder til i Overhalla kommune.</p>
  <a class="btn" href="{c.link('kontakt')}">Kontakt oss</a>
</div></main>"""


def p_kontakt(c):
    return f"""<main><div class="wrap stack" style="gap:24px">
  <h1>Kontakt oss</h1>
  <p class="lead">Spørsmål om utstyr, henting eller en bestilling? Send e-post eller ring.</p>
  <div class="two">
    <div class="panel"><h3>E-post</h3><p><a href="mailto:post@namsenutleie.no">post@namsenutleie.no</a></p></div>
    <div class="panel"><h3>Telefon</h3><p><a href="tel:+4795946855">+47 95 94 68 55</a></p></div>
    <div class="panel"><h3>Henting</h3><p>Namsen Utleie (AKRI Holding AS)<br>Svalivegen 84, 7863 Overhalla</p></div>
  </div>
</div></main>"""


TERMS = [
    ("1. Bestilling og betaling", ["Hele leiesummen betales ved bestilling, via digitale betalingsløsninger.", "Bestillingen er bindende når den er bekreftet.", "Depositum kan kreves for enkelte objekter."]),
    ("2. Henting og levering", ["Utstyret hentes og leveres på avtalt sted og til avtalt tid.", "Leietaker skal kontrollere utstyret ved henting.", "Avvik må meldes før bruken starter."]),
    ("3. Ansvar og bruk", ["Leietaker skal bruke utstyret forsvarlig, i tråd med trafikkregler og bruksanvisninger.", "Leietaker må selv sørge for riktig førerkortklasse og tillatt totalvekt.", "Kjøring utenfor Norge krever særskilt avtale."]),
    ("4. Skader og tap", ["Leietaker har fullt erstatningsansvar for skader og mangler i leieperioden.", f"Egenandel ved kaskoskade er inntil {kr(10000)}.", f"Et administrasjonsgebyr på {kr(1000)} kan komme i tillegg."]),
    ("5. Forsinket levering", [f"Ved forsinkelse belastes leietaker {kr(500)} per påbegynt time, med mindre annet er avtalt.", "Hvis forsinkelsen hindrer neste utleieforhold, kan leietaker holdes ansvarlig for utleierens øvrige tap."]),
    ("6. Rengjøring", ["Utstyret skal leveres tilbake rengjort og tømt for avfall.", f"Ved manglende rengjøring faktureres et gebyr etter tidsbruk og omfang, minimum {kr(500)}."]),
    ("7. Særskilte vilkår: Campingvogn", ["Leietaker må være minst 23 år.", "Røyking og husdyr er forbudt innvendig.", f"Toalett og vanntanker må tømmes før retur. Ved brudd belastes {kr(1500)}."]),
    ("8. Særskilte vilkår: Tilhenger", ["Lasten må sikres forsvarlig etter gjeldende forskrifter.", "Maksimal nyttelast må ikke overskrides.", "Skader på drag, lemmer eller lys skal meldes straks."]),
    ("9. Særskilte vilkår: Småutstyr", ["Utstyr som bruker drivstoff leveres tilbake med full tank.", "Bruk av feil drivstoff medfører fullt erstatningsansvar.", "Utstyret skal være rengjort for jord og gress."]),
    ("10. Avbestilling", ["Avbestilling inntil 7 dager før gir full refusjon.", f"Avbestilling 2–7 dager før gir 50{NB}% refusjon.", "Avbestilling senere enn 48 timer før gir ingen refusjon."]),
    ("11. Kansellering fra utleier", ["Ved teknisk svikt eller skade som gjør utstyret uegnet for utleie, kan utleier kansellere bestillingen.", "Leietaker får hele beløpet refundert."]),
    ("12. Kontakt", ['E-post: <a href="mailto:post@namsenutleie.no">post@namsenutleie.no</a>', 'Telefon: <a href="tel:+4795946855">+47 95 94 68 55</a>']),
]


def p_vilkar(c):
    secs = "".join(f'<section><h2>{t}</h2><ul class="tick">{"".join(f"<li>{x}</li>" for x in items)}</ul></section>' for t, items in TERMS)
    return f"""<main><div class="wrap stack" style="gap:24px">
  <h1>Vilkår for utleie</h1>
  <p class="lead">Namsen Utleie drives av AKRI Holding AS. Vilkårene er sist oppdatert januar 2026.</p>
  <div class="terms">{secs}</div>
</div></main>"""


BODY = {"": p_home, "utleie": p_utleie, "adria-altea-552-pk-galleri": p_vogn, "snoskuter": p_skuter, "henger": p_henger,
        "racing-simulator": p_sim, "om-oss": p_om, "kontakt": p_kontakt, "vilkar": p_vilkar}

META = {
    "": ("Lei campingvogn, snøskuter og henger i Overhalla | Namsen Utleie", "Lei campingvogn, snøskuter, henger og racing-simulator hos Namsen Utleie i Overhalla. Book på nett og hent utstyret i Overhalla."),
    "utleie": ("Utleie | Namsen Utleie", "Utleie av campingvogn, snøskuter, henger og racing-simulator i Overhalla og Namdalen."),
    "adria-altea-552-pk-galleri": ("Adria Altea 552 m/3 køyer | Namsen Utleie", "Lei Adria Altea 552 PK. Moderne og komfortabel campingvogn med praktiske løsninger for ferie og helgeturer."),
    "snoskuter": ("Snøskuter | Namsen Utleie", "Lei Polaris snøskuter i Overhalla. Enkeltvis eller som pakke med henger."),
    "henger": ("Henger | Namsen Utleie", "Lei lukket henger for snøskuter og varer i Overhalla."),
    "racing-simulator": ("Racing-simulator | Namsen Utleie", "Lei profesjonell racing-simulator med Fanatec-utstyr og tre skjermer."),
    "om-oss": ("Om oss | Namsen Utleie", "Namsen Utleie er et lokalt utleiefirma i Namdalen, drevet av AKRI Holding AS."),
    "kontakt": ("Kontakt | Namsen Utleie", "Kontakt Namsen Utleie på e-post eller telefon."),
    "vilkar": ("Vilkår | Namsen Utleie", "Vilkår for utleie hos Namsen Utleie."),
}


def header(c, cur):
    def li(s):
        on = ' aria-current="page"' if (s == cur or (s == "utleie" and cur in SUB_NAV)) else ""
        return f'<li><a href="{c.link(s)}"{on}>{PAGES[s][1]}</a></li>'
    out = (f'<header class="site-head"><div class="wrap"><a class="mark" href="{c.link("")}">Namsen <span>Utleie</span></a>'
           f'<nav aria-label="Hovedmeny"><ul>{"".join(li(s) for s in MAIN_NAV)}</ul></nav></div></header>')
    if cur == "utleie" or cur in SUB_NAV:
        sub = "".join(f'<li><a href="{c.link(s)}"{' aria-current="page"' if s == cur else ''}>{PAGES[s][1]}</a></li>' for s in SUB_NAV)
        out += f'<div class="subnav"><div class="wrap"><nav aria-label="Utstyr"><ul>{sub}</ul></nav></div></div>'
    return out


def footer(c):
    return f"""<footer class="site-foot"><div class="wrap">
  <div class="stack"><a class="mark" href="{c.link('')}">Namsen <span>Utleie</span></a>
    <p>Din lokale utleie av campingvogn, snøskuter, henger og racing-simulator i Namdalen.</p>
    <p>© 2026 Namsen Utleie (AKRI Holding AS). Alle rettigheter reservert.</p></div>
  <div class="stack"><h2>Kontakt oss</h2>
    <address>Namsen Utleie (AKRI Holding AS)<br>Svalivegen 84, 7863 Overhalla<br>
    <a href="mailto:post@namsenutleie.no">post@namsenutleie.no</a><br><a href="tel:+4795946855">+47 95 94 68 55</a></address></div>
  <div class="stack"><h2>Snarveier</h2>
    <a href="{c.link('utleie')}">Alt utstyr</a><a href="{c.link('vilkar')}">Vilkår</a></div>
</div></footer>"""


def build_site():
    dist = os.path.join(ROOT, "dist")
    shutil.rmtree(dist, ignore_errors=True)
    os.makedirs(os.path.join(dist, "images"))
    c = Ctx(False)
    with open(os.path.join(dist, "style.css"), "w") as f:
        f.write(CSS.strip() + "\n")
    urls = []
    for slug in PAGES:
        title, desc = META[slug]
        url = DOMAIN + ("/" + slug if slug else "")
        urls.append(url)
        doc = f"""<!DOCTYPE html>
<html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:image" content="{DOMAIN}/images/adria-eksterior-1.jpg">
{FONTS}<link rel="stylesheet" href="{BASE}/style.css"></head>
<body>{header(c, slug)}{BODY[slug](c)}{footer(c)}</body></html>
"""
        d = os.path.join(dist, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(doc)
    with open(os.path.join(dist, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(dist, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    open(os.path.join(dist, ".nojekyll"), "w").close()
    shutil.copy(os.path.join(dist, "index.html"), os.path.join(dist, "404.html"))
    with open(os.path.join(ROOT, "fetch-images.sh"), "w") as f:
        f.write("#!/bin/sh\n# Henter bilder som mangler i images/. Kjøres av GitHub Actions.\nset -u\nmkdir -p images\n")
        for name, src in IMAGES.items():
            f.write(f'[ -s "images/{name}" ] || curl -fsSL --retry 3 -o "images/{name}" "{src}" || echo "MANGLER: {name}"\n')
    src_img = os.path.join(ROOT, "images")
    if os.path.isdir(src_img):
        for fn in os.listdir(src_img):
            shutil.copy(os.path.join(src_img, fn), os.path.join(dist, "images", fn))
    zpath = os.path.join(ROOT, "namsenutleie-nettsted.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(dist):
            for fn in files:
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, dist))
        z.write(os.path.join(ROOT, "build.py"), "kilde/build.py")


def build_preview():
    c = Ctx(True)
    views = "".join(
        f'<div class="view" id="{PAGES[s][0]}" data-title="{html.escape(PAGES[s][1])}">{header(c, s)}{BODY[s](c)}</div>' for s in PAGES)
    names = [PAGES[s][0] for s in PAGES]
    doc = f"""<!DOCTYPE html>
<html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Namsen Utleie nettside</title>
{FONTS}<style>{CSS}
.js .view{{display:none}} .js .view.on{{display:block}}
.banner{{background:var(--signal);color:#fff;font-size:.9rem;padding:8px 20px;text-align:center}}
</style></head>
<body><div class="banner">Forhåndsvisning. Skraverte felt er plasser for bilder.</div>
{views}{footer(c)}
<script>
(function(){{
  var names={names!r};
  document.documentElement.classList.add('js');
  function show(){{
    var h=(location.hash||'').slice(1); if(names.indexOf(h)<0) h='hjem';
    names.forEach(function(n){{document.getElementById(n).classList.toggle('on',n===h);}});
    window.scrollTo(0,0);
  }}
  window.addEventListener('hashchange',show); show();
}})();
</script></body></html>
"""
    os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
    with open(os.path.join(ROOT, "preview", "index.html"), "w") as f:
        f.write(doc)


if __name__ == "__main__":
    build_site()
    build_preview()
    print("ok")
