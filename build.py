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
    # adria-eksterior-5.jpg: lokalt bilde (ikke på Wix) – ligger i images/
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
    "hytte": ("hytte", "Hytte"),
    "om-oss": ("om-oss", "Om oss"),
    "kontakt": ("kontakt", "Kontakt"),
    "vilkar": ("vilkar", "Vilkår"),
}
MAIN_NAV = ["", "utleie", "om-oss", "kontakt", "vilkar"]
SUB_NAV = ["adria-altea-552-pk-galleri", "snoskuter", "henger", "racing-simulator", "hytte"]
# Utkast: bygges bare i forhåndsvisningen, ikke på det publiserte nettstedet.
# Fjern sluggen herfra når siden skal ut. Bildene ligger i utkast-bilder/ (ikke i git) til da.
DRAFT = {"hytte"}
# Sider som åpner med en fullskjerms bildescene (menyen legges over bildet).
HERO = {"", "adria-altea-552-pk-galleri", "snoskuter", "henger", "racing-simulator", "hytte"}

CSS = """
:root{
  /* Stil: mørk granskog og varm sand. Fullskjerms bildescener med korte setninger, rolige flater imellom. */
  --snow:#f5f0e8; --paper:#fbf8f3; --ink:#1f2a24; --muted:#58645d; --line:#ddd3c4;
  --brand:#1d4a3b; --deep:#14281f; --on-deep:#f3ead9; --on-deep-muted:#cdc1ab; --sand:#e6cfb3; --signal:#a8481a;
  --btn:#1d4a3b; --btn-ink:#ffffff;
  --display:"Cormorant Garamond","Iowan Old Style",Georgia,serif;
  --body:"Source Sans 3",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark; --snow:#0f1a15; --paper:#16241d; --ink:#efe7d8; --muted:#b3aa98; --line:#2c3b33;
  --brand:#a9d6c1; --deep:#0c1812; --btn:#e6cfb3; --btn-ink:#14281f; --signal:#f0a36b;}}
:root[data-theme="dark"]{
  color-scheme:dark; --snow:#0f1a15; --paper:#16241d; --ink:#efe7d8; --muted:#b3aa98; --line:#2c3b33;
  --brand:#a9d6c1; --deep:#0c1812; --btn:#e6cfb3; --btn-ink:#14281f; --signal:#f0a36b;}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--snow);color:var(--ink);font:400 1.0625rem/1.65 var(--body)}
img{max-width:100%;display:block}
a{color:var(--brand)}
a:focus-visible,.btn:focus-visible,summary:focus-visible,.strip:focus-visible{outline:3px solid var(--signal);outline-offset:3px}
h1,h2,h3{font-family:var(--display);font-weight:500;line-height:1.08;text-wrap:balance;margin:0}
h1{font-size:clamp(2.4rem,6vw,3.8rem)}
h2{font-size:clamp(1.9rem,4vw,2.8rem)}
h3{font:700 1.05rem/1.25 var(--body)}
p{margin:0;max-width:65ch}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.stack{display:flex;flex-direction:column;gap:18px}
.site-head{background:var(--deep);color:var(--on-deep)}
.site-head.over{position:absolute;inset:0 0 auto 0;z-index:5;background:linear-gradient(rgba(8,16,12,.72),rgba(8,16,12,0))}
.site-head .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 24px;padding-top:16px;padding-bottom:16px}
.mark{font:500 1.7rem/1 var(--display);color:var(--on-deep);text-decoration:none;letter-spacing:.02em}
.mark span{color:var(--sand);font-style:italic}
nav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 20px}
.site-head nav a{color:var(--on-deep);text-decoration:none;font-weight:600;font-size:.95rem;letter-spacing:.04em;padding:6px 0;display:inline-block;border-bottom:1px solid transparent}
.site-head nav a:hover,.site-head nav a[aria-current="page"]{border-bottom-color:var(--sand)}
.subnav{background:var(--paper);border-bottom:1px solid var(--line)}
.subnav .wrap{padding-top:10px;padding-bottom:10px}
.subnav a{text-decoration:none;font-weight:600;color:var(--muted)}
.subnav a[aria-current="page"],.subnav a:hover{color:var(--brand)}
main .wrap{padding-top:40px;padding-bottom:56px}
main .scene .wrap{padding-top:0;padding-bottom:0}
.lead{font-size:1.2rem;color:var(--muted)}
.btn{display:inline-block;background:var(--btn);color:var(--btn-ink);font:600 .95rem/1 var(--body);letter-spacing:.08em;text-transform:uppercase;text-decoration:none;padding:16px 24px;border:1px solid var(--btn);border-radius:2px;align-self:flex-start}
.btn:hover{filter:brightness(1.12)}
.btn.ghost{background:transparent;color:var(--brand);border-color:var(--brand)}
.row{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:20px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:2px;overflow:hidden;display:flex;flex-direction:column}
.card .body{padding:20px;display:flex;flex-direction:column;gap:10px;flex:1}
.card .btn{margin-top:auto}
.card h2{font-size:1.9rem}
.price{font:600 1.1rem/1.2 var(--body);font-variant-numeric:tabular-nums;color:var(--ink)}
.tag{font:600 .78rem/1 var(--body);letter-spacing:.16em;text-transform:uppercase;color:var(--signal);max-width:none}
.price small{font:400 .95rem var(--body);color:var(--muted)}
.shot{margin:0;aspect-ratio:4/3;background:var(--line);overflow:hidden}
.shot img{width:100%;height:100%;object-fit:cover}
.shot.ph{display:flex;align-items:center;justify-content:center;padding:14px;text-align:center;color:var(--muted);font-size:.9rem;
  background:repeating-linear-gradient(135deg,var(--line) 0 12px,transparent 12px 24px)}
mark.todo{background:#ffe9a8;color:#5a4300;padding:1px 6px;border-radius:4px;font-size:.85em;font-weight:600}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:2px;padding:24px;display:flex;flex-direction:column;gap:12px}
dl.spec{margin:0;display:grid;grid-template-columns:auto 1fr;gap:6px 18px;font-variant-numeric:tabular-nums}
dl.spec dt{color:var(--muted)} dl.spec dd{margin:0;font-weight:600;text-align:right;overflow-wrap:anywhere}
ul.tick{margin:0;padding-left:1.1em;display:flex;flex-direction:column;gap:4px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;background:var(--paper);border:1px solid var(--line);font-variant-numeric:tabular-nums}
th,td{padding:12px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.9rem;color:var(--muted)}
td.num,th.num{text-align:right;white-space:nowrap}
tr:last-child td{border-bottom:0}
.note{border-left:3px solid var(--signal);background:var(--paper);padding:16px 18px}
.terms{display:flex;flex-direction:column;gap:22px;max-width:70ch}
.terms section{display:flex;flex-direction:column;gap:8px}
.terms h2{font-size:1.7rem}

/* Bildescener */
.scene{position:relative;min-height:100svh;display:flex;align-items:flex-end;color:var(--on-deep);background:var(--deep);overflow:hidden;isolation:isolate}
.scene.half{min-height:72svh}
.scene.mid{align-items:center}
.scene>.bg{position:absolute;inset:0;z-index:-2;background:var(--deep)}
.scene>.bg img{width:100%;height:100%;object-fit:cover}
.bg.plain,.bg.ph{background:radial-gradient(120% 90% at 20% 10%,#2c5646 0,var(--deep) 70%)}
.scene::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(8,16,12,.5) 0,rgba(8,16,12,.12) 38%,rgba(8,16,12,.78) 100%)}
.scene>.wrap{width:100%;display:flex;flex-direction:column;gap:20px;padding-top:130px;padding-bottom:clamp(48px,11vh,120px)}
.scene .tag{color:var(--sand)}
.stmt{display:flex;flex-direction:column;font-size:clamp(2.6rem,8.4vw,6rem);font-weight:500;line-height:1;text-shadow:0 2px 36px rgba(0,0,0,.4);max-width:none}
.stmt .ln:nth-child(even){padding-left:clamp(1.2rem,13vw,10rem)}
.scene.r>.wrap{align-items:flex-end;text-align:right}
.scene.r .stmt{align-items:flex-end}
.scene.r .stmt .ln:nth-child(even){padding-left:0;padding-right:clamp(1.2rem,13vw,10rem)}
.scene .sub{font-size:1.2rem;max-width:44ch;text-shadow:0 1px 18px rgba(0,0,0,.45)}
.scene .btn{background:var(--sand);border-color:var(--sand);color:#14281f}
.scene .btn.ghost{background:transparent;color:var(--on-deep);border-color:var(--on-deep)}
.glass{background:rgba(12,22,17,.66);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:24px;max-width:440px;display:flex;flex-direction:column;gap:12px;text-align:left}
.glass h3{font:500 2rem/1.05 var(--display)}
.glass dl.spec dt{color:var(--on-deep-muted)}
.glass .price,.glass .price small{color:var(--on-deep)}
@media (min-width:900px){
  .scene.split{display:grid;grid-template-columns:1fr 1fr;align-items:stretch}
  .scene.split::after{display:none}
  .scene.split>.bg{position:relative;inset:auto;z-index:auto;grid-column:2;grid-row:1;min-height:100svh}
  .scene.split>.bg img{position:absolute;inset:0}
  .scene.split.fl>.bg{grid-column:1}
  .scene.split>.wrap{grid-column:1;grid-row:1;max-width:none;margin:0;justify-content:center;padding:130px clamp(32px,6vw,96px) 80px}
  .scene.split.fl>.wrap{grid-column:2}
  .scene.split .stmt{font-size:clamp(2.6rem,5.2vw,4.8rem)}
  .scene.split.r>.wrap{align-items:flex-start;text-align:left}
  .scene.split.r .stmt{align-items:flex-start}
  .scene.split.r .stmt .ln:nth-child(even){padding-right:0;padding-left:clamp(1.2rem,6vw,5rem)}
}
.sec{padding:clamp(56px,10vw,120px) 0}
.sec.tint{background:var(--paper);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.sec>.wrap{padding-top:0!important;padding-bottom:0!important}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:30px 20px}
.facts b{display:block;font:500 clamp(2.3rem,5.5vw,3.4rem)/1 var(--display);font-variant-numeric:lining-nums;margin-bottom:8px}
.facts span{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,6vw,88px);align-items:center}
.duo .shot{aspect-ratio:var(--r,4/5)}
.duo .txt{gap:18px}
.duo.flip .txt{order:2}
.duo p{font-size:1.12rem}
@media (max-width:760px){.duo{grid-template-columns:1fr}.duo.flip .txt{order:0}}
.strip{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding:0 20px;padding:4px 20px 18px;margin:0 -20px}
.strip figure{flex:0 0 min(78vw,400px);margin:0;scroll-snap-align:start}
.strip .shot{aspect-ratio:var(--r,3/4)}
.strip figcaption{font-size:.92rem;color:var(--muted);padding-top:8px}
details.acc{border-top:1px solid var(--line)}
details.acc:last-of-type{border-bottom:1px solid var(--line)}
details.acc summary{list-style:none;cursor:pointer;padding:18px 0;font:500 1.6rem/1.2 var(--display);display:flex;justify-content:space-between;gap:16px;align-items:center}
details.acc summary::-webkit-details-marker{display:none}
details.acc summary::after{content:"+";font:400 1.5rem/1 var(--body);color:var(--muted)}
details.acc[open] summary::after{content:"\\2013"}
details.acc .inner{padding:0 0 24px;max-width:65ch}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.tile{position:relative;aspect-ratio:3/4;display:flex;align-items:flex-end;color:#fff;text-decoration:none;overflow:hidden;background:var(--deep);isolation:isolate}
.tile .bg{position:absolute;inset:0;z-index:-2}
.tile .bg img{width:100%;height:100%;object-fit:cover}
.tile::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(8,16,12,0) 35%,rgba(8,16,12,.82) 100%)}
.tile .t{padding:20px;display:flex;flex-direction:column;gap:4px}
.tile h3{font:500 2.1rem/1 var(--display)}
.tile span{font-size:.95rem;color:var(--on-deep)}
.tile .bg img{transition:transform .8s ease}
.tile:hover .bg img,.tile:focus-visible .bg img{transform:scale(1.05)}
.site-foot{background:var(--deep);color:var(--on-deep-muted)}
.site-foot .wrap{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px;padding-top:40px;padding-bottom:40px}
.site-foot h2{font:600 .8rem/1 var(--body);letter-spacing:.14em;text-transform:uppercase;color:var(--on-deep)}
.site-foot a{color:var(--on-deep)}
.site-foot address{font-style:normal}
.site-foot .stack{gap:10px}
@media (prefers-reduced-motion:no-preference){
  .btn{transition:filter .15s}
  .js .rv{opacity:0;transform:translateY(24px);transition:opacity 1.1s ease,transform 1.1s ease;transition-delay:calc(var(--i,0)*.22s)}
  .js .rv.in{opacity:1;transform:none}
  .js .scene>.bg img{transform:scale(1.08);transition:transform 2.6s ease}
  .js .scene.on>.bg img{transform:none}
}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">')

# Liten skript for rolleeffekt: tekst og bilder glir inn når de kommer til syne. Uten JS vises alt som vanlig.
JS_REVEAL = """<script>
(function(){var d=document;d.documentElement.classList.add('js');
var els=d.querySelectorAll('.rv,.scene');
if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in','on')});return;}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in','on');io.unobserve(e.target);}})},{threshold:.2});
els.forEach(function(e){io.observe(e)});})();
</script>"""


class Ctx:
    def __init__(self, preview):
        self.preview = preview

    def link(self, slug):
        return "#" + PAGES[slug][0] if self.preview else (BASE + "/" + slug + "/" if slug else BASE + "/")

    def live(self, slug):
        return self.preview or slug not in DRAFT

    def _has(self, fname):
        return any(os.path.exists(os.path.join(ROOT, d, fname)) for d in ("images", "utkast-bilder"))

    def img(self, fname, alt, eager=False):
        if self.preview and self._has(fname):
            return f'<div class="shot"><img src="images/{fname}" alt="{html.escape(alt)}" loading="lazy"></div>'
        if self.preview:
            return f'<div class="shot ph" role="img" aria-label="{html.escape(alt)}"><span>Bilde: {html.escape(alt)}</span></div>'
        load = "" if eager else ' loading="lazy"'
        return f'<div class="shot"><img src="{BASE}/images/{fname}" alt="{html.escape(alt)}"{load}></div>'

    def bg(self, fname, alt, eager=False):
        if fname is None:
            return '<div class="bg plain"></div>'
        if self.preview and self._has(fname):
            return f'<div class="bg"><img src="images/{fname}" alt="{html.escape(alt)}"></div>'
        if self.preview:
            return f'<div class="bg ph" role="img" aria-label="{html.escape(alt)}"></div>'
        load = "" if eager else ' loading="lazy"'
        return f'<div class="bg"><img src="{BASE}/images/{fname}" alt="{html.escape(alt)}"{load}></div>'


def kr(n):
    return f"{n:,}".replace(",", NB) + NB + "kr"


def book(url, label="Sjekk tilgjengelighet og book"):
    return f'<a class="btn" href="{url}">{label}</a>'


# ---------- Byggeklosser for opplevelsen ----------

def lines(ls, h="h2"):
    spans = "".join(f'<span class="ln rv" style="--i:{i}">{t}</span>' for i, t in enumerate(ls))
    return f'<{h} class="stmt">{spans}</{h}>'


def scene(c, f, alt, ls, cls="", tag="", sub="", cta="", panel="", h="h2", eager=False):
    n = len(ls)
    t = f'<p class="tag rv">{tag}</p>' if tag else ""
    s = f'<p class="sub rv" style="--i:{n}">{sub}</p>' if sub else ""
    k = f'<div class="row rv" style="--i:{n + 1}">{cta}</div>' if cta else ""
    p = f'<div class="glass rv" style="--i:{n}">{panel}</div>' if panel else ""
    return (f'<section class="scene {cls}">{c.bg(f, alt, eager)}<div class="wrap">{t}{lines(ls, h)}{s}{p}{k}</div></section>')


def facts(items):
    return ('<section class="sec"><div class="wrap"><div class="facts">'
            + "".join(f'<div class="rv" style="--i:{i}"><b>{v}</b><span>{k}</span></div>' for i, (v, k) in enumerate(items))
            + '</div></div></section>')


def duo(c, f, alt, h, text, tag="", flip=False, ratio="4/5", extra="", tint=False):
    tg = f'<p class="tag">{tag}</p>' if tag else ""
    return (f'<section class="sec{" tint" if tint else ""}"><div class="wrap"><div class="duo{" flip" if flip else ""}" style="--r:{ratio}">'
            f'<div class="txt stack rv">{tg}<h2>{h}</h2>{text}{extra}</div>'
            f'<div class="rv" style="--i:1">{c.img(f, alt)}</div></div></div></section>')


def strip(c, h, lst, text=""):
    figs = "".join(f'<figure class="rv" style="--i:{min(i, 3)};--r:{(it[3] if len(it) > 3 else "3/4")}">{c.img(it[0], it[1])}<figcaption>{it[2]}</figcaption></figure>'
                   for i, it in enumerate(lst))
    tx = f"<p>{text}</p>" if text else ""
    return (f'<section class="sec"><div class="wrap stack" style="gap:24px"><div class="stack rv"><h2>{h}</h2>{tx}</div>'
            f'<div class="strip" tabindex="0" role="region" aria-label="{html.escape(h)}">{figs}</div></div></section>')


def acc(title, inner, open_=False):
    return f'<details class="acc"{" open" if open_ else ""}><summary>{title}</summary><div class="inner stack">{inner}</div></details>'


def section(inner, tint=False):
    return f'<section class="sec{" tint" if tint else ""}"><div class="wrap stack" style="gap:28px">{inner}</div></section>'


TILES = [
    ("adria-altea-552-pk-galleri", "adria-eksterior-1.jpg", "Adria Altea 552 PK campingvogn", "Campingvogn", f"Adria Altea 552 PK · {kr(6500)} per uke"),
    ("snoskuter", "snoskuter-hero.jpg", "To Polaris snøskutere i dyp snø", "Snøskuter", f"Polaris SKS og RMK · fra {kr(1990)} per døgn"),
    ("henger", "henger-side.jpg", "Skuter- og varehenger", "Henger", f"Skuter- og varehenger · fra {kr(700)} per døgn"),
    ("racing-simulator", None, "", "Simulator", f"Fullskala rigg · {kr(5500)} inntil 4 døgn"),
    ("hytte", "hytte-ute-1.jpg", "Mørk tømmerhytte med overbygd veranda", "Hytte", "Ved Grong skisenter · bookes på Airbnb"),
]


def tiles(c, cur="", heading="Mer å leie"):
    items = "".join(
        f'<a class="tile rv" style="--i:{i % 4}" href="{c.link(s)}">{c.bg(f, a)}<span class="t"><h3>{t}</h3><span>{d}</span></span></a>'
        for i, (s, f, a, t, d) in enumerate(x for x in TILES if x[0] != cur and c.live(x[0])))
    return section(f'<h2 class="rv">{heading}</h2><div class="tiles">{items}</div>')


# ---------- Sider ----------

def p_home(c):
    return f"""<main>
{scene(c, 'snoskuter-hero.jpg', 'To Polaris snøskutere i dyp snø – snøskuter til leie i Overhalla', ['Utstyr til tur', 'og transport,', 'hele året.'], h='h1', eager=True,
       sub='Lei campingvogn, snøskuter, henger og racing-simulator i Overhalla og Namdalen.',
       cta=f'<a class="btn" href="{c.link("utleie")}">Se utstyr</a>')}
{scene(c, 'adria-eksterior-4.jpg', 'Campingvogn koblet til bil, klar for tur', ['Book på nett.', 'Hent i Overhalla.'], cls='half r',
       sub='Velg utstyr, sjekk ledige datoer og betal. Resten gjør vi klart.')}
{tiles(c, heading='Dette kan du leie')}
</main>"""


def p_vogn(c):
    return f"""<main>
{scene(c, 'adria-eksterior-1.jpg', 'Adria Altea 552 PK campingvogn sett utvendig fra front og side', ['Leie av', 'Adria Altea 552 PK'], h='h1', eager=True, tag='Campingvogn',
       sub='Moderne vogn med dobbeltseng foran og tre køyer bak. Lett nok til å trekke med elbil.',
       cta=book(SHOP_VOGN, 'Lei Adria Altea'))}
{facts([('opptil 7', 'soveplasser'), (f'1{NB}310 kg', 'egenvekt'), ('230 cm', 'bredde'), ('760 cm', 'lengde')])}
{scene(c, 'adria-eksterior-4.jpg', 'Adria Altea 552 PK koblet til bil, klar for tur', ['Lett og smal,', 'enkel bak elbilen.'], cls='half r')}
{duo(c, 'adria-interior-1.jpg', 'Interiør i Adria Altea 552 PK campingvogn med lyst og moderne oppholdsrom', 'Lyst og moderne inni',
     '<p>Sittegruppe til måltidene, smart-TV og elektrisk gulvvarme. Kjøkkenet har det du trenger for å lage mat på tur, og vogna har eget bad med dusjkabinett.</p>',
     tag='Innvendig', ratio='4/3')}
{scene(c, 'adria-interior-2.jpg', 'Dobbeltseng foran i Adria Altea 552 PK campingvogn', ['Dobbeltseng foran,', 'tre køyer bak.'], cls='split fl')}
{strip(c, 'Rommene i vogna', [
    ('adria-interior-3.jpg', 'Tre køyesenger bak i Adria Altea 552 PK familievogn', 'Tre køyesenger bak'),
    ('adria-interior-4.jpg', 'Kjøkken i Adria Altea 552 PK med kokeplater, vask og oppbevaring', 'Kjøkken med alt du trenger', '4/3'),
    ('adria-interior-5.jpg', 'Sittegruppe i Adria Altea 552 PK campingvogn', 'Sittegruppe for måltider og avslapning', '4/3'),
    ('adria-interior-6.jpg', 'Bad og toalett i Adria Altea 552 PK campingvogn', 'Kompakt og funksjonelt bad'),
    ('adria-interior-7.jpg', 'Dusjrom i Adria Altea 552 PK campingvogn', 'Eget dusjkabinett')])}
{strip(c, 'Utenfor', [
    ('adria-eksterior-2.jpg', 'Adria Altea 552 PK campingvogn sett fra siden med moderne eksteriør', 'Enkel utsveivbar markise', '4/3'),
    ('adria-eksterior-5.jpg', 'Adria Altea 552 PK campingvogn med utrullet markise, sidematte og stativ', 'Markise og uteplass', '4/3'),
    ('adria-eksterior-3.jpg', 'Adria Altea 552 PK campingvogn sett forfra', 'Moderne design', '4/3')])}
{section(f'''<div class="two">
    <div class="panel"><h3>Nøkkeldata</h3><dl class="spec">
      <dt>Modellår</dt><dd>2026</dd><dt>Lengde</dt><dd>760 cm</dd><dt>Bredde</dt><dd>230 cm</dd>
      <dt>Egenvekt</dt><dd>1310 kg</dd><dt>Totalvekt</dt><dd>1500 kg</dd><dt>Soveplasser</dt><dd>opptil 7</dd></dl></div>
    <div class="panel"><h3>Viktig utstyr</h3><ul class="tick">
      <li>Smart-TV</li><li>Elektrisk gulvvarme</li><li>Sentralvarme på strøm/gass</li><li>Markise</li>
      <li>Komplett kjøkkenutstyr</li><li>Noe campingmøbler inkludert</li></ul></div></div>''', tint=True)}
{scene(c, 'adria-eksterior-3.jpg', 'Adria Altea 552 PK campingvogn sett forfra', ['Klar for tur?'], cls='half',
       sub=f'{kr(6500)} per uke · depositum {kr(10000)} · aldersgrense 23 år. Les <a href="{c.link("vilkar")}" style="color:inherit">vilkårene</a> før du bestiller.',
       cta=book(SHOP_VOGN, 'Lei Adria Altea'))}
{tiles(c, 'adria-altea-552-pk-galleri')}
</main>"""


def p_skuter(c):
    def sk(img, alt, tag, name, txt, motor, price, helg, slug):
        return f"""<article class="card">{c.img(img, alt)}<div class="body">
      <p class="tag">{tag}</p><h2>{name}</h2><p>{txt}</p>
      <dl class="spec"><dt>Motor</dt><dd>{motor}</dd><dt>Belte</dt><dd>155″</dd><dt>Depositum</dt><dd>{kr(5000)}</dd></dl>
      <p class="price">Fra {kr(price)} <small>per døgn · helg {kr(helg)}</small></p>{book(SHOP_P + slug, 'Book nå')}</div></article>"""
    def pk(name, txt, price, slug):
        return f"""<article class="card"><div class="body"><h3>{name}</h3><p>{txt}</p>
      <p class="price">Fra {kr(price)} <small>per døgn</small></p>{book(SHOP_P + slug, 'Book pakke')}</div></article>"""
    must = (f'<ul class="tick"><li>Førerkort klasse S, eller førerett i klasse B fra før 1. juli 2006. Vi sjekker førerkort ved utlevering.</li>'
            f'<li>Kjøring kun i lovlige snøskuterløyper eller der du har tillatelse. Du er selv ansvarlig for løypekort og lokale regler.</li>'
            f'<li>Hjelm er påbudt.</li><li>Skuteren leveres med full tank og skal leveres tilbake med full tank.</li>'
            f'<li>Se våre <a href="{c.link("vilkar")}">leievilkår</a>.</li></ul>')
    return f"""<main>
{scene(c, 'snoskuter-hero.jpg', 'To Polaris snøskutere i dyp snø', ['Snøskuter til leie', 'i Namdalen'], h='h1', eager=True, tag='Snøskuter',
       sub='En dag på løypa, en helg på hytta eller en isfisketur. To Polaris-skutere: én for trygg løypekjøring og én for deg som vil ut i dyp snø.',
       cta=book(SHOP_P + 'polaris-800-sks-155', 'Book SKS 800') + book(SHOP_P + 'polaris-850-pro-rmk-155', 'Book PRO RMK 850'))}
{section(f'''<p class="tag rv">To skutere, to retninger</p>
  <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">
    {sk('polaris-sks.jpg', 'Sort Polaris 800 SKS 155 snøskuter', 'Løype og tur', 'Polaris 800 SKS 155', 'Allsidig skuter med god komfort og justerbare støtdempere. Stabil på hardpakket løype – et trygt valg for deg som kjører mest i løypene.', '800 cc totakt', 1990, 3980, 'polaris-800-sks-155')}
    {sk('polaris-rmk.jpg', 'Gul Polaris 850 PRO RMK 155 snøskuter', 'Dyp snø og fjell', 'Polaris 850 PRO RMK 155', 'Lett fjellskuter bygget for løs snø og bratt terreng. Passer for erfarne førere som vil utforske.', '850 cc totakt', 2290, 4580, 'polaris-850-pro-rmk-155')}
  </div>''')}
{section(f'''<h2 class="rv">Pakker med skuterhenger</h2><p>Ca. 10{NB}% rimeligere enn å leie hver for seg.</p>
  <div class="cards">
    {pk('SKS 800 + henger', 'Løypeskuteren og skuterhengeren i én bestilling.', 2421, 'pakke-polaris-800-sks-henger')}
    {pk('PRO RMK 850 + henger', 'Fjellskuteren og skuterhengeren i én bestilling.', 2691, 'pakke-polaris-850-pro-rmk-henger')}
    {pk('2 snøskutere + henger', 'Begge skuterne og hengeren – ta med hele gjengen.', 4482, 'pakke-2-snoskutere-henger')}
  </div>''', tint=True)}
{section(f'<h2 class="rv">Dette må du vite</h2><div>{acc("Førerkort, løype og utstyr", must, True)}</div>')}
{tiles(c, 'snoskuter')}
</main>"""


def p_henger(c):
    must = (f'<ul class="tick"><li>Bilen må ha hengerfeste og tillatt tilhengervekt som dekker hengeren med last (inntil 1{NB}260 kg).</li>'
            f'<li>Med førerkort B kan bil og henger ha samlet tillatt totalvekt på inntil 3{NB}500 kg. Over det trengs B96 (inntil 4{NB}250 kg) eller BE. Sjekk bilens vognkort.</li>'
            f'<li>Lasten skal sikres forskriftsmessig, og hengeren leveres tilbake ryddet og uten avfall.</li>'
            f'<li>Skader meldes umiddelbart. Se våre <a href="{c.link("vilkar")}">leievilkår</a>.</li></ul>')
    return f"""<main>
{scene(c, 'henger-side.jpg', 'Skuter- og varehengeren sett fra siden', ['Henger til leie', 'i Overhalla'], h='h1', eager=True, tag='Henger',
       sub='Både skuterhenger og varehenger. Frakt snøskuteren til hytta om vinteren, og bruk den til flytting, hageavfall og byggevarer resten av året.',
       cta=book(SHOP_P + 'snoskutertilhenger', 'Book henger'))}
{facts([(f'880 kg', 'nyttelast'), (f'1{NB}260 kg', 'tillatt totalvekt'), ('5,96 × 2,01 m', 'total lengde og bredde'), (f'fra {kr(700)}', 'per døgn')])}
{duo(c, 'henger.jpg', 'Lasterommet i hengeren', 'Rom for det meste',
     f'<p>Allsidig henger for snøskuter og vanlig varetransport. Henting i Overhalla. Helgepris {kr(1400)} og depositum {kr(2000)}.</p>',
     tag='Hele året', ratio='16/10', extra=book(SHOP_P + 'snoskutertilhenger', 'Book henger'))}
{section(f'''<p class="tag rv">Vinterpakke</p><h2 class="rv">Henger og snøskuter</h2>
  <p>Lei hengeren sammen med én eller begge skuterne og spar ca. 10{NB}%.</p>
  <dl class="spec" style="max-width:520px"><dt>SKS 800 + henger</dt><dd>fra {kr(2421)}/døgn</dd><dt>PRO RMK 850 + henger</dt><dd>fra {kr(2691)}/døgn</dd><dt>2 skutere + henger</dt><dd>fra {kr(4482)}/døgn</dd></dl>
  <a class="btn ghost" href="{c.link('snoskuter')}">Se skuterpakkene</a>''', tint=True)}
{section(f'<h2 class="rv">Dette må du vite</h2><div>{acc("Bil, førerkort og last", must, True)}</div>')}
{tiles(c, 'henger')}
</main>"""


def TODO(t):
    return f'<mark class="todo">[{t}]</mark>'


AIRBNB_HYTTE = "https://www.airbnb.no/"  # byttes til lenken til hytteannonsen

HYTTE_TERMS = [
    ("Bestilling og betaling", [
        "Hytta bestilles og betales gjennom Airbnb. Pris, betaling, avbestilling og refusjon følger reglene som står i annonsen på Airbnb.",
        "Den som bestiller er ansvarlig leietaker og skal selv bo i hytta under oppholdet.",
        f"Antall gjester skal ikke overstige det som er oppgitt i bestillingen. {TODO('MAKS ANTALL GJESTER')}"]),
    ("Innsjekk og utsjekk", [
        f"Innsjekk fra kl. {TODO('KLOKKESLETT')}, utsjekk innen kl. {TODO('KLOKKESLETT')}.",
        "Hytta har selvbetjent innsjekk. Praktisk informasjon sendes i Airbnb før ankomst.",
        "Forsinket utsjekk som hindrer neste gjest eller klargjøring, kan bli belastet."]),
    ("Sengetøy og håndklær", [
        "Leietaker tar med eget sengetøy og egne håndklær. Dyner og puter finnes i hytta.",
        "Av hygieniske grunner skal senger ikke brukes uten sengetøy."]),
    ("Rengjøring ved avreise", [
        "Hytta skal vaskes etter bruk, slik at den er klar til neste gjest: gulv, kjøkken, bad og overflater rengjøres, oppvask tas, og søppel tas med eller kastes i anvist container.",
        f"Vaskes ikke hytta tilfredsstillende, belastes et rengjøringsgebyr. {TODO('BELØP')}"]),
    ("Røyking, dyr og ro", [
        "Røyking er ikke tillatt inne i hytta.",
        "Dyr er tillatt. Dyr skal ikke ligge i senger eller sofa, og hår og spor etter dyr fjernes før avreise.",
        "Ta hensyn til naboene. Fest og arrangementer er ikke tillatt uten avtale."]),
    ("Ansvar og skader", [
        "Leietaker er ansvarlig for hytta og inventaret i leieperioden og erstatter skader og tap som skyldes uaktsomhet.",
        "Skader og mangler meldes til utleier så snart de oppdages.",
        "Utleier er ikke ansvarlig for forhold utenfor utleiers kontroll, som strømbrudd, vær eller stengte veier og skianlegg."]),
    ("Brannsikkerhet", [
        "Gjør deg kjent med røykvarslere, slokkeutstyr og rømningsveier ved ankomst.",
        "Levende lys skal ikke forlates uten tilsyn."]),
    ("Kontakt", [
        "Utleier er Namsen Utleie, AKRI Holding AS. Henvendelser om oppholdet sendes i Airbnb, eller til post@namsenutleie.no og +47 95 94 68 55."]),
]



def p_hytte(c):
    terms = "".join(acc(f"{i}. {h}", f'<ul class="tick">{"".join(f"<li>{x}</li>" for x in items)}</ul>')
                    for i, (h, items) in enumerate(HYTTE_TERMS, 1))
    airbnb = book(AIRBNB_HYTTE, 'Se pris og book på Airbnb')
    return f"""<main>
{scene(c, 'hytte-ute-1.jpg', 'Mørk tømmerhytte med hvite vinduer og overbygd veranda', ['Hytte ved', 'Grong skisenter'], cls='split', h='h1', eager=True, tag='Til leie',
       sub='Tømmerhytte med to soverom og hems, kort vei til bakken og skistua. Pris og ledige datoer finner du på Airbnb.',
       cta=airbnb + ' ' + TODO('AIRBNB-LENKE MANGLER'))}
{scene(c, 'hytte-ute-2.jpg', 'Gavlveggen på hytta med vindu i første etasje og på hemsen', ['Skia av.', 'Støvlene i gangen.', 'Nå er du fremme.'], cls='split fl r')}
{facts([('2', 'soverom'), ('1', 'hems'), (TODO('ANTALL'), 'sengeplasser'), ('1', 'overbygd veranda')])}
{duo(c, 'hytte-stue-1.jpg', 'Stue med hjørnesofa, salongbord og dører inn til soverommene', 'Samles i stua',
     '<p>Hjørnesofa, TV og spiseplass i samme rom. Kveldsmat, kortspill og en film når bakken har stengt for dagen.</p>', tag='Stue')}
{scene(c, 'hytte-stue-2.jpg', 'Hjørnesofa mot brun panelvegg under skrått hvitt tak', ['Høyt under taket,', 'lavt i skuldrene.'], cls='split')}
{duo(c, 'hytte-kjokken.jpg', 'Kjøkken med hvite skap, mørk benkeplate, vask og platetopp', 'Lag maten sammen',
     f'<p>Kjøkken med platetopp og vask, og spisebordet like ved. {TODO("UTSTYR MÅ BEKREFTES: OPPVASKMASKIN, KAFFEMASKIN OSV.")}</p>', tag='Kjøkken', flip=True)}
{scene(c, 'hytte-spis-2.jpg', 'Smårutete vinduer med utsikt mot verandaen', ['Lys fra', 'to sider.'], cls='split fl r')}
{strip(c, 'To soverom og en hems',
    [('hytte-sov-1.jpg', 'Soverom med dobbeltseng og kommode', 'Soverom 1: dobbeltseng'),
     ('hytte-sov-2.jpg', 'Soverom med køyeseng og stige', 'Soverom 2: køyeseng'),
     ('hytte-hems.jpg', 'Hems med rød sovesofa under skråtak i furupanel', 'Hems med sovesofa'),
     ('hytte-spis-1.jpg', 'Hvitt spisebord i hjørnet med TV på veggen og vinduer på to sider', 'Spiseplass og TV'),
     ('hytte-gang.jpg', 'Dør fra stua ut til gang med flislagt gulv og knaggrekke', 'Gang med plass til yttertøy')],
    text='Ta med eget sengetøy og egne håndklær. Hytta vaskes etter bruk, slik at den er klar til neste gjest.')}
{section(f'''<h2 class="rv">Det praktiske</h2>
  <div class="two">
    <div class="panel"><h3>Nøkkeldata</h3><dl class="spec">
      <dt>Beliggenhet</dt><dd>Grong skisenter {TODO('ADRESSE')}</dd>
      <dt>Soverom</dt><dd>2 + hems</dd>
      <dt>Sengeplasser</dt><dd>dobbeltseng, køyeseng og sovesofa på hems {TODO('ANTALL MÅ BEKREFTES')}</dd>
      <dt>Bad</dt><dd>{TODO('DUSJ/WC')}</dd>
      <dt>Oppvarming</dt><dd>{TODO('MÅ FYLLES INN')}</dd>
      <dt>Parkering</dt><dd>{TODO('MÅ FYLLES INN')}</dd></dl></div>
    <div class="note stack" style="gap:8px"><h3>Dette må du vite</h3><ul class="tick">
      <li>Sengetøy og håndklær må du ta med selv.</li>
      <li>Hytta vaskes etter bruk, slik at den er klar til neste gjest.</li>
      <li>Røyking er ikke tillatt inne.</li>
      <li>Dyr er tillatt.</li>
      <li>Inn- og utsjekk: {TODO('KLOKKESLETT OG NØKKELBOKS')}</li></ul></div>
  </div>''', tint=True)}
{section(f'<h2 class="rv">Leievilkår for hytta</h2><div>{terms}</div>')}
{scene(c, 'hytte-ute-1.jpg', 'Mørk tømmerhytte med hvite vinduer og overbygd veranda', ['Ledige datoer', 'og pris på Airbnb.'], cls='split fl', 
       sub='Kombiner hytteturen med snøskuter og henger fra Namsen Utleie.',
       cta=airbnb + f'<a class="btn ghost" href="{c.link("snoskuter")}">Se snøskuterne</a>')}
{tiles(c, 'hytte')}
</main>"""


def p_sim(c):
    return f"""<main>
{scene(c, None, '', ['Racing-simulator', 'til leie'], h='h1', eager=True, cls='half', tag='Simulator',
       sub='Til firmafesten, bursdagen eller helgen. Fullskala simulator med direktedrevet ratt, pedaler i klubbsportklasse og tre 32″ buede skjermer.',
       cta=book(SHOP_P + 'racing-simulator', 'Book nå'))}
{section(f'''<div class="two">
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
  </div>''')}
{section(f'''<div class="panel"><h2>Bedrift og arrangement</h2>
    <p>Firmafest, messe eller teambuilding – med konkurranse og resultatliste.</p>
    <p>Vi leverer, rigger opp og henter i Namdalen. Pris etter omfang, fra {kr(5500)}.</p>
    <a class="btn ghost" href="{c.link('kontakt')}">Be om tilbud</a></div>
  <p>Utstyret skal stå innendørs og tørt. Se våre <a href="{c.link('vilkar')}">leievilkår</a>.</p>''', tint=True)}
{tiles(c, 'racing-simulator')}
</main>"""


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
    if c.live("hytte"):
        rows.append(("hytte", "hytte-ute-1.jpg", "Mørk tømmerhytte med hvite vinduer og overbygd veranda",
                     "Hytte ved Grong skisenter", "Hytte med to soverom og hems, kort vei til bakken og skistua.",
                     "Pris på Airbnb <small>varierer med sesong</small>"))
    cards = "".join(
        f'<article class="card">{c.img(f, alt) if f else ""}<div class="body"><h2>{t}</h2><p>{d}</p><p class="price">{pr}</p>'
        f'<a class="btn" href="{c.link(s)}">Se detaljer og book</a></div></article>' for s, f, alt, t, d, pr in rows)
    return f"""<main><div class="wrap stack" style="gap:24px">
  <h1>Utleie i Overhalla og Namdalen</h1>
  <p class="lead">Velg utstyr, sjekk tilgjengelighet og betal på nett. Alle priser er inkludert mva.</p>
  <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">{cards}</div>
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


BODY = {"": p_home, "utleie": p_utleie, "adria-altea-552-pk-galleri": p_vogn, "snoskuter": p_skuter, "henger": p_henger, "hytte": p_hytte,
        "racing-simulator": p_sim, "om-oss": p_om, "kontakt": p_kontakt, "vilkar": p_vilkar}

META = {
    "": ("Lei campingvogn, snøskuter og henger i Overhalla | Namsen Utleie", "Lei campingvogn, snøskuter, henger og racing-simulator hos Namsen Utleie i Overhalla. Book på nett og hent utstyret i Overhalla."),
    "utleie": ("Utleie | Namsen Utleie", "Utleie av campingvogn, snøskuter, henger og racing-simulator i Overhalla og Namdalen."),
    "adria-altea-552-pk-galleri": ("Adria Altea 552 m/3 køyer | Namsen Utleie", "Lei Adria Altea 552 PK. Moderne og komfortabel campingvogn med praktiske løsninger for ferie og helgeturer."),
    "snoskuter": ("Snøskuter | Namsen Utleie", "Lei Polaris snøskuter i Overhalla. Enkeltvis eller som pakke med henger."),
    "henger": ("Henger | Namsen Utleie", "Lei lukket henger for snøskuter og varer i Overhalla."),
    "racing-simulator": ("Racing-simulator | Namsen Utleie", "Lei profesjonell racing-simulator med Fanatec-utstyr og tre skjermer."),
    "hytte": ("Hytte ved Grong skisenter | Namsen Utleie", "Lei hytte med to soverom og hems ved Grong skisenter."),
    "om-oss": ("Om oss | Namsen Utleie", "Namsen Utleie er et lokalt utleiefirma i Namdalen, drevet av AKRI Holding AS."),
    "kontakt": ("Kontakt | Namsen Utleie", "Kontakt Namsen Utleie på e-post eller telefon."),
    "vilkar": ("Vilkår | Namsen Utleie", "Vilkår for utleie hos Namsen Utleie."),
}


def header(c, cur):
    def li(s):
        on = ' aria-current="page"' if (s == cur or (s == "utleie" and cur in SUB_NAV)) else ""
        return f'<li><a href="{c.link(s)}"{on}>{PAGES[s][1]}</a></li>'
    over = " over" if cur in HERO else ""
    out = (f'<header class="site-head{over}"><div class="wrap"><a class="mark" href="{c.link("")}">Namsen <span>Utleie</span></a>'
           f'<nav aria-label="Hovedmeny"><ul>{"".join(li(s) for s in MAIN_NAV)}</ul></nav></div></header>')
    if cur == "utleie":
        sub = "".join(f'<li><a href="{c.link(s)}">{PAGES[s][1]}</a></li>' for s in SUB_NAV if c.live(s))
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
        if slug in DRAFT:
            continue
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
<body>{header(c, slug)}{BODY[slug](c)}{footer(c)}{JS_REVEAL}</body></html>
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
.js .view{{display:none}} .js .view.on{{display:block}} .view{{position:relative}}
.banner{{background:var(--signal);color:#fff;font-size:.9rem;padding:8px 20px;text-align:center}}
</style></head>
<body><div class="banner">Forhåndsvisning. Hyttesiden er et utkast og er ikke publisert. Gule felt må fylles inn.</div>
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
</script>{JS_REVEAL}</body></html>
"""
    os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
    with open(os.path.join(ROOT, "preview", "index.html"), "w") as f:
        f.write(doc)
    pimg = os.path.join(ROOT, "preview", "images")
    shutil.rmtree(pimg, ignore_errors=True)
    os.makedirs(pimg)
    for d in ("images", "utkast-bilder"):
        if os.path.isdir(os.path.join(ROOT, d)):
            for fn in os.listdir(os.path.join(ROOT, d)):
                shutil.copy(os.path.join(ROOT, d, fn), os.path.join(pimg, fn))


if __name__ == "__main__":
    build_site()
    build_preview()
    print("ok")
