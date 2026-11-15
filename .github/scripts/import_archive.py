#!/usr/bin/env python3
"""One-time, bounded archival import of currently public family-site content.

Copies HTML/PDF/media to GitHub Pages project-relative paths.
Preserves raw source HTML in site/source-original/ and publishes a readable
wrapper at the original paths. Never overwrites the redesigned home page.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import posixpath
import re
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, quote

import requests
from bs4 import BeautifulSoup

HOST = "afsharnaderi.com"
ORIGIN = "https://" + HOST
ROOT = Path("site")
SEEDS = [
    "/", "/tabaar/tabaar1.html", "/docs/kashkoul.html",
    "/ismail/ismail.html", "/davoud2/davoudm2.html",
    "/drghan/drghan.html", "/drnader/drnader.html",
    "/docs/shajareh.pdf", "/docs/ismail_memo.pdf",
]
ALLOWED = {".html", ".htm", ".pdf", ".png", ".jpg", ".jpeg", ".gif",
           ".webp", ".svg", ".css", ".js", ".txt", ".doc", ".docx",
           ".mp3", ".ogg"}
HTML_EXTS = {".html", ".htm"}
MAX_ITEMS = 700
MAX_HTML = 175
MAX_BYTES = 175 * 1024 * 1024
MAX_FILE = 28 * 1024 * 1024
TIMEOUT = (12, 45)
s = requests.Session()
s.headers.update({"User-Agent": "AfsharNaderiArchiveMigration/1.0 (family history preservation; public site)", "Accept": "*/*"})
queue = deque(SEEDS)
seen = set()
pages = []
assets = []
missing = []
total_bytes = 0
root_resolved = ROOT.resolve()
url_attributes = {"a": ["href"], "img": ["src", "data-src"], "source": ["src", "srcset"],
                  "script": ["src"], "link": ["href"], "video": ["src", "poster"],
                  "audio": ["src"], "iframe": ["src"], "embed": ["src"]}
_asset_url_re = re.compile(r"url\(\s*['\"]?([^'\")]+)", re.I)


def path_for(url):
    parsed = urlparse(urljoin(ORIGIN + "/", url))
    if parsed.scheme not in ("http", "https") or parsed.netloc.lower().removeprefix("www.") != HOST:
        return None
    path = unquote(parsed.path or "/")
    if "\x00" in path or "\\" in path:
        return None
    safe = posixpath.normpath("/" + path.lstrip("/"))
    if any(piece in (".", "..") for piece in safe.split("/")):
        return None
    if safe.endswith("/") or safe == "/":
        safe = safe.rstrip("/") + "/index.html"
    suffix = posixpath.splitext(safe)[1].lower()
    if not suffix:
        safe += "/index.html"
        suffix = ".html"
    if suffix not in ALLOWED:
        return None
    local = safe.lstrip("/")
    target = (ROOT / local).resolve()
    if not target.is_relative_to(root_resolved):
        return None
    return local


def local_link(current, remote):
    target = path_for(remote)
    if target is None:
        return None
    if target == "index.html":
        target = "index.html"
    return posixpath.relpath(target, posixpath.dirname(current) or ".")


def enqueue(url):
    normalized = urljoin(ORIGIN + "/", url)
    local = path_for(normalized)
    if local and local not in seen and len(queue) < MAX_ITEMS * 3:
        queue.append(normalized)


def get(url):
    global total_bytes
    resp = s.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True)
    resp.raise_for_status()
    if path_for(resp.url) is None:
        raise ValueError("Offsite redirect")
    length = int(resp.headers.get("content-length", "0") or "0")
    if length > MAX_FILE:
        raise ValueError("File over per-file cap")
    chunks = []
    size = 0
    for part in resp.iter_content(64 * 1024):
        if not part:
            continue
        chunks.append(part)
        size += len(part)
        if size > MAX_FILE or total_bytes + size > MAX_BYTES:
            raise ValueError("Archive size limit reached")
    total_bytes += size
    return b"".join(chunks), resp.headers.get("content-type", "")


def write(local, data):
    dest = ROOT / local
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def rewrite_sources(soup, local, remote_url):
    for tag in soup.find_all(True):
        for attr in url_attributes.get(tag.name, []):
            if not tag.has_attr(attr):
                continue
            val = tag.get(attr)
            if not isinstance(val, str) or not val.strip():
                continue
            if attr == "srcset":
                new_parts = []
                for entry in val.split(","):
                    parts = entry.strip().split(" ", 1)
                    if not parts:
                        continue
                    full = urljoin(remote_url, parts[0])
                    rewritten = local_link(local, full)
                    if rewritten:
                        enqueue(full)
                    new_parts.append((rewritten or parts[0]) + (" " + parts[1] if len(parts) > 1 else ""))
                tag[attr] = ", ".join(new_parts)
                continue
            if val.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                if val.startswith("javascript:"):
                    del tag[attr]
                continue
            full = urljoin(remote_url, val)
            rewritten = local_link(local, full)
            if rewritten:
                enqueue(full)
                fragment = urlparse(full).fragment
                tag[attr] = rewritten + ("#" + fragment if fragment else "")
        if tag.has_attr("style"):
            style = str(tag["style"])
            def repl(match):
                full = urljoin(remote_url, match.group(1).strip())
                new = local_link(local, full)
                if new:
                    enqueue(full)
                return "url('" + (new or match.group(1)) + "')"
            tag["style"] = _asset_url_re.sub(repl, style)


def clean_body(doc):
    for tag in doc.select("script, iframe, object, form, meta, base"):
        tag.decompose()
    # Strip on-event JavaScript attributes; preserve substantive text and links.
    for tag in doc.find_all(True):
        for attr in list(tag.attrs):
            if attr.lower().startswith("on"):
                del tag[attr]
    return str(doc.body or doc)


def make_page(local, data, url):
    soup = BeautifulSoup(data, "html.parser")
    title = (soup.title.get_text(" ", strip=True) if soup.title else
             (soup.h1.get_text(" ", strip=True) if soup.h1 else local))
    raw_local = "source-original/" + local
    write(raw_local, data)
    rewrite_sources(soup, local, url)
    body = clean_body(soup)
    css = local_link(local, ORIGIN + "/styles.css") or "./styles.css"
    # local_link for /styles.css would create a local path even if not imported;
    # calculate the actual theme location instead.
    css = posixpath.relpath("styles.css", posixpath.dirname(local) or ".")
    homepage = posixpath.relpath("index.html", posixpath.dirname(local) or ".")
    archive = posixpath.relpath("archive.html", posixpath.dirname(local) or ".")
    family = posixpath.relpath("family.html", posixpath.dirname(local) or ".")
    old_title = html.escape(title)
    output = f'''<!doctype html><html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{old_title} | آرشیو خاندان افشار نادری</title>
<link rel="stylesheet" href="{html.escape(css, quote=True)}"></head><body>
<header class="header"><div class="container nav-wrap">
<a class="logo" href="{homepage}"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a>
<nav aria-label="فهرست اصلی"><a href="{homepage}">خانه</a><a href="{archive}">آرشیو</a><a href="{family}">تبارنامه</a></nav></div></header>
<main class="container legacy-layout"><div class="legacy-breadcrumb"><a href="{homepage}">خانه</a> / <a href="{archive}">آرشیو</a> / <span>{old_title}</span></div>
<div class="legacy-heading"><div class="kicker dark">بازیابی از آرشیو اولیه</div><h1>{old_title}</h1></div>
<article class="legacy-document" id="original-record">{body}</article>
<p class="legacy-provenance">منبع ثبت اولیه: وب‌سایت افشار نادری · این صفحه برای حفظ محتوای تاریخی به سایت جدید منتقل شده است.</p>
<p class="legacy-next"><a href="{archive}">بازگشت به فهرست آرشیو ←</a></p>
</main><footer class="footer"><div class="container footer-bottom"><span>خاندان افشار نادری · آرشیو آزمایشی</span><a href="{homepage}">صفحهٔ اصلی ←</a></div></footer>
</body></html>'''
    if local == "index.html":
        write("original/index.html", output.encode("utf-8"))
    else:
        write(local, output.encode("utf-8"))
    pages.append({"path": local, "title": title, "source": url,
                  "original_sha256": hashlib.sha256(data).hexdigest()})


def write_catalog():
    entries = []
    all_items = sorted(pages + assets, key=lambda v: v["path"])
    for item in all_items:
        path = item["path"]
        if path == "index.html":
            href = "original/index.html"
        else:
            href = path
        name = item.get("title") or posixpath.basename(path)
        t = html.escape(name)
        category = "صفحهٔ تاریخی" if item in pages else "سند یا رسانه"
        entries.append(f'<article class="resource" data-category="{category}"><div class="pills"><span>{category}</span></div>'
                       f'<h2>{t}</h2><p dir="ltr">{html.escape(path)}</p>'
                       f'<a href="{html.escape(href, quote=True)}">مشاهده در همین سایت ←</a></article>')
    cards = "\n".join(entries)
    template = f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<link rel="stylesheet" href="./styles.css"><title>تمام منابع منتقل‌شده | خاندان افشار نادری</title></head><body>
<header class="header"><div class="container nav-wrap"><a class="logo" href="./"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a>
<nav><a href="./">خانه</a><a href="./archive.html">آرشیو</a><a href="./family.html">تبارنامه</a></nav></div></header>
<main><section class="subhero"><div class="container"><div class="kicker">محتوای بازیابی‌شده</div><h1>تمام منابع منتقل‌شده</h1><p>پرونده‌ها و فایل‌های دانلودشده از سایت اولیه؛ هر لینک در همین سایت باز می‌شود.</p></div></section>
<section class="section container"><div class="archive-controls"><label class="search"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="جست‌وجوی عنوان یا نام فایل..."></label>
<label><select id="category"><option value="all">همهٔ موارد</option><option value="صفحهٔ تاریخی">صفحات تاریخی</option><option value="سند یا رسانه">اسناد و رسانه‌ها</option></select></label></div>
<div class="archive-grid" id="archive-list">{cards}</div><p id="no-results" hidden>موردی پیدا نشد.</p></section></main>
<footer class="footer"><div class="container footer-bottom">آرشیو خاندان افشار نادری</div></footer><script defer src="./site.js"></script></body></html>'''
    write("legacy-index.html", template.encode("utf-8"))
    manifest = {"source": ORIGIN, "pages": pages, "assets": assets,
                "missing": missing, "download_bytes": total_bytes}
    write("IMPORT_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))


def fix_new_site_links():
    for name in ["index.html", "archive.html", "family.html"]:
        dest = ROOT / name
        if not dest.exists():
            continue
        source = dest.read_text(encoding="utf-8")
        for item in pages + assets:
            if item["path"] == "index.html":
                continue
            remote = ORIGIN + "/" + item["path"]
            local = "./" + item["path"]
            source = source.replace(remote, local)
        if name == "archive.html":
            source = source.replace('<div class="archive-controls">',
                '<div class="editorial"><strong>آرشیو منتقل‌شده</strong><p>برای مشاهدهٔ فهرست کامل صفحات و فایل‌هایی که به‌صورت محلی منتقل شده‌اند، '
                '<a href="./legacy-index.html">فهرست جامع منابع منتقل‌شده ←</a> را باز کنید.</p></div><div class="archive-controls">')
        dest.write_text(source, encoding="utf-8")


while queue and len(seen) < MAX_ITEMS and len(pages) < MAX_HTML and total_bytes < MAX_BYTES:
    url = queue.popleft()
    local = path_for(url)
    if not local or local in seen:
        continue
    seen.add(local)
    try:
        raw, mime = get(url)
        if local.lower().endswith((".html", ".htm")) or "text/html" in mime.lower():
            make_page(local, raw, url)
            print("PAGE", local, len(raw), flush=True)
        else:
            write(local, raw)
            assets.append({"path": local, "bytes": len(raw),
                           "sha256": hashlib.sha256(raw).hexdigest()})
            print("FILE", local, len(raw), flush=True)
            if local.lower().endswith(".css"):
                css = raw.decode("utf-8", errors="replace")
                for match in _asset_url_re.finditer(css):
                    enqueue(urljoin(url, match.group(1)))
    except Exception as exc:
        missing.append({"path": local, "error": str(exc)[:180]})
        print("FAILED", local, repr(exc), flush=True)

if len(pages) < 4:
    raise SystemExit(f"Import incomplete: only {len(pages)} HTML pages retrieved; refusing to modify site.")
write_catalog()
fix_new_site_links()
print(f"IMPORTED {len(pages)} pages, {len(assets)} files, {len(missing)} failures, {total_bytes} bytes", flush=True)
