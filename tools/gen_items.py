"""Print the ITEMS table for ddvhud/items.py from the game's item data. Read-only.

Tidied fallback names only; the game's English names come from tools/gen_names.py.
Usage: python3 tools/gen_items.py [ActivityItem.json] > new_table.txt
"""
import re
import sys

DEFAULT = ("~/.local/share/Steam/steamapps/common/Disney Dreamlight Valley/ddv_Data"
           "/StreamingAssets/itemlist/ActivityItem.json")
GIFT_BLOCKS = (302, 303, 308, 310, 311, 316, 317)   # id // 100000: crops, meals, flowers, fish, products, gems, materials
SKIP = re.compile(r"Mission|Secret|TreasureHunt|Shards|SnippetCatching|^Event!(Spring!|.*Note)")
NOISE = re.compile(r"^(Expansion\d+|Mini01|Event|Vegetable|Fruit|Grain|Spice|Basic|Refinement|Product"
                   r"|TimeBending|Seafood|Protein|Meat|Summer|Spring|FloatingFestival|Winter2025|Parks?)$")


def words(s):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|_", " ", s).strip()


def tidy(raw):
    parts = [p for p in raw.split("!") if not NOISE.match(p)] or raw.split("!")[-1:]
    base = re.sub(r"^RPT_(Summer|Park)_", "", parts[0]).removesuffix("01").replace("LilyOTheValley", "LilyOfTheValley")
    if len(parts) > 1:   # Flower!FlowerWhite -> Flower (White)
        var = parts[-1]
        return f"{words(base)} ({words(var[len(base):] if var.startswith(base) else var)})"
    return re.sub(r"^(.*?)( [A-Z][a-z]+)$", r"\1 (\2)", words(base)).replace("( ", "(") if base.count("_") else words(base)


def varint(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1; r |= (x & 0x7F) << s; s += 7
        if x < 0x80:
            return r, i


def main(path):
    b = open(path, "rb").read()   # protobuf records: 0x08 id-varint 0x12 len ascii-name
    items = {}
    for m in re.finditer(rb"\x08", b):
        try:
            i, j = varint(b, m.end())
            name = b[j + 2:j + 2 + b[j + 1]].decode("ascii") if b[j] == 0x12 else ""
        except (IndexError, UnicodeDecodeError):
            continue
        if i // 100000 in GIFT_BLOCKS and re.fullmatch(r"[A-Za-z0-9_!]{2,}", name) and not SKIP.search(name):
            items.setdefault(i, tidy(name))
    for i in sorted(items):
        print(f"    {i}: {items[i]!r},")


main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT.replace("~", __import__("os").path.expanduser("~")))
