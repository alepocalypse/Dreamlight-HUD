"""Roster: the save's characters + the saved daily reset -> counts, in-village Villager rows,
the Villagers who are not in the valley, and which of them are To-do."""
import re
from datetime import datetime, timezone

from .catalog import item_name, villager_name, villager_wiki_url
from .villagers import VILLAGERS

MAX_LEVEL = 10


def _parse_time(text):
    """ISO time such as 2026-10-19T05:00:00Z (fraction may be 9 digits) -> aware datetime, or None."""
    if not isinstance(text, str):
        return None
    try:
        return datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", text)).astimezone(timezone.utc)
    except ValueError:
        return None


def _distinct(labelled):
    """[(name, variant)] -> names, with the variant appended only where two names on one card collide."""
    counts = {}
    for name, _ in labelled:
        counts[name] = counts.get(name, 0) + 1
    return [f"{name} ({variant})" if counts[name] > 1 else name for name, variant in labelled]


def _wanted_gifts(c, reset):
    """The gifts still wanted, in slot order, as (item id, name). A slot counts as given only if
    it is flagged Gifted and recorded on or after the saved daily reset."""
    given_today = True
    if reset:
        gifted_at = _parse_time(c["last_gift"])
        given_today = gifted_at is not None and gifted_at >= reset
    wanted = [item for item, gifted in c["gift_slots"] if not (given_today and gifted)]
    names = _distinct([(item_name(i), f"#{i}") for i in wanted])
    return list(zip(wanted, names))


class Roster:
    """Built once from a SaveView (its characters and daily_reset) and `names` ({id: name} of the known Villagers). The game does not advance LastDailyReset when the day rolls,
    so the saved per-day flags are trusted as they are, whatever the clock says.

    Counts: village, realm, unavailable (Secret Villagers), unidentified (ids not on the roster,
    which are in no list), max_level (over Villagers in village, realm or unavailable).
    `villagers`: one row per in-village Villager, in save order: id, name, status, level,
    profession, talk_needed, gifts [(item id, name)] still wanted.
    `not_in_village`: name, where ("realm" | "unavailable"), wiki_url, in save order.
    `todo`: the villagers rows below Max level with Daily talk or any Favorite gift outstanding,
    in save order; `todo_by_priority()` is the same rows, highest level first, then by name.
    """

    def __init__(self, save, names=VILLAGERS):
        reset = _parse_time(save.daily_reset)
        self.village = self.realm = self.unavailable = self.unidentified = self.max_level = 0
        self.villagers = []
        self.not_in_village = []
        for c in save.characters:
            cid = c["id"]
            status = c["status"]
            level = c["level"]
            if status == "Secret":
                if cid in names:
                    self.unavailable += 1
                else:
                    self.unidentified += 1
                    continue
            elif status == "InVillage":
                self.village += 1
            elif status == "InRealm":
                self.realm += 1
            else:
                continue
            if level >= MAX_LEVEL:
                self.max_level += 1
            if status != "InVillage":
                # not living in the valley: only a name and a wiki link, nothing else
                self.not_in_village.append({"name": villager_name(cid, names), "where": "unavailable" if status == "Secret" else "realm",
                                            "wiki_url": villager_wiki_url(cid, names)})
                continue
            self.villagers.append({"id": cid, "name": villager_name(cid, names), "status": status, "level": level,
                                   "profession": c["profession"],
                                   "talk_needed": not c["talked_today"],
                                   "gifts": _wanted_gifts(c, reset)})

    @property
    def available(self):
        return self.village + self.realm

    @property
    def todo(self):
        # a Villager leaves the To-do once today's talk and all three gifts are done
        return [v for v in self.villagers if v["level"] < MAX_LEVEL and (v["talk_needed"] or v["gifts"])]

    def todo_by_priority(self):
        return sorted(self.todo, key=lambda v: (v["status"] != "InVillage", -v["level"], v["name"]))
