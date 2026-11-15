#!/usr/bin/env python3
"""Recover same-origin HTML documents embedded via <object data=...> in legacy pages.
Bounded download only for missing public resources. Preserves original bytes and
keeps old paths. Uses the same manifest maintained by the initial importer.
"""
from __future__ import annotations
import hashlib
import html
import json
import posixpath
from collections import deque
from pathlib import Path
from urllib.parse import unquote,urljoin,urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path("site")
HOST="afsharnaderi.com"
ORIGIN="https://"+HOST+"/"
manifest_path=ROOT/"IMPORT_MANIFEST.json"
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
pages={x["path"]:x for x in manifest["pages"]}
assets={x["path"]:x for x in manifest["assets"]}
missing={x["path"]:x for x in manifest.get("missing",[])}
MAX_COUNT=100
MAX_TOTAL=80*1024*1024
MAX_EACH=18*1024*1024
ALLOWED={".html",".htm",".jpg",".jpeg",".png",".gif",".webp",".css",".js",".pdf"}
queue=deque()
seen=set()
bytes_read=0
session=requests.Session()
session.headers.update({"User-Agent":"AfsharNaderiArchiveMigration/1.1 (public archival preservation)"})

def convert(u,base=ORIGIN):
    joined=urljoin(base,u.replace("\\","/"))
    p=urlparse(joined)
    if p.scheme not in ("http","https") or p.hostname is None or p.hostname.lower().removeprefix("www.")!=HOST:
        return None,None
    local=posixpath.normpath("/"+unquote(p.path).lstrip("/")).lstrip("/")
    if not local or local.startswith("../") or "/../" in local or "\x00" in local:
        return None,None
    if Path(local).suffix.lower() not in ALLOWED:return None,None
    return local,ORIGIN+local

def queue_link(u,base):
    local,url=convert(u,base)
    if local and local not in seen and local not in pages and local not in assets and local not in missing:
        queue.append((local,url))

# Source HTML is immutable. Examine all original public pages for embedded
# <object data> and linked material under /davoud2/poems/.
for source in ROOT.glob("source-original/**/*"):
    if not source.is_file() or source.suffix.lower() not in (".html",".htm"):continue
    source_rel=source.relative_to(ROOT/"source-original").as_posix()
    base=ORIGIN+source_rel
    soup=BeautifulSoup(source.read_bytes(),"html.parser")
    for tag in soup.find_all(["object","embed","iframe"]):
        item=tag.get("data") or tag.get("src")
        if item:queue_link(item,base)
    # Some historic pages have CSS/JS that refers to other HTML files.
    if source_rel=="davoud2/dpoems.html":
        for name in ("p00","p0","p1","p2","p3","p4","p5","p6","p7","p8","p9"):
            queue_link("poems/"+name+".html",base)

def get(url):
    global bytes_read
    with session.get(url,stream=True,timeout=(10,35)) as resp:
        resp.raise_for_status()
        redirected,_=convert(resp.url)
        if not redirected:raise RuntimeError("Off-domain redirect")
        size=0
        chunks=[]
        for chunk in resp.iter_content(65536):
            if not chunk:continue
            chunks.append(chunk)
            size+=len(chunk)
            if size>MAX_EACH or bytes_read+size>MAX_TOTAL:raise RuntimeError("Download size cap")
        bytes_read+=size
        return b"".join(chunks),resp.headers.get("content-type","")

def write(rel,buf):
    out=ROOT/rel
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(buf)

def local_relative(path,target):
    return posixpath.relpath(target,posixpath.dirname(path) or ".")

def as_page(rel,raw):
    soup=BeautifulSoup(raw,"html.parser")
    title=(soup.title.get_text(" ",strip=True) if soup.title else Path(rel).stem)
    body=soup.body or soup
    for tag in body.select("script,style,iframe,object,form,base,meta"):
        tag.decompose()
    for tag in body.find_all(True):
        for att in list(tag.attrs):
            if att.lower().startswith("on"):del tag[att]
        for att in ("href","src","poster","data-src"):
            if not isinstance(tag.get(att),str):continue
            val=tag[att]
            if not val or val.startswith(("#","mailto:","tel:","javascript:","data:")):continue
            target,url=convert(val,ORIGIN+rel)
            if target:
                tag[att]=local_relative(rel,target)
                queue_link(val,ORIGIN+rel)
    home=local_relative(rel,"index.html")
    archive=local_relative(rel,"archive.html")
    poemlist=local_relative(rel,"davoud2/dpoems.html")
    css=local_relative(rel,"styles.css")
    pretty=html.escape(title)
    result=f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="{css}"><title>{pretty} | خاندان افشار نادری</title></head><body>
<header class="header"><div class="container nav-wrap"><a class="logo" href="{home}"><span class="logo-mark">ا‌ن</span><span><strong>خاندان افشار نادری</strong><small>آرشیو تاریخ و تبار خانواده</small></span></a>
<nav><a href="{home}">خانه</a><a href="{archive}">آرشیو</a><a href="{poemlist}">اشعار داود میرزا</a></nav></div></header>
<main class="container legacy-layout"><div class="legacy-breadcrumb"><a href="{archive}">آرشیو</a> / <a href="{poemlist}">اشعار داود میرزا</a> / {pretty}</div>
<article class="legacy-document poem-original">{str(body)}</article>
<p class="legacy-provenance">متن از سند اصلی سایت خانوادگی بازیابی شده؛ فایل خام جداگانه حفظ شده است.</p><div class="diagram-links"><a href="{poemlist}">بازگشت به فهرست شعرها ←</a><a href="{home}">صفحهٔ اصلی ←</a></div></main>
<footer class="footer"><div class="container footer-bottom">خاندان افشار نادری</div></footer></body></html>'''
    write(rel,result.encode("utf-8"))
    pages[rel]={"path":rel,"title":title,"source":ORIGIN+rel,"original_sha256":hashlib.sha256(raw).hexdigest()}
    write("source-original/"+rel,raw)

completed=0
failed=0
while queue and completed<MAX_COUNT and bytes_read<MAX_TOTAL:
    path,url=queue.popleft()
    if path in seen or path in pages or path in assets or path in missing:continue
    seen.add(path)
    try:
        buf,mime=get(url)
        if Path(path).suffix.lower() in (".html",".htm") or "text/html" in mime.lower():
            as_page(path,buf)
            completed+=1
            print("EMBEDDED_HTML",path,len(buf),flush=True)
        else:
            write(path,buf)
            assets[path]={"path":path,"bytes":len(buf),"sha256":hashlib.sha256(buf).hexdigest()}
            completed+=1
            print("EMBEDDED_ASSET",path,len(buf),flush=True)
    except Exception as exc:
        failed+=1
        missing[path]={"path":path,"error":str(exc)[:180]}
        print("EMBEDDED_FAILED",path,str(exc)[:180],flush=True)

manifest["pages"]=list(pages.values())
manifest["assets"]=list(assets.values())
manifest["missing"]=list(missing.values())
manifest["download_bytes"]=manifest.get("download_bytes",0)+bytes_read
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("EMBEDDED_IMPORT_RESULT",completed,"new files;",failed,"errors;",bytes_read,"bytes",flush=True)
