"""The ordered task list: duty_plan(duties, groups) -> entries.

Input: duties, every open duty of every Star Path in save order (main duties, then each week's) as
{path, text, current, target, weekly}; groups, shared_actions.do_together's groups over them.
A duty with current >= target is done and left out.

Output: [{tier, label, duties, spans}] to work top to bottom, each duty once. Tiers: 'cross' (one action
advances duties in two Star Paths), 'together' (it doubles up inside one Star Path), 'single' (a duty in no
group, its label the duty's own text). Within a tier: most duties advanced first, then the earliest duties in
the input (Star Path save order, main before weekly, list order). The groups' input order never matters.

A duty in several groups (do_together allows it) is listed under each of them, since one action advances
it every time; a group keeps only its open duties, and one left with fewer than two gives them up. A group
whose duties all share one 'family' (e.g. 'Fish') is dropped as well: that family's entry holds them. A duty
in no remaining group is a single, unless it carries a 'family' and a 'row' (the colour, the Villager): those
merge, per family, into one 'rows' entry at the first one's place, even when it is the family's only duty, its rows
sorted by their 'rank' (lowest, the most generic, first). Groups are ranked by their size before the drops.
"""


def duty_plan(duties, groups):
    order = {}
    for i, d in enumerate(duties):
        order.setdefault(_key(d), i)
    open_keys = {_key(d) for d in duties if d["current"] < d["target"]}
    full = {_key(d): d for d in duties}   # the groups' duties are copies without the keys the page uses
    ranked = sorted(groups, key=lambda g: (-g["spans"], -len(g["duties"]),
                                           sorted(order.get(_key(d), len(order)) for d in g["duties"])))
    plan, grouped = [], set()
    for g in ranked:
        mine = [full[_key(d)] for d in g["duties"] if _key(d) in open_keys and _key(d) in full]
        if len(mine) < 2 or (mine[0].get("family") and len({d.get("family") for d in mine}) == 1):
            continue   # too small, or wholly one family: its duties merge into that family's entry below
        grouped.update(_key(d) for d in mine)
        spans = len({d["path"] for d in mine})
        plan.append({"tier": "cross" if spans >= 2 else "together", "label": g["label"],
                     "duties": mine, "spans": spans})
    plan.sort(key=lambda e: e["tier"] != "cross")   # stable: a group with finished duties may drop a tier
    singles, merged = [], {}
    for d in duties:
        if _key(d) not in open_keys or _key(d) in grouped:
            continue
        if d.get("row") and d.get("family"):
            if d["family"] in merged:
                merged[d["family"]]["duties"].append(d)
                continue
            merged[d["family"]] = entry = {"tier": "rows", "label": d["family"], "duties": [d], "spans": 1}
            singles.append(entry)
        else:
            singles.append({"tier": "single", "label": d["text"], "duties": [d], "spans": 1})
    for e in singles:
        if e["tier"] == "rows":
            e["spans"] = len({d["path"] for d in e["duties"]})
            e["duties"].sort(key=lambda d: d.get("rank", 2))   # most generic first; ties keep the list order
    return plan + singles


def _key(d):
    return d["path"], d["text"], d["weekly"]
