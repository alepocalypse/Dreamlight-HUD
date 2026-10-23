"""Print the Star Path duty text table rows for ddvhud/duty_text.py. Read-only.

Usage: python3 tools/gen_duties.py > duties.txt
Prints the STAR_PATHS = {...} block to paste into ddvhud/duty_text.py (one Star Path per entry: title,
currency name, duty texts, weekly duty texts). The English text is Liveops.locbin in the game's plain zip
Localization/LocDB_en-US.zip (read in memory); the file layout is the one gen_names.py describes.
"""
import re
import zipfile

import gen_names


def parse_locbin(data):
    """{key: English text} from the bytes of one .locbin (same layout gen_names.loc reads)."""
    out, i = {}, 0
    while i < len(data):
        _, i = gen_names.varint(data, i)
        n, i = gen_names.varint(data, i)
        rec, i = data[i:i + n], i + n
        j, f = 0, {}
        while j < len(rec):
            tag, j = gen_names.varint(rec, j)
            ln, j = gen_names.varint(rec, j)
            f[tag >> 3] = rec[j:j + ln].decode("utf-8"); j += ln
        out[f.get(1)] = f.get(2, "")
    return out


def star_paths(text):
    """{Star Path id: {title, currency, duties, weeks}} from the parsed Liveops text.

    A Star Path id is letters then a 4-digit year (Seafaring2026) with a _Title and at least one duty
    text (event news such as Seafaring2026Start has no year at the end). Duty texts are in numeric task
    order (the numbers skip), weeks in week order with their slots in slot order; no-break spaces become
    normal spaces."""
    def clean(t):
        return t.replace("\u00a0", " ")

    out = {}
    for key in text:
        m = re.fullmatch(r"([A-Za-z]+\d{4})_Title", key)
        if not m:
            continue
        sid = m[1]
        duties = sorted((int(n), clean(text[k])) for k in text
                        for n in re.findall(rf"{sid}_Task(\d+)_Description", k))
        if not duties:
            continue
        weeks = {}
        for k in text:
            w = re.fullmatch(rf"{sid}_Week(\d+)Task(\d+)_Description", k)
            if w:
                weeks.setdefault(int(w[1]), []).append((int(w[2]), clean(text[k])))
        out[sid] = {"title": clean(text[key]), "currency": clean(text.get(sid + "_CurrencyName", "")),
                    "duties": [t for _, t in duties],
                    "weeks": [[t for _, t in sorted(weeks[w])] for w in sorted(weeks)]}
    return out


def main():
    zp = f"{gen_names.GAME}/Localization/LocDB_en-US.zip"
    paths = star_paths(parse_locbin(zipfile.ZipFile(zp).read("Liveops.locbin")))
    print("STAR_PATHS = {")
    for sid in sorted(paths):
        p = paths[sid]
        print(f"    {sid!r}: {{")
        print(f"        'title': {p['title']!r},")
        print(f"        'currency': {p['currency']!r},")
        print("        'duties': [")
        for t in p["duties"]:
            print(f"            {t!r},")
        print("        ],")
        print("        'weeks': [")
        for w in p["weeks"]:
            print(f"            {w!r},")
        print("        ],")
        print("    },")
    print("}")


if __name__ == "__main__":
    main()
