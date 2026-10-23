"""Print the RECIPES table for ddvhud/recipes.py from dreamlightvalleywiki.com (MediaWiki API, read-only).
Meal pages carry |ingredients={{IngredientList | A, B, C, D | ...}}. Usage: python3 tools/gen_recipes.py > table.txt
"""
import json
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from ddvhud.items import ITEMS

API = "https://dreamlightvalleywiki.com/api.php"


def fetch(titles):
    q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                "redirects": 1, "format": "json", "titles": "|".join(titles)})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req))["query"]
    back = {}
    for r in data.get("redirects", []):
        back[r["to"]] = r["from"]
    for page in data["pages"].values():
        revs = page.get("revisions")
        if revs:
            yield back.get(page["title"], page["title"]), revs[0]["slots"]["main"]["*"]


meals = sorted({n for i, n in ITEMS.items() if 30300000 <= i < 30400000})
for k in range(0, len(meals), 40):
    for title, text in fetch(meals[k:k + 40]):
        m = re.search(r"\|\s*ingredients\s*=\s*(?:<!--)?\{\{IngredientList\s*\|([^|}]*)", text)
        if m and "{{" not in m.group(1):
            print(f"{title}\t{m.group(1).strip()}")
