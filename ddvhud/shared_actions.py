"""Duties one action advances together: do_together(duties) -> groups.

Input: open duties as dicts {path, text, current, target, weekly, requires} (requires is a
duty_requirements.Requirement; path names the Star Path, weekly is the week number or None).
Coverage (Requirement.covers) is a partial order, not an equivalence, so a group is built around
one requirement R, the action to do: it holds every duty whose requirement covers R (equal ones
included), because an action that satisfies R satisfies those too. A group with a single duty is
dropped, and so is one whose duties all sit inside a bigger group (R is then not the narrowest
action). Unknown requirements equal and cover nothing, so they never join.

Real save: 'Catch any fish.', 'Catch Fish from Dazzle Beach.', weekly 'Catch 20 fish.' and 'Go
fishing for seaweed' give two groups, around Dazzle Beach fish and around seaweed, sharing the any
and weekly duties: the Dazzle Beach and seaweed duties do not cover each other (nothing proves
seaweed can be caught there), so no one action is claimed for all four. The same Scrooge McDuck
purchase in two Star Paths is one group with spans 2.

Output: [{label (R's), spans (Star Paths in the group), duties (the input dicts without requires)}],
in the order of each R's first duty in the input, duties in input order.
"""


def do_together(duties):
    candidates = []   # (requirement, duties covering it), one per distinct requirement
    for d in duties:
        if all(d["requires"] != r for r, _ in candidates):
            candidates.append((d["requires"], [x for x in duties if x["requires"].covers(d["requires"])
                                               or x["requires"] == d["requires"]]))
    sets = [{id(x) for x in ds} for _, ds in candidates]
    groups = []
    for (r, ds), mine in zip(candidates, sets):
        if len(ds) > 1 and not any(mine < other for other in sets):
            groups.append({"label": r.label, "spans": len({x["path"] for x in ds}),
                           "duties": [{k: v for k, v in x.items() if k != "requires"} for x in ds]})
    return groups
