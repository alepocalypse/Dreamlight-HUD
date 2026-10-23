"""Print the INGREDIENTS table for ddvhud/ingredients.py from dreamlightvalleywiki.com (MediaWiki API, read-only).
Each ingredient page's infobox gives |ingtype= (its category) and where to get it (|from=, |biomes=, |pool=).
Usage: python3 tools/gen_ingredients.py > table.txt     (review the AMBIGUOUS lines on stderr by hand)
"""
import json
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from ddvhud.recipes import RECIPES

API = "https://dreamlightvalleywiki.com/api.php"
CATEGORIES = ("Vegetables", "Spices", "Fruit", "Sweets", "Dairy and Oil", "Seafood", "Meat", "Fish", "Grains")


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


def clean(v):
    v = re.sub(r"<!--.*?-->", "", v or "", flags=re.S)
    v = re.sub(r"\{\{(?:name|pool|inlineIcon)\|([^|}]*)[^}]*\}\}", r"\1", v, flags=re.I)
    return re.sub(r"\{\{[^}]*\}\}|<br\s*/?>|\[\[|\]\]", " ", v)


SHORT = {"Dazzle Beach": "Dazzle", "Forest of Valor": "Valor", "Peaceful Meadow": "Meadow", "Sunlit Plateau": "Plateau",
         "Glade of Trust": "Glade", "Forgotten Lands": "Forgotten", "Frosted Heights": "Frosted",
         "Glittering Dunes": "Dunes", "Wild Tangle": "Tangle", "Ancient's Landing": "Landing",
         "Wishblossom Mountains": "Wishblossom", "Wishing Alps": "Alps", "The Bind": "Bind", "The Docks": "Docks",
         "The Overlook": "Overlook", "Pixie Acres": "Pixie", "Glamour Gulch": "Gulch", "Honeyglow Woods": "Honeyglow",
         "The Oasis": "Oasis", "The Grasslands": "Grasslands", "The Promenade": "Promenade", "The Grove": "Grove",
         "The Lagoon": "Lagoon", "Mythopia": "Mythopia", "Everafter": "Everafter"}
# the wiki's |ingtype= is blank, a template or a comment on a few pages; set by hand from the page text
CATEGORY_FIXES = {"Acorn Snail": "Dairy and Oil", "Plush Fish": "Fish", "Sweet Jelly": "Sweets", "Truffle": "Vegetables"}
MAX_PLACES = 3


def where(text):
    """'A, B' or 'A<br>B' of wiki place names -> short names, at most MAX_PLACES then '+n'."""
    places = [SHORT.get(p.strip(), p.strip()) for p in re.split(r",|<br\s*/?>", text) if p.strip()]
    places = list(dict.fromkeys(places))
    return "/".join(places[:MAX_PLACES]) + (f"/+{len(places) - MAX_PLACES}" if len(places) > MAX_PLACES else "")


def tag(f):
    """'Method, place, extra' for the first way the wiki lists, best method first: Farm, Fish, Forage, Dig, Bees, Bought."""
    src = (f.get("from") or "").lower()
    raw = f.get("biomes") or f.get("found") or ""
    names = re.findall(r"\{\{name\|([^|}]+)", raw)
    biomes = where(", ".join(names) if names else re.sub(r"<[^>]*>|\{\{.*|<!--.*", "", raw).strip())
    if "eggstravaganza" in src:
        return "Event"
    if "gardening" in src:
        return ", ".join(x for x in ("Farm", biomes) if x)
    if "fishing" in src:
        colours = [c for c in re.findall(r"Gold|Blue|White|None", f.get("pool") or "")]
        colours = "/".join(dict.fromkeys(colours))
        return ", ".join(x for x in ("Fish", biomes, colours) if x)
    if "foraging" in src:
        return ", ".join(x for x in ("Forage", biomes) if x)
    if "digging" in src:
        return "Dig"
    if "beekeeping" in src:
        return "Bees"
    if "chez remy" in src:
        return "Bought, Remy"
    if "goofy" in src:
        up = re.search(r"Upgrade (\d)", f.get("from") or "")
        return "Bought, Goofy" + (f" upg {up.group(1)}" if up else "")
    if "gaston" in src:
        return "Bought, Gaston"
    if "mulan" in src:
        return "Bought, Mulan"
    return ""


def main():
    names = sorted({i.strip() for r in RECIPES.values() for i in r.split(",")} - set(CATEGORIES) - {"Meat"})
    pages = {}
    for k in range(0, len(names), 40):
        pages.update(fetch(names[k:k + 40]))
    print("# name: (category, where to get it)")
    for n in names:
        f = infobox(pages.get(n, ""))
        cat = CATEGORY_FIXES.get(n) or f.get("ingtype") or ""
        cat = {"Protein": "Meat"}.get(cat, cat)
        if cat not in CATEGORIES:
            cat = ""
        print(f"    {n!r}: ({cat!r}, {tag(f)!r}),")


main()
