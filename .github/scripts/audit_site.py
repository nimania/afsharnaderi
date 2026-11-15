#!/usr/bin/env python3
"""Audit locally linked HTML resources without changing DNS or contacting websites."""
import json
import posixpath
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
root=Path("site")
class Scanner(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.urls=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  for k in ("href","src","poster","data-src","action"):
   v=attrs.get(k)
   if v: self.urls.append((k,v))
  if attrs.get("srcset"):
   for item in attrs["srcset"].split(","):
    if item.strip():self.urls.append(("srcset",item.strip().split()[0]))
pages=[x for x in root.rglob("*") if x.suffix.lower() in (".html",".htm") and "source-original" not in x.parts]
known={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
broken=[]
old=[]
offsite=Counter()
count=0
for file in pages:
 rel=file.relative_to(root).as_posix()
 parser=Scanner()
 try:parser.feed(file.read_text(encoding="utf-8"))
 except Exception as exc:
  broken.append((rel,"parser",str(exc)));continue
 for key,value in parser.urls:
  count+=1
  raw=value.strip()
  if not raw or raw.startswith(("#","mailto:","tel:","data:","javascript:")):continue
  u=urlparse(raw.replace("\\","/"))
  if raw.startswith("//"):u=urlparse("https:"+raw)
  if u.scheme:
   if u.scheme in ("https","http"):
    host=(u.hostname or "").lower().removeprefix("www.")
    if host=="afsharnaderi.com":old.append((rel,raw))
    else:offsite[host]+=1
   continue
  if not u.path:continue
  if u.path.startswith("/"):
   if u.path.startswith("/afsharnaderi/"):target=u.path[len("/afsharnaderi/"):]
   else:
    broken.append((rel,"root-relative",raw))
    continue
  else:target=posixpath.normpath(posixpath.join(posixpath.dirname(rel),unquote(u.path)))
  if target==".":target="index.html"
  if target.endswith("/"):target+="index.html"
  if target not in known and target+"/index.html" not in known:
   broken.append((rel,key,raw))
report={"html_pages_checked":len(pages),"references_checked":count,
        "broken_local_links":len(broken),"links_to_old_domain":len(old),
        "offsite_reference_hosts":dict(offsite),
        "broken_examples":[{"page":a,"type":b,"url":c} for a,b,c in broken[:150]],
        "old_domain_examples":[{"page":a,"url":b} for a,b in old[:80]]}
(root/"LINK_AUDIT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
lines=["# Link audit",f"- HTML pages inspected: {len(pages)}",f"- URLs inspected: {count}",
       f"- Broken internal URLs: {len(broken)}",f"- Remaining links to previous domain: {len(old)}",
       "", "## Broken links"]
lines.extend(["- "+str(a)+" -> "+str(c)+" ("+str(b)+")" for a,b,c in broken[:100]] or ["None."])
lines.extend(["","## Original-domain links"])
lines.extend(["- "+str(a)+" -> "+str(b) for a,b in old[:80]] or ["None."])
lines.extend(["","Historical external references to other domains are not mirrored.",
              "Static checks do not substitute for browser-based visual review."])
Path("docs/LINK_AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"LINK_AUDIT html={len(pages)} refs={count} missing={len(broken)} old_domain={len(old)}")
for a,b,c in broken[:40]:print("BROKEN",a,b,c)
for a,b in old[:15]:print("OLD_LINK",a,b)
