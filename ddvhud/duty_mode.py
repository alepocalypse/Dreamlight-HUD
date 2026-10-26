"""Duty mode's Action list: duty_actions(duties, groups) -> actions.

Input: as duty_plan's, every open duty (with the page's helper keys: zones, spot, food, grows) and
shared_actions.do_together's groups over them.

Output: [{size, label, value, duties}], one per Action, ranked by value (the sum of its duties' value keys,
Dreamlight-equivalent, see duty_value), ties by Size then the order before ranking (groups, then Singles in
input order). A group is an Action whose duties are the full input dicts; a duty in no group is a Single, its
label its own text.
"""

TOKEN_VALUE = 10   # Dreamlight per Star Path token; Dreamlight, Mist and Storybook Magic at par (ADR-0001)


def duty_value(reward, per_unit=1, fallback=None):
    """A Duty's Reward in Dreamlight-equivalent: its amount (`fallback` when it has no Reward, 0 without either)
    times `per_unit` (TOKEN_VALUE for Star Path tokens)."""
    return round((reward["amount"] if reward else fallback or 0) * per_unit)   # a median can fall on a half token


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
    for a in actions:
        a["value"] = sum(d.get("value", 0) for d in a["duties"])
    actions.sort(key=lambda a: (-a["value"], -len(a["duties"])))   # stable: ties keep the order above
    return actions


def _size(n):
    return {1: "Single", 2: "Double", 3: "Triple"}.get(n, "Quad")


def _key(d):
    return d["path"], d["text"], d["weekly"]
