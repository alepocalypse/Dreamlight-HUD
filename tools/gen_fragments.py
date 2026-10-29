"""Print the Timebending Fragment table (id -> English name). Read-only.

Usage: python3 tools/gen_fragments.py > fragments.tsv
One line per Fragment: id <TAB> internal name <TAB> English name.
Fragments are the items in itemlist/ActivityItem.json whose internal name starts with
"TimeBending!Expansion01!Shards!"; English names come from Localization/LocDB_en-US.zip
(ActivityItem.locbin, key = internal name + "_DisplayName"). Both are under the installed
game's ddv_Data/StreamingAssets. Copy the result into ddvhud/fragments.py.
Reuses the readers in gen_names.py.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_names import GAME, display_name, loc, varint  # noqa: E402

PREFIX = "TimeBending!Expansion01!Shards!"


def fragment_rows():
    """Sorted [(id, internal name)] for every Fragment in ActivityItem.json."""
    b = open(f"{GAME}/itemlist/ActivityItem.json", "rb").read()
    seen = {}
    for m in re.finditer(rb"\x08", b):
        try:
            i, j = varint(b, m.end())
            name = b[j + 2:j + 2 + b[j + 1]].decode("ascii") if b[j] == 0x12 else ""
        except (IndexError, UnicodeDecodeError):
            continue
        if name.startswith(PREFIX):
            seen.setdefault(i, name)
    return sorted(seen.items())


def main():
    text = loc(f"{GAME}/Localization/LocDB_en-US.zip", "ActivityItem.locbin")
    for i, name in fragment_rows():
        print(i, name, display_name(text, name, ""), sep="\t")


if __name__ == "__main__":
    main()
