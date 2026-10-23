"""Print the raw Companion and Critter records from the game's Companion.json. Read-only.

Usage: python3 tools/gen_companions.py [Companion.json] > raw.txt
One line per record: id, internal name, and for Critters the Companion id it unlocks
(field 23) and the feedings needed (field 20, inferred). Tidy the names and assign Jobs
by species by hand when updating (the English names come from tools/gen_names.py) ddvhud/companions.py (see its header).
"""
import os
import sys

DEFAULT = ("~/.local/share/Steam/steamapps/common/Disney Dreamlight Valley/ddv_Data"
           "/StreamingAssets/itemlist/Companion.json")


def varint(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1; r |= (x & 0x7F) << s; s += 7
        if x < 0x80:
            return r, i


def fields(m):
    i, out = 0, {}
    while i < len(m):
        tag, i = varint(m, i)
        kind = tag & 7
        if kind == 0:
            v, i = varint(m, i)
        elif kind == 2:
            n, i = varint(m, i); v = m[i:i + n]; i += n
        elif kind == 1:
            v = m[i:i + 8]; i += 8
        elif kind == 5:
            v = m[i:i + 4]; i += 4
        else:
            raise ValueError(f"unexpected wire type {kind}")
        out.setdefault(tag >> 3, []).append(v)
    return out


def main(path):
    b = open(path, "rb").read()   # file = repeated (varint tag, varint length, record)
    i = 0
    while i < len(b):
        _, i = varint(b, i)
        n, i = varint(b, i)
        f = fields(b[i:i + n]); i += n
        rid, name = f[1][0], f[2][0].decode()
        if rid >= 120100000:
            print(rid, name, f.get(23, [None])[0], f.get(20, [None])[0])
        else:
            print(rid, name)


main(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(DEFAULT))
