#!/usr/bin/env python3
"""Build navigable, locally hosted archive views from the verified import manifest.
Preserves unmodified original HTML in source-original; never changes original DNS.
Idempotent: deterministic output; uses only Python standard library.
"""
from __future__ import annotations
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT=Path("site")
manifest=json.loads((ROOT/"IMPORT_MANIFEST.json").read_text(encoding="utf-8"))
assets={x["path"] for x in manifest["assets"]}
pages={x["path"] for x in manifest["pages"]}
names=["افشار","شجرهٔ ۱","شجرهٔ ۲","افشار نادری","افشار نادری ۱","افشار نادری ۲","افشار نادری ۳","پژند","توانا","خاوری","دارویی","سیار","شیخ","طاهری لطفی","عظیم‌زاده","کامل","مهذب","نیکنام"]
people=[
 ("اسماعیل میرزا افشار نادری","ismail/ismail.html","اسناد، تألیفات و یادنامه"),
 ("داود میرزا دوم","davoud2/davoudm2.html","زندگی و اشعار"),
 ("دکتر غلامرضا افشار نادری","drghan/drghan.html","زندگی، آثار و خاطرات"),
 ("دکتر نادر افشار نادری","drnader/drnader.html","زندگی و آثار پژوهشی"),
]
docs=[
 ("تبارنامهٔ خاندان (PDF)","docs/shajareh.pdf","نسخهٔ اصلی سند"),
 ("تاریخچهٔ خاندان افشار (PDF)","docs/ismail_memo.pdf","یادنامه و تاریخچه"),
 ("تولدهای ثبت‌شده","docs/kashkoul.html","اسناد و یادداشت‌های تصویری"),
]
gallery_groups=[
 ("خاطرات و عکس‌های قدیمی خاندان","images/","g1"),
 ("اسناد و تألیفات اسماعیل میرزا","ismail/books/","g2"),
 ("تصاویر داود میرزا دوم","davoud2/photos/","g3"),
 ("تصاویر دکتر غلامرضا افشار نادری","drghan/images/","g4"),
 ("تصاویر آثار دکتر غلامرضا افشار نادری","drghan/data1/images/","g5"),
 ("تصاویر دکتر نادر افشار نادری","drnader/images/","g6"),
 ("اسناد تولد ثبت‌شده","docs/pages/","g7"),
]

def e(text):return html.escape(str(text),quote=True)
def href(path):return "./"+quote(path,safe="/")
def shell(title,subtitle,kicker,body,active="archive"):
    nav=[("خانه","./","home"),("آرشیو","./archive.html","archive"),("تبارنامه","./family.html","family"),("گالری تصاویر","./gallery.html","gallery"),("درباره","./about.html","about")]
    links="".join(f'<a href="{u}"'+(' class="active"' if v==active else "")+f'>{label}</a>' for label,u,v in nav)
    return f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="{e(subtitle)}"><link rel="icon" type="image/svg+xml" href="./favicon.svg"><link rel="stylesheet" href="./styles.css"><title>{e(title)} | خاندان افشار نادری</title></head><body>
<a class="skip" href="#main">رفتن به محتوا</a><header class="header"><div class="container nav-wrap">
<a href="./" class="logo"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a>
<nav aria-label="فهرست اصلی">{links}</nav></div></header>
<main id="main"><section class="subhero"><div class="container"><div class="kicker">{e(kicker)}</div><h1>{e(title)}</h1><p>{e(subtitle)}</p></div></section>{body}</main>
<footer class="footer"><div class="container footer-columns"><div><h3>خاندان افشار نادری</h3><p>حفظ اسناد و خاطرات برای نسل‌های آینده.</p><small>نسخهٔ آزمایشی؛ دامنهٔ اصلی تغییر نکرده است.</small></div><div class="footer-links"><a href="./archive.html">آرشیو</a><a href="./family.html">تبارنامه</a><a href="./gallery.html">گالری</a><a href="./about.html">درباره</a></div></div><div class="container footer-bottom"><span>آرشیو تاریخی خاندان افشار نادری</span><span>منابع اصلی محفوظ است</span></div></footer>
<script defer src="./site.js"></script></body></html>'''

def store(file,source): (ROOT/file).write_text(source,encoding="utf-8")

# NEW: native branch gallery with 18 locally hosted full-resolution diagrams.
options="".join(
 f'<button type="button" class="branch-choice'+(' selected' if i==1 else '')+f'" data-branch="{i}" aria-pressed="{str(i==1).lower()}"><span class="branch-num">{i:02d}</span>{e(label)}</button>'
 for i,label in enumerate(names,1) if f"tabaar/png_{i}.png" in assets
)
family_body=f'''<section class="section container"><div class="heritage-lead"><div><div class="kicker dark">نمودارهای اصلی</div><h2>۱۸ نمودار شجره‌نامه،<br>در یک محل.</h2><p>هر شاخه را انتخاب کنید؛ تصویر اصلی همان‌جا نمایش داده می‌شود. نمودارها از نسخهٔ قدیمی منتقل شده‌اند و بدون مراجعه به دامنهٔ قبلی قابل مشاهده‌اند.</p></div><div class="heritage-hint">نمودارها اسناد تصویری هستند و روابط جدیدی به آن‌ها اضافه نشده است.</div></div>
<div class="family-browser"><aside class="branch-sidebar"><h2>انتخاب شاخه</h2><div class="branch-menu" role="group" aria-label="شاخه‌های تبارنامه">{options}</div></aside>
<div class="branch-stage"><div class="stage-toolbar"><div><small>شجره‌نامهٔ خاندان</small><h2 id="branch-heading">{e(names[0])}</h2></div><div class="zoom-actions"><button id="zoom-out" type="button" aria-label="کوچک‌نمایی">−</button><button id="zoom-reset" type="button" aria-label="اندازهٔ اولیه">۱:۱</button><button id="zoom-in" type="button" aria-label="بزرگ‌نمایی">+</button></div></div>
<div class="diagram-scroll" id="diagram-scroll"><img id="branch-image" src="./tabaar/png_1.png" alt="شجره‌نامهٔ شاخهٔ افشار" loading="eager"></div>
<div class="diagram-links"><a id="branch-full" href="./tabaar/png_1.png" target="_blank" rel="noopener">تصویر اصلی با کیفیت کامل ↗</a><a id="branch-page" href="./tabaar/png_1.htm">صفحهٔ مستقل این نمودار ←</a></div></div></div>
<div class="family-downloads"><a href="./docs/shajareh.pdf" target="_blank" rel="noopener">نسخهٔ PDF شجره‌نامه ↗</a><a href="./tabaar/tabaar1.html">صفحهٔ تبارنامه در ساختار قدیمی ←</a></div>
<div class="editorial"><strong>دربارهٔ دقت تاریخی</strong><p>این تصاویر عین نمودارهای عمومی سایت اولیه‌اند؛ بازسازی اطلاعات و پیوندها نیازمند بررسی منابع است. اسناد اشخاص زنده نیز پیش از انتشار نهایی باید از نظر حریم خصوصی بازبینی شوند.</p></div></section>
<script id="branch-data" type="application/json">{json.dumps(names,ensure_ascii=False)}</script>
'''
store("family.html",shell("تبارنامهٔ خاندان","تمام شاخه‌های ثبت‌شده در نمودار قدیمی، یکجا و قابل بزرگ‌نمایی.","پیوندهای خانوادگی",family_body,"family"))

# CURATED ARCHIVE with all public original pages available locally.
def card(title,url,kind,description):
    return f'<article class="resource" data-category="{e(kind)}"><div class="pills"><span>{e(kind)}</span></div><h2>{e(title)}</h2><p>{e(description)}</p><a href="{href(url)}">مشاهده در همین سایت ←</a></article>'
cards=[]
for title,path,desc in people:
    if path in pages: cards.append(card(title,path,"زندگی‌نامه",desc))
for title,path,desc in docs:
    if path in pages or path in assets: cards.append(card(title,path,"اسناد",desc))
for title,path,desc in [("اشعار داود میرزا دوم","davoud2/dpoems.html","مجموعهٔ اشعار"),("آلبوم داود میرزا","davoud2/dslide.html","تصاویر خانوادگی"),("گالری آثار دکتر غلامرضا افشار نادری","drghan/index.html","تصاویر آثار")]:
    if path in pages: cards.append(card(title,path,"مجموعه‌ها",desc))
cards.append(card("نمودارهای ۱۸ شاخهٔ تبارنامه","family.html","تبارنامه","مشاهدهٔ یکپارچه و بزرگ‌نمایی نمودارها"))
cards.append(card("گالری تصاویر و آثار","gallery.html","گالری","تمام تصاویر تاریخی و آثار منتقل‌شده"))
archive_body=f'''<section class="section container"><div class="section-head"><div><div class="kicker dark">میراث به‌جا‌مانده</div><h2>از زندگی‌نامه تا سند و تصویر</h2></div><a href="./legacy-index.html" class="see-all">فهرست همهٔ فایل‌ها ←</a></div>
<div class="archive-controls"><label class="search"><span aria-hidden="true">⌕</span><input type="search" id="search" aria-label="جست‌وجو در آرشیو" placeholder="جست‌وجو در نام‌ها، سندها و آثار..."></label><label><span class="sr-only">فیلتر</span><select id="category"><option value="all">همهٔ موضوع‌ها</option><option value="زندگی‌نامه">زندگی‌نامه</option><option value="اسناد">اسناد</option><option value="مجموعه‌ها">مجموعه‌ها</option><option value="تبارنامه">تبارنامه</option><option value="گالری">گالری</option></select></label></div>
<div class="archive-grid" id="archive-list">{''.join(cards)}</div><p id="no-results" class="no-results" hidden>هیچ موردی با این عبارت پیدا نشد.</p>
<div class="editorial"><strong>نسخه‌های اصلی نزد ما محفوظ است</strong><p>تمام لینک‌های این صفحه به فایل‌ها و صفحات همین سایت اشاره می‌کنند. فهرست فایل‌های منتقل‌شده در <a href="./legacy-index.html">آرشیو جامع</a> نیز در دسترس است. جزئیات تاریخی بر اساس منابع اولیه ثبت شده‌اند و صحت‌سنجی مستقل آن‌ها هنوز کامل نیست.</p></div></section>'''
store("archive.html",shell("آرشیو تاریخی","زندگی‌نامه‌ها، تبارنامه، تصاویر و اسناد منتقل‌شده از وب‌سایت اولیه.","آرشیو اسناد و روایت‌ها",archive_body,"archive"))

# Unified visual gallery of available real assets (no placeholders).
sections=[]
for name,prefix,anchor in gallery_groups:
    files=sorted(x for x in assets if x.startswith(prefix) and x.lower().endswith((".jpg",".jpeg",".png",".gif",".webp")))
    if not files:continue
    items=[]
    for idx,path in enumerate(files,1):
        filename=Path(path).name
        label=filename.rsplit(".",1)[0].replace("_"," ").replace("-"," ")
        items.append(f'<a href="{href(path)}" class="gallery-tile" target="_blank" rel="noopener" title="تصویر اصلی: {e(filename)}"><img src="{href(path)}" loading="lazy" alt="{e(label)}"><span class="gallery-caption">{e(label)}</span></a>')
    sections.append(f'<section class="gallery-section" id="{anchor}"><div class="gallery-heading"><h2>{e(name)}</h2><span>{len(files)} تصویر</span></div><div class="gallery-grid">{"".join(items)}</div></section>')
gallery_body=f'''<section class="section container"><p class="bodycopy">تصاویر زیر از منابع قدیمی به همین سایت منتقل شده‌اند. روی هر تصویر کلیک کنید تا نسخهٔ کامل فایل در همین دامنه باز شود. برای پرهیز از برداشت نادرست، نام فایل‌های اصلی حفظ شده است.</p>
<div class="gallery-jump">{''.join(f'<a href="#{anchor}">{e(name)}</a>' for name,pre,anchor in gallery_groups if any(a.startswith(pre) for a in assets))}</div>
{''.join(sections)}
</section>'''
store("gallery.html",shell("گالری تصاویر و آثار","آلبوم‌های خانوادگی، اسناد تصویری، کتاب‌ها و آثار ثبت‌شده در آرشیو.","تصاویر آرشیوی",gallery_body,"gallery"))

# Replace inherited external links to the old site with local provenance pages;
# the original domain name remains plain-text on About, not used to load any content.
for name in ["index.html","about.html"]:
    p=ROOT/name
    val=p.read_text(encoding="utf-8")
    val=val.replace('href="https://afsharnaderi.com/"','href="./original/index.html"')
    val=val.replace('سایت اولیه ↗','نسخهٔ آرشیوی سایت اولیه ←')
    val=val.replace('بازدید از نسخهٔ قدیمی ↗','مشاهدهٔ نسخهٔ آرشیوی صفحهٔ قدیمی ←')
    if name=="index.html":
        val=val.replace('<a href="./family.html">تبارنامه</a>','<a href="./family.html">تبارنامه</a><a href="./gallery.html">گالری</a>',1)
        val=val.replace('<a href="./archive.html">آرشیو اسناد</a>','<a href="./archive.html">آرشیو اسناد</a><a href="./gallery.html">گالری تصاویر</a>')
        val=val.replace('بازکردن منبع اصلی ↗','مشاهدهٔ محتوای منتقل‌شده ←')
        val=val.replace('مشاهدهٔ منبع اصلی ↗','مشاهدهٔ محتوای منتقل‌شده ←')
    p.write_text(val,encoding="utf-8")

# Replace old fragile Visio/JavaScript wrappers with standalone responsive views.
for i,name in enumerate(names,1):
    rel=f"tabaar/png_{i}.htm"
    pic=f"tabaar/png_{i}.png"
    if rel not in pages or pic not in assets:continue
    content=f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="../styles.css"><title>شجره‌نامهٔ {e(name)} | خاندان افشار نادری</title></head><body>
<header class="header"><div class="container nav-wrap"><a class="logo" href="../"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a><nav><a href="../">خانه</a><a href="../family.html">تبارنامه</a><a href="../archive.html">آرشیو</a></nav></div></header>
<main class="container legacy-layout"><div class="legacy-breadcrumb"><a href="../family.html">تبارنامه</a> / {e(name)}</div><div class="legacy-heading"><div class="kicker dark">تصویر اصلی شجره‌نامه</div><h1>شاخهٔ {e(name)}</h1></div>
<div class="diagram-scroll standalone"><img src="png_{i}.png" alt="تصویر شجره‌نامهٔ {e(name)}"></div>
<div class="diagram-links"><a href="../family.html?branch={i}">نمایش در مرورگر تبارنامه ←</a><a href="png_{i}.png" target="_blank" rel="noopener">فایل تصویر کامل ↗</a><a href="../docs/shajareh.pdf" target="_blank" rel="noopener">PDF شجره‌نامه ↗</a></div>
<p class="legacy-provenance">تصویر از شجره‌نامهٔ اولیه؛ نسخهٔ منبع HTML اولیه در پوشهٔ source-original نگهداری می‌شود.</p></main><footer class="footer"><div class="container footer-bottom">خاندان افشار نادری</div></footer></body></html>'''
    store(rel,content)

# Improve important existing biography pages: local navigation to related complete collections.
related={
 "ismail/ismail.html":[("تاریخچهٔ خاندان (PDF)","../docs/ismail_memo.pdf"),("تصاویر اسناد و تألیفات","../gallery.html#g2")],
 "davoud2/davoudm2.html":[("اشعار","dpoems.html"),("آلبوم تصاویر","dslide.html"),("گالری","../gallery.html#g3")],
 "drghan/drghan.html":[("گالری تصاویر","../gallery.html#g4"),("تصاویر آثار","../gallery.html#g5"),("مجموعهٔ آثار تصویری","index.html")],
 "drnader/drnader.html":[("گالری تصاویر","../gallery.html#g6")],
 "docs/kashkoul.html":[("گالری تصاویر اسناد","../gallery.html#g7")],
 "tabaar/tabaar1.html":[("مرور تعاملی ۱۸ شاخه","../family.html")],
}
for key,links in related.items():
    if key not in pages:continue
    p=ROOT/key
    val=p.read_text(encoding="utf-8")
    target='<article class="legacy-document"'
    if target not in val:continue
    nav='<nav class="source-related" aria-label="بخش‌های مرتبط"><strong>بخش‌های مرتبط</strong>'+''.join(f'<a href="{url}">{e(label)} ←</a>' for label,url in links)+'</nav>'
    # Remove any previous generated nav, then insert exactly once.
    val=re.sub(r'<nav class="source-related"[\s\S]*?</nav>',"",val)
    val=val.replace(target,nav+target,1)
    p.write_text(val,encoding="utf-8")

# Styles for new browseable sections (idempotent).
css=ROOT/"styles.css"
base=css.read_text(encoding="utf-8")
marker="/* Integrated archival views v2 */"
if marker in base:base=base.split(marker)[0].rstrip()
addition="""
/* Integrated archival views v2 */
.heritage-lead{display:flex;justify-content:space-between;gap:35px;align-items:end;margin-bottom:30px}
.heritage-lead h2{font-size:clamp(26px,3vw,39px)}
.heritage-lead p{color:#5d6b67;font-size:13px;max-width:620px}
.heritage-hint{max-width:250px;border-right:2px solid #bfa57e;padding:15px;color:#68766f;font-size:12px;line-height:2}
.family-browser{display:grid;grid-template-columns:245px minmax(0,1fr);gap:16px;align-items:stretch}
.branch-sidebar{background:white;border:1px solid var(--line);padding:18px;max-height:820px;overflow:auto}
.branch-sidebar h2{font-size:16px;margin:0 0 15px}
.branch-menu{display:grid;gap:6px}
.branch-choice{border:1px solid transparent;background:#f7f5ef;padding:12px;display:flex;gap:13px;align-items:center;cursor:pointer;text-align:right;color:#203339;font-size:13px}
.branch-choice.selected,.branch-choice:hover{border-color:#b9a17e;background:#ede6d7}
.branch-choice.selected{font-weight:700}
.branch-num{font-family:Georgia,serif;color:#aa8e64;direction:ltr;font-size:12px}
.branch-stage{min-width:0;background:white;border:1px solid var(--line);padding:16px;display:flex;flex-direction:column}
.stage-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
.stage-toolbar small{font-size:11px;color:#a58a65}
.stage-toolbar h2{font-size:22px;margin:1px 0}
.zoom-actions{display:flex;gap:6px}
.zoom-actions button{border:1px solid #d1cbc0;background:#f6f3ed;min-width:39px;height:39px;cursor:pointer}
.zoom-actions button:hover{background:#eadfcc}
.diagram-scroll{overflow:auto;max-width:100%;min-height:390px;background:#f8f7f3;border:1px solid #e5e0d6;display:flex;align-items:flex-start;justify-content:flex-start}
.diagram-scroll img{display:block;max-width:none;max-height:none;width:100%;height:auto}
.diagram-scroll.standalone{min-height:480px;padding:14px}
.diagram-scroll.standalone img{width:auto;max-width:none}
.diagram-links{display:flex;flex-wrap:wrap;gap:15px;border-top:1px solid #e5e1d6;padding-top:15px;margin-top:14px;font-size:12px;color:#80653e;font-weight:700}
.family-downloads{display:flex;flex-wrap:wrap;gap:15px;margin-top:23px}
.family-downloads a,.gallery-jump a{padding:12px 16px;border:1px solid #c9c0af;font-size:12px}
.gallery-jump{display:flex;gap:9px;flex-wrap:wrap;margin:25px 0 45px}
.gallery-jump a:hover{background:#e7ddce}
.gallery-section{padding:37px 0;border-top:1px solid var(--line)}
.gallery-heading{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:20px}
.gallery-heading h2{font-size:23px}
.gallery-heading span{font-size:11px;color:#7b817b;white-space:nowrap}
.gallery-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}
.gallery-tile{background:white;border:1px solid #ddd8ce;display:block;min-width:0}
.gallery-tile img{display:block;width:100%;height:180px;object-fit:contain;background:#f0ede5}
.gallery-caption{display:block;padding:10px;color:#67716f;font-size:11px;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;direction:auto}
.gallery-tile:hover{box-shadow:0 9px 26px #10212917}
.source-related{display:flex;align-items:center;flex-wrap:wrap;gap:10px;background:#ece8dd;border:1px solid #e0d6c6;padding:12px 15px;margin:0 0 18px}
.source-related strong{font-size:12px;margin-left:5px}
.source-related a{padding:6px 10px;background:white;color:#765c38;font-size:12px}
@media(max-width:850px){.family-browser{grid-template-columns:1fr}.branch-sidebar{max-height:none}.branch-menu{grid-template-columns:repeat(3,minmax(0,1fr))}.gallery-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.heritage-hint{display:none}}
@media(max-width:600px){.branch-menu{grid-template-columns:repeat(2,minmax(0,1fr))}.gallery-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.gallery-tile img{height:145px}.gallery-heading h2{font-size:19px}.stage-toolbar h2{font-size:18px}.diagram-scroll{min-height:300px}.branch-choice{padding:9px;font-size:12px}.gallery-jump{gap:7px}}
"""
css.write_text(base+"\n"+marker+"\n"+addition,encoding="utf-8")

js=ROOT/"site.js"
original=js.read_text(encoding="utf-8")
mark="// Family chart browser v2"
if mark in original:original=original.split(mark)[0].rstrip()
chart_js=r"""
// Family chart browser v2
(() => {
 const image=document.getElementById('branch-image');
 const buttons=[...document.querySelectorAll('.branch-choice')];
 if(!image||!buttons.length)return;
 const names=JSON.parse(document.getElementById('branch-data').textContent);
 const heading=document.getElementById('branch-heading');
 const full=document.getElementById('branch-full');
 const page=document.getElementById('branch-page');
 const width=document.getElementById('diagram-scroll');
 let zoom=1;
 const select=(i,updateUrl=true)=>{
   if(!(i>=1&&i<=names.length))return;
   image.src='./tabaar/png_'+i+'.png';
   image.alt='شجره‌نامهٔ شاخهٔ '+names[i-1];
   heading.textContent=names[i-1];
   full.href=image.src;
   page.href='./tabaar/png_'+i+'.htm';
   buttons.forEach(b=>{const on=Number(b.dataset.branch)===i;b.classList.toggle('selected',on);b.setAttribute('aria-pressed',String(on))});
   zoom=1;image.style.width='100%';width.scrollTop=0;width.scrollLeft=0;
   if(updateUrl&&window.history?.replaceState) {
     const next=new URL(window.location.href);next.searchParams.set('branch',String(i));
     window.history.replaceState(null,'',next.pathname+next.search);
   }
 };
 const resize=(factor)=>{zoom=Math.max(.4,Math.min(4,factor));image.style.width=(zoom*100)+'%'};
 buttons.forEach(b=>b.addEventListener('click',()=>select(Number(b.dataset.branch))));
 document.getElementById('zoom-in')?.addEventListener('click',()=>resize(zoom*1.25));
 document.getElementById('zoom-out')?.addEventListener('click',()=>resize(zoom/1.25));
 document.getElementById('zoom-reset')?.addEventListener('click',()=>resize(1));
 const branch=Number(new URL(window.location.href).searchParams.get('branch'))||1;
 select(branch,false);
})();
"""
js.write_text(original+"\n"+mark+"\n"+chart_js,encoding="utf-8")
print(f"ARCHIVE_RENDER_OK: {len(pages)} pages, {len(assets)} assets, {len(sections)} gallery collections, {len(cards)} curated records")


# Preserve the archived original homepage under /original/index.html while
# making all its same-site relative links resolve from the nested directory.
archived=ROOT/"original/index.html"
if archived.exists():
    original=archived.read_text(encoding="utf-8")
    def repair_archived_url(match):
        start,value,end=match.groups()
        lower=value.lower()
        if not value or lower.startswith(("../","./../","http:","https:","//","#","mailto:","tel:","data:","javascript:")):
            return match.group(0)
        # Every link in the archived homepage originally resolved from /.
        return start+"../"+value+end
    fixed=re.sub(r'((?:href|src|poster|data-src)=["\x27])([^"\x27]+)(["\x27])',
                 repair_archived_url,original,flags=re.I)
    if fixed!=original:
        archived.write_text(fixed,encoding="utf-8")


# FULL_TEXT_INDEX_V1: local, private-to-browser full-text search over historical text.
from html.parser import HTMLParser as _HTMLParser
class _ExtractText(_HTMLParser):
 def __init__(self):
  super().__init__()
  self.skip=0
  self.stack=[]
  self.bits=[]
 def handle_starttag(self,tag,attrs):
  if tag in ("style","script","noscript"):self.skip+=1
  if tag in ("p","div","h1","h2","h3","li","br","tr"):self.bits.append(" ")
 def handle_endtag(self,tag):
  if tag in ("style","script","noscript"):self.skip=max(0,self.skip-1)
  if tag in ("p","div","h1","h2","h3","li","br","tr"):self.bits.append(" ")
 def handle_data(self,data):
  if not self.skip:self.bits.append(data)
def _text_from_html(source):
 ex=_ExtractText()
 ex.feed(source)
 return re.sub(r"\s+"," "," ".join(ex.bits)).strip()

text_records=[]
search_targets=people+[("اشعار داود میرزا دوم","davoud2/dpoems.html","اشعار تاریخی"),
 ("گالری داود میرزا دوم","davoud2/dslide.html","توضیحات آلبوم"),
 ("اسناد و تألیفات اسماعیل میرزا","ismail/ismail.html","تألیفات ثبت‌شده"),
 ("مجموعهٔ آثار و خاطرات دکتر غلامرضا","drghan/drghan.html","آثار ثبت‌شده")]
unique=set()
for title,key,description in search_targets:
 if key not in pages or key in unique:continue
 unique.add(key)
 original=ROOT/"source-original"/key
 if not original.exists():continue
 extracted=_text_from_html(original.read_text(encoding="utf-8",errors="replace"))
 if not extracted:continue
 text_records.append({"title":title,"description":description,"path":href(key),"content":extracted[:50000]})
store("search-index.json",json.dumps(text_records,ensure_ascii=False,separators=(",",":")))
search_body='''<section class="section container"><div class="heritage-lead"><div><div class="kicker dark">در متن سندها</div><h2>جست‌وجو در تاریخچه‌ها و زندگی‌نامه‌ها</h2><p>بخشی از متن زندگی‌نامه‌ها، اشعار و نوشته‌های موجود در آرشیو اولیه جست‌وجوپذیر شده است. جست‌وجو محلی و بدون ارسال عبارت شما به سرور انجام می‌شود.</p></div></div>
<label class="search full-search-box"><span aria-hidden="true">⌕</span><input type="search" id="full-search" placeholder="نام، موضوع یا عبارتی از متن..." aria-label="جست‌وجو در متن" autocomplete="off"></label>
<p class="search-count" id="full-search-count" role="status">برای آغاز، نام یا عبارتی را وارد کنید.</p><div class="archive-grid" id="full-results"></div>
<div class="editorial"><strong>دامنهٔ جست‌وجو</strong><p>این نمایه از متن عمومی برخی زندگی‌نامه‌ها و مجموعه‌های نوشتاری ساخته شده است. متن PDFها و تصاویر دست‌نویس هنوز وارد جست‌وجوی متنی نشده‌اند. برای مشاهدهٔ همهٔ مدارک از <a href="./archive.html">آرشیو</a> استفاده کنید.</p></div></section>'''
store("search.html",shell("جست‌وجو در متن","پیدا کردن اشخاص و واژه‌ها در زندگی‌نامه‌ها و اسناد نوشتاری.","جست‌وجوی محلی",search_body,"archive").replace('</body>','<script defer src="./search.js"></script></body>'))
search_js=r"""(()=>{
const input=document.getElementById('full-search');
const status=document.getElementById('full-search-count');
const results=document.getElementById('full-results');
if(!input||!status||!results)return;
const norm=s=>s.normalize('NFKC').replace(/[يى]/g,'ی').replace(/ك/g,'ک').replace(/[\u064b-\u065f]/g,'').toLowerCase();
let records=[];
fetch('./search-index.json').then(r=>{if(!r.ok)throw new Error('index unavailable');return r.json()}).then(data=>{records=data;status.textContent='نمایهٔ متنی آماده است؛ عبارت مورد نظر را بنویسید.';if(input.value)show()}).catch(()=>{status.textContent='نمایهٔ متنی در دسترس نیست.'});
const show=()=>{
 const q=norm(input.value.trim());
 results.replaceChildren();
 if(q.length<2){status.textContent='حداقل دو نویسه برای جست‌وجو وارد کنید.';return}
 const found=records.map(x=>({...x,hay:norm(x.content)})).filter(x=>norm(x.title+' '+x.content).includes(q)).slice(0,30);
 status.textContent=found.length+' نتیجه از '+records.length+' پروندهٔ متنی';
 for(const x of found){
  const box=document.createElement('article');box.className='resource';
  const h=document.createElement('h2');h.textContent=x.title;
  const p=document.createElement('p');
  const pos=x.hay.indexOf(q);const at=Math.max(0,pos-85);
  p.textContent=(at?'…':'')+x.content.slice(at,Math.min(x.content.length,at+260))+'…';
  const a=document.createElement('a');a.href=x.path;a.textContent='مشاهدهٔ متن کامل ←';
  box.append(h,p,a);results.append(box);
 }
};
input.addEventListener('input',show);
})();"""
store("search.js",search_js)
# The curated archive remains the primary landing; full-text search is additive.
archive=ROOT/"archive.html"
v=archive.read_text(encoding="utf-8")
v=v.replace('<div class="archive-controls">','<p class="fulltext-cta"><a href="./search.html">جست‌وجو در متن زندگی‌نامه‌ها و نوشته‌ها ←</a></p><div class="archive-controls">',1)
archive.write_text(v,encoding="utf-8")
home=ROOT/"index.html"
v=home.read_text(encoding="utf-8")
if 'href="./search.html"' not in v:
 v=v.replace('<a href="./gallery.html">گالری</a>','<a href="./gallery.html">گالری</a><a href="./search.html">جست‌وجو</a>',1)
home.write_text(v,encoding="utf-8")
css=ROOT/"styles.css"
v=css.read_text(encoding="utf-8")
if "/* Text search UI v1 */" not in v:
 v+="""
/* Text search UI v1 */
.fulltext-cta{margin:4px 0 24px;font-size:13px;font-weight:700}
.fulltext-cta a{color:#765b34;text-decoration:underline;text-underline-offset:5px}
.full-search-box{background:#fff;border:1px solid var(--line);display:flex;align-items:center;gap:12px;padding:0 18px}
.full-search-box input{border:0;min-height:64px;width:100%;background:transparent;outline:0}
.full-search-box span{font-size:27px;color:#a18453}
.full-search-box:focus-within{border-color:#bc9e68}
.search-count{font-size:12px;color:#68756f;margin:14px 0 22px}
"""
 css.write_text(v,encoding="utf-8")
print("TEXT_SEARCH_READY:",len(text_records),"archival documents indexed")


# HISTORIC_POEMS_V1: recover and typeset the complete eleven-document
# verse collection which the old site displayed through <object> embeds.
poem_ids=["p0","p00"]+["p"+str(n) for n in range(1,10)]
poem_labels={"p0":"تولد","p00":"زندگی‌نامهٔ منظوم"}
for n in range(1,10):poem_labels["p"+str(n)]="قطعهٔ "+str(n)
poem_sections=[]
poem_count=0
for ident in poem_ids:
 key="davoud2/poems/"+ident+".html"
 raw=ROOT/"source-original"/key
 if not raw.exists():continue
 src=raw.read_text(encoding="utf-8",errors="replace")
 verses=[]
 for part in re.findall(r'<p\b[^>]*>([\s\S]*?)</p>',src,flags=re.I):
  line=html.unescape(re.sub(r'<[^>]+>',"",part)).strip()
  if line:verses.append(line)
 intro_match=re.search(r'<h4\b[^>]*>([\s\S]*?)</h4>',src,flags=re.I)
 intro=(html.unescape(re.sub(r'<[^>]+>',"",intro_match.group(1))).strip() if intro_match else "")
 label=poem_labels[ident]
 if not verses:continue
 poem_count+=1
 verse_html=''.join('<p>'+e(v)+'</p>' for v in verses)
 note=('<p class="poem-intro">'+e(intro)+'</p>' if intro else '')
 poem_sections.append('<details class="poem-card" id="'+ident+'"'+(' open' if ident=="p0" else '')+'><summary>'+e(label)+'<span>'+str(len(verses))+' سطر</span></summary>'+note+'<div class="poem-lines">'+verse_html+'</div><p class="poem-standalone"><a href="poems/'+ident+'.html">صفحهٔ مستقل این شعر ←</a></p></details>')
 # Recreate a clean, standalone reading page at the original poem URL.
 pbody='''<header class="header"><div class="container nav-wrap"><a class="logo" href="../../"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a><nav><a href="../../">خانه</a><a href="../dpoems.html">اشعار داود میرزا</a><a href="../../gallery.html#g3">آلبوم تصاویر</a></nav></div></header>
<main class="container legacy-layout"><div class="legacy-breadcrumb"><a href="../dpoems.html">اشعار داود میرزا</a> / '''+e(label)+'''</div>
<div class="legacy-heading"><div class="kicker dark">متن آرشیوی</div><h1>'''+e(label)+''' — داود میرزا</h1></div>
<article class="legacy-document poem-original">'''+note+'<div class="poem-lines">'+verse_html+'''</div></article>
<p class="legacy-provenance">متن از سند HTML اصلی؛ نسخهٔ خام در source-original محفوظ است.</p><div class="diagram-links"><a href="../dpoems.html">همهٔ شعرها ←</a><a href="../../gallery.html#g3">گالری تصاویر ←</a></div></main><footer class="footer"><div class="container footer-bottom">خاندان افشار نادری</div></footer>'''
 ppage='<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="متن شعر داود میرزا افشار نادری"><link rel="stylesheet" href="../../styles.css"><title>'+e(label)+' | اشعار داود میرزا افشار نادری</title></head><body>'+pbody+'</body></html>'
 store(key,ppage)
 # Extend full-text search without indexing private scans.
 text_records.append({"title":"اشعار داود میرزا — "+label,"description":"متن شعر","path":"./"+key,"content":((intro+" " if intro else "")+" ".join(verses))[:50000]})
if poem_sections:
 page='''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="../styles.css"><title>اشعار داود میرزا | خاندان افشار نادری</title></head><body>
<header class="header"><div class="container nav-wrap"><a href="../" class="logo"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a><nav><a href="../">خانه</a><a href="../archive.html">آرشیو</a><a href="../gallery.html#g3">گالری</a></nav></div></header>
<main><section class="subhero"><div class="container"><div class="kicker">متن‌های بازیابی‌شده از آرشیو اولیه</div><h1>اشعار داود میرزا</h1><p>مجموعهٔ کامل شعرها و زندگی‌نامهٔ منظوم، بدون نیاز به افزونه‌های قدیمی و فایل‌های توکار.</p></div></section>
<section class="section container"><div class="kicker dark">یازده سند مستقل</div><h2>شعرها را بخوانید</h2><p class="bodycopy">با انتخاب عنوان هر قطعه، متن کامل آن نمایش داده می‌شود. صورت اصلی هر شعر، با همان واژگان و ترتیب بیت‌ها، در فایل‌های اولیه محفوظ است.</p>
<div class="poem-jump">'''+''.join('<a href="#'+ident+'">'+e(poem_labels[ident])+'</a>' for ident in poem_ids if (ROOT/"source-original/davoud2/poems"/(ident+".html")).exists())+'''</div>
<div class="poems-list">'''+''.join(poem_sections)+'''</div><div class="family-downloads"><a href="../gallery.html#g3">آلبوم داود میرزا ←</a><a href="davoudm2.html">صفحهٔ زندگی‌نامه ←</a></div></section></main>
<footer class="footer"><div class="container footer-bottom"><span>خاندان افشار نادری · آرشیو تاریخی</span><a href="../archive.html">بازگشت به آرشیو ←</a></div></footer>
<script>if(location.hash){let el=document.getElementById(location.hash.slice(1));if(el&&el.tagName==="DETAILS")el.open=true}</script></body></html>'''
 store("davoud2/dpoems.html",page)
 store("search-index.json",json.dumps(text_records,ensure_ascii=False,separators=(",",":")))
css=ROOT/"styles.css"
v=css.read_text(encoding="utf-8")
if "/* Restored historical poems v1 */" not in v:
 v+="""
/* Restored historical poems v1 */
.poem-jump{display:flex;flex-wrap:wrap;gap:8px;margin:25px 0}
.poem-jump a{border:1px solid #c7b9a3;padding:9px 13px;font-size:12px}
.poem-card{background:white;border:1px solid #e4ded1;margin:12px 0}
.poem-card summary{font-size:16px;font-weight:700;padding:18px 23px;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.poem-card summary span{font-size:11px;color:#988773;font-weight:400}
.poem-card[open] summary{border-bottom:1px solid #eee9df;background:#f4f0e7}
.poem-intro{font-size:13px;color:#62716b;text-align:center;margin:18px auto;max-width:620px}
.poem-lines{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:30px;max-width:810px;margin:22px auto;align-items:baseline}
.poem-lines p{font-size:15px;line-height:2.1;padding:4px;margin:0;text-align:center;min-width:0}
.poem-standalone{padding:0 20px 20px;text-align:center;font-size:12px;color:#846642}
.poem-original{overflow-wrap:break-word}
@media(max-width:600px){.poem-lines{grid-template-columns:1fr;gap:1px}.poem-lines p{font-size:14px}.poem-card summary{padding:15px}}
"""
 css.write_text(v,encoding="utf-8")
print("HISTORIC_POEMS_RENDERED",poem_count,"standalone poems; full-text index",len(text_records))
