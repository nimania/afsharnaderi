#!/usr/bin/env python3
import json
import re
from pathlib import Path
root=Path("site")
manifest=json.loads((root/"IMPORT_MANIFEST.json").read_text(encoding="utf-8"))
names={"tabaar/tabaar1.html":"نمودار شجره‌نامه",
"ismail/ismail.html":"اسماعیل میرزا افشار نادری",
"davoud2/davoudm2.html":"داود میرزا دوم",
"drghan/drghan.html":"دکتر غلامرضا افشار نادری",
"drnader/drnader.html":"دکتر نادر افشار نادری",
"docs/kashkoul.html":"تولدهای ثبت‌شده"}
count=0
for item in manifest["pages"]:
    key=item["path"]
    page=root/("original/index.html" if key=="index.html" else key)
    if not page.is_file(): continue
    old=page.read_text(encoding="utf-8")
    val=re.sub(r'(<article class="legacy-document" id="original-record">)\s*<body\b[^>]*>',r'\1',old,count=1,flags=re.I)
    val=re.sub(r'</body>\s*</article>',r'</article>',val,count=1,flags=re.I)
    val=re.sub(r'<!--[\s\S]*?-->','',val)
    if key=="tabaar/tabaar1.html":
        val=re.sub(r'<div class="iframe-container">\s*</div>',
          '<div class="iframe-container"><iframe name="frmDrawing" id="family-chart" title="نمودار شاخه‌های خاندان" src="png_1.htm" loading="lazy"></iframe></div>',
          val,count=1,flags=re.I)
        val=val.replace("<span>Afshar</span>","<span>نمودار شجره‌نامه</span>")
    if key in names:
        title=names[key]
        val=re.sub(r'<title>[^<]*</title>',f'<title>{title} | آرشیو خاندان افشار نادری</title>',val,count=1)
        val=re.sub(r'(<div class="legacy-heading">[\s\S]*?<h1>)[\s\S]*?(</h1>)',
          lambda match:match.group(1)+title+match.group(2),val,count=1)
    if val!=old:
        page.write_text(val,encoding="utf-8")
        count+=1
home=root/"index.html"
val=home.read_text(encoding="utf-8")
val=val.replace("این نسخه آزمایشی است. پیوندها فعلاً اسناد را در سایت اصلی باز می‌کنند؛ فایل‌های قدیمی هنوز به مخزن منتقل نشده‌اند.",
"این نسخه آزمایشی است. منابع عمومی در همین سایت میزبانی می‌شوند؛ <a href='./legacy-index.html'>فهرست کامل اسناد منتقل‌شده</a> را ببینید.")
home.write_text(val,encoding="utf-8")
about=root/"about.html"
val=about.read_text(encoding="utf-8")
val=val.replace("تا پایان انتقال کامل صفحات و مدارک، لینک‌های نسخهٔ جدید به منبع اصلی ارجاع می‌دهند. DNS و دامنهٔ afsharnaderi.com تغییر نکرده است.",
"صفحات و اسناد عمومی شناسایی‌شده به نسخهٔ جدید منتقل شده‌اند؛ بررسی و تطبیق همهٔ جزئیات ادامه دارد. DNS و دامنهٔ afsharnaderi.com تغییر نکرده است.")
about.write_text(val,encoding="utf-8")
family=root/"family.html"
val=family.read_text(encoding="utf-8")
val=val.replace("با پیوند به نمودار و نسخهٔ سندی اصلی.","با پیوند به نمودار و نسخهٔ PDF که در همین سایت میزبانی می‌شوند.")
family.write_text(val,encoding="utf-8")
style=root/"styles.css"
val=style.read_text(encoding="utf-8")
if "/* Restored family viewer */" not in val:
 val+="""
/* Restored family viewer */
.legacy-document .menu-container{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 22px}
.legacy-document .menu-container>div{border:1px solid #e5e0d3;background:#f6f4ee;padding:8px 14px;font-size:12px}
.legacy-document .menu-container a{color:#654d2c;text-decoration:none}
.legacy-document .iframe-container{width:100%;min-height:640px}
.legacy-document iframe[name="frmDrawing"]{width:100%;height:min(75vh,850px);min-height:640px;border:1px solid #d8d0c3;background:#fff}
.legacy-document img[usemap]{max-width:none!important}
.legacy-document .image-gallery{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:12px}
@media(max-width:720px){.legacy-document .iframe-container{min-height:500px}.legacy-document iframe[name="frmDrawing"]{height:66vh;min-height:490px}}
"""
 style.write_text(val,encoding="utf-8")
print("Updated",count,"historical page wrappers")
