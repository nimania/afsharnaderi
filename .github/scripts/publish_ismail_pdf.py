#!/usr/bin/env python3
"""Publish the user's exact 34-page family-history PDF as accessible HTML.

Source: site/docs/ismail_memo.pdf
The upload and archived original have identical SHA-256. Never rewrite the
original PDF or source-original HTML files. The HTML includes the real PDF
text layer, original embedded images and per-page facsimiles for verification.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

import fitz

ROOT = Path("site")
SOURCE = ROOT / "docs/ismail_memo.pdf"
TARGET = ROOT / "ismail/ismail.html"
IMAGES = ROOT / "ismail/tarikhcheh-images"
EXPECTED_SHA = "4f29bf92d22f38716bf875ee4efe9354a9b7fc0c123cc58a1f19763f0acbb6d3"
START = "<!-- ISMAIL_HISTORY_HTML_START -->"
END = "<!-- ISMAIL_HISTORY_HTML_END -->"
PAGES = 34

chapters = [
    ("توضیحات ویراستار", 3),
    ("مقدمهٔ اسماعیل میرزا", 4),
    ("چگونگی ایل افشاریه", 6),
    ("احوالات نادر قلی بیک افشار", 6),
    ("احوالات امام قلی بیک افشار", 6),
    ("احوالات نادرشاه افشار", 7),
    ("احوالات رضا قلی میرزا", 8),
    ("احوالات شاهرخ‌شاه افشار", 8),
    ("احوالات امام قلی میرزا افشار", 9),
    ("احوالات اسماعیل میرزای اول", 9),
    ("احوالات داود میرزای اول", 10),
    ("داود میرزا پس از تولد اسماعیل میرزا", 13),
    ("احوالات اسماعیل میرزا، نویسنده", 19),
    ("وصیت‌نامه و اسناد پایانی", 33),
]

def esc(s):
    return html.escape(str(s), quote=True)

def clean(s):
    s = s.replace("\ufeff", "").replace("\u00ad", "").replace("\uf0d8", "•")
    s = re.sub(r"[\u200e\u200f\u202a-\u202e]", "", s)
    return re.sub(r"[ \t\r\n]+", " ", s).strip()

def fix_punctuation(s):
    # Only whitespace, not wording, dates or historical content.
    s = clean(s)
    s = re.sub(r"\s+([،؛؟!])", r"\1", s)
    return s

def text_from_block(block):
    pieces = []
    fonts = []
    max_size = 0.0
    for line in block.get("lines", []):
        text = "".join(span.get("text", "") for span in line.get("spans", []))
        if text.strip():
            pieces.append(text.strip())
        for span in line.get("spans", []):
            if span.get("text", "").strip():
                fonts.append(span.get("font", ""))
                max_size = max(max_size, float(span.get("size", 0)))
    return fix_punctuation(" ".join(pieces)), max_size, fonts

def title_block(text, size, fonts, page_no):
    if page_no == 1:
        return False
    return bool(
        size >= 15.6
        and len(text) <= 120
        and ("Compset" in " ".join(fonts) or page_no in (3, 4, 6))
        and len(text) >= 4
    )

def page_ordinal(num):
    return "صفحهٔ " + str(num) + " از " + str(PAGES)

def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

if not SOURCE.exists():
    raise SystemExit("Missing archived source PDF; refusing to publish partial text")
pdf_hash = sha256(SOURCE)
if pdf_hash != EXPECTED_SHA:
    raise SystemExit("Archived PDF hash differs from user's document, refusing conversion")
doc = fitz.open(SOURCE)
if len(doc) != PAGES:
    raise SystemExit("Unexpected PDF page count")
IMAGES.mkdir(parents=True, exist_ok=True)

page_sections = []
image_count = 0
page_texts = []
word_count = 0
chapter_list = "".join(
    '<a href="#ism-page-' + str(page) + '"><span>' + str(i + 1).zfill(2)
    + '</span>' + esc(title) + '</a>'
    for i, (title, page) in enumerate(chapters)
)

for page_index, page in enumerate(doc):
    n = page_index + 1
    # Render a complete facsimile to preserve layout, footnotes, drawings and
    # any text which the PDF's digital text layer may extract imperfectly.
    facsimile = "page-" + str(n).zfill(2) + ".jpg"
    dest = IMAGES / facsimile
    raster = page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25), alpha=False)
    jpeg = raster.tobytes("jpg", jpg_quality=73)
    if not dest.exists() or dest.read_bytes() != jpeg:
        dest.write_bytes(jpeg)

    raw_blocks = page.get_text("dict", sort=True)["blocks"]
    fragments = []
    footnotes = []
    pending = []
    last_bottom = None
    seen_figures = set()
    figures_on_page = 0
    textbuf = []

    def flush():
        nonlocal_frag = fix_punctuation(" ".join(pending))
        if nonlocal_frag:
            fragments.append('<p class="ism-paragraph">' + esc(nonlocal_frag) + '</p>')
        pending.clear()

    for block in raw_blocks:
        bbox = block.get("bbox", (0, 0, 0, 0))
        y0, y1 = float(bbox[1]), float(bbox[3])
        if block.get("type") == 1:
            payload = block.get("image")
            if not payload:
                continue
            digest = hashlib.sha256(payload).hexdigest()
            if digest in seen_figures:
                continue
            seen_figures.add(digest)
            flush()
            figures_on_page += 1
            image_count += 1
            ext = block.get("ext", "png").lower()
            ext = "jpg" if ext in ("jpeg", "jpg") else (ext if ext in ("png", "webp", "gif") else "png")
            fn = "figure-" + str(n).zfill(2) + "-" + str(figures_on_page).zfill(2) + "." + ext
            out = IMAGES / fn
            if not out.exists() or out.read_bytes() != payload:
                out.write_bytes(payload)
            width = float(bbox[2]) - float(bbox[0])
            kind = "wide" if width >= 270 else "small"
            fragments.append(
                '<figure class="ism-figure ism-figure-' + kind + '">'
                '<a href="tarikhcheh-images/' + fn + '" target="_blank" rel="noopener" '
                'aria-label="بازکردن تصویر اصلی">'
                '<img src="tarikhcheh-images/' + fn + '" loading="lazy" '
                'alt="تصویر یا سند تاریخی درج‌شده در صفحهٔ ' + str(n) + '، تصویر ' + str(figures_on_page) + '">'
                '</a><figcaption>تصویر ' + str(figures_on_page) + ' از صفحهٔ ' + str(n)
                + ' · مشاهده در اندازهٔ اصلی</figcaption></figure>'
            )
            last_bottom = None
            continue

        if block.get("type") != 0:
            continue
        text, size, fonts = text_from_block(block)
        if not text or text.isspace():
            continue
        # PDF footer's page numbers, not part of the text body.
        if y0 > 770 and len(text) < 12 and re.fullmatch(r"[\s\d۰-۹]+", text):
            continue
        textbuf.append(text)

        if page_index == 0:
            # Title page is typeset natively in the new article header.
            continue
        if page_index == 1:
            # PDF's dotted-leader TOC is replaced with accessible chapter links.
            continue
        if title_block(text, size, fonts, n):
            flush()
            fragments.append('<h3 class="ism-source-heading">' + esc(text) + '</h3>')
            last_bottom = None
            continue

        if y0 > 710 and size and size <= 11.2:
            flush()
            footnotes.append('<span>' + esc(text) + '</span>')
            last_bottom = None
            continue

        if pending and last_bottom is not None and y0 - last_bottom > 9:
            flush()
        pending.append(text)
        last_bottom = y1

    flush()
    if n == 1:
        fragments.insert(0,
            '<p class="ism-title-page-note">عنوان سند: تاریخچهٔ خاندان افشار · '
            'به قلم اسماعیل میرزا افشار نادری · به کوشش علی افشار نادری</p>')
    if n == 2:
        fragments.append('<p class="ism-page-note">فهرست اصلی سند به‌صورت '
                         'فهرست پیونددار در ابتدای این نسخه بازآفرینی شده است. '
                         'تصویر کامل صفحه در ادامه قابل مشاهده است.</p>')
    if not fragments:
        fragments.append('<p class="ism-page-note">این صفحه عمدتاً '
                         'حاوی تصویر سند است. نسخهٔ کامل صفحه را نیز می‌توانید باز کنید.</p>')
    notes = ('<aside class="ism-footnotes" aria-label="یادداشت‌ها و زیرنویس‌های صفحه">'
             + "".join(footnotes) + '</aside>') if footnotes else ""
    img = 'tarikhcheh-images/' + facsimile
    sections = (
        '<section class="ism-page" id="ism-page-' + str(n) + '">'
        '<div class="ism-page-top"><span>متن صفحهٔ ' + str(n) + '</span>'
        '<a href="../docs/ismail_memo.pdf#page=' + str(n) + '" target="_blank" rel="noopener">'
        'صفحه در PDF ↗</a></div>'
        '<div class="ism-page-body">' + "".join(fragments) + notes + '</div>'
        '<details class="ism-facsimile"><summary>نمایش تصویر کامل صفحهٔ '
        + str(n) + ' از سند</summary><a href="' + img + '" target="_blank" rel="noopener">'
        '<img src="' + img + '" loading="lazy" alt="تصویر کامل صفحهٔ '
        + str(n) + ' از تاریخچهٔ خاندان افشار"></a>'
        '<p>این تصویر برای تطبیق با متن و حفظ جای‌گذاری دقیق عکس‌ها و زیرنویس‌ها ارائه شده است.</p>'
        '</details></section>'
    )
    page_sections.append(sections)
    page_texts.append(" ".join(textbuf))
    word_count += len(" ".join(textbuf).split())

pdf_title = "تاریخچهٔ خاندان افشار"
cover = (
    '<section class="ism-book-intro" id="tarikhcheh">'
    '<div class="ism-book-kicker">متن کامل کتاب · آرشیو خانوادگی</div>'
    '<h2>' + pdf_title + '</h2>'
    '<p class="ism-book-byline">به قلم <strong>اسماعیل میرزا افشار نادری</strong>'
    ' · به کوشش <strong>علی افشار نادری</strong></p>'
    '<p>این نسخهٔ دیجیتال از PDF ۳۴ صفحه‌ای تهیه شده و متن آن برای مطالعه و جست‌وجو '
    'در مرورگر بازآفرینی شده است. تصاویر اصلی کتاب، دست‌نوشته‌ها و نمودارها در کنار متن قرار دارند؛ '
    'تصویر کامل هر صفحه نیز برای بررسی دقیق قابل بازکردن است.</p>'
    '<div class="ism-book-actions">'
    '<a class="btn btn-dark" href="#ism-reading">شروع مطالعه ←</a>'
    '<a class="btn btn-pale" href="../docs/ismail_memo.pdf" target="_blank" rel="noopener">نسخهٔ اصلی PDF ↗</a>'
    '<a class="btn btn-pale" href="#ism-chapters">فهرست فصل‌ها ↓</a>'
    '</div>'
    '<p class="ism-book-disclaimer">توجه: متن از لایهٔ متنی خود PDF استخراج شده است و '
    'ممکن است برخی فاصله‌ها و ترکیب حروف دقیق نباشند. تصاویر کامل صفحات، مرجع تطبیق با اصل سند هستند. '
    'متن و ادعاهای تاریخی بدون بازنویسی محتوایی منتشر شده‌اند.</p>'
    '</section>'
)
nav = (
    '<div class="ism-document-layout">'
    '<aside class="ism-chapters" id="ism-chapters">'
    '<h3>فهرست فصل‌ها</h3><nav aria-label="فهرست فصل‌های تاریخچه">'
    + chapter_list + '</nav><a class="ism-chapters-pdf" href="../docs/ismail_memo.pdf" '
    'target="_blank" rel="noopener">PDF کامل سند ↗</a></aside>'
    '<div class="ism-pages" id="ism-reading">' + "".join(page_sections) + '</div>'
    '</div>'
)
article = START + '\n' + cover + nav + '\n' + END

current = TARGET.read_text(encoding="utf-8")
# Remove any previously generated book from this exact page.
current = re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END), "", current)
# Preserve all legacy book-sample images; remove only obsolete status label.
current = re.sub(r'<footer>\s*<h6>در دست ساخت</h6>\s*</footer>', '', current)
# Insert book before the existing publications gallery.
point = '<article class="legacy-document" id="original-record">'
if point not in current:
    raise SystemExit("Legacy Ismail page structure changed; refusing to overwrite it")
current = current.replace(point,
    article + '\n<div class="ism-other-works" id="ism-other-works">'
    '<div class="kicker dark">آرشیو تألیفات</div>'
    '<h2>دیگر آثار و دست‌نوشته‌های اسماعیل میرزا</h2>'
    '<p>تصاویر و اطلاعات تألیفات که قبلاً در این صفحه منتشر شده بودند، در ادامه محفوظ‌اند.</p>'
    '</div>\n' + point, 1)
current = current.replace('<link rel="stylesheet" href="../styles.css">',
    '<link rel="stylesheet" href="../styles.css"><link rel="stylesheet" href="tarikhcheh.css">', 1)
current = current.replace('href="../docs/ismail_memo.pdf">تاریخچهٔ خاندان (PDF) ←</a>',
    'href="#tarikhcheh">مطالعهٔ کامل تاریخچه ←</a>'
    '<a href="../docs/ismail_memo.pdf" target="_blank" rel="noopener">PDF اصلی ↗</a>', 1)
TARGET.write_text(current, encoding="utf-8")

# Update the already generated archive's original PDF-only entry. Preserve the
# original PDF as a separate entry and preserve other resources intact.
archive = ROOT / "archive.html"
if archive.exists():
    original = archive.read_text(encoding="utf-8")
    original = original.replace(
        '<h2>تاریخچهٔ خاندان افشار (PDF)</h2>',
        '<h2>تاریخچهٔ خاندان افشار (PDF)</h2>',
    )
    # Insert a link to the HTML article immediately before PDF card, once.
    marker = 'href="./docs/ismail_memo.pdf"'
    link = ('<p class="ism-inline-archive-link"><a href="./ismail/ismail.html#tarikhcheh">'
            'مطالعهٔ متن و تصاویر کتاب در HTML ←</a></p>')
    if marker in original and link not in original:
        original = original.replace(marker, marker, 1)
        # Append prominent callout before the result grid to avoid breaking the card's HTML.
        original = original.replace(
            '<div class="archive-controls">',
            '<div class="editorial"><strong>تاریخچهٔ خاندان افشار</strong><p>'
            '<a href="./ismail/ismail.html#tarikhcheh">متن کامل و تصاویر ۳۴ صفحه، '
            'در صفحهٔ اسماعیل میرزا ←</a></p></div><div class="archive-controls">',
            1,
        )
    archive.write_text(original, encoding="utf-8")

# Add full book text to existing browser-side search index.
search_file = ROOT / "search-index.json"
if search_file.exists():
    records = json.loads(search_file.read_text(encoding="utf-8"))
    records = [r for r in records if r.get("path") != "./ismail/ismail.html#tarikhcheh"]
    records.append({
        "title": "تاریخچهٔ خاندان افشار — اسماعیل میرزا",
        "description": "متن کامل ۳۴ صفحهٔ سند تاریخی",
        "path": "./ismail/ismail.html#tarikhcheh",
        "content": " ".join(page_texts)[:150000]
    })
    search_file.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

meta = {
    "source_pdf_path": "site/docs/ismail_memo.pdf",
    "source_sha256": pdf_hash,
    "page_count": len(doc),
    "total_words_extracted_approx": word_count,
    "text_characters_extracted": sum(len(x) for x in page_texts),
    "original_images_extracted": image_count,
    "facsimile_page_images": len(doc),
    "chapters": [{"title": name, "page": page} for name, page in chapters],
    "notes": "Native HTML text is machine extracted from the PDF text layer. PDF is authoritative."
}
(ROOT / "ismail/tarikhcheh-manifest.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("ISMAIL_PDF_TO_HTML_OK",
      "pages=" + str(len(doc)),
      "figures=" + str(image_count),
      "chars=" + str(meta["text_characters_extracted"]),
      "hash=" + pdf_hash, flush=True)
