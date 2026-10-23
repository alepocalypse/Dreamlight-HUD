"""Print the game's English display names for the Companion, Critter and gift tables. Read-only.

Usage: python3 tools/gen_names.py [companions|items] > names.tsv
One line per id: id <TAB> internal name <TAB> English name (empty when the game text lacks the key).
The English text is in the game's plain zip Localization/LocDB_en-US.zip (read in memory):
Companion.locbin and ActivityItem.locbin are repeated (0x0a, varint length, record); a record is
field 1 = key string (the internal name + "_DisplayName"), field 2 = English text.
Internal names come from itemlist/Companion.json and itemlist/ActivityItem.json (see
gen_companions.py / gen_items.py). Copy the names into ddvhud/companions.py and ddvhud/items.py,
keeping the old tidied name wherever the third column is empty.
"""
import os
import re
import sys
import zipfile

GAME = os.path.expanduser("~/.local/share/Steam/steamapps/common/Disney Dreamlight Valley/ddv_Data/StreamingAssets")
GIFT_BLOCKS = (302, 303, 308, 310, 311, 316, 317)
SKIP = re.compile(r"Mission|Secret|TreasureHunt|Shards|SnippetCatching|^Event!(Spring!|.*Note)")


def varint(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1; r |= (x & 0x7F) << s; s += 7
        if x < 0x80:
            return r, i


def loc(zip_path, member):
    """{key: English text} from one .locbin inside the localisation zip."""
    b = zipfile.ZipFile(zip_path).read(member)
    out, i = {}, 0
    while i < len(b):
        _, i = varint(b, i)
        n, i = varint(b, i)
        rec, i = b[i:i + n], i + n
        j, f = 0, {}
        while j < len(rec):
            tag, j = varint(rec, j)
            ln, j = varint(rec, j)
            f[tag >> 3] = rec[j:j + ln].decode("utf-8"); j += ln
        out[f.get(1)] = f.get(2, "")
    return out


def display_name(text, internal, fallback):
    """The game's English name for an internal name, or `fallback` (the old tidied name) if the text lacks the key."""
    # a few fish are keyed under a "Fish!" prefix (Fish!Expansion01!Shad_DisplayName)
    return text.get(internal + "_DisplayName") or text.get("Fish!" + internal + "_DisplayName") or fallback


def companion_names():
    b = open(f"{GAME}/itemlist/Companion.json", "rb").read()
    i = 0
    while i < len(b):
        _, i = varint(b, i)
        n, i = varint(b, i)
        rec, i = b[i:i + n], i + n
        j, f = 0, {}
        while j < len(rec):
            tag, j = varint(rec, j)
            if tag & 7 == 0:
                v, j = varint(rec, j)
            elif tag & 7 == 2:
                ln, j = varint(rec, j); v = rec[j:j + ln]; j += ln
            elif tag & 7 == 1:
                j += 8; continue
            else:
                j += 4; continue
            f.setdefault(tag >> 3, v)
        yield f[1], f[2].decode()


def item_names():
    b = open(f"{GAME}/itemlist/ActivityItem.json", "rb").read()
    seen = {}
    for m in re.finditer(rb"\x08", b):
        try:
            i, j = varint(b, m.end())
            name = b[j + 2:j + 2 + b[j + 1]].decode("ascii") if b[j] == 0x12 else ""
        except (IndexError, UnicodeDecodeError):
            continue
        if i // 100000 in GIFT_BLOCKS and re.fullmatch(r"[A-Za-z0-9_!]{2,}", name) and not SKIP.search(name):
            seen.setdefault(i, name)
    return sorted(seen.items())


def main(which):
    zp = f"{GAME}/Localization/LocDB_en-US.zip"
    if which == "items":
        text, rows = loc(zp, "ActivityItem.locbin"), item_names()
    else:
        text, rows = loc(zp, "Companion.locbin"), sorted(companion_names())
    for i, name in rows:
        print(i, name, display_name(text, name, ""), sep="\t")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "companions")
