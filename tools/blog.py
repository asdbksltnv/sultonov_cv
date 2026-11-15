#!/usr/bin/env python3
"""Build the blog from the posts/ folder.

Each post is a folder in posts/ with an en.md file and, optionally, uz.md and
ru.md translations. Run from the site folder:

    python3 tools/build.py

See posts/README.md for the post format.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages  # noqa: E402

try:  # used only to write image sizes into the pages, which stops layout shift
    from PIL import Image
except ImportError:
    Image = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "posts")
BASE = "https://asadbeksultonov.com/"
LANGS = ["en", "uz", "ru"]
LOCALE = {"en": "en_US", "uz": "uz_UZ", "ru": "ru_RU"}
VIDEO_EXT = (".mp4", ".webm", ".mov", ".m4v")

UI = {
    "en": dict(
        about="About", experience="Experience", research="Research", achievements="Achievements",
        skills="Skills", projects="Projects", blog="Blog", contact="Contact", skip="Skip to content", main="Main",
        menu_open="Open menu", menu_close="Close menu", language="Language", home="Asadbek Sultonov, home",
        blog_title="Notes along<br> the way",
        blog_sub="Conferences, clinical training and moments from my medical career, in photos and a few words.",
        blog_desc="Posts from Asadbek Sultonov's medical career: conferences, clinical training, research and milestones.",
        read="Read post", latest="Latest", in_en="In English", all_posts="All posts",
        share="Share", copied="Link copied.", share_error="Sharing failed. Copy the address from your browser instead.",
        newer="Newer", older="Older", empty_title="No posts yet", empty_body="New posts will appear here.",
        back_portfolio="Back to portfolio", back_top="Back to top", viewer="Image viewer", close="Close",
        no_video="Your browser can't play this video.", views_label="Views",
        v_one="{n} view", v_few="{n} views", v_many="{n} views", v_other="{n} views",
        months=["January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December"],
    ),
    "uz": dict(
        about="Men haqimda", experience="Tajriba", research="Tadqiqotlar", achievements="Yutuqlar",
        skills="Koʻnikmalar", projects="Loyihalar", blog="Blog", contact="Aloqa", skip="Asosiy matnga oʻtish", main="Asosiy menyu",
        menu_open="Menyuni ochish", menu_close="Menyuni yopish", language="Til", home="Asadbek Sultonov, bosh sahifa",
        blog_title="Yoʻldagi<br> qaydlar",
        blog_sub="Konferensiyalar, klinik tayyorgarlik va tibbiy faoliyatimdagi lahzalar: suratlar va qisqa hikoyalar.",
        blog_desc="Asadbek Sultonovning tibbiy faoliyatidan yozuvlar: konferensiyalar, klinik tayyorgarlik, ilmiy ishlar va muhim voqealar.",
        read="Oʻqish", latest="Soʻnggi", in_en="Ingliz tilida", all_posts="Barcha yozuvlar",
        share="Ulashish", copied="Havola nusxalandi.", share_error="Ulashib boʻlmadi. Manzilni brauzerdan nusxalang.",
        newer="Yangiroq", older="Eskiroq", empty_title="Hozircha yozuvlar yoʻq", empty_body="Yangi yozuvlar shu yerda paydo boʻladi.",
        back_portfolio="Portfolioga qaytish", back_top="Yuqoriga", viewer="Rasmni koʻrish", close="Yopish",
        no_video="Brauzeringiz bu videoni ijro eta olmaydi.", views_label="Koʻrishlar",
        v_one="{n} marta koʻrilgan", v_few="{n} marta koʻrilgan", v_many="{n} marta koʻrilgan", v_other="{n} marta koʻrilgan",
        months=["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust",
                "sentyabr", "oktabr", "noyabr", "dekabr"],
    ),
    "ru": dict(
        about="Обо мне", experience="Опыт", research="Исследования", achievements="Достижения",
        skills="Навыки", projects="Проекты", blog="Блог", contact="Контакты", skip="Перейти к содержанию", main="Основное меню",
        menu_open="Открыть меню", menu_close="Закрыть меню", language="Язык", home="Asadbek Sultonov, главная",
        blog_title="Заметки<br> в пути",
        blog_sub="Конференции, клиническая подготовка и моменты из моей медицинской карьеры в фотографиях и коротких заметках.",
        blog_desc="Записи из медицинской карьеры Асадбека Султонова: конференции, клиническая подготовка, исследования и важные события.",
        read="Читать", latest="Новое", in_en="На английском", all_posts="Все записи",
        share="Поделиться", copied="Ссылка скопирована.", share_error="Не удалось поделиться. Скопируйте адрес из браузера.",
        newer="Новее", older="Раньше", empty_title="Записей пока нет", empty_body="Новые записи появятся здесь.",
        back_portfolio="Вернуться к портфолио", back_top="Наверх", viewer="Просмотр изображения", close="Закрыть",
        no_video="Ваш браузер не может воспроизвести это видео.", views_label="Просмотры",
        v_one="{n} просмотр", v_few="{n} просмотра", v_many="{n} просмотров", v_other="{n} просмотра",
        months=["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август",
                "сентябрь", "октябрь", "ноябрь", "декабрь"],
        months_gen=["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
                    "сентября", "октября", "ноября", "декабря"],
    ),
}

BLOG_NAME = {"en": "Blog", "uz": "Blog", "ru": "Блог"}

ICONS = {
    "arrow-left": "M224,128a8,8,0,0,1-8,8H59.31l58.35,58.34a8,8,0,0,1-11.32,11.32l-72-72a8,8,0,0,1,0-11.32l72-72a8,8,0,0,1,11.32,11.32L59.31,120H216A8,8,0,0,1,224,128Z",
    "arrow-right": "M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z",
    "arrow-up": "M205.66,117.66a8,8,0,0,1-11.32,0L136,59.31V216a8,8,0,0,1-16,0V59.31L61.66,117.66a8,8,0,0,1-11.32-11.32l72-72a8,8,0,0,1,11.32,0l72,72A8,8,0,0,1,205.66,117.66Z",
    "x": "M205.66,194.34a8,8,0,0,1-11.32,11.32L128,139.31,61.66,205.66a8,8,0,0,1-11.32-11.32L116.69,128,50.34,61.66A8,8,0,0,1,61.66,50.34L128,116.69l66.34-66.35a8,8,0,0,1,11.32,11.32L139.31,128Z",
    "eye": "M247.31,124.76c-.35-.79-8.82-19.58-27.65-38.41C194.57,61.26,162.88,48,128,48S61.43,61.26,36.34,86.35C17.51,105.18,9,124,8.69,124.76a8,8,0,0,0,0,6.5c.35.79,8.82,19.57,27.65,38.4C61.43,194.74,93.12,208,128,208s66.57-13.26,91.66-38.34c18.83-18.83,27.3-37.61,27.65-38.4A8,8,0,0,0,247.31,124.76ZM128,192c-30.78,0-57.67-11.19-79.93-33.25A133.47,133.47,0,0,1,25,128,133.33,133.33,0,0,1,48.07,97.25C70.33,75.19,97.22,64,128,64s57.67,11.19,79.93,33.25A133.46,133.46,0,0,1,231.05,128C223.84,141.46,192.43,192,128,192Zm0-112a48,48,0,1,0,48,48A48.05,48.05,0,0,0,128,80Zm0,80a32,32,0,1,1,32-32A32,32,0,0,1,128,160Z",
    "calendar": "M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32ZM72,48v8a8,8,0,0,0,16,0V48h80v8a8,8,0,0,0,16,0V48h24V80H48V48ZM208,208H48V96H208V208Z",
    "share": "M176,160a39.89,39.89,0,0,0-28.62,12.09l-46.1-29.63a39.8,39.8,0,0,0,0-28.92l46.1-29.63a40,40,0,1,0-8.66-13.45l-46.1,29.63a40,40,0,1,0,0,55.82l46.1,29.63A40,40,0,1,0,176,160Zm0-128a24,24,0,1,1-24,24A24,24,0,0,1,176,32ZM64,152a24,24,0,1,1,24-24A24,24,0,0,1,64,152Zm112,72a24,24,0,1,1,24-24A24,24,0,0,1,176,224Z",
    "article": "M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm0,160H40V56H216V200ZM184,96a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,96Zm0,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,128Zm0,32a8,8,0,0,1-8,8H80a8,8,0,0,1,0-16h96A8,8,0,0,1,184,160Z",
}

e = lambda s: html.escape(s or "", quote=True)


# ---------------------------------------------------------------- posts

def read_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    meta, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body.strip()


def load_posts():
    posts = []
    if not os.path.isdir(POSTS):
        return posts
    for slug in sorted(os.listdir(POSTS)):
        folder = os.path.join(POSTS, slug)
        if not os.path.isdir(folder) or slug.startswith((".", "_")):
            continue
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
            sys.exit("ERROR: post folder name %r must be lowercase letters, numbers and dashes." % slug)
        versions = {}
        for lang in LANGS:
            p = os.path.join(folder, lang + ".md")
            if os.path.exists(p):
                versions[lang] = read_md(p)
        if "en" not in versions:
            sys.exit("ERROR: posts/%s needs an en.md file." % slug)
        base = versions["en"][0]
        if not base.get("title"):
            sys.exit("ERROR: posts/%s/en.md needs a title." % slug)
        date = base.get("date", "")
        if date and not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", date):
            sys.exit("ERROR: posts/%s/en.md date must look like 2025, 2025-10 or 2025-10-23." % slug)
        if base.get("draft", "").lower() in ("yes", "true"):
            continue
        post = {"slug": slug, "date": date, "cover": base.get("cover", ""), "v": {}}
        for lang in LANGS:
            src_lang = lang if lang in versions else "en"
            meta, body = versions[src_lang]
            merged = dict(base)
            merged.update({k: v for k, v in meta.items() if v})
            post["v"][lang] = {
                "lang": src_lang,
                "title": merged.get("title", ""),
                "summary": merged.get("summary", ""),
                "cover_alt": merged.get("cover_alt", merged.get("title", "")),
                "body": body,
            }
        if not post["cover"]:
            m = re.search(r"!\[[^\]]*\]\(([^)\s]+)", versions["en"][1])
            if m and not m.group(1).lower().endswith(VIDEO_EXT):
                post["cover"] = m.group(1)
        posts.append(post)
    # newest first; undated posts go last
    posts.sort(key=lambda p: (p["date"] or "0000"), reverse=True)
    return posts


def fmt_date(date, lang):
    if not date:
        return ""
    parts = [int(x) for x in date.split("-")]
    ui = UI[lang]
    if len(parts) == 1:
        return str(parts[0])
    y, mo = parts[0], parts[1]
    if len(parts) == 2:
        if lang == "en":
            return "%s %d" % (ui["months"][mo - 1], y)
        if lang == "uz":
            return "%d yil %s" % (y, ui["months"][mo - 1])
        return "%s %d" % (ui["months"][mo - 1], y)
    d = parts[2]
    if lang == "en":
        return "%s %d, %d" % (ui["months"][mo - 1], d, y)
    if lang == "uz":
        return "%d yil %d %s" % (y, d, ui["months"][mo - 1])
    return "%d %s %d" % (d, ui["months_gen"][mo - 1], y)


def plural_posts(n, lang):
    if lang == "en":
        return "1 post" if n == 1 else "%d posts" % n
    if lang == "uz":
        return "%d ta yozuv" % n
    if n % 10 == 1 and n % 100 != 11:
        return "%d запись" % n
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return "%d записи" % n
    return "%d записей" % n


# ---------------------------------------------------------------- markdown

def inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)

    def link(m):
        label, url = m.group(1), m.group(2)
        ext = url.startswith("http")
        extra = ' target="_blank" rel="noopener"' if ext else ""
        return '<a class="text-link" href="%s"%s>%s</a>' % (url, extra, label)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)


def media_url(path, root, slug):
    if re.match(r"^(https?:)?//", path):
        return path
    if "/" not in path:
        path = "posts/%s/%s" % (slug, path)
    return root + path.lstrip("/")


_sizes = {}


def size_attrs(path, slug):
    """' width="W" height="H"' for a local image, so the browser reserves its space."""
    if Image is None or not path or re.match(r"^(https?:)?//", path) or path.lower().endswith(VIDEO_EXT):
        return ""
    rel = path if "/" in path else "posts/%s/%s" % (slug, path)
    if rel not in _sizes:
        try:
            with Image.open(os.path.join(ROOT, rel)) as im:
                _sizes[rel] = im.size
        except OSError:
            _sizes[rel] = None
    s = _sizes[rel]
    return ' width="%d" height="%d"' % s if s else ""


IMG_LINE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$')


def figure(alt, src, caption, root, slug, ui):
    url = media_url(src, root, slug)
    cap = caption or ""
    figcap = '<figcaption class="caption-2">%s</figcaption>' % e(cap) if cap else ""
    if src.lower().endswith(VIDEO_EXT):
        return ('<figure class="post-figure"><video controls playsinline preload="metadata" src="%s#t=0.1" aria-label="%s">%s</video>%s</figure>'
                % (e(url), e(alt), e(ui["no_video"]), figcap))
    return ('<figure class="post-figure"><button type="button" class="post-photo" data-full="%s" data-caption="%s">'
            '<img src="%s" alt="%s"%s loading="lazy" decoding="async"></button>%s</figure>'
            % (e(url), e(cap or alt), e(url), e(alt), size_attrs(src, slug), figcap))


def markdown(md, root, slug, ui):
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = [l.rstrip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        if all(IMG_LINE.match(l) for l in lines):
            figs = [figure(*IMG_LINE.match(l).groups(), root=root, slug=slug, ui=ui) for l in lines]
            if len(figs) == 1:
                out.append(figs[0])
            else:
                out.append('<div class="post-gallery">%s</div>' % "".join(figs))
        elif lines[0].startswith("### "):
            out.append('<h3 class="title-1">%s</h3>' % inline(lines[0][4:]))
        elif lines[0].startswith("## "):
            out.append('<h2 class="heading-5">%s</h2>' % inline(lines[0][3:]))
        elif all(l.startswith("- ") for l in lines):
            out.append('<ul class="bullets">%s</ul>' % "".join("<li>%s</li>" % inline(l[2:]) for l in lines))
        elif all(l.startswith(">") for l in lines):
            out.append('<blockquote class="body-7">%s</blockquote>' % inline(" ".join(l.lstrip("> ") for l in lines)))
        else:
            out.append("<p>%s</p>" % inline(" ".join(lines)))
    return "\n".join(out)


# ---------------------------------------------------------------- page parts

def blog_dir(lang):
    return "blog/" if lang == "en" else "%s/blog/" % lang


def root_prefix(lang):
    return "../" if lang == "en" else "../../"


def gc_paths(slug):
    page = "%s.html" % slug
    return ",".join("/" + blog_dir(l) + page for l in LANGS)


def views(slug, lang):
    ui = UI[lang]
    return ('<span class="views" data-views data-paths="%s" data-one="%s" data-few="%s" data-many="%s" data-other="%s" hidden>'
            '<svg class="icon icon-sm" aria-hidden="true"><use href="#i-eye"/></svg><span></span></span>'
            % (gc_paths(slug), e(ui["v_one"]), e(ui["v_few"]), e(ui["v_many"]), e(ui["v_other"])))


def date_el(date, lang):
    if not date:
        return ""
    return '<time datetime="%s">%s</time>' % (date, e(fmt_date(date, lang)))


def sprite():
    syms = "\n".join('  <symbol id="i-%s" viewBox="0 0 256 256"><path d="%s"/></symbol>' % (k, v) for k, v in ICONS.items())
    return ('<!-- Phosphor icons (regular), MIT licensed -->\n'
            '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n%s\n</svg>' % syms)


def lang_switch(lang, page, cls):
    links = []
    for target, label, name in (("en", "EN", "English"), ("uz", "UZ", "Oʻzbekcha"), ("ru", "RU", "Русский")):
        href = root_prefix(lang) + blog_dir(target) + ("" if page == "index.html" else page)
        if target == lang:
            href = "./" if page == "index.html" else page
        cur = ' aria-current="true"' if target == lang else ""
        links.append('<a href="%s" data-lang="%s" hreflang="%s" lang="%s" aria-label="%s"%s>%s</a>'
                     % (href, target, target, target, name, cur, label))
    return '<div class="lang-switch%s" role="group" aria-label="%s">\n      %s\n    </div>' % (cls, e(UI[lang]["language"]), "\n      ".join(links))


def ld_script(data):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(
        {"@context": "https://schema.org", "@graph": data}, ensure_ascii=False, indent=2)


def breadcrumbs(lang, *trail):
    """trail: (name, path) pairs after the home page."""
    home = BASE + ("" if lang == "en" else lang + "/")
    names = {"en": "Home", "uz": "Bosh sahifa", "ru": "Главная"}
    items = [(names[lang], home)] + [(n, BASE + p) for n, p in trail]
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def head(lang, title, desc, canonical_path, alt_page, image, og_type, image_alt="", ld=None, extra=""):
    root = root_prefix(lang)
    alts = "\n".join('<link rel="alternate" hreflang="%s" href="%s%s%s">' % (l, BASE, blog_dir(l), alt_page) for l in LANGS)
    alts += '\n<link rel="alternate" hreflang="x-default" href="%s%s%s">' % (BASE, blog_dir("en"), alt_page)
    img = BASE + (image or "assets/img/brand/og-image.png")
    if not image:
        image_alt = pages.OG_IMAGE_ALT
    img_alt = ('<meta property="og:image:alt" content="%s">\n<meta name="twitter:image:alt" content="%s">\n'
               % (e(image_alt), e(image_alt))) if image_alt else ""
    extra = img_alt + extra + (ld_script(ld) + "\n" if ld else "")
    return f"""<!DOCTYPE html>
<!-- Generated by tools/build.py from the posts/ folder. Edit the posts, then run: python3 tools/build.py -->
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>document.documentElement.classList.add("js");</script>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Asadbek Sultonov">
<meta name="theme-color" content="#FAFAF9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#181818" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{BASE}{canonical_path}">
{alts}
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta property="og:site_name" content="Asadbek Sultonov">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}{canonical_path}">
<meta property="og:image" content="{e(img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(img)}">
{extra}<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="{root}assets/img/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css">
<!-- Visitor analytics (GoatCounter: cookie-free, no consent banner needed).
     Dashboard: https://asadbeksultonov.goatcounter.com -->
<script data-goatcounter="https://asadbeksultonov.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</head>
<body>

{sprite()}

<a class="skip-link" href="#main">{e(UI[lang]["skip"])}</a>
"""


def nav(lang, page):
    ui = UI[lang]
    home = "../"
    blog_href = "./"
    items = [(k, k + ".html") for k in pages.MENU]
    links = "\n".join('      <li><a href="%s%s">%s</a></li>' % (home, h, e(ui[k])) for k, h in items)
    links += '\n      <li><a href="%s" aria-current="page">%s</a></li>' % (blog_href, e(ui["blog"]))
    panel = links.replace("      <li>", "    <li>")
    return f"""
<header class="nav">
  <nav class="nav-bar" aria-label="{e(ui['main'])}">
    <a href="{home}" class="brand" aria-label="{e(ui['home'])}">
      <span class="brand-mark" aria-hidden="true"><img src="{root_prefix(lang)}assets/img/brand/mark.png" alt="" width="32" height="32"></span>
      <span class="brand-name">Asadbek Sultonov</span>
    </a>
    <ul class="nav-links">
{links}
    </ul>
    {lang_switch(lang, page, " caption-3")}
    <a href="{home}contact.html" class="btn btn-primary btn-sm nav-cta">{e(ui['contact'])}</a>
    <button class="nav-toggle" id="navToggle" type="button" aria-label="{e(ui['menu_open'])}" data-label-open="{e(ui['menu_open'])}" data-label-close="{e(ui['menu_close'])}" aria-expanded="false" aria-controls="navPanel">
      <span></span><span></span>
    </button>
  </nav>
</header>

<div class="nav-panel" id="navPanel" aria-hidden="true">
  <ul>
{panel}
  </ul>
  <a href="{home}contact.html" class="btn btn-primary">{e(ui['contact'])}</a>
  {lang_switch(lang, page, " lang-switch-lg button-sm")}
</div>
"""


def footer(lang, with_lightbox):
    ui = UI[lang]
    lb = ""
    if with_lightbox:
        lb = f"""
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="{e(ui['viewer'])}" aria-hidden="true">
  <button class="lightbox-close" id="lightboxClose" type="button" aria-label="{e(ui['close'])}">
    <svg class="icon" aria-hidden="true"><use href="#i-x"/></svg>
  </button>
  <figure>
    <img id="lightboxImg" alt="">
    <video id="lightboxVideo" controls playsinline hidden></video>
    <figcaption id="lightboxCaption"></figcaption>
  </figure>
</div>
"""
    return f"""
<footer class="footer">
  <div class="container footer-inner">
    <p class="caption-2">&copy; <span id="year">{datetime.date.today().year}</span> Asadbek Sultonov</p>
    <div class="footer-links caption-1">
      <a href="../">
        <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-left"/></svg>
        <span>{e(ui['back_portfolio'])}</span>
      </a>
      <a href="#top">
        <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-up"/></svg>
        <span>{e(ui['back_top'])}</span>
      </a>
    </div>
  </div>
</footer>
{lb}
<script src="{root_prefix(lang)}js/main.js"></script>
</body>
</html>
"""


def badge_lang(v, lang):
    if v["lang"] != lang:
        return '<span class="badge badge-muted">%s</span>' % e(UI[lang]["in_en"])
    return ""


def card(post, lang, featured):
    ui = UI[lang]
    v = post["v"][lang]
    root = root_prefix(lang)
    cover = ""
    if post["cover"]:
        cover = ('<span class="post-cover"><img src="%s" alt="%s"%s loading="%s" decoding="async"></span>'
                 % (e(media_url(post["cover"], root, post["slug"])), e(v["cover_alt"]),
                    size_attrs(post["cover"], post["slug"]), "eager" if featured else "lazy"))
    lang_attr = ' lang="en"' if v["lang"] != lang else ""
    latest = '<span class="badge">%s</span>' % e(ui["latest"]) if featured else ""
    title_cls = "heading-5" if featured else "title-1"
    meta = " ".join(x for x in (latest, badge_lang(v, lang), date_el(post["date"], lang), views(post["slug"], lang)) if x)
    return f"""      <article class="post-card-wrap reveal{' is-featured' if featured else ''}"{lang_attr}>
        <a class="post-card card{' card-lg post-card-featured' if featured else ''}" href="{post['slug']}.html">
          {cover}
          <span class="post-card-body">
            <span class="post-meta caption-1">{meta}</span>
            <h2 class="{title_cls} post-card-title">{e(v['title'])}</h2>
            <span class="body-6 post-card-summary">{e(v['summary'])}</span>
            <span class="post-card-more button-sm">{e(ui['read'])} <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-right"/></svg></span>
          </span>
        </a>
      </article>"""


def render_index(lang, posts):
    ui = UI[lang]
    title = {"en": "Blog · Asadbek Sultonov", "uz": "Asadbek Sultonov blogi",
             "ru": "Блог · Асадбек Султонов"}[lang]
    url = BASE + blog_dir(lang)
    ld = [
        {"@type": "Blog", "@id": url + "#blog", "url": url, "name": title, "description": ui["blog_desc"],
         "inLanguage": lang, "author": {"@id": pages.PERSON_ID},
         "blogPost": [{"@type": "BlogPosting", "headline": p["v"][lang]["title"],
                       "url": url + p["slug"] + ".html"} for p in posts]},
        breadcrumbs(lang, (BLOG_NAME[lang], blog_dir(lang))),
    ]
    page = head(lang, title, ui["blog_desc"], blog_dir(lang), "", None, "website", ld=ld) + nav(lang, "index.html")
    if posts:
        cards = card(posts[0], lang, True)
        rest = "\n".join(card(p, lang, False) for p in posts[1:])
        listing = f"""    <div class="post-featured">
{cards}
    </div>
    <div class="post-grid">
{rest}
    </div>"""
    else:
        listing = f"""    <div class="card card-lg empty-state">
      <svg class="icon" aria-hidden="true"><use href="#i-article"/></svg>
      <h2 class="title-1">{e(ui['empty_title'])}</h2>
      <p class="body-6 text-secondary">{e(ui['empty_body'])}</p>
    </div>"""
    page += f"""
<main id="main">
  <section class="page-hero" id="top">
    <div class="container reveal">
      <h1 class="heading-1 hero-title">{ui['blog_title']}</h1>
      <p class="body-7 hero-sub">{e(ui['blog_sub'])}</p>
      <p class="caption-1">
        <svg class="icon icon-sm" aria-hidden="true"><use href="#i-article"/></svg>
        <span>{e(plural_posts(len(posts), lang))}</span>
      </p>
    </div>
  </section>

  <section class="section blog-list" aria-label="{e(BLOG_NAME[lang])}">
    <div class="container">
{listing}
    </div>
  </section>
</main>
"""
    return page + footer(lang, False)


def render_post(lang, post, newer, older):
    ui = UI[lang]
    v = post["v"][lang]
    root = root_prefix(lang)
    page_name = post["slug"] + ".html"
    title = "%s · Asadbek Sultonov" % v["title"]
    desc = v["summary"] or v["title"]
    url = BASE + blog_dir(lang) + page_name
    image = media_url(post["cover"], "", post["slug"]) if post["cover"] else ""
    posting = {"@type": "BlogPosting", "@id": url + "#post", "url": url, "mainEntityOfPage": url,
               "headline": v["title"], "description": desc, "inLanguage": v["lang"],
               "author": {"@type": "Person", "@id": pages.PERSON_ID, "name": "Asadbek Sultonov", "url": BASE},
               "publisher": {"@id": pages.PERSON_ID},
               "isPartOf": {"@id": BASE + blog_dir(lang) + "#blog"}}
    if image:
        posting["image"] = BASE + image
    extra = ""
    if post["date"]:
        posting["datePublished"] = post["date"]
        extra = '<meta property="article:published_time" content="%s">\n' % post["date"]
    ld = [posting, breadcrumbs(lang, (BLOG_NAME[lang], blog_dir(lang)), (v["title"], blog_dir(lang) + page_name))]
    out = head(lang, title, desc, blog_dir(lang) + page_name, page_name, image, "article",
               image_alt=v["cover_alt"], ld=ld, extra=extra)
    out += nav(lang, page_name)
    lang_attr = ' lang="en"' if v["lang"] != lang else ""
    cover = ""
    if post["cover"]:
        url = e(media_url(post["cover"], root, post["slug"]))
        cover = (f'  <figure class="post-hero-media container reveal"><button type="button" class="post-photo" data-full="{url}" data-caption="{e(v["cover_alt"])}">'
                 f'<img src="{url}" alt="{e(v["cover_alt"])}"{size_attrs(post["cover"], post["slug"])} fetchpriority="high"></button></figure>')
    meta = " ".join(x for x in (badge_lang(v, lang), date_el(post["date"], lang), views(post["slug"], lang)) if x)
    pager = []
    for p, label, cls in ((newer, ui["newer"], "is-newer"), (older, ui["older"], "is-older")):
        if p:
            icon = "arrow-left" if cls == "is-newer" else "arrow-right"
            pager.append(f"""      <a class="card pager-link {cls}" href="{p['slug']}.html">
        <span class="caption-1 text-tertiary"><svg class="icon icon-sm" aria-hidden="true"><use href="#i-{icon}"/></svg>{e(label)}</span>
        <span class="title-3">{e(p['v'][lang]['title'])}</span>
      </a>""")
    pager_html = '    <nav class="pager" aria-label="%s">\n%s\n    </nav>' % (e(ui["all_posts"]), "\n".join(pager)) if pager else ""
    out += f"""
<main id="main">
  <article class="post" id="top"{lang_attr}>
    <header class="post-header container-narrow reveal">
      <a class="back-link caption-1" href="./"><svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-left"/></svg>{e(ui['all_posts'])}</a>
      <p class="post-meta caption-1">{meta}</p>
      <h1 class="heading-2 hero-title post-title">{e(v['title'])}</h1>
      <p class="body-7 hero-sub">{e(v['summary'])}</p>
      <div class="post-actions">
        <button type="button" class="btn btn-secondary btn-sm" data-share data-title="{e(v['title'])}" data-msg-copied="{e(ui['copied'])}" data-msg-error="{e(ui['share_error'])}" data-goatcounter-click="share-{post['slug']}" data-goatcounter-title="Share: {e(post['slug'])}">
          <svg class="icon icon-sm" aria-hidden="true"><use href="#i-share"/></svg>
          <span>{e(ui['share'])}</span>
        </button>
        <p class="caption-1 share-status" role="status" aria-live="polite"></p>
      </div>
    </header>
{cover}
    <div class="post-body container-narrow body-7 reveal">
{markdown(v['body'], root, post['slug'], ui)}
    </div>
    <footer class="post-footer container-narrow">
{pager_html}
      <a class="btn btn-secondary" href="./"><svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow-left"/></svg><span>{e(ui['all_posts'])}</span></a>
    </footer>
  </article>
</main>
"""
    return out + footer(lang, True)


def redirect_stub(target, lang):
    return f"""<!DOCTYPE html>
<!-- The gallery is now the blog. Generated by tools/build.py -->
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{BASE}{'' if lang == 'en' else lang + '/'}{target}">
<title>{e(BLOG_NAME[lang])} · Asadbek Sultonov</title>
<script>location.replace("{target}" + location.hash);</script>
</head>
<body>
<p><a href="{target}">{e(BLOG_NAME[lang])}</a></p>
</body>
</html>
"""


def last_changed(*paths):
    """Date of the last commit touching these source files (today if they have uncommitted changes)."""
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--"] + list(paths), cwd=ROOT,
                               capture_output=True, text=True, timeout=20).stdout.strip()
        if not dirty:
            day = subprocess.run(["git", "log", "-1", "--format=%cs", "--"] + list(paths), cwd=ROOT,
                                 capture_output=True, text=True, timeout=20).stdout.strip()
            if day:
                return day
    except (OSError, subprocess.SubprocessError):
        pass
    return datetime.date.today().isoformat()


def sitemap(posts):
    """Every page in every language, each listing its translations (hreflang)."""
    groups = []
    for p in pages.PAGES:
        tail = "" if p["file"] == "index.html" else p["file"]
        src = "src/" + pages.src_name(p)
        groups.append(([("" if l == "en" else l + "/") + tail for l in LANGS], last_changed(src, "tools/pages.py", "tools/i18n.py")))
    newest = max([last_changed("posts/" + p["slug"]) for p in posts] or [datetime.date.today().isoformat()])
    groups.append(([blog_dir(l) for l in LANGS], newest))
    for p in posts:
        groups.append(([blog_dir(l) + p["slug"] + ".html" for l in LANGS], last_changed("posts/" + p["slug"])))
    rows = []
    for urls, lastmod in groups:
        alts = "".join('\n    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (l, BASE, u) for l, u in zip(LANGS, urls))
        alts += '\n    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (BASE, urls[0])
        for u in urls:
            rows.append(f"""  <url>
    <loc>{BASE}{u}</loc>
    <lastmod>{lastmod}</lastmod>{alts}
  </url>""")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    posts = load_posts()
    # missing media is the most common mistake when adding a post
    for p in posts:
        refs = [p["cover"]] + re.findall(r"!\[[^\]]*\]\(([^)\s]+)", "".join(v["body"] for v in p["v"].values()))
        for r in filter(None, refs):
            if re.match(r"^(https?:)?//", r):
                continue
            rel = r if "/" in r else "posts/%s/%s" % (p["slug"], r)
            if not os.path.exists(os.path.join(ROOT, rel)):
                sys.exit("ERROR: posts/%s refers to %s, which does not exist." % (p["slug"], rel))

    # remove pages of posts that were deleted or renamed
    for lang in LANGS:
        d = os.path.join(ROOT, blog_dir(lang))
        if os.path.isdir(d):
            keep = {p["slug"] + ".html" for p in posts} | {"index.html"}
            for f in os.listdir(d):
                if f.endswith(".html") and f not in keep:
                    os.remove(os.path.join(d, f))

    for lang in LANGS:
        write(blog_dir(lang) + "index.html", render_index(lang, posts))
        for i, p in enumerate(posts):
            newer = posts[i - 1] if i > 0 else None
            older = posts[i + 1] if i + 1 < len(posts) else None
            write(blog_dir(lang) + p["slug"] + ".html", render_post(lang, p, newer, older))
        write(("" if lang == "en" else lang + "/") + "gallery.html", redirect_stub("blog/", lang))
    write("sitemap.xml", sitemap(posts))
    print("Built the blog: %d posts in %s" % (len(posts), ", ".join(LANGS)))


if __name__ == "__main__":
    main()
