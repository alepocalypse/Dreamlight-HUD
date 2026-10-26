"""The seasonal Event duty lists (Trick-or-Treat Event, ...): event_lists(achievements, now).

An Event's duties live in the save as achievements (SaveView.achievements) and their text and milestones
in event_duty_data (from the game's data). Which Event is on, and until when, the game learns from its
servers and never writes to the save, so the window of each Event is kept by hand in EVENTS (ADR-0002).
"""
import re

from .event_duty_data import EVENT_DUTIES
from .roster import _parse_time

# Event key (the duties' internal-name prefix) -> its in-game title and the window of its current run.
# ASSUMPTION: Trick-or-Treat 2026 runs from October 14 ("From October 14 until October 31", the game's own inbox
# message) and ends at 14:00 UTC like the Star Paths do ("Ends in: 5 Day(s)" on 2026-10-26 fits that).
EVENTS = {
    "Halloween": {"title": "Trick-or-Treat Event", "starts": "2026-10-14T14:00:00Z", "ends": "2026-10-31T14:00:00Z"},
}


def event_lists(achievements, now):
    """[{key, title, ends, duties}] for each Event in EVENTS whose window holds `now` and whose duties the save
    knows, in EVENTS order. duties: [{id, text (the title), hint (what it asks), current, target, done, reward}]
    in id order, one per Event duty the save holds with a milestone still unclaimed: target is the first
    milestone above the claimed one (a lone X in the hint becomes it: "Perform X ... actions"), done whether
    current reaches it, reward {amount, currency (the item's name)} that milestone's item. A duty whose
    milestones are all claimed is left out."""
    out = []
    for key, event in EVENTS.items():
        starts, ends = _parse_time(event["starts"]), _parse_time(event["ends"])
        if starts is None or ends is None or not starts <= now < ends:
            continue
        duties = []
        for duty_id in sorted(EVENT_DUTIES):
            event_key, title, hint, milestones = EVENT_DUTIES[duty_id]
            state = achievements.get(duty_id)
            if event_key != key or state is None:
                continue
            left = [(count, item) for count, item in milestones if count > state["claimed"]]
            if not left:
                continue
            target, item = left[0]
            hint = re.sub(r"\bX\b", str(target), hint)
            duties.append({"id": duty_id, "text": title, "hint": hint, "current": state["current"], "target": target,
                           "done": state["current"] >= target, "reward": {"amount": 1, "currency": item}})
        if duties:
            out.append({"key": key, "title": event["title"], "ends": event["ends"], "duties": duties})
    return out
