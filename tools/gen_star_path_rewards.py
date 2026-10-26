"""Print ddvhud/star_path_rewards.py: each Star Path Duty's token Reward, from dreamlightvalleywiki.com (read-only).
Each Star Path page has a Duties table whose rows match the game's duty order one for one, and a Routine Duties
table grouped by week (a "Week N" cell spanning its rows); a week not yet out is one "Releasing ..." row. Rows are
read by position, never by text. Warnings (stderr): a row whose text does not resemble the game's text at that
position (ddvhud/duty_text.py), and a week whose row count differs from the game's, which is then left out.
Usage: python3 tools/gen_star_path_rewards.py > ddvhud/star_path_rewards.py
"""
import difflib
import json
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from ddvhud.duty_text import STAR_PATHS

API = "https://dreamlightvalleywiki.com/api.php"

PAGES = {   # Star Path id (as the save names it) -> its wiki page title, kept by hand. Current Star Paths only:
    # pages of past ones list their rows in another order than the game (dozens of mismatch warnings each).
    "HauntingElegance2026": "Haunting Elegance Star Path",
    "Seafaring2026": "Seafaring Star Path",
}
LIKE = 0.5   # difflib ratio below which a wiki row's text does not resemble the game's


def fetch(titles):
    q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                "redirects": 1, "format": "json", "titles": "|".join(titles)})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req))["query"]
    back = {r["to"]: r["from"] for r in data.get("redirects", [])}
    for page in data["pages"].values():
        if "revisions" in page:
            yield back.get(page["title"], page["title"]), page["revisions"][0]["slots"]["main"]["*"]


def plain(raw):
    raw = re.sub(r"<ref[^>/]*/>|<ref[^>]*>.*?</ref>", "", raw, flags=re.S)
    raw = re.sub(r"\{\{.*?\}\}", "", raw)
    raw = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", raw)
    raw = re.sub(r"<[^>]+>|'''?", "", raw).replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", raw).strip()


def _section(wikitext, heading):
    m = re.search(r"^==\s*" + heading + r"\s*==\s*$(.*?)(?=^==[^=]|\Z)", wikitext, flags=re.M | re.S)
    if not m:
        return ""
    table = re.search(r"^\{\|.*?^\|\}", m.group(1), flags=re.M | re.S)
    return re.sub(r"<!--.*?-->", "", table.group(0), flags=re.S) if table else ""


def _cells(row):
    """The row's cells in order, attributes ('align="center" | ') removed."""
    out = []
    for line in row.splitlines():
        if not line.startswith("|") or line.startswith(("|}", "|-", "|+")):
            continue
        for cell in line[1:].split("||"):
            m = re.match(r"\s*(?:(?:align|rowspan|colspan|style|width)\s*=\s*\"?[^|\"]*\"?\s*)+\|(?!\|)(.*)$", cell)
            out.append((m.group(1) if m else cell).strip())
    return out


def _rows(table):
    return [_cells(r) for r in re.split(r"^\|-.*$", table, flags=re.M)[1:]]


def _reward(cells):
    """(text, amount) of a duty row: [#, icon, text, amount, {{price|N|token}}, ...]; amount None without a price."""
    m = next((re.search(r"\{\{\s*price\s*\|\s*([\d,]+)", c) for c in cells if re.search(r"\{\{\s*price", c)), None)
    return (plain(cells[2]) if len(cells) > 2 else ""), (int(m.group(1).replace(",", "")) if m else None)


def parse_tables(wikitext):
    """{duties: [(text, amount)] by row, weeks: [[(text, amount)] by slot, or None for a 'Releasing ...' week]}."""
    duties = []
    for cells in _rows(_section(wikitext, "Duties")):
        if cells and re.fullmatch(r"\d+", cells[0]):
            duties.append(_reward(cells))
    weeks = []
    for cells in _rows(_section(wikitext, "Routine Duties")):
        if cells and re.match(r"Week\s*\d+", cells[0]):
            weeks.append([])
            cells = cells[1:]
        if not weeks or not cells or not re.fullmatch(r"\d+", cells[0]):
            continue
        if weeks[-1] is None or any("Releasing" in c for c in cells):
            weeks[-1] = None
        else:
            weeks[-1].append(_reward(cells))
    return {"duties": duties, "weeks": weeks}


def _alike(wiki, game):
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
    return difflib.SequenceMatcher(None, norm(wiki), norm(game)).ratio() >= LIKE


def rewards(sid, tables, game, warn):
    """{duties: [amount], weeks: [[amount]]} for one Star Path, checked against the game's texts `game`."""
    for i, (text, _) in enumerate(tables["duties"]):
        if i < len(game["duties"]) and not _alike(text, game["duties"][i]):
            warn(f"{sid} duty {i + 1}: wiki {text!r} vs game {game['duties'][i]!r}")
    weeks = []
    for w, rows in enumerate(tables["weeks"]):
        theirs = game["weeks"][w] if w < len(game["weeks"]) else []
        if rows is None:
            weeks.append([])
            continue
        if len(rows) != len(theirs):
            warn(f"{sid} week {w + 1}: wiki has {len(rows)} rows, game {len(theirs)}; left out")
            weeks.append([])
            continue
        for s, (text, _) in enumerate(rows):
            if not _alike(text, theirs[s]):
                warn(f"{sid} week {w + 1} slot {s + 1}: wiki {text!r} vs game {theirs[s]!r}")
        weeks.append([a for _, a in rows])
    while weeks and not weeks[-1]:
        weeks.pop()
    return {"duties": [a for _, a in tables["duties"]], "weeks": weeks}


def main():
    warn = lambda msg: print("warning:", msg, file=sys.stderr)
    titles = sorted(PAGES.values())
    pages = {}
    for k in range(0, len(titles), 40):
        pages.update(dict(fetch(titles[k:k + 40])))
    print('"""Generated by tools/gen_star_path_rewards.py from dreamlightvalleywiki.com; do not edit.')
    print("STAR_PATH_REWARDS: Star Path id -> {duties: token amount by 0-based duty position, weeks: per 0-based week,")
    print("the amount by 0-based slot}. None, a short list or an empty week means the wiki does not list that duty.\"\"\"")
    print("STAR_PATH_REWARDS = {")
    for sid, title in sorted(PAGES.items()):
        if title not in pages:
            warn(f"{sid}: no wiki page {title!r}")
            continue
        table = rewards(sid, parse_tables(pages[title]), STAR_PATHS.get(sid, {"duties": [], "weeks": []}), warn)
        print(f"    {sid!r}: {{  # {title}")
        print(f"        'duties': {table['duties']!r},")
        print(f"        'weeks': {table['weeks']!r},")
        print("    },")
    print("}")


if __name__ == "__main__":
    main()
