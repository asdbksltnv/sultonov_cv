#!/usr/bin/env python3
"""Build the English portfolio pages from src/.

Each page's content lives in src/<name>.html. This script wraps it in the
shared head (title, description, canonical, hreflang, social tags and
structured data), navigation and footer, and writes index.html, about.html
and the other pages to the site folder. tools/i18n.py then builds the Uzbek
and Russian versions from these English pages.

Edit the files in src/ (or the page list below), then run from the site folder:

    python3 tools/build.py
"""
import datetime
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://asadbeksultonov.com/"
EMAIL = "asadbeksltnv90@gmail.com"
OG_IMAGE = BASE + "assets/img/brand/og-image.png"
OG_IMAGE_ALT = "Asadbek Sultonov logo: a letter A formed by a knee joint, with the words Orthopaedic surgeon"

# Order = order in the menu and in the previous/next links.
PAGES = [
    dict(file="index.html", key="home", name="Home",
         title="Asadbek Sultonov · Orthopedic surgery resident and clinical AI researcher",
         desc="Asadbek Sultonov, PGY2 orthopedic surgery resident at Akfa Medline University Hospital in Tashkent, researching bone regeneration and AI for knee osteoarthritis.",
         og_desc="PGY2 orthopedic surgery resident at Akfa Medline University Hospital. Clinical work, applied AI research, publications and awards.",
         og_type="profile"),
    dict(file="about.html", key="about", name="About",
         title="About Asadbek Sultonov · Orthopedic surgery resident in Tashkent",
         desc="Asadbek Sultonov, PGY2 orthopedic surgery resident at Akfa Medline University Hospital in Tashkent: trauma, arthroplasty, arthroscopy and clinical AI."),
    dict(file="experience.html", key="experience", name="Experience",
         title="Clinical experience · Asadbek Sultonov",
         desc="The clinical and professional path of Asadbek Sultonov: orthopedic surgery residency and research at Akfa Medline, teaching, and earlier clinical roles since 2019."),
    dict(file="research.html", key="research", name="Research",
         title="Research and publications · Asadbek Sultonov",
         desc="Publications, conference talks and applied AI research by Asadbek Sultonov, including a Q1 systematic review and an AAHKS 2026 ePoster."),
    dict(file="achievements.html", key="achievements", name="Achievements",
         title="Awards and certifications · Asadbek Sultonov",
         desc="Medical olympiad awards, the AKFA MEDINNOVA gold medal, USMLE Step 1, AHA ACLS and BLS certification and continuing medical education of Asadbek Sultonov.",
         lightbox=True),
    dict(file="skills.html", key="skills", name="Skills",
         title="Skills · Asadbek Sultonov",
         desc="Clinical, research and technical skills of Asadbek Sultonov, from evidence based medicine and meta-analysis to data analysis in Python."),
    dict(file="contact.html", key="contact", name="Contact",
         title="Contact · Asadbek Sultonov",
         desc="Contact Asadbek Sultonov, orthopedic surgery resident at Akfa Medline University Hospital in Tashkent, about research collaborations and clinical projects."),
]
MENU = ["about", "experience", "research", "achievements", "skills"]
BLOG = dict(file="blog/", key="blog", name="Blog")

PERSON_ID = BASE + "#person"
PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": "Asadbek Sultonov",
    "url": BASE,
    "image": BASE + "assets/img/gallery/portrait-suit.jpg",
    "jobTitle": "Orthopedic Surgery Resident (PGY-2)",
    "email": "mailto:" + EMAIL,
    "description": "PGY2 orthopedic surgery resident at Akfa Medline University Hospital in Tashkent with interests in arthroplasty, arthroscopy and AI in orthopedics.",
    "worksFor": {
        "@type": "Hospital",
        "name": "Akfa Medline University Hospital",
        "address": {"@type": "PostalAddress", "addressLocality": "Tashkent", "addressCountry": "UZ"},
    },
    "alumniOf": {
        "@type": "CollegeOrUniversity",
        "name": "Central Asian University",
        "address": {"@type": "PostalAddress", "addressLocality": "Tashkent", "addressCountry": "UZ"},
    },
    "knowsAbout": ["Orthopedic surgery", "Trauma", "Arthroplasty", "Arthroscopy",
                   "Evidence based medicine", "Knee osteoarthritis", "Deep learning in medical imaging"],
    "knowsLanguage": ["Uzbek", "English", "Russian", "German"],
}
PAPER = {
    "@type": "ScholarlyArticle",
    "headline": "Piezoelectric Biomaterials for Bone Regeneration: Mechanistic Insights and Preclinical Evidence. A Systematic Review of In Vitro and In Vivo Studies",
    "datePublished": "2026-08",
    "author": {"@id": PERSON_ID},
    "isPartOf": {"@type": "Periodical", "name": "Biomedical Materials & Devices"},
    "sameAs": "https://doi.org/10.1007/s44174-026-00757-3",
    "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.1007/s44174-026-00757-3"},
}

ICONS = {
    "envelope": "M224,48H32a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A8,8,0,0,0,224,48ZM203.43,64,128,133.15,52.57,64ZM216,192H40V74.19l82.59,75.71a8,8,0,0,0,10.82,0L216,74.19V192Z",
    "arrow-up-right": "M200,64V168a8,8,0,0,1-16,0V83.31L69.66,197.66a8,8,0,0,1-11.32-11.32L172.69,72H88a8,8,0,0,1,0-16H192A8,8,0,0,1,200,64Z",
    "arrow-up": "M205.66,117.66a8,8,0,0,1-11.32,0L136,59.31V216a8,8,0,0,1-16,0V59.31L61.66,117.66a8,8,0,0,1-11.32-11.32l72-72a8,8,0,0,1,11.32,0l72,72A8,8,0,0,1,205.66,117.66Z",
    "arrow-left": "M224,128a8,8,0,0,1-8,8H59.31l58.35,58.34a8,8,0,0,1-11.32,11.32l-72-72a8,8,0,0,1,0-11.32l72-72a8,8,0,0,1,11.32,11.32L59.31,120H216A8,8,0,0,1,224,128Z",
    "arrow-right": "M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z",
    "x": "M205.66,194.34a8,8,0,0,1-11.32,11.32L128,139.31,61.66,205.66a8,8,0,0,1-11.32-11.32L116.69,128,50.34,61.66A8,8,0,0,1,61.66,50.34L128,116.69l66.34-66.35a8,8,0,0,1,11.32,11.32L139.31,128Z",
    "copy": "M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32ZM160,208H48V96H160Zm48-48H176V88a8,8,0,0,0-8-8H96V48H208Z",
    "article": "M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm0,160H40V56H216V200ZM184,96a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,96Zm0,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,128Zm0,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,160Z",
    "map-pin": "M128,64a40,40,0,1,0,40,40A40,40,0,0,0,128,64Zm0,64a24,24,0,1,1,24-24A24,24,0,0,1,128,128Zm0-112a88.1,88.1,0,0,0-88,88c0,31.4,14.51,64.68,42,96.25a254.19,254.19,0,0,0,41.45,38.3,8,8,0,0,0,9.18,0A254.19,254.19,0,0,0,174,200.25c27.45-31.57,42-64.85,42-96.25A88.1,88.1,0,0,0,128,16Zm0,206c-16.53-13-72-60.75-72-118a72,72,0,0,1,144,0C200,161.23,144.53,209,128,222Z",
}

# Old links to sections of the one-page site (/#research) open the new page.
OLD_ANCHORS = '<script>(function(h){if(/^#(about|experience|research|achievements|skills|contact)$/.test(h))location.replace(h.slice(1)+".html");})(location.hash);</script>\n'

e = lambda s: html.escape(s or "", quote=True)


def url(file):
    return BASE + ("" if file == "index.html" else file)


def jsonld(data):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(data, ensure_ascii=False, indent=2)


def structured(p):
    graph = []
    if p["key"] == "home":
        graph.append({"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": "Asadbek Sultonov",
                      "inLanguage": "en", "publisher": {"@id": PERSON_ID}})
        graph.append(PERSON)
    else:
        page_type = {"about": "ProfilePage", "contact": "ContactPage"}.get(p["key"], "WebPage")
        page = {"@type": page_type, "url": url(p["file"]), "name": p["title"], "description": p["desc"],
                "inLanguage": "en", "isPartOf": {"@id": BASE + "#website"}}
        if p["key"] == "about":
            page["mainEntity"] = PERSON
        else:
            page["about"] = {"@id": PERSON_ID}
        graph.append(page)
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": p["name"], "item": url(p["file"])},
        ]})
        if p["key"] == "research":
            graph.append(PAPER)
    return jsonld({"@context": "https://schema.org", "@graph": graph})


def head(p):
    canonical = url(p["file"])
    tail = "" if p["file"] == "index.html" else p["file"]
    alts = "\n".join('<link rel="alternate" hreflang="%s" href="%s%s">' % (l, BASE + ("" if l == "en" else l + "/"), tail)
                     for l in ("en", "uz", "ru"))
    og_desc = p.get("og_desc", p["desc"])
    first_last = ('<meta property="profile:first_name" content="Asadbek">\n'
                  '<meta property="profile:last_name" content="Sultonov">\n') if p.get("og_type") == "profile" else ""
    return f"""<!DOCTYPE html>
<!-- Generated by tools/pages.py from src/{"home.html" if p["file"] == "index.html" else p["file"]}. Edit that file, then run: python3 tools/build.py -->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>document.documentElement.classList.add("js");</script>
{OLD_ANCHORS if p["key"] == "home" else ""}<title>{e(p["title"])}</title>
<meta name="description" content="{e(p["desc"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Asadbek Sultonov">
<meta name="theme-color" content="#FAFAF9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#181818" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{canonical}">
{alts}
<link rel="alternate" hreflang="x-default" href="{canonical}">

<!-- Open Graph / social sharing -->
<meta property="og:type" content="{p.get("og_type", "website")}">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="Asadbek Sultonov">
<meta property="og:title" content="{e(p["title"])}">
<meta property="og:description" content="{e(og_desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(OG_IMAGE_ALT)}">
{first_last}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(p["title"])}">
<meta name="twitter:description" content="{e(og_desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">

<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="assets/img/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
<!-- Visitor analytics (GoatCounter: cookie-free, no consent banner needed).
     Dashboard: https://asadbeksultonov.goatcounter.com -->
<script data-goatcounter="https://asadbeksultonov.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
{structured(p)}
</head>
<body>

<!-- Phosphor icons (regular), MIT licensed -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
{chr(10).join('  <symbol id="i-%s" viewBox="0 0 256 256"><path d="%s"/></symbol>' % kv for kv in ICONS.items())}
</svg>

<a class="skip-link" href="#main">Skip to content</a>
"""


def lang_switch(p, cls):
    tail = "" if p["file"] == "index.html" else p["file"]
    out = []
    for code, label, name in (("en", "EN", "English"), ("uz", "UZ", "Oʻzbekcha"), ("ru", "RU", "Русский")):
        href = (tail or "./") if code == "en" else "%s/%s" % (code, tail)
        cur = ' aria-current="true"' if code == "en" else ""
        out.append('<a href="%s" data-lang="%s" hreflang="%s" lang="%s" aria-label="%s"%s>%s</a>' % (href, code, code, code, name, cur, label))
    return '<div class="lang-switch%s" role="group" aria-label="Language">\n      %s\n    </div>' % (cls, "\n      ".join(out))


def nav(p):
    by_key = {q["key"]: q for q in PAGES}
    items = [by_key[k] for k in MENU] + [BLOG]
    def li(q, indent):
        cur = ' aria-current="page"' if q["key"] == p["key"] else ""
        return '%s<li><a href="%s"%s>%s</a></li>' % (indent, q["file"], cur, q["name"])
    links = "\n".join(li(q, "      ") for q in items)
    panel = "\n".join(li(q, "    ") for q in items)
    cta_cur = ' aria-current="page"' if p["key"] == "contact" else ""
    return f"""
<header class="nav">
  <nav class="nav-bar" aria-label="Main">
    <a href="./" class="brand" aria-label="Asadbek Sultonov, home">
      <span class="brand-mark" aria-hidden="true"><img src="assets/img/brand/mark.png" alt="" width="32" height="32"></span>
      <span class="brand-name">Asadbek Sultonov</span>
    </a>
    <ul class="nav-links">
{links}
    </ul>
    {lang_switch(p, " caption-3")}
    <a href="contact.html" class="btn btn-primary btn-sm nav-cta"{cta_cur}>Contact</a>
    <button class="nav-toggle" id="navToggle" type="button" aria-label="Open menu" data-label-open="Open menu" data-label-close="Close menu" aria-expanded="false" aria-controls="navPanel">
      <span></span><span></span>
    </button>
  </nav>
</header>

<div class="nav-panel" id="navPanel" aria-hidden="true">
  <ul>
{panel}
  </ul>
  <a href="contact.html" class="btn btn-primary"{cta_cur}>Contact</a>
  {lang_switch(p, " lang-switch-lg button-sm")}
</div>
"""


def pager(i):
    """Previous and next page, so every page links on to the rest of the site."""
    if i == 0:
        return ""
    prev = PAGES[i - 1]
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else BLOG
    href = lambda q: "./" if q["file"] == "index.html" else q["file"]
    return f"""
  <section class="section page-pager">
    <div class="container">
      <nav class="pager" aria-label="More pages">
        <a class="card pager-link is-newer" href="{href(prev)}">
          <span class="caption-1 text-tertiary"><svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-left"/></svg>Previous</span>
          <span class="title-3">{prev["name"]}</span>
        </a>
        <a class="card pager-link is-older" href="{href(nxt)}">
          <span class="caption-1 text-tertiary">Next<svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-right"/></svg></span>
          <span class="title-3">{nxt["name"]}</span>
        </a>
      </nav>
    </div>
  </section>
"""


LIGHTBOX = """
<!-- LIGHTBOX -->
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Image viewer" aria-hidden="true">
  <button class="lightbox-close" id="lightboxClose" type="button" aria-label="Close">
    <svg class="icon" aria-hidden="true"><use href="#i-x"/></svg>
  </button>
  <figure>
    <img id="lightboxImg" alt="">
    <video id="lightboxVideo" controls playsinline hidden></video>
    <figcaption id="lightboxCaption"></figcaption>
  </figure>
</div>
"""


def footer(p):
    return f"""
<footer class="footer">
  <div class="container footer-inner">
    <p class="caption-2">&copy; <span id="year">{datetime.date.today().year}</span> Asadbek Sultonov</p>
    <div class="footer-links caption-1">
      <a href="blog/">
        <svg class="icon icon-sm" aria-hidden="true"><use href="#i-article"/></svg>
        <span>Blog</span>
      </a>
      <a href="#top">
        <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-up"/></svg>
        <span>Back to top</span>
      </a>
    </div>
  </div>
</footer>
{LIGHTBOX if p.get("lightbox") else ""}
<script src="js/main.js"></script>
</body>
</html>
"""


def src_name(p):
    return "home.html" if p["file"] == "index.html" else p["file"]


def main():
    for i, p in enumerate(PAGES):
        with open(os.path.join(ROOT, "src", src_name(p)), encoding="utf-8") as f:
            content = f.read().rstrip("\n")
        out = head(p) + nav(p) + '\n<main id="main">\n\n' + content + "\n" + pager(i) + "\n</main>\n" + footer(p)
        with open(os.path.join(ROOT, p["file"]), "w", encoding="utf-8") as f:
            f.write(out)
    print("Built the English pages: " + ", ".join(p["file"] for p in PAGES))


if __name__ == "__main__":
    main()
