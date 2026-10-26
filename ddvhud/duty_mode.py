"""Duty mode's Action list: duty_actions(duties, groups) -> actions.

Input: as duty_plan's, every open duty (with the page's helper keys: zones, spot, food, grows) and
shared_actions.do_together's groups over them.

Output: [{size, label, duties}], one per Action. A group is an Action whose duties are the full input
dicts; a duty in no group is a Single, its label its own text.
"""


def duty_actions(duties, groups):
    order = {_key(d): i for i, d in reversed(list(enumerate(duties)))}
    full = {_key(d): d for d in duties}
    actions, grouped = [], set()
    for g in groups:
        mine = [full[_key(d)] for d in g["duties"]]
        grouped.update(_key(d) for d in mine)
        actions.append({"size": _size(len(mine)), "label": g["label"], "duties": mine})
    actions.sort(key=lambda a: (-len({d["path"] for d in a["duties"]}), -len(a["duties"]),
                                sorted(order[_key(d)] for d in a["duties"])))
    for d in duties:
        if _key(d) not in grouped:
            actions.append({"size": "Single", "label": d["text"], "duties": [d]})
    return actions


def _size(n):
    return {1: "Single", 2: "Double", 3: "Triple"}.get(n, "Quad")


def _key(d):
    return d["path"], d["text"], d["weekly"]
