"""Print the SPAWNS rows for ddvhud/spawns.py from dreamlightvalleywiki.com (MediaWiki API, read-only).
Each item page's infobox lists where it is found (|biomes= or |found=) and how (|from=, |type=).
Usage: python3 tools/gen_spawns.py > rows.txt      (meals, block 303, are left out: they are cooked)
"""
import json
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from ddvhud.items import ITEMS

API = "https://dreamlightvalleywiki.com/api.php"
# first match wins, so a gem with a stall in `from` is still Mining
METHODS = (("mining", "Mining"), ("digging", "Digging"), ("fishing", "Fishing"), ("gardening", "Gardening"),
           ("foraging", "Foraging"))


def fetch(titles):
    q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                "redirects": 1, "format": "json", "titles": "|".join(titles)})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req))["query"]
    back = {r["to"]: r["from"] for r in data.get("redirects", [])}
    for page in data["pages"].values():
        revs = page.get("revisions")
        if revs:
            yield back.get(page["title"], page["title"]), revs[0]["slots"]["main"]["*"]


def infobox(text):
    m = re.search(r"\{\{infobox(.*?)\n\}\}", text, re.S | re.I)
    fields = {}
    for part in re.split(r"\n\|", m.group(1)) if m else []:
        if "=" in part:
            k, v = part.split("=", 1)
            fields[k.strip().lower()] = v.strip()
    return fields


def zones(f):
    raw = re.sub(r"<!--.*?-->", "", f.get("biomes") or f.get("found") or "", flags=re.S)
    names = re.findall(r"\{\{name\|([^|}]+)", raw)
    if not names:
        names = [p.strip() for p in re.split(r",|<br\s*/?>|\n", re.sub(r"\{\{.*?\}\}", "", raw)) if p.strip()]
    return tuple(dict.fromkeys(names))


def method(f):
    src = ((f.get("from") or "") + " " + (f.get("type") or "")).lower()
    return next((name for key, name in METHODS if key in src), None)


names = sorted(n for i, n in ITEMS.items() if not 30300000 <= i < 30400000)
by_name = {}
for k in range(0, len(names), 40):
    by_name.update(dict(fetch(names[k:k + 40])))
for i, n in sorted(ITEMS.items()):
    if 30300000 <= i < 30400000 or n not in by_name:
        continue
    f = infobox(by_name[n])
    z, m = zones(f), method(f)
    if z and m:
        print(f"    {i}: ({m!r}, {z!r}),  # {n}")
