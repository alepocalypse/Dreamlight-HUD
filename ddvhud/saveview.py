"""Save view: the decoded profile -> what the player holds and where, who the characters are and when
the daily reset was saved. All reading of raw save keys and the rules for missing or odd data live
here, so callers get plain dicts and lists."""

import re
from datetime import datetime, timezone

from .cookbook_data import RECIPE_MEALS


def _totals(profile, wanted):
    """{item id: total amount} over the player's containers that `wanted(container)` accepts.
    ContainerInventories may be a dict or a list. Empty slots (ItemID 0 or missing, Amount missing,
    not an int or not above 0) and malformed entries are skipped."""
    containers = (profile.get("Player") or {}).get("ContainerInventories") or {}
    if isinstance(containers, dict):
        containers = containers.values()
    totals = {}
    for cont in containers:
        if not isinstance(cont, dict) or not wanted(cont):
            continue
        for slot in cont.get("Inventory") or []:
            item = slot.get("ItemID") if isinstance(slot, dict) else None
            amount = slot.get("Amount") if item else None
            if item and isinstance(amount, int) and amount > 0:
                totals[item] = totals.get(item, 0) + amount
    return totals


class Inventory:
    """Item totals, each computed once. Treat the dicts as read-only.
    backpack: container ID 0 (not the 48-slot storage, ID 1, and not a Chest).
    chests: placed Chests: the player's containers that have a ParentItemID (the backpack and the
        48-slot storage have none; other furniture has BelongsToPlayer false).
    owned: every container with BelongsToPlayer (backpack, 48-slot storage, Chests, ...)."""

    def __init__(self, profile):
        self.backpack = _totals(profile, lambda c: c.get("ID") == 0)
        self.chests = _totals(profile, lambda c: c.get("BelongsToPlayer") and c.get("ParentItemID"))
        self.owned = _totals(profile, lambda c: c.get("BelongsToPlayer"))


_WILD_PLOT = 20200007   # the patch a wild crop (herb, mushroom) grows in; the player's own garden plots are other items


def _when(text):
    """A save timestamp ('2026-10-22T06:39:44.4759192Z', up to 9 fraction digits) as an aware datetime, None if it is not one."""
    m = re.fullmatch(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?Z", text) if isinstance(text, str) else None
    if not m:
        return None
    return datetime.fromisoformat(m[1]).replace(microsecond=int((m[2] or "0")[:6].ljust(6, "0")), tzinfo=timezone.utc)


# PendingFishes' VillageArea names -> the first area key (see World.special_rocks): the Valley's eight areas by name,
# Eternity Isle's by name and number (AtlanteanOutpost01 is key 8, Desert01 12, Jungle01 16).
_RIPPLE_AREAS = {"Beach": 0, "Wetland": 1, "Meadow": 2, "Urban": 3, "Savannah": 4, "Forest": 5, "DarkMountains": 6,
                 "Cliff": 7, "AtlanteanOutpost": 8, "Desert": 12, "Jungle": 16}


class World:
    """What lies in the world.
    loose(item): how many objects with that ItemID lie loose in the world's grids (0 when none or no data).
    time_nodes: {village area: Time-bending nodes still to mine there}, the area name without its
        "VillageAreaType_" prefix. One TimeLostTreasures entry per node; entries without a
        Location.VillageArea are skipped. Treat the dict as read-only.
    special_rocks: {village area key: MiningData item id} for each area whose Special mining rock (the one
        that yields a named gem) is still there: present and not yet hit NumberOfHitsNeeded times. The area
        keys are the ints of Villages[].Areas (0-7 the Valley, 8-19 Eternity Isle).
    items_by_area: {village area key: {item id: count}} for the objects lying in that area's grids
        (Areas[].GridIDs), dry flowers left out.
    wild_crops: {village area key: {wild seed item id: [datetime each patch is ready at]}} for the wild plots
        (herbs, mushrooms) in that area's grids that hold a seed with a harvest left; a patch is ripe once its
        datetime has passed.
    ripples: {village area key: {ripple rarity: count}} for the fish ripples now on the water
        (PendingFishes), the rarity without its "FishRippleRarity_" prefix. Treat the dicts as read-only."""

    def __init__(self, profile):
        world = profile.get("World") or {}
        grids = (world.get("GridCollection") or {}).get("Grids") or {}
        if isinstance(grids, dict):
            grids = grids.values()
        self._loose = {}
        for grid in grids:
            objects = grid.get("Objects") or {} if isinstance(grid, dict) else {}
            if isinstance(objects, dict):
                objects = objects.values()
            for o in objects:
                item = o.get("ItemID") if isinstance(o, dict) else None
                if item:
                    self._loose[item] = self._loose.get(item, 0) + 1
        treasures = world.get("TimeLostTreasures") or {}
        if isinstance(treasures, dict):
            treasures = treasures.values()
        self.time_nodes = {}
        for t in treasures:
            area = ((t or {}).get("Location") or {}).get("VillageArea") if isinstance(t, dict) else None
            if area and isinstance(area, str):
                area = area.removeprefix("VillageAreaType_")
                self.time_nodes[area] = self.time_nodes.get(area, 0) + 1

        self.special_rocks, self.items_by_area, self.ripples, self.wild_crops = {}, {}, {}, {}
        by_id = {g.get("ID"): g for g in grids if isinstance(g, dict)}
        for village in world.get("Villages") or []:
            areas = village.get("Areas") if isinstance(village, dict) else None
            for key, area in (areas.items() if isinstance(areas, dict) else []):
                if not (isinstance(area, dict) and str(key).isdigit()):
                    continue
                for rock in area.get("MiningRocks") or []:
                    sp = rock.get("Special") if isinstance(rock, dict) else None
                    if isinstance(sp, dict) and sp.get("MiningDataItemID") and \
                            sp.get("NumberOfHits", 0) < sp.get("NumberOfHitsNeeded", 1):
                        self.special_rocks[int(key)] = sp["MiningDataItemID"]
                for gid in area.get("GridIDs") or []:
                    objects = (by_id.get(gid) or {}).get("Objects") or {}
                    for o in objects.values() if isinstance(objects, dict) else objects:
                        item = o.get("ItemID") if isinstance(o, dict) else None
                        if item == _WILD_PLOT:
                            self._add_wild(int(key), o)
                        dry = ((o.get("State") or {}).get("FlowerData") or {}).get("Dry") if isinstance(o, dict) else None
                        if item and not dry:
                            counts = self.items_by_area.setdefault(int(key), {})
                            counts[item] = counts.get(item, 0) + 1
        pending = world.get("PendingFishes") or {}
        for f in pending.values() if isinstance(pending, dict) else pending:
            loc = ((f.get("Location") or {}).get("VillageArea") or "") if isinstance(f, dict) else ""
            m = re.fullmatch(r"VillageAreaType_(\D+?)(\d*)", loc if isinstance(loc, str) else "")
            rarity = (f.get("Rarity") or "").removeprefix("FishRippleRarity_") if isinstance(f, dict) else ""
            base = _RIPPLE_AREAS.get(m.group(1)) if m else None
            if base is not None and rarity and (m.group(2) or base < 8):
                key = base + (int(m.group(2)) - 1 if m.group(2) else 0)
                self.ripples.setdefault(key, {})
                self.ripples[key][rarity] = self.ripples[key].get(rarity, 0) + 1

    def _add_wild(self, area, plot):
        for slot in ((plot.get("State") or {}).get("GardenData") or {}).get("Slots") or []:
            harvest = slot.get("Harvest") if isinstance(slot, dict) else None
            seed = slot.get("PlantedSeedItemID") if isinstance(slot, dict) else None
            ready = _when((harvest or {}).get("EndOfGrowth"))
            if seed and ready and (harvest.get("NumberOfProductionLeft") or 0) > 0:
                self.wild_crops.setdefault(area, {}).setdefault(seed, []).append(ready)

    def loose(self, item):
        return self._loose.get(item, 0)


class Companions:
    """What the save says about Companions and Critters (no names, Jobs or goals: those are game data).
    unlocked: {Companion item ID: Companion level}; level 1 when FriendshipLevel is missing.
    equipped: set of Companion item IDs currently assigned (Player.AssignedPets).
    critters: {Critter item ID: feedings done}; 0 when NumberOfFeedingDone is missing. Critters stay
        listed after they unlock their Companion. Entries that are not dicts or lack the ID are skipped.
    Treat the containers as read-only."""

    def __init__(self, profile):
        player = profile.get("Player") or {}
        self.unlocked = {p["PetItemID"]: p.get("FriendshipLevel", 1)
                         for p in player.get("Pets") or [] if isinstance(p, dict) and "PetItemID" in p}
        self.equipped = set(player.get("AssignedPets") or [])
        self.critters = {c["CritterItemID"]: c.get("NumberOfFeedingDone", 0)
                         for c in (profile.get("World") or {}).get("Critters") or []
                         if isinstance(c, dict) and "CritterItemID" in c}


def _characters(profile):
    """World.Characters as plain facts, in save order: id, status (without its "CharacterStatus_" prefix,
    "" when missing), level (FriendshipLevel, 0), profession (ProfessionID, 0), talked_today, last_gift
    (the LastGiftDate text or None), gift_slots [(item id, gifted)] in slot order. Entries that are not
    dicts or lack Base.id, and slots that are not dicts, are skipped."""
    entries = (profile.get("World") or {}).get("Characters") or []
    return [{"id": c["Base"]["id"],
             "status": (c.get("Status") or "").removeprefix("CharacterStatus_"),
             "level": c.get("FriendshipLevel", 0),
             "profession": c.get("ProfessionID", 0),
             "talked_today": bool(c.get("DiscussedWithTheAvatarToday")),
             "last_gift": c.get("LastGiftDate"),
             "gift_slots": [(s.get("PreferredItemId"), bool(s.get("Gifted")))
                            for s in c.get("PreferredItemSlots") or [] if isinstance(s, dict)]}
            for c in entries if isinstance(c, dict) and isinstance(c.get("Base"), dict) and c["Base"].get("id")]


def _dict(value):
    return value if isinstance(value, dict) else {}


def _str(value):
    return value if isinstance(value, str) else ""


def _star_paths(profile):
    """Star Paths, each built from its entry in Player.BattlePassStates.Progress."""
    progress = _dict(_dict(_dict(profile.get("Player")).get("BattlePassStates")).get("Progress"))
    weeks = lambda entry: entry.get("WeeklyTasksProgress") if isinstance(entry.get("WeeklyTasksProgress"), list) else []
    return [{"id": sid, "tokens": entry.get("CurrencyAmount", 0), "end_date": entry.get("EndDate"),
             "duties": _duties(entry.get("TasksProgress")), "weekly": [_duties(_dict(w).get("TasksProgress"))
                        for w in weeks(entry)]}
            for sid, entry in progress.items() if isinstance(entry, dict)]


def _plain(value):
    """A nested filter's payload as plain values: the UseField/Random/ShowRandomCheckbox switches are
    dropped, single-key wrappers are unwrapped and "Enum_Name" strings become "Name"."""
    if isinstance(value, dict):
        rest = {k: v for k, v in value.items() if k not in ("UseField", "Random", "ShowRandomCheckbox")}
        return _plain(next(iter(rest.values()))) if len(rest) == 1 else {k: _plain(v) for k, v in rest.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value.split("_", 1)[-1] if isinstance(value, str) else value


def _filter(objective):
    """The meaningful (non-default) fields of a duty's requirement filter (Objective.ItemFilter.Data):
    item, item_list, kind, type (prefixes dropped), tags (tags_any true when one tag is enough, not
    all), any (AnyActivityItem), min_meal_stars, ingredient_tags, roughness, and every nested filter that is switched on
    (UseField true) under its snake_case name with its payload reduced by _plain (fish_location:
    ["Beach"]). {} when there is no Data."""
    item_filter = objective.get("ItemFilter")
    data = item_filter.get("Data") if isinstance(item_filter, dict) else None
    if not isinstance(data, dict):
        return {}
    facts = {}
    if data.get("Item"):
        facts["item"] = data["Item"]
    if data.get("ItemList"):
        facts["item_list"] = data["ItemList"]
    kind = _str(data.get("ActivityItemType")).removeprefix("ActivityItemType_")
    if kind and kind != "Default":
        facts["kind"] = kind
    if _str(data.get("Type")):
        facts["type"] = data["Type"].removeprefix("ItemType_")
    if data.get("Tags"):
        facts["tags"] = data["Tags"]
    if data.get("TagCondition") == "TagFilterCondition_AtLeastOneTag":
        facts["tags_any"] = True
    if data.get("AnyActivityItem"):
        facts["any"] = True
    if data.get("MinMealStarRating"):
        facts["min_meal_stars"] = data["MinMealStarRating"]
    if data.get("IngredientsType"):
        facts["ingredient_tags"] = data["IngredientsType"]
    if _str(data.get("MineralRoughness")) not in ("", "MineralRoughness_Any"):
        facts["roughness"] = data["MineralRoughness"].removeprefix("MineralRoughness_")
    for key, nested in data.items():
        if isinstance(nested, dict) and nested.get("UseField") is True:
            facts[re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()] = _plain(nested)
    return facts


def _duties(tasks):
    """Duties in order; position counts every slot, so a skipped (non-dict) one leaves a gap."""
    duties = []
    for i, t in enumerate(tasks if isinstance(tasks, list) else [], 1):
        if not isinstance(t, dict):
            continue
        objective = t.get("Objective") if isinstance(t.get("Objective"), dict) else {}
        duties.append({"position": i, "state": _str(t.get("TaskState")).removeprefix("BattlePassTaskState_"),
                       "current": objective.get("CurAmount", 0), "target": objective.get("TargetAmount", 0),
                       "filter": _filter(objective)})
    return duties


def _duty_slots(profile):
    """The rotating Dreamlight Duties and Mist Duties: one entry per village set in Player.DutySlots."""
    sets = ((profile.get("Player") or {}).get("DutySlots")) or {}
    out = []
    for key, entry in sets.items() if isinstance(sets, dict) else []:
        slots = entry.get("Slots") if isinstance(entry, dict) else None
        duties = []
        for i, sl in enumerate(slots if isinstance(slots, list) else [], 1):
            if not isinstance(sl, dict) or not sl.get("DutyId"):
                continue
            step = sl.get("StepData") if isinstance(sl.get("StepData"), dict) else {}
            duties.append({"position": i, "duty_id": sl["DutyId"],
                           "state": (sl.get("State") or "").removeprefix("DutySlotState_"),
                           "current": step.get("curAmount", 0), "target": step.get("TargetAmount", 0),
                           "filter": _filter(step)})
        if duties:
            out.append({"key": str(key), "duties": duties})
    return out


def _known_meals(profile):
    """Meal item ids whose recipe is in the player's cookbook (Player.Cookbook.Recipes), None when the
    save has no cookbook, so a meal is not called unknown on missing data."""
    recipes = ((profile.get("Player") or {}).get("Cookbook") or {}).get("Recipes")
    if not isinstance(recipes, list):
        return None
    return {RECIPE_MEALS[r] for r in recipes if r in RECIPE_MEALS}


class SaveView:
    """Read-only view over a decoded profile dict.
    star_paths: [{id, tokens, end_date, duties, weekly}] in save order, one per entry of
        Player.BattlePassStates.Progress (the tutorial pass FtueProgress is not one). tokens is
        CurrencyAmount (0), end_date the EndDate text (None). duties: [{position, state, current,
        target, filter}] in duty order: position counts from 1, state is the task state without its
        "BattlePassTaskState_" prefix (NotStarted, OnGoing, Completed, CurrencyClaimed; "" when
        missing), current/target the amounts (0), filter the requirement from _filter ({} when the
        duty has none). weekly: one list of such duties per week, in week order (position counts
        within the week).
    known_meals: set of meal item ids the player has discovered the recipe for, None without a cookbook.
    duty_slots: [{key, duties}] one per village set of the rotating Dreamlight Duties (Valley) and Mist
        Duties (Eternity Isle) in Player.DutySlots, key the village's scene item id as text; duties:
        [{position, duty_id, state (OnGoing, Completed, ...), current, target, filter}] in slot order,
        position counting from 1. Treat the lists and dicts as read-only."""

    def __init__(self, profile):
        self.inventory = Inventory(profile)
        self.known_meals = _known_meals(profile)
        self.world = World(profile)
        self.companions = Companions(profile)
        self.characters = _characters(profile)
        self.star_paths = _star_paths(profile)
        self.duty_slots = _duty_slots(profile)
        self.daily_reset = profile.get("LastDailyReset")
