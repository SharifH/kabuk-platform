#!/usr/bin/env python3
"""
KabuK Platform — static page generator (Python 3.8+, standard library only).

Why this exists: the site ships in five languages (en, ja, ko, zh-TW, ar) with
localized, crawlable routes (/ja/…, /ko/…, /zh-tw/…, /ar/…). Hand-maintaining
35+ HTML files with duplicated header/footer markup would drift quickly, so the
pages are rendered from i18n/<locale>.json + site-config.json by this script.

The generated HTML is committed. Deploying needs no build step, no npm and no
runtime framework: upload the folder to any static host.

Usage (from the site root):
    python3 tools/build.py            # regenerate every page, sitemap, robots, review inventory
    python3 tools/build.py --check    # fail if any locale is missing keys (CI-friendly)
"""
import datetime
import html
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEAR = datetime.date.today().year


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


CONFIG = load("site-config.json")
LOCALES = CONFIG["locales"]
BASE = CONFIG["site"]["canonicalBase"].rstrip("/")
VERIFIED = bool(CONFIG["site"].get("canonicalVerified"))
EN = load("i18n/en.json")

PAGES = [
    # id, path, i18n meta key
    ("home", "", "home"),
    ("solutions", "solutions/", "solutions"),
    ("technology", "technology/", "technology"),
    ("why", "why-platform/", "why"),
    ("about", "about/", "about"),
    ("contact", "contact/", "contact"),
    ("privacy", "privacy/", "privacy"),
]
PAGE_PATH = {p[0]: p[1] for p in PAGES}

SEGMENTS = [  # key in common.segments / audienceCopy, anchor id, contact type
    ("hotels", "hotels", "hotel"),
    ("destinations", "destinations", "tourism"),
    ("wholesalers", "wholesalers", "wholesaler"),
    ("travel", "travel-companies", "travel-company"),
]
DOMAINS = ["pricing", "booking", "billing", "content", "identity", "analytics"]

# ---------------------------------------------------------------------------
# Icons — geometric monochrome line icons in the Lucide visual language
# (design library: 1.5px stroke, minimal detail).
# ---------------------------------------------------------------------------
_I = {
    "pricing": '<path d="M12.6 2.6 21.4 11.4a2 2 0 0 1 0 2.8l-7.2 7.2a2 2 0 0 1-2.8 0L2.6 12.6A2 2 0 0 1 2 11.2V4a2 2 0 0 1 2-2h7.2a2 2 0 0 1 1.4.6Z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "availability": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
    "booking": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="m9 16 2 2 4-4"/>',
    "reservations": '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4M12 16h4M8 11h.01M8 16h.01"/>',
    "billing": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8M12 17.5v-11"/>',
    "content": '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "identity": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><circle cx="12" cy="10" r="2"/><path d="M12 12v3"/>',
    "operations": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "analytics": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    "connectivity": '<rect x="9" y="2" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="16" y="16" width="6" height="6" rx="1"/><path d="M5 16v-3h14v3M12 8v5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "external": '<path d="M7 17 17 7M8 7h9v9"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10Z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "visibility": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "brand": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
    "partner": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/><path d="M8 9h8M8 13h5"/>',
    "hotel": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v8h4M18 9h2a2 2 0 0 1 2 2v11h-4M10 6h4M10 10h4M10 14h4M10 18h4"/>',
}
DOMAIN_ICON = {"pricing": "pricing", "booking": "booking", "billing": "billing", "content": "content", "identity": "identity", "analytics": "analytics"}
# Hotel benefit cards: (i18n index -> icon, gating module or None). Copy lives in home.benefits.items / solutions.benefits.items.
BENEFIT_ICONS = ["connectivity", "visibility", "pricing", "analytics", "brand", "partner"]
BENEFIT_MODULES = [None, None, "rateTransparency", "marketInsights", "whiteLabel", None]
CONTROL_MODULES = [None, "rateTransparency", None, None]  # home.control.items
CHANNELS = ["hafh", "omakastay", "exchange"]
HOTEL_CONTACT = "?type=hotel&amp;interest=onboarding"


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{_I[name]}</svg>')


# ---------------------------------------------------------------------------
# Translation access with English fallback (fallbacks are recorded for review)
# ---------------------------------------------------------------------------
class Tr:
    def __init__(self, data, code):
        self.data, self.code, self.missing = data, code, set()

    def _get(self, src, key):
        cur = src
        for part in key.split("."):
            if isinstance(cur, list):
                cur = cur[int(part)]
            elif isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    def raw(self, key):
        v = self._get(self.data, key)
        if v is None:
            self.missing.add(key)
            v = self._get(EN, key)
            if v is None:
                raise KeyError(f"Missing English key: {key}")
        return v

    def __call__(self, key, **fmt):
        v = self.raw(key)
        s = html.escape(str(v), quote=False)
        for k, val in fmt.items():
            s = s.replace("{" + k + "}", str(val))
        return s


def esc(s):
    return html.escape(str(s), quote=True)


def href(loc, page_id, anchor=""):
    if page_id not in PAGE_PATH:
        page_id = "home"
    prefix = f"/{loc['path']}/" if loc["path"] else "/"
    return prefix + PAGE_PATH[page_id] + (f"#{anchor}" if anchor else "")


def abs_url(loc, page_id):
    return BASE + href(loc, page_id)


def ext_link(key, label, t, cls=""):
    url = CONFIG["urls"][key]
    return (f'<a class="{cls}" href="{esc(url)}" data-config-link="{key}" target="_blank" rel="noopener">'
            f'{label}<span class="sr-only"> ({t("common.external")})</span>{icon("external", "ext")}</a>')


# Status value -> chip style. Unknown values fall back to "planned" (the most conservative label).
CHIP_CLASS = {"live": "core", "eligible": "core", "pilot": "development", "development": "development",
              "comingSoon": "planned", "planned": "planned", "unconfirmed": "planned"}


def chip(status, t):
    status = status if status in CHIP_CLASS else "planned"
    return f'<span class="chip chip-{CHIP_CLASS[status]}">{t("common.status." + status)}</span>'


def status_chip(key, t):
    return chip(CONFIG["capabilityStatus"].get(key, "planned"), t)


def module_state(name):
    """site-config.json modules.<name>: 'comingSoon' or 'hidden'. Anything else (missing, typo, 'live') is
    treated as hidden, so a module is never published as live by accident."""
    state = CONFIG.get("modules", {}).get(name)
    return state if state == "comingSoon" else "hidden"


def coming_soon_chip(t):
    return f'<span class="chip chip-planned">{t("common.status.comingSoon")}</span>'


def channel_chip(key, t):
    return chip(CONFIG.get("channelStatus", {}).get(key, "planned"), t)


# ---------------------------------------------------------------------------
# Shared components
# ---------------------------------------------------------------------------
def head(loc, t, page_id, meta_key):
    title = t(f"{meta_key}.meta.title")
    desc = t(f"{meta_key}.meta.description")
    alts = "".join(
        f'<link rel="alternate" hreflang="{l["hreflang"]}" href="{abs_url(l, page_id)}">' for l in LOCALES
    ) + f'<link rel="alternate" hreflang="x-default" href="{abs_url(LOCALES[0], page_id)}">'
    robots = "" if VERIFIED else '<meta name="robots" content="noindex, nofollow"><!-- pre-launch: set site.canonicalVerified=true and rebuild -->'
    locale_paths = json.dumps({l["code"]: l["path"] for l in LOCALES})
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebPage", "name": html.unescape(title), "description": html.unescape(desc),
        "url": abs_url(loc, page_id), "inLanguage": loc["htmlLang"],
        "isPartOf": {"@type": "WebSite", "name": "KabuK Platform", "url": BASE + "/"},
        "publisher": {"@type": "Organization", "name": "KabuK Style Inc.", "url": CONFIG["urls"]["corporate"]},
    }, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="{loc['htmlLang']}" dir="{loc['dir']}" class="no-js" data-locale="{loc['code']}" data-page="{page_id}" data-root="__ROOT__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{abs_url(loc, page_id)}">
{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="KabuK Platform">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{abs_url(loc, page_id)}">
<meta property="og:locale" content="{loc['ogLocale']}">
<meta name="theme-color" content="#FAFAF8">
<link rel="icon" type="image/png" href="/assets/brand/kabuk-logo.png">
<script>(function(d){{d.classList.replace('no-js','js');try{{var p={locale_paths},s=localStorage.getItem('kbk-locale'),c=d.getAttribute('data-locale');if(c==='en'&&s&&s!=='en'&&p[s]&&!/[?&]lang=en/.test(location.search)){{var r=new URL(d.getAttribute('data-root')||'./',location.href).pathname;location.replace(r+p[s]+'/'+location.pathname.slice(r.length)+location.hash);}}}}catch(e){{}}}})(document.documentElement);</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={loc['fonts']}&display=swap">
<link rel="stylesheet" href="/assets/css/tokens.css">
<link rel="stylesheet" href="/assets/css/site.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip-link" href="#main">{t("common.skip")}</a>
"""


def lockup(loc, t, footer=False):
    return (f'<a class="lockup" href="{href(loc, "home")}" aria-label="{t("common.home")}">'
            f'<img src="/assets/brand/kabuk-logo.png" alt="" width="50" height="33">'
            f'<span class="lockup-text" lang="en" dir="ltr"><span class="lockup-product">Platform</span>'
            f'<span class="lockup-parent">by KabuK Style</span></span></a>')


def header(loc, t, page_id):
    def cur(pid):
        return ' aria-current="page"' if page_id == pid else ""
    sol_items = f'<li class="menu-overview"><a href="{href(loc, "solutions")}">{t("common.nav.solutionsOverview")}</a></li>' + "".join(
        f'<li><a href="{href(loc, "solutions", anchor)}">{t(f"common.segments.{k}.name")}<small>{t(f"common.segments.{k}.hint")}</small></a></li>'
        for k, anchor, _ in SEGMENTS) + "".join(
        f'<li><a href="{href(loc, "solutions", anchor)}">{t("common.nav." + k)}</a></li>' for k, anchor in [("benefits", "benefits"), ("ecosystem", "ecosystem"), ("connectOptions", "connect")])
    tech_items = f'<li class="menu-overview"><a href="{href(loc, "technology")}">{t("common.nav.technologyOverview")}</a></li>' + "".join(
        f'<li><a href="{href(loc, "technology", d)}">{t(f"common.services.{d}")}</a></li>' for d in DOMAINS)
    lang_items = "".join(
        f'<li><a href="{href(l, page_id)}" hreflang="{l["hreflang"]}" lang="{l["htmlLang"]}" data-set-locale="{l["code"]}"'
        f'{" aria-current=" + chr(34) + "true" + chr(34) if l["code"] == loc["code"] else ""}>{esc(l["label"])}</a></li>'
        for l in LOCALES)
    sol_cur = " is-current" if page_id == "solutions" else ""
    tech_cur = " is-current" if page_id == "technology" else ""
    return f"""<header class="site-header">
<div class="container header-inner">
{lockup(loc, t)}
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="nav-toggle-bars" aria-hidden="true"></span><span class="sr-only">{t("common.menu")}</span></button>
<nav class="site-nav" id="site-nav" aria-label="{t("common.mainNav")}">
<ul class="nav-list">
<li class="nav-item"><button class="nav-link nav-trigger{sol_cur}" type="button" aria-expanded="false" aria-controls="menu-solutions">{t("common.nav.solutions")}{icon("chevron", "chev")}</button>
<div class="nav-menu" id="menu-solutions"><ul>{sol_items}</ul></div></li>
<li class="nav-item"><button class="nav-link nav-trigger{tech_cur}" type="button" aria-expanded="false" aria-controls="menu-technology">{t("common.nav.technology")}{icon("chevron", "chev")}</button>
<div class="nav-menu" id="menu-technology"><ul>{tech_items}</ul></div></li>
<li class="nav-item"><a class="nav-link" href="{href(loc, "why")}"{cur("why")}>{t("common.nav.why")}</a></li>
<li class="nav-item"><a class="nav-link" href="{href(loc, "about")}"{cur("about")}>{t("common.nav.about")}</a></li>
</ul>
<div class="nav-actions">
<div class="lang nav-item"><button class="nav-link nav-trigger lang-trigger" type="button" aria-expanded="false" aria-controls="menu-lang" aria-label="{t("common.languageChoose")}: {esc(loc["label"])}">{icon("globe")}<span>{esc(loc["short"])}</span>{icon("chevron", "chev")}</button>
<div class="nav-menu lang-menu" id="menu-lang"><ul>{lang_items}</ul></div></div>
<a class="btn btn-primary btn-sm" href="{href(loc, "contact")}{HOTEL_CONTACT}"{cur("contact")}>{t("common.nav.connect")}</a>
</div>
</nav>
</div>
</header>
"""


def draft_banner(loc, t, page_id):
    if loc.get("review") != "draft":
        return ""
    return (f'<div class="container" style="padding-top:16px"><p class="notice notice-info" role="note">{icon("info")}'
            f'<span>{t("common.draftBanner")} <a href="{href(LOCALES[0], page_id)}?lang=en" hreflang="en" lang="en" data-set-locale="en">{t("common.draftBannerLink")}</a></span></p></div>')


def footer(loc, t, page_id):
    sol = "".join(f'<li><a href="{href(loc, "solutions", a)}">{t(f"common.segments.{k}.name")}</a></li>' for k, a, _ in SEGMENTS)
    tech = "".join(f'<li><a href="{href(loc, "technology", a)}">{t("common.footer." + k)}</a></li>' for k, a in
                   [("techCore", "core-services"), ("techConnectivity", "connectivity"), ("techOperations", "operations"), ("techAnalytics", "analytics")])
    langs = "".join(
        f'<li><a href="{href(l, page_id)}" hreflang="{l["hreflang"]}" lang="{l["htmlLang"]}" data-set-locale="{l["code"]}"'
        f'{" aria-current=" + chr(34) + "true" + chr(34) if l["code"] == loc["code"] else ""}>{esc(l["label"])}</a></li>' for l in LOCALES)
    draft = f'<p>{t("common.footer.draftNotice")}</p>' if loc.get("review") == "draft" else ""
    return f"""<footer class="site-footer">
<div class="container">
<div class="footer-top">
<div class="footer-brand">{lockup(loc, t, True)}<p>{t("common.footer.tagline")}</p></div>
<div class="footer-col"><h2>{t("common.footer.solutions")}</h2><ul>{sol}</ul></div>
<div class="footer-col"><h2>{t("common.footer.technology")}</h2><ul>{tech}</ul></div>
<div class="footer-col"><h2>{t("common.footer.company")}</h2><ul>
<li><a href="{href(loc, "about")}">{t("common.footer.about")}</a></li>
<li><a href="{href(loc, "contact")}">{t("common.footer.contact")}</a></li>
<li><a href="{href(loc, "privacy")}">{t("common.footer.privacy")}</a></li>
</ul></div>
<div class="footer-col"><h2>{t("common.footer.products")}</h2><ul>
<li><a class="is-current" href="{href(loc, "home")}" aria-current="true">{t("common.footer.platformCurrent")}<span class="sr-only"> ({t("common.footer.currentSite")})</span></a></li>
<li>{ext_link("exchange", t("common.footer.exchange"), t)}</li>
<li>{ext_link("hafh", t("common.footer.hafh"), t)}</li>
<li>{ext_link("corporate", t("common.footer.corporate"), t)}</li>
</ul></div>
</div>
<div class="footer-bottom">
<div><p>{t("common.footer.copyright", year=YEAR)}</p>{draft}</div>
<nav aria-label="{t("common.footer.languages")}"><ul class="footer-langs">{langs}</ul></nav>
</div>
</div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def section_head(eyebrow, title, lead="", hid="", cls=""):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    id_attr = f' id="{hid}"' if hid else ""
    return (f'<div class="section-head {cls}" data-reveal><p class="eyebrow">{eyebrow}</p>'
            f'<h2{id_attr}>{title}</h2>{lead_html}</div>')


def page_hero(t, key, actions=""):
    actions_html = f'<div class="actions">{actions}</div>' if actions else ""
    return (f'<section class="hero hero-page"><div class="container">'
            f'<p class="eyebrow eyebrow-bar">{t(key + ".hero.eyebrow")}</p>'
            f'<h1>{t(key + ".hero.title")}</h1><p class="lead">{t(key + ".hero.lead")}</p>{actions_html}</div></section>')


def connect_btn(loc, label, cls="btn btn-primary"):
    return f'<a class="{cls}" href="{href(loc, "contact")}{HOTEL_CONTACT}">{label}{icon("arrow", "icon icon-dir")}</a>'


def cta_band(loc, t):
    return f"""<section class="section-surface cta-band" aria-labelledby="cta-title"><div class="container cta-inner" data-reveal>
<div><h2 id="cta-title">{t("home.cta.title")}</h2><p class="lead">{t("home.cta.body")}</p></div>
<div class="actions">{connect_btn(loc, t("home.cta.button"))}<a class="btn btn-secondary" href="{href(loc, "contact")}">{t("home.cta.secondary")}</a></div>
</div></section>"""


# ---- Hotel-first components -------------------------------------------------
def benefit_cards(t, key):
    """Six hotel benefits. Cards tied to a gated module carry a Coming soon chip, or are dropped when it is hidden."""
    out = ""
    for i, item in enumerate(t.raw(key)):
        mod = BENEFIT_MODULES[i]
        if mod and module_state(mod) == "hidden":
            continue
        chip = f'<span class="card-foot">{coming_soon_chip(t)}</span>' if mod else ""
        out += (f'<article class="card" data-reveal style="--d:{i % 3}"><span class="card-icon">{icon(BENEFIT_ICONS[i])}</span>'
                f'<h3>{t(f"{key}.{i}.title")}</h3><p>{t(f"{key}.{i}.body")}</p>{chip}</article>')
    return f'<div class="grid grid-3">{out}</div>'


def eco_diagram(t, uid="eco"):
    """Diagram 4 · Hotel → KabuK Platform → three KabuK channels. Platform is the foundation;
    KabuK Exchange is one channel built on it, not a peer infrastructure layer."""
    k = "diagram.eco."
    branches = ""
    for i, c in enumerate(CHANNELS):
        extra = ""
        if c == "exchange":
            items = "".join(f"<li>{esc(x)}</li>" for x in t.raw(k + "distributorItems"))
            extra = f'<div class="eco-downstream"><p>{t(k + "distributors")}</p><ul>{items}</ul></div>'
        planned = " eco-channel--planned" if CONFIG.get("channelStatus", {}).get(c) in ("planned", "comingSoon") else ""
        branches += (f'<li class="eco-channel{planned}" data-reveal style="--d:{i + 2}"><p class="eco-kind">{t(k + "channels." + c + ".kind")}</p>'
                     f'<p class="eco-name" lang="en" dir="ltr">{t(k + "channels." + c + ".name")}</p>'
                     f'<p class="eco-desc">{t(k + "channels." + c + ".body")}</p>{channel_chip(c, t)}{extra}</li>')
    roles = "".join(f"<li>{esc(x)}</li>" for x in t.raw(k + "platformRoles"))
    return f"""<figure class="eco" role="group" aria-labelledby="{uid}-label">
<p class="sr-only" id="{uid}-label">{t(k + "label")}</p>
<div class="eco-hotels" data-reveal>{icon("hotel")}<span>{t(k + "hotels")}</span></div>
<div class="eco-stem" aria-hidden="true"></div>
<div class="eco-platform" data-reveal style="--d:1"><p class="eco-platform-name"><span lang="en" dir="ltr">KabuK Platform</span></p>
<p class="eco-platform-desc">{t(k + "platformDesc")}</p><ul class="eco-roles">{roles}</ul></div>
<div class="eco-fork" aria-hidden="true"><span></span><span></span><span></span></div>
<ul class="eco-channels">{branches}</ul>
<figcaption class="rel-caption">{t(k + "caption")}</figcaption>
</figure>"""


def connect_options(loc, t):
    """Solutions > Ways to connect: KabuK direct integrations, payment options, and the channel manager /
    PMS integrations provided through Bakuun (assets/data/bakuun-integrations.json, refreshed with
    tools/fetch_bakuun.py). The full list is rendered statically; site.js adds search and filters."""
    k = "solutions.connect."
    conn = CONFIG.get("connections", {})
    bk = conn.get("bakuun", {})
    provider = bk.get("provider", "Bakuun")
    prov_html = f'<span lang="en" dir="ltr">{esc(provider)}</span>'
    data = load(bk["data"]) if bk.get("data") else {"integrations": []}
    items = data["integrations"]

    def rows(entries):
        return "".join(f'<li><span class="connect-name" lang="en" dir="ltr">{esc(e["name"])}</span>{chip(e.get("status"), t)}</li>' for e in entries)

    pays = "".join(f'<li><span class="connect-name">{t(k + "payments." + p)}</span>{chip(st, t)}</li>'
                   for p, st in conn.get("payments", {}).items())
    dir_items = ""
    for e in items:
        st = e.get("status") or "unconfirmed"
        badge = f'<span class="dir-badge">{t(k + "types.premium")}</span>' if e.get("type") == "premium" else ""
        dir_items += (f'<li data-name="{esc(e["name"].lower())}" data-status="{st}" data-type="{esc(e.get("type") or "")}">'
                      f'<span class="dir-name" lang="en" dir="ltr">{esc(e["name"])}</span>{badge}{chip(st, t)}</li>')
    count = len(items)
    opt = lambda v, label: f'<option value="{v}">{label}</option>'
    status_opts = opt("", t(k + "statusAll")) + opt("live", t("common.status.live")) + opt("development", t("common.status.development"))
    type_opts = opt("", t(k + "typeAll")) + opt("premium", t(k + "types.premium")) + opt("connectivity", t(k + "types.connectivity"))
    source = (t(k + "source").replace("{provider}", prov_html).replace("{date}", f'<time dir="ltr" datetime="{esc(data.get("_retrieved", ""))}">{esc(data.get("_retrieved", ""))}</time>'))
    return f"""<section class="section" id="connect" aria-labelledby="connect-title"><div class="container">
{section_head(t(k + "eyebrow"), t(k + "title"), t(k + "lead").replace("{count}", str(count)), "connect-title")}
<div class="grid grid-2">
<article class="card" data-reveal><span class="card-icon">{icon("connectivity")}</span><h3>{t(k + "directTitle")}</h3><p>{t(k + "directBody")}</p><ul class="connect-list">{rows(conn.get("direct", []))}</ul></article>
<article class="card" data-reveal style="--d:1"><span class="card-icon">{icon("billing")}</span><h3>{t(k + "paymentsTitle")}</h3><p>{t(k + "paymentsBody")}</p><ul class="connect-list">{pays}</ul></article>
</div>
<div class="card dir" id="bakuun-integrations" data-dir data-count-template="{esc(t.raw(k + "count"))}" data-reveal>
<div class="dir-head"><div><h3 id="dir-title">{t(k + "bakuunTitle")}</h3><p>{t(k + "provided").replace("{provider}", prov_html)} {t(k + "bakuunBody").replace("{count}", str(count))}</p></div>
<span class="card-foot">{ext_link("bakuun", t(k + "sourceLink"), t, "text-link")}</span></div>
<form class="dir-filters" role="search" aria-label="{t(k + "filtersLabel")}" data-dir-filters>
<div class="field"><label for="dir-q">{t(k + "search")}</label><input class="input" id="dir-q" type="search" autocomplete="off" placeholder="{t(k + "searchPlaceholder")}" data-dir-q></div>
<div class="field"><label for="dir-status">{t(k + "statusLabel")}</label><select class="select" id="dir-status" data-dir-status>{status_opts}</select></div>
<div class="field"><label for="dir-type">{t(k + "typeLabel")}</label><select class="select" id="dir-type" data-dir-type>{type_opts}</select></div>
</form>
<p class="dir-count" role="status" aria-live="polite" data-dir-count>{t(k + "count").replace("{shown}", str(count)).replace("{total}", str(count))}</p>
<ul class="dir-list" aria-labelledby="dir-title" data-dir-list>{dir_items}</ul>
<p class="dir-empty" data-dir-empty hidden>{t(k + "empty")}</p>
<p class="fineprint" style="margin-top:16px">{source}</p>
</div>
<p class="fineprint" style="margin-top:24px">{t(k + "note")}</p>
</div></section>"""


def gated_modules(loc, t):
    """Market intelligence and white-label: register-interest modules while unverified (site-config modules.*)."""
    cards = ""
    for i, (mod, key, interest, ic) in enumerate([("marketInsights", "home.market", "market-insights", "analytics"),
                                                  ("whiteLabel", "home.whiteLabel", "white-label", "brand")]):
        if module_state(mod) == "hidden":
            continue
        items = "".join(f'<li><strong>{esc(x["title"])}</strong> {esc(x["body"])}</li>' for x in t.raw(key + ".items"))
        cards += f"""<article class="card module-card" id="{interest}" data-module="{mod}" data-module-state="comingSoon" data-reveal style="--d:{i}">
<div class="module-top"><span class="card-icon">{icon(ic)}</span>{coming_soon_chip(t)}</div>
<p class="eyebrow">{t(key + ".eyebrow")}</p><h3>{t(key + ".title")}</h3><p>{t(key + ".lead")}</p>
<ul class="module-list">{items}</ul>
<span class="card-foot"><a class="btn btn-secondary" href="{href(loc, "contact")}?type=hotel&amp;interest={interest}">{t(key + ".cta")}{icon("arrow", "icon icon-dir")}</a></span>
</article>"""
    if not cards:
        return ""
    return f"""<section class="section" aria-labelledby="soon-title"><div class="container">
{section_head(t("home.soon.eyebrow"), t("home.soon.title"), t("home.soon.lead"), "soon-title")}
<div class="grid grid-2">{cards}</div>
</div></section>"""


# ---- Diagram 1 · Platform service architecture ----------------------------
def arch_diagram(t, compact=False, uid="arch"):
    top = "".join(f'<li class="arch-pill">{esc(x)}</li>' for x in t.raw("diagram.arch.topItems"))
    top += f'<li class="arch-pill arch-pill--network" lang="en" dir="ltr">{t("diagram.arch.topExchange")}</li>'
    nodes = [("pricing", "pricing"), ("availability", "availability"), ("booking", "booking"), ("reservations", "reservations"),
             ("billing", "billing"), ("content", "content"), ("identity", "identity"), ("analytics", "analytics")]
    node_html = ""
    for i, (k, ic) in enumerate(nodes):
        planned = k == "analytics"
        tag = f'<span class="arch-node-tag">{t("diagram.arch.plannedTag")}</span>' if planned else ""
        node_html += (f'<li class="arch-node" style="--i:{i};--d:{i}" data-reveal>'
                      f'{icon(ic)}<span class="arch-node-name">{t("diagram.arch.nodes." + k)}</span>{tag}</li>')
    base = "".join(f'<li>{esc(x)}</li>' for x in t.raw("diagram.arch.baseItems"))
    links = '<div class="arch-links" aria-hidden="true"><span></span><span></span><span></span><span></span></div>'
    links_up = '<div class="arch-links arch-links--up" aria-hidden="true"><span></span><span></span><span></span><span></span></div>'
    return f"""<figure class="arch{" arch--compact" if compact else ""}" role="group" aria-labelledby="{uid}-label">
<div class="arch-frame">
<p class="sr-only" id="{uid}-label">{t("diagram.arch.label")}</p>
<div class="arch-top"><p class="arch-layer-label">{t("diagram.arch.top")}</p><ul class="arch-row">{top}</ul></div>
{links}
<div class="arch-core"><p class="arch-layer-label"><span lang="en" dir="ltr">KabuK Platform</span><span aria-hidden="true">·</span>{t("diagram.arch.core")}</p><ul class="arch-grid">{node_html}</ul></div>
{links_up}
<div class="arch-base"><p class="arch-layer-label" style="margin-top:12px">{t("diagram.arch.base")}</p><ul class="arch-row">{base}</ul></div>
</div>
<figcaption class="arch-caption">{t("diagram.arch.caption")}</figcaption>
</figure>"""


# ---- Diagram 2 · Product relationship -------------------------------------
def rel_diagram(t, uid="rel"):
    both = f'<span class="rel-both">{t("diagram.rel.bothSides")}</span>'
    supply_items = t.raw("diagram.rel.supplyItems")
    demand_items = t.raw("diagram.rel.demandItems")
    supply = "".join(f'<li class="rel-node">{esc(x)}{both if i >= 1 else ""}</li>' for i, x in enumerate(supply_items))
    demand = "".join(f'<li class="rel-node">{esc(x)}{both if i >= 1 else ""}</li>' for i, x in enumerate(demand_items))
    funcs = "".join(f'<li>{esc(x)}</li>' for x in t.raw("diagram.rel.exchangeFunctions"))
    arrow = f'<div class="rel-link" aria-hidden="true"><span class="rel-link-line"></span>{icon("arrow")}</div>'
    return f"""<figure class="rel" role="group" aria-labelledby="{uid}-label">
<p class="sr-only" id="{uid}-label">{t("diagram.rel.label")}</p>
<div class="rel-grid">
<div class="rel-col" data-reveal><p class="rel-head">{t("diagram.rel.supply")}</p><ul class="rel-list">{supply}</ul>
<p class="rel-enablers"><strong>{t("diagram.rel.enablersTitle")}</strong>{t("diagram.rel.enablers")}</p></div>
{arrow}
<div class="rel-exchange" data-reveal style="--d:2"><p class="rel-head" lang="en" dir="ltr">{t("diagram.rel.exchange")}</p>
<div class="rel-exchange-box"><p class="rel-exchange-name" lang="en" dir="ltr">KabuK Exchange</p><p class="rel-exchange-desc">{t("diagram.rel.exchangeDesc")}</p><ul class="rel-exchange-functions">{funcs}</ul></div></div>
{arrow}
<div class="rel-col" data-reveal style="--d:4"><p class="rel-head">{t("diagram.rel.demand")}</p><ul class="rel-list">{demand}</ul></div>
<div class="rel-riser" aria-hidden="true"></div>
<div class="rel-foundation" data-reveal style="--d:5"><p class="rel-foundation-title"><span>{t("diagram.rel.foundationPrefix")} <b lang="en" dir="ltr">{t("diagram.rel.foundationName")}</b></span></p>
<p class="rel-foundation-services">{t("diagram.rel.foundationServices")}</p></div>
</div>
<figcaption class="rel-caption">{t("diagram.rel.caption")}</figcaption>
</figure>"""


# ---- Diagram 3 · Point-to-point vs shared foundation ----------------------
def compare_diagram(t):
    pts = [(40, 40), (160, 24), (280, 40), (40, 140), (160, 156), (280, 140)]
    mesh_lines = ""
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            mesh_lines += f'<line x1="{pts[i][0]}" y1="{pts[i][1]}" x2="{pts[j][0]}" y2="{pts[j][1]}"/>'
    nodes = "".join(f'<rect class="node-sys" x="{x - 14}" y="{y - 10}" width="28" height="20" rx="4"/>' for x, y in pts)
    hub_lines = "".join(f'<line x1="{x}" y1="{y + (10 if y < 90 else -10)}" x2="{x}" y2="{82 if y < 90 else 98}"/>' for x, y in pts)
    flows = "".join(f'<line class="flow" x1="{x}" y1="{y + (10 if y < 90 else -10)}" x2="{x}" y2="{82 if y < 90 else 98}" style="animation-delay:{i * .5}s"/>' for i, (x, y) in enumerate(pts))
    return f"""<div class="compare" role="group" aria-label="{t("diagram.compare.label")}">
<div class="compare-panel" data-reveal>
<svg viewBox="0 0 320 180" aria-hidden="true"><g class="mesh">{mesh_lines}</g>{nodes}</svg>
<h3>{t("diagram.compare.beforeTitle")}</h3><p>{t("diagram.compare.beforeBody")}</p></div>
<div class="compare-panel" data-reveal style="--d:2">
<svg viewBox="0 0 320 180" aria-hidden="true"><g class="hub">{hub_lines}{flows}</g>
<rect class="node-core" x="20" y="80" width="280" height="20" rx="4"/><rect class="node-core-bar" x="20" y="80" width="280" height="3"/>{nodes}</svg>
<h3>{t("diagram.compare.afterTitle")}</h3><p>{t("diagram.compare.afterBody")}</p></div>
</div>"""


def ai_chip(t):
    status = CONFIG["capabilityStatus"].get("ai", "planned")
    return f'<span class="chip chip-{CHIP_CLASS.get(status, "planned")}">{t("diagram.arch.plannedTag")}</span>'


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_home(loc, t):
    control = "".join(f'<div class="pillar" data-reveal style="--d:{i}"><span class="card-index">0{i + 1}</span><h3>{esc(p["title"])}</h3><p>{esc(p["body"])}</p>'
                      f'{"<span>" + coming_soon_chip(t) + "</span>" if CONTROL_MODULES[i] else ""}</div>'
                      for i, p in enumerate(t.raw("home.control.items")) if not (CONTROL_MODULES[i] and module_state(CONTROL_MODULES[i]) == "hidden"))
    steps = "".join(f'<li class="step" data-reveal style="--d:{i}"><h3>{esc(s["title"])}</h3><p>{esc(s["body"])}</p></li>'
                    for i, s in enumerate(t.raw("home.onboarding.steps")))
    also = "".join(f'<li><a href="{href(loc, "solutions", a)}">{t(f"common.segments.{k}.name")}</a></li>' for k, a, _ in SEGMENTS[1:])
    return f"""<main id="main">
{draft_banner(loc, t, "home")}
<section class="hero"><div class="container hero-grid">
<div>
<p class="eyebrow eyebrow-bar">{t("home.hero.eyebrow")}</p>
<h1>{t("home.hero.title")}</h1>
<p class="hero-sub">{t("home.hero.subtitle")}</p>
<p class="lead">{t("home.hero.lead")}</p>
<div class="actions">{connect_btn(loc, t("home.hero.primary"))}
<a class="btn btn-secondary" href="{href(loc, "solutions", "benefits")}">{t("home.hero.secondary")}</a></div>
<p class="fineprint hero-note">{t("home.hero.note")}</p>
</div>
<div data-reveal>{arch_diagram(t, compact=True, uid="arch-hero")}</div>
</div></section>

<section class="section section-surface" aria-labelledby="ben-title"><div class="container">
{section_head(t("home.benefits.eyebrow"), t("home.benefits.title"), t("home.benefits.lead"), "ben-title")}
{benefit_cards(t, "home.benefits.items")}
</div></section>

<section class="section" id="ecosystem" aria-labelledby="eco-title"><div class="container">
{section_head(t("home.ecosystem.eyebrow"), t("home.ecosystem.title"), t("home.ecosystem.lead"), "eco-title")}
{eco_diagram(t, "eco-home")}
<div class="actions"><a class="btn btn-secondary" href="{href(loc, "solutions", "ecosystem")}">{t("home.ecosystem.cta")}{icon("arrow", "icon icon-dir")}</a></div>
</div></section>

<section class="section section-surface" aria-labelledby="ctl-title"><div class="container">
{section_head(t("home.control.eyebrow"), t("home.control.title"), t("home.control.lead"), "ctl-title")}
<div class="pillars">{control}</div>
<p class="scope-note" style="margin-top:40px" data-reveal>{icon("info")}<span>{t("home.control.qualifier")}</span></p>
</div></section>

{gated_modules(loc, t)}

<section class="section section-surface" aria-labelledby="onb-title"><div class="container">
{section_head(t("home.onboarding.eyebrow"), t("home.onboarding.title"), "", "onb-title")}
<ol class="steps">{steps}</ol>
<p class="notice notice-info" style="margin-top:40px" data-reveal>{icon("info")}<span><strong>{t("home.onboarding.note")}</strong></span></p>
<div class="actions">{connect_btn(loc, t("home.onboarding.cta"))}</div>
</div></section>

<section class="section" aria-labelledby="aud-title"><div class="container split">
<div class="section-head" style="margin:0"><p class="eyebrow">{t("home.audiences.eyebrow")}</p><h2 id="aud-title">{t("home.audiences.title")}</h2></div>
<div class="prose" data-reveal><p class="strong lead" style="color:var(--text)">{t("home.audiences.lead")}</p>
<p>{t("home.audiences.also")}</p><ul class="also-list">{also}</ul></div>
</div>
<div class="container"><p class="notice notice-info" style="margin-top:48px" data-reveal>{icon("info")}<span><strong>{t("home.transparency.title")}.</strong> {t("home.transparency.body")} <a href="{href(loc, "technology", "status")}">{t("home.transparency.link")}</a></span></p></div>
</section>

{cta_band(loc, t)}
</main>
"""


def page_solutions(loc, t):
    rows = ""
    for k, a, ctype in SEGMENTS:
        topics = "".join(f"<li>{esc(x)}</li>" for x in t.raw(f"audienceCopy.{k}.topics"))
        rows += f"""<article class="audience" id="{a}" aria-labelledby="{a}-title" data-reveal>
<div><p class="eyebrow">{t(f"common.segments.{k}.name")}</p><h3 id="{a}-title">{t(f"audienceCopy.{k}.title")}</h3></div>
<div class="audience-body"><p>{t(f"audienceCopy.{k}.body")}</p>
<p class="field-hint">{t("solutions.topicsLabel")}</p><ul class="tick-list">{topics}</ul>
<p><a class="btn btn-secondary" href="{href(loc, "contact")}{HOTEL_CONTACT if ctype == "hotel" else "?type=" + ctype}">{t(f"audienceCopy.{k}.cta")}{icon("arrow", "icon icon-dir")}</a></p></div>
</article>"""
    steps = "".join(f'<li class="step" data-reveal style="--d:{i}"><h3>{esc(s["title"])}</h3><p>{esc(s["body"])}</p></li>'
                    for i, s in enumerate(t.raw("solutions.pathway.steps")))
    faq = "".join(f'<details class="faq-item"><summary>{esc(q["q"])}</summary><p>{esc(q["a"])}</p></details>' for q in t.raw("solutions.faq.items"))
    k = "solutions.ecosystem."
    eco_cols = (f'<div class="card"><p class="eyebrow">{t(k + "consumerTitle")}</p><ul class="eco-text-list">'
                f'<li><strong lang="en" dir="ltr">HafH</strong> {t(k + "hafh")} {channel_chip("hafh", t)}</li>'
                f'<li><strong lang="en" dir="ltr">Omakastay</strong> {t(k + "omakastay")} {channel_chip("omakastay", t)}</li></ul></div>'
                f'<div class="card"><p class="eyebrow" lang="en" dir="ltr" style="text-align:start">KabuK Exchange</p><p>{t(k + "exchangeBody")}</p>'
                f'<span class="card-foot">{ext_link("exchange", t("solutions.exchangeNote.cta"), t, "text-link")}</span></div>'
                f'<div class="card is-foundation"><p class="eyebrow">{t(k + "platformTitle")}</p><p>{t(k + "platformBody")}</p></div>')
    return f"""<main id="main">
{draft_banner(loc, t, "solutions")}
{page_hero(t, "solutions", connect_btn(loc, t("solutions.hero.cta")))}
<section class="section section-surface" id="benefits" aria-labelledby="ben-title"><div class="container">
{section_head(t("solutions.benefits.eyebrow"), t("solutions.benefits.title"), "", "ben-title")}
{benefit_cards(t, "solutions.benefits.items")}
</div></section>
<section class="section" id="faq" aria-labelledby="faq-title"><div class="container split">
<div class="section-head" style="margin:0"><p class="eyebrow">{t("solutions.faq.eyebrow")}</p><h2 id="faq-title">{t("solutions.faq.title")}</h2></div>
<div class="faq" data-reveal>{faq}</div>
</div></section>
<section class="section section-surface" id="ecosystem" aria-labelledby="eco-sol-title"><div class="container">
{section_head(t(k + "eyebrow"), t(k + "title"), t(k + "lead"), "eco-sol-title")}
{eco_diagram(t, "eco-sol")}
<div class="grid grid-3" style="margin-top:48px">{eco_cols}</div>
<div class="actions">{connect_btn(loc, t(k + "cta"))}</div>
</div></section>
{connect_options(loc, t)}
<section class="section" aria-labelledby="seg-title"><div class="container">
{section_head(t("solutions.segments.eyebrow"), t("solutions.segments.title"), t("solutions.segments.lead"), "seg-title")}
{rows}</div></section>
<section class="section section-surface" aria-labelledby="path-title"><div class="container">
{section_head(t("solutions.pathway.eyebrow"), t("solutions.pathway.title"), t("solutions.pathway.lead"), "path-title")}
<ol class="steps">{steps}</ol>
</div></section>
{cta_band(loc, t)}
</main>
"""


def page_technology(loc, t):
    legend = "".join(f'<div class="legend-item"><span>{chip(s, t)}</span><p>{t("technology.legend." + s)}</p></div>'
                     for s in ["live", "development", "comingSoon"])
    domains = ""
    for d in DOMAINS:
        covers = "".join(f"<li>{esc(x)}</li>" for x in t.raw(f"technology.domains.{d}.covers"))
        extra = ai_chip(t) if d == "analytics" else ""
        domains += f"""<article class="domain" id="{d}" aria-labelledby="{d}-title" data-reveal>
<div class="domain-head"><span class="card-icon">{icon(DOMAIN_ICON[d])}</span><h3 id="{d}-title">{t("common.services." + d)}</h3><span style="display:flex;gap:8px;flex-wrap:wrap">{status_chip(d, t)}{extra}</span></div>
<div class="domain-body"><p>{t(f"technology.domains.{d}.body")}</p>
<div><p class="field-hint" style="margin-bottom:12px">{t("technology.covers")}</p><ul class="tick-list">{covers}</ul></div>
<p class="scope-note">{icon("info")}<span><strong>{t("technology.scopeNote")}:</strong> {t(f"technology.domains.{d}.note")}</span></p></div>
</article>"""

    def points(key):
        return "".join(f"<li>{esc(x)}</li>" for x in t.raw(key))
    return f"""<main id="main">
{draft_banner(loc, t, "technology")}
{page_hero(t, "technology")}
<section class="section" aria-labelledby="arch-title"><div class="container">
{section_head(t("technology.architecture.eyebrow"), t("technology.architecture.title"), t("technology.architecture.lead"), "arch-title")}
<div data-reveal>{arch_diagram(t, uid="arch-tech")}</div>
<div id="status" style="margin-top:48px" data-reveal><h3 style="font:var(--type-h4);font-family:var(--font-sans);margin-bottom:16px">{t("technology.legend.title")}</h3><div class="legend">{legend}</div></div>
</div></section>
<section class="section section-surface" id="core-services" aria-labelledby="dom-title"><div class="container">
<div class="section-head"><p class="eyebrow">{t("home.capabilities.eyebrow")}</p><h2 id="dom-title">{t("technology.domainsTitle")}</h2></div>
{domains}
</div></section>
<section class="section" aria-label="{t("technology.connectivity.eyebrow")} · {t("technology.operations.eyebrow")}"><div class="container grid grid-2">
<article class="card" id="connectivity" data-reveal><span class="card-icon">{icon("connectivity")}</span><p class="eyebrow">{t("technology.connectivity.eyebrow")}</p><h3>{t("technology.connectivity.title")}</h3><p>{t("technology.connectivity.body")}</p><ul class="tick-list" style="grid-template-columns:1fr">{points("technology.connectivity.points")}</ul><span class="card-foot"><a class="text-link" href="{href(loc, "solutions", "connect")}">{t("technology.connectivity.link")}{icon("arrow", "icon icon-dir")}</a></span></article>
<article class="card" id="operations" data-reveal style="--d:1"><span class="card-icon">{icon("operations")}</span><p class="eyebrow">{t("technology.operations.eyebrow")}</p><h3>{t("technology.operations.title")}</h3><p>{t("technology.operations.body")}</p><ul class="tick-list" style="grid-template-columns:1fr">{points("technology.operations.points")}</ul></article>
</div>
<div class="container"><p class="fineprint" style="margin-top:32px">{t("technology.disclaimer")}</p></div>
</section>
{cta_band(loc, t)}
</main>
"""


def page_why(loc, t):
    pillars = "".join(
        f'<article class="card" data-reveal style="--d:{i % 2}"><span class="card-index">0{i + 1}</span><h3>{esc(p["title"])}</h3><p style="color:var(--text)">{esc(p["body"])}</p><p>{esc(p["detail"])}</p></article>'
        for i, p in enumerate(t.raw("why.pillarsDetail")))
    principles = "".join(f'<div class="pillar" data-reveal style="--d:{i}"><h3>{esc(p["title"])}</h3><p>{esc(p["body"])}</p></div>'
                         for i, p in enumerate(t.raw("why.principles.items")))
    nots = "".join(f"<li>{esc(x)}</li>" for x in t.raw("why.notList.items"))
    return f"""<main id="main">
{draft_banner(loc, t, "why")}
{page_hero(t, "why")}
<section class="section" aria-labelledby="prob-title"><div class="container">
{section_head(t("why.problem.eyebrow"), t("why.problem.title"), t("why.problem.lead"), "prob-title")}
{compare_diagram(t)}
</div></section>
<section class="section section-surface" aria-labelledby="pil-title"><div class="container">
<div class="section-head"><p class="eyebrow">{t("why.hero.eyebrow")}</p><h2 id="pil-title">{t("why.pillarsTitle")}</h2></div>
<div class="grid grid-2">{pillars}</div>
</div></section>
<section class="section" aria-labelledby="pr-title"><div class="container">
{section_head(t("why.principles.eyebrow"), t("why.principles.title"), "", "pr-title")}
<div class="pillars" style="grid-template-columns:repeat(3,minmax(0,1fr))">{principles}</div>
<div class="card" style="margin-top:48px" data-reveal><h3>{t("why.notList.title")}</h3><ul class="tick-list">{nots}</ul><p>{t("why.notList.body")} {ext_link("exchange", t("home.relationship.cta"), t, "text-link")}</p></div>
</div></section>
{cta_band(loc, t)}
</main>
"""


def page_about(loc, t):
    fam = ""
    for i, item in enumerate(t.raw("about.family.items")):
        current = item.get("current")
        link = ""
        if current:
            link = f'<span class="chip chip-core">{t("about.family.youAreHere")}</span>'
        elif item.get("link"):
            link = ext_link(item["link"], t("about.family.visit"), t, "text-link")
        fam += (f'<article class="card{" is-current" if current else ""}" data-reveal style="--d:{i}"><p class="family-role">{esc(item["role"])}</p>'
                f'<h3 lang="en" dir="ltr" style="text-align:start">{esc(item["name"])}</h3><p>{esc(item["body"])}</p><span class="card-foot">{link}</span></article>')
    return f"""<main id="main">
{draft_banner(loc, t, "about")}
{page_hero(t, "about")}
<section class="section section-surface" aria-labelledby="focus-title"><div class="container split">
<div class="section-head" style="margin:0"><p class="eyebrow">{t("about.hero.eyebrow")}</p><h2 id="focus-title">{t("about.focus.title")}</h2></div>
<p class="lead" style="color:var(--text);font-size:clamp(20px,2.2vw,26px);line-height:1.45" data-reveal>{t("about.focus.body")}</p>
</div></section>
<section class="section" aria-labelledby="fam-title"><div class="container">
{section_head(t("about.family.eyebrow"), t("about.family.title"), t("about.family.lead"), "fam-title")}
<div class="family">{fam}</div>
</div></section>
<section class="section section-dark theme-dark" aria-labelledby="rel-ab-title"><div class="container">
{section_head(t("home.relationship.eyebrow"), t("home.relationship.title"), t("home.relationship.body"), "rel-ab-title")}
{rel_diagram(t, "rel-about")}
</div></section>
<section class="section" aria-labelledby="team-title"><div class="container split">
<div class="section-head" style="margin:0"><p class="eyebrow">{t("about.team.eyebrow")}</p><h2 id="team-title">{t("about.team.title")}</h2></div>
<div class="prose" data-reveal><p class="strong">{t("about.team.body")}</p></div>
</div></section>
{cta_band(loc, t)}
</main>
"""


def page_contact(loc, t):
    f = "contact.form."

    def options(group, choose):
        opts = f'<option value="">{t(f + choose)}</option>'
        for k in t._get(EN, f + group).keys():
            opts += f'<option value="{k}">{t(f + group + "." + k)}</option>'
        return opts

    def field(fid, label_key, control, required=True, hint_key=None, full=False):
        hint = f'<span class="field-hint" id="{fid}-hint">{t(f + hint_key)}</span>' if hint_key else ""
        opt = "" if required else f' <span class="optional">({t(f + "optional")})</span>'
        req = f' <span class="req" aria-hidden="true">*</span>' if required else ""
        described = f"{fid}-error" + (f" {fid}-hint" if hint_key else "")
        control = control.replace("{described}", described)
        return (f'<div class="field{" field-full" if full else ""}"><label for="{fid}">{t(f + label_key)}{req}{opt}</label>{control}{hint}'
                f'<span class="field-error" id="{fid}-error"></span></div>')

    privacy_link = f'<a href="{href(loc, "privacy")}">{t(f + "privacyLink")}</a>'
    privacy_text = t(f + "privacy").replace("{link}", privacy_link)
    aside = "".join(f'<li><strong>{esc(i["title"])}</strong><span>{esc(i["body"])}</span></li>' for i in t.raw("contact.aside.items"))
    ui = {
        "errors": t.raw(f + "errors"), "confirmation": t.raw(f + "confirmation"), "fallback": t.raw(f + "fallback"),
        "configError": t.raw(f + "configError"), "emailSubject": t.raw(f + "emailSubject"), "emailLabels": t.raw(f + "emailLabels"),
    }
    ui_json = json.dumps(ui, ensure_ascii=False).replace("</", "<\\/")
    return f"""<main id="main">
{draft_banner(loc, t, "contact")}
{page_hero(t, "contact")}
<section class="section section-tight"><div class="container form-layout">
<div>
<p class="notice notice-info" style="margin-bottom:24px">{icon("mail")}<span>{t("contact.mailtoNotice")}</span></p>
<form class="form-card" id="lead-form" novalidate aria-labelledby="form-title">
<h2 id="form-title" style="font:var(--type-h3);font-family:var(--font-sans);margin-bottom:8px">{t(f + "title")}</h2>
<p class="field-hint" style="margin-bottom:24px"><span aria-hidden="true">*</span> {t(f + "required")}</p>
<div class="form-summary notice" id="form-summary" role="alert" tabindex="-1" hidden></div>
<div class="form-grid">
{field("name", "name", '<input class="input" id="name" name="name" autocomplete="name" required aria-describedby="{described}">')}
{field("company", "company", '<input class="input" id="company" name="company" autocomplete="organization" required aria-describedby="{described}">')}
{field("email", "email", '<input class="input" id="email" name="email" type="email" autocomplete="email" inputmode="email" dir="ltr" required aria-describedby="{described}">', full=True)}
{field("orgType", "orgType", '<select class="select" id="orgType" name="orgType" required aria-describedby="{described}">' + options("orgTypes", "orgTypeChoose") + '</select>')}
{field("region", "region", '<select class="select" id="region" name="region" required aria-describedby="{described}">' + options("regions", "regionChoose") + '</select>')}
{field("interest", "interest", '<select class="select" id="interest" name="interest" required aria-describedby="{described}">' + options("interests", "interestChoose") + '</select>', full=True)}
{field("systems", "systems", '<input class="input" id="systems" name="systems" aria-describedby="{described}">', required=False, hint_key="systemsHint", full=True)}
{field("message", "message", '<textarea class="textarea" id="message" name="message" required aria-describedby="{described}"></textarea>', hint_key="messageHint", full=True)}
<div class="field field-full"><label class="check"><input type="checkbox" id="privacy" name="privacy" required aria-describedby="privacy-error"><span>{privacy_text}</span></label><span class="field-error" id="privacy-error"></span></div>
</div>
<div class="form-actions"><button class="btn btn-primary" type="submit">{icon("mail")}{t(f + "submit")}</button></div>
<div class="form-status" id="form-status" role="status" aria-live="polite"></div>
</form>
<script type="application/json" id="form-i18n">{ui_json}</script>
</div>
<aside aria-labelledby="next-title"><h2 id="next-title" style="font:var(--type-h4);font-family:var(--font-sans);margin-bottom:8px">{t("contact.aside.title")}</h2>
<ul class="aside-list">{aside}</ul>
<p class="fineprint" style="margin-top:16px">{t("contact.aside.only")}</p></aside>
</div></section>
</main>
"""


def page_privacy(loc, t):
    secs = "".join(f'<h2>{esc(s["title"])}</h2><p>{esc(s["body"])}</p>' for s in t.raw("privacy.sections"))
    return f"""<main id="main">
{draft_banner(loc, t, "privacy")}
{page_hero(t, "privacy")}
<section class="section section-tight"><div class="container">
<p class="notice" role="note">{icon("alert")}<span><strong>{t("privacy.draft")}</strong></span></p>
<div class="prose" style="margin-top:32px">{secs}</div>
</div></section>
</main>
"""


RENDER = {"home": page_home, "solutions": page_solutions, "technology": page_technology, "why": page_why,
          "about": page_about, "contact": page_contact, "privacy": page_privacy}


def page_404(loc, t):
    body = f"""<main id="main"><section class="hero hero-page"><div class="container">
<p class="eyebrow eyebrow-bar">404</p><h1>{t("notFound.title")}</h1><p class="lead">{t("notFound.body")}</p>
<div class="actions"><a class="btn btn-primary" href="/">{t("notFound.home")}</a><a class="btn btn-secondary" href="/contact/">{t("notFound.contact")}</a></div>
</div></section></main>"""
    base = CONFIG["site"].get("deployBasePath", "/")
    h = head(loc, t, "home", "notFound").replace(f'<link rel="canonical" href="{abs_url(loc, "home")}">', "")
    out = ROOT_ABS.sub(lambda m: m.group(1), h + header(loc, t, "notfound") + body + footer(loc, t, "home"))
    return out.replace('<meta charset="utf-8">', f'<meta charset="utf-8">\n<base href="{esc(base)}">', 1).replace('data-root="__ROOT__"', f'data-root="{esc(base)}"')


# ---------------------------------------------------------------------------
ROOT_ABS = re.compile(r'(\s(?:href|src)=")/(?!/)')


def relativize(rel, content):
    """Rewrite root-absolute href/src ("/x") to page-relative ("../x") so the site
    works at a domain root AND under a subpath such as GitHub Pages /<repo>/."""
    depth = rel.replace("\\", "/").count("/")
    prefix = "../" * depth if depth else "./"
    content = ROOT_ABS.sub(lambda m: m.group(1) + prefix, content)
    return content.replace('data-root="__ROOT__"', f'data-root="{prefix}"')


def write(rel, content):
    if rel.endswith(".html") and rel != "404.html":
        content = relativize(rel, content)
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def count_strings(o):
    if isinstance(o, str):
        return 1
    if isinstance(o, list):
        return sum(count_strings(x) for x in o)
    if isinstance(o, dict):
        return sum(count_strings(v) for k, v in o.items() if not k.startswith("_"))
    return 0


def main():
    check = "--check" in sys.argv
    report = []
    total = 0
    for loc in LOCALES:
        fpath = os.path.join(ROOT, "i18n", f"{loc['code']}.json")
        data = EN if loc["code"] == "en" else (load(f"i18n/{loc['code']}.json") if os.path.exists(fpath) else {})
        t = Tr(data, loc["code"])
        for pid, path, meta in PAGES:
            out = head(loc, t, pid, meta) + header(loc, t, pid) + RENDER[pid](loc, t) + footer(loc, t, pid)
            write(os.path.join(loc["path"], path, "index.html"), out)
            total += 1
        if loc["code"] == "en":
            write("404.html", page_404(loc, t))
        report.append((loc, count_strings(data), sorted(t.missing)))

    # sitemap with hreflang alternates
    urls = ""
    for pid, _, _ in PAGES:
        if pid == "privacy":
            continue
        for loc in LOCALES:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l["hreflang"]}" href="{abs_url(l, pid)}"/>' for l in LOCALES)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(LOCALES[0], pid)}"/>'
            urls += f"<url><loc>{abs_url(loc, pid)}</loc>{alts}</url>\n"
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
    robots = ("User-agent: *\nAllow: /\n" if VERIFIED else "# Pre-launch: canonical domain not verified (site-config.json site.canonicalVerified=false).\nUser-agent: *\nDisallow: /\n")
    write("robots.txt", robots + f"Sitemap: {BASE}/sitemap.xml\n")

    # translation review inventory
    lines = ["# Translation review inventory", "",
             "Generated by `tools/build.py`. English (`i18n/en.json`) is the master copy. Every other locale is a **draft** written without native-speaker review and must not be presented as approved.", "",
             "| Locale | Route | Status | Strings | Keys falling back to English |", "|---|---|---|---|---|"]
    for loc, n, missing in report:
        lines.append(f"| {loc['label']} (`{loc['code']}`) | `/{loc['path'] + '/' if loc['path'] else ''}` | {loc['review']} | {n} | {len(missing)} |")
    lines += ["", "To approve a locale after native review, set its `review` value to `approved` in `site-config.json` and rebuild; the draft banner and footer note are then removed.", ""]
    for loc, n, missing in report:
        if missing:
            lines.append(f"## Missing in {loc['code']}")
            lines += [f"- `{k}`" for k in missing]
            lines.append("")
    write("docs/TRANSLATION_REVIEW_INVENTORY.md", "\n".join(lines))

    missing_any = any(m for _, _, m in report)
    print(f"Built {total} pages + 404 for {len(LOCALES)} locales. Canonical base: {BASE} (verified: {VERIFIED}).")
    for loc, n, missing in report:
        print(f"  {loc['code']:6} {n:4} strings, {len(missing)} fallback keys")
    if check and missing_any:
        sys.exit(1)


if __name__ == "__main__":
    main()
