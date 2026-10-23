"""Print each Companion's Job as the wiki's Companion page gives it (|hangout=), for ddvhud/companions.py. Read-only.
Usage: python3 tools/gen_companion_jobs.py > jobs.txt
One line per Companion: id, name, the Job in the table, the Job on the wiki (blank when the page has none).
Lines where the two differ are the ones to fix by hand. The wiki's wording is mapped to the table's Jobs:
Flowers -> Flower pick-up, Wood -> Wood pick-up, Snippets -> Snippet catching, Parts -> Time-bending.
"""
import json
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from ddvhud.companions import COMPANIONS, JOBS

API = "https://dreamlightvalleywiki.com/api.php"
WORDING = {"Flowers": "Flower pick-up", "Wood": "Wood pick-up", "Snippets": "Snippet catching", "Parts": "Time-bending"}


def fetch(titles):
    q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                "redirects": 1, "format": "json", "titles": "|".join(titles)})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req))["query"]
    back = {r["to"]: r["from"] for r in data.get("redirects", [])}
    for page in data["pages"].values():
        if "revisions" in page:
            yield back.get(page["title"], page["title"]), page["revisions"][0]["slots"]["main"]["*"]


names = sorted({v[0] for v in COMPANIONS.values()})
pages = {}
for k in range(0, len(names), 40):
    pages.update(dict(fetch(names[k:k + 40])))
for cid, (name, _species, job) in COMPANIONS.items():
    m = re.search(r"\|\s*hangout\s*=\s*([^\n|<]*)", pages.get(name, ""), re.I)
    wiki = (m.group(1).strip() if m else "")
    wiki = WORDING.get(wiki, wiki)
    print(cid, name, job, wiki if wiki in JOBS else "", "" if wiki not in JOBS or wiki == job else "<<< differs")
