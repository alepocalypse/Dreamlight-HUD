"""Report builder: decoded profile dict + current time -> plain HUD data."""
import math

from . import catalog, duty_mode, duty_plan, duty_requirements, duty_text, shared_actions, slot_duties, stock_zones
from .companions import COMPANIONS, JOBS  # COMPANIONS: tests patch the table in place through this name
from .ingredients import CATEGORIES
from .recipes import RECIPES
from .roster import MAX_LEVEL, Roster, _distinct, _parse_time
from .saveview import SaveView
from .spawns import spawn_for
from .villagers import PROFESSIONS, VILLAGERS

GARDENING_ID = 1500000001


def _bonus(pid, levels):
    """Bonus-resource chance of one Profession card, or None for no Villagers / an unknown Profession.

    Source: dreamlightvalleywiki.com, the Roles and Bonuses pages ('Villager Companion Role Benefits'),
    read 2026-10-20; the wiki itself marks some high tiers as needing confirmation.
    chance = base + 3.5 * level_of_active + sum(level of every other Villager with that Profession)
    base = 20 for Gardening, 25 for the others; levels 0..10; no cap at 100.
    ASSUMPTION: the Villager the player hangs out with (the active one) is the highest-level one (best case).
    `levels` holds ALL in-village Villagers with this Profession, including those at Max level.
    """
    if not levels or pid not in PROFESSIONS:
        return None
    base = 20 if pid == GARDENING_ID else 25
    active = max(levels)
    chance = base + 3.5 * active + (sum(levels) - active)
    if chance >= 200:
        tier = "more than 1 guaranteed bonus item (wiki table)"
    elif chance > 100:
        tier = "guaranteed 1 bonus item, chance of more"
    elif chance == 100:
        tier = "1 bonus item"
    else:
        tier = None
    return {"chance": float(chance), "base": base, "active_level": active,
            "tier": tier}


def _profession_cards(villagers):
    groups = {pid: [] for pid in PROFESSIONS}
    for v in villagers:
        if v["profession"]:
            # every unrecognised ID shares one card, keyed None
            groups.setdefault(v["profession"] if v["profession"] in PROFESSIONS else None, []).append(v)
    cards = []
    for pid, members in sorted(groups.items(), key=lambda g: (g[0] is None, PROFESSIONS.get(g[0], ""))):
        # below Max level: lowest first (then name); at Max level: just the names, for one "done" line
        below = sorted((v for v in members if v["level"] < MAX_LEVEL), key=lambda v: (v["level"], v["name"]))
        done = sorted(v["name"] for v in members if v["level"] >= MAX_LEVEL)
        cards.append({
            "name": catalog.profession_name(pid),
            "count": len(members),
            "not_max": len(below),
            "villagers": [{"name": v["name"], "level": v["level"]} for v in below],
            "done": done,
            "bonus": _bonus(pid, [v["level"] for v in members]),
        })
    return cards


def _no_profession(villagers):
    """Villagers living in the valley with no Profession: lowest level first, those at Max level last."""
    rows = sorted((v for v in villagers if not v["profession"]), key=lambda v: (v["level"] >= MAX_LEVEL, v["level"], v["name"]))
    return [{"name": v["name"], "level": v["level"]} for v in rows]


def _todo_list(roster, chests, backpack):
    rows = roster.todo_by_priority()
    wanted = {}   # item id -> how many of these Villagers want it
    for v in rows:
        for i in {i for i, _ in v["gifts"]}:
            wanted[i] = wanted.get(i, 0) + 1
    return [{"id": v["id"], "name": v["name"],
             "profession": catalog.profession_name(v["profession"]) if v["profession"] else None,
             "level": v["level"],
             "daily_talk_needed": v["talk_needed"], "gifts": [{"name": name, "in_chest": chests.get(i, 0) > 0, "chest_count": chests.get(i, 0),
                                   "backpack_count": backpack.get(i, 0),
                                   "wanted": wanted[i],
                                   "wiki_url": catalog.item_wiki_url(i),
                                   "spawn": None if backpack.get(i, 0) else spawn_for(i)}
                        for i, name in v["gifts"]],
             "location": "valley"} for v in rows]


def _ingredients(recipe, have):
    """A recipe string -> [{name, have, where}] in recipe order. `have` is True or False, None when the
    ingredient has no item id here so the save cannot say. `where` is the wiki's tag for getting it,
    empty when it is in stock. A category ("Vegetables") is met by any one item of that category, and
    every slot takes its own unit, so two slots need two units. Named ingredients are taken first so a
    category slot cannot eat the stock a later named one needs."""
    left = dict(have)
    rows = [{"name": n.strip(), "have": None, "where": ""} for n in recipe.split(",") if n.strip()]
    for row in sorted(rows, key=lambda r: r["name"] in CATEGORIES):
        n = row["name"]
        if n in CATEGORIES:
            members = catalog.category_item_ids(n)
            item, row["where"] = max(members, key=lambda i: left.get(i, 0), default=None), "any"
        else:
            item, row["where"] = catalog.item_id(n), catalog.ingredient_where(n)
        if item is None:
            continue
        row["have"] = left.get(item, 0) > 0
        if row["have"]:
            left[item] -= 1
            row["where"] = ""
    return rows


def _ready(ingredients):
    """True: all in stock. False: one is missing. None: no recipe, or one that cannot be checked."""
    states = [x["have"] for x in ingredients]
    if False in states:
        return False
    return None if not states or None in states else True


def _cook_list(roster, held, known):
    """The "Cook" card: meals wanted as gifts (block 303) that the player holds none of (`held`), each once with
    its recipe ('' when the wiki lists none), the recipe's `ingredients` checked against `held` (everything
    the player owns: backpack, storage, chests), `ready`, `known` (recipe discovered: True or False, None
    when the save has no cookbook) and who wants it. Same villagers as the to-do cards."""
    meals = {}
    for v in roster.todo:
        for i, name in v["gifts"]:
            if 30300000 <= i < 30400000 and not held.get(i, 0):
                meals.setdefault(i, {"name": name, "recipe": RECIPES.get(name, ""), "for": []})["for"].append(v["name"])
    for i, m in meals.items():
        m["known"] = None if known is None else i in known
        m["ingredients"] = _ingredients(m["recipe"], held)
        m["ready"] = _ready(m["ingredients"])
    return sorted(meals.values(), key=lambda m: m["name"])


FARM_TARGET = 25  # stock wanted of every ingredient the Cook card's recipes use


def _farm_list(cook, held, known):
    """The "Gather" card: [{name, have, need, how, where}] for named ingredients held fewer than FARM_TARGET
    of (backpack, storage, chests), the emptiest first. `how` and `where` split the wiki's tag ('Farm, Valor'
    -> 'Farm', 'Valor'). Grown ingredients (tag Farm: they take time) count for every recipe the player
    knows (every recipe when `known` is None, no cookbook) as well as the Cook card's; all others (fish,
    forage, bought) only for the Cook card's recipes. Category slots ("Vegetables") are skipped, as are
    names with no item id (the save cannot count them)."""
    wanted = {x["name"] for meal in cook for x in meal["ingredients"]}
    for meal, recipe in RECIPES.items():
        if known is None or catalog.item_id(meal) in known:
            wanted.update(n.strip() for n in recipe.split(",") if catalog.ingredient_where(n.strip()).startswith("Farm"))
    rows = []
    for name in wanted:
        item = catalog.item_id(name)
        if name in CATEGORIES or item is None or held.get(item, 0) >= FARM_TARGET:
            continue
        how, _, where = catalog.ingredient_where(name).partition(", ")
        rows.append({"name": name, "have": held.get(item, 0), "need": FARM_TARGET, "how": how, "where": where,
                     "wiki_url": catalog.item_wiki_url(item)})
    return sorted(rows, key=lambda r: (r["have"], r["name"]))


DARK_WOOD, GOLD_INGOT, GOLD_NUGGET, COAL_ORE =31700002, 31700007, 31700018, 31700017
CHESTS_WANTED = 5
SHOW_MIN_WOOD = 6  # fewer loose Dark Wood than this: no card, wood is the choke point
TRIP_WORTH = 7  # this many loose items in the world is worth a trip: the line gets its green check


def _gather_for_chests(save):
    """The "Gather For Chests" card, or None once the player holds enough for CHESTS_WANTED Large Chests,
    or while fewer than SHOW_MIN_WOOD Dark Wood lie loose in the world (the choke point: not worth a trip).
    Only the materials still short get a line.

    Recipe (dreamlightvalleywiki.com Large Chest and guides, read 2026-10-21): 25 Dark Wood + 5 Gold Ingot
    (+ 5,000 Dreamlight, ignored). Gold Ingot = 5 Gold Nugget + 1 Coal Ore (one guide; unconfirmed).
    The card lists raw materials, crediting Gold Ingots already held as their nuggets and coal.
    Held = every container of the player (backpack, 48-slot storage, chests).
    A line's `spawned` is the loose world count (None: the save cannot tell), `ok` whether it covers
    the shortfall or at least TRIP_WORTH of it (None when `spawned` is None or nothing is short)."""
    have = save.inventory.owned
    wood, ingots = have.get(DARK_WOOD, 0), have.get(GOLD_INGOT, 0)
    nuggets, coal = have.get(GOLD_NUGGET, 0), have.get(COAL_ORE, 0)
    craftable = min(wood // 25, (ingots + min(nuggets // 5, coal)) // 5)
    if craftable >= CHESTS_WANTED:
        return None
    ingot_credit = min(ingots, 5 * CHESTS_WANTED)
    ingots_to_make = 5 * CHESTS_WANTED - ingot_credit
    spawned = {DARK_WOOD: save.world.loose(DARK_WOOD)}  # loose pickups only: mined and dug materials are not in the save
    if spawned[DARK_WOOD] < SHOW_MIN_WOOD:
        return None
    lines = []
    for item, need in ((DARK_WOOD, 25 * CHESTS_WANTED), (GOLD_NUGGET, 5 * ingots_to_make), (COAL_ORE, ingots_to_make)):
        held = have.get(item, 0)
        short = max(0, need - held)
        if not short:
            continue
        world = spawned.get(item)
        lines.append({"name": catalog.item_name(item), "have": held, "need": need, "short": short,
                      "spawned": world,
                      "ok": None if world is None or not short else world >= min(short, TRIP_WORTH),
                      "wiki_url": catalog.item_wiki_url(item)})
    # push toward what is short AND can be found in the world, then what the save cannot tell, then the rest
    rank = {True: 0, None: 1, False: 2}
    lines.sort(key=lambda l: (rank[l["ok"]], -l["short"] / l["need"] if l["need"] else 0))
    return {"chests": CHESTS_WANTED, "craftable": craftable, "lines": lines}


# Time-bending nodes: `World.TimeLostTreasures` holds one entry per node still to mine (mining removes it).
# Zone = a set of village areas; a zone is full when it holds its cap per area (observed in the real save:
# every Valley area 3, every Eternity Isle area 2; the Docks is AtlanteanOutpost01).
TIME_ZONES = (("Valley", 8, 3, ("Beach", "Wetland", "Meadow", "Urban", "Savannah", "Forest", "DarkMountains", "Cliff")),
              ("Eternity Isle", 12, 2, ("AtlanteanOutpost", "Desert", "Jungle")))


def _time_bending(save):
    """A card per zone that still has a node: [{zone, nodes, total, areas, full}]; `full` when every node is back."""
    counts = save.world.time_nodes
    cards = []
    for zone, areas, cap, prefixes in TIME_ZONES:
        nodes = sum(n for a, n in counts.items() if a.startswith(prefixes))
        if nodes:
            cards.append({"zone": zone, "nodes": nodes, "total": areas * cap, "areas": areas,
                          "full": nodes == areas * cap})
    return cards


def _companions(save):
    """Companions by Job: the goal is two per Job, each at Companion level 5."""
    equipped = save.companions.equipped
    unlocked = save.companions.unlocked
    by_job = {j: [] for j in JOBS}
    no_job = []
    for pid, level in sorted(unlocked.items(), key=lambda kv: (-kv[1], catalog.companion(kv[0]).name)):
        comp = catalog.companion(pid)
        row = {"id": pid, "name": comp.name, "level": level, "equipped": pid in equipped}
        by_job.get(comp.job, no_job).append(row)
    critters = {j: [] for j in JOBS}
    no_job_critters = []
    for cid, done_fed in save.companions.critters.items():
        crit = catalog.critter(cid)
        row = {"name": crit.name, "companion": catalog.companion(crit.companion).name if crit.companion else None,
               "fed": done_fed, "needed": crit.needed}
        if (crit.needed is not None and done_fed >= crit.needed) or crit.companion in unlocked:
            continue
        critters.get(catalog.companion(crit.companion).job, no_job_critters).append(row)
    for row in no_job:
        del row["id"]
    jobs = []
    for j in JOBS:
        have = by_job[j]
        for row, label in zip(have, _distinct([(r["name"], f"#{r['id']}") for r in have])):
            row["name"] = label
            del row["id"]
        at_max = sum(r["level"] >= 5 for r in have)
        jobs.append({"job": j, "goal": 2, "unlocked": have, "unlocked_count": len(have),
                     "at_max_count": at_max, "complete": at_max >= 2, "critters": critters[j]})
    return {"jobs": jobs, "no_job": no_job, "no_job_critters": no_job_critters}


def _days_left(ends, now):
    """Whole days until `ends` (a part day counts as a day, 0 once over), or None without a readable date."""
    end = _parse_time(ends)
    return None if end is None else max(0, math.ceil((end - now).total_seconds() / 86400))


def _event_duties(save, now):
    """(star_paths, shared, plan, actions). star_paths: one entry per Star Path, then one per rotating duty set (Dreamlight Duties, Mist Duties: tokens and ends None, no weekly): [{id, title, currency, tokens, ends, days_left, duties, weekly}]. duties: the OnGoing and
    Completed-but-unclaimed duties as {text, current, target, done, requires}, requires (see
    duty_requirements.Requirement.to_json) only for the duties it could classify; weekly: [{week (from 1), duties}] for every
    week that has any such duty. NotStarted and CurrencyClaimed duties are left out. The save's positions count
    from 1, the text table's from 0. shared: the 'do together' groups across them (shared_actions.do_together,
    open duties only), each duty as {path (the Star Path title), text, current, target, weekly (week or None)}. plan: the ordered task
    list over every open duty, classified or not (duty_plan.duty_plan). actions: Duty mode's Action list over the
    same duties (duty_mode.duty_actions); a rotating duty there carries reward {amount, currency} when the game's
    table has one for its set (slot_duties.slot_reward)."""
    open_duties, all_open = [], []

    def shown(duties, text, title, week, zoned=False, reward=lambda i: None):
        out = []
        for d in duties:
            if d["state"] not in ("OnGoing", "Completed"):
                continue
            shown_text = text(d["position"] - 1)
            duty = {"text": shown_text, "current": d["current"], "target": d["target"],
                    "done": d["state"] == "Completed" or d["current"] >= d["target"]}
            req = duty_requirements.classify(shown_text, d["filter"])
            if zoned and slot_duties.names_a_zone(shown_text):
                req = duty_requirements.Requirement(duty_requirements.UNKNOWN)
            if not duty["done"]:
                entry = {"path": title, "text": shown_text, "current": d["current"],
                         "target": d["target"], "weekly": week}
                if reward(d["position"] - 1):
                    entry["reward"] = reward(d["position"] - 1)
                fam = (duty_requirements.colour_family(shown_text, req)
                       or duty_requirements.hang_out_family(shown_text, d["filter"])
                       or duty_requirements.cook_family(shown_text, d["filter"])
                       or duty_requirements.node_family(shown_text)
                       or duty_requirements.fish_family(shown_text, req, d["filter"])
                       or duty_requirements.sell_family(shown_text)
                       or duty_requirements.gift_family(shown_text)
                       or duty_requirements.currency_family(shown_text, d["filter"])
                       or duty_requirements.feed_family(shown_text)
                       or duty_requirements.craft_family(shown_text)
                       or duty_requirements.clean_family(shown_text))
                if fam:
                    entry["family"], entry["row"] = fam
                    entry["rank"] = duty_requirements.generic_rank(fam[0], fam[1], shown_text, d["filter"])
                    if fam[0] == "Feed" and duty_requirements.food_for(fam[1]):
                        entry["food"] = duty_requirements.food_for(fam[1])
                    place = duty_requirements.node_place(shown_text)
                    if place:
                        entry["place"] = place
                zones = stock_zones.duty_zones(req, d["filter"], fam[1] if fam else None, save.world, shown_text, now)
                if zones is not None:
                    entry["zones"] = zones
                spot = stock_zones.fish_spot(req)
                if spot:
                    entry["spot"] = spot
                grows = stock_zones.growth_zones(req)
                if grows:
                    entry["grows"] = grows
                all_open.append(entry)
            if req.action != duty_requirements.UNKNOWN:
                duty["requires"] = req.to_json()
                if not duty["done"]:
                    open_duties.append({"path": title, "text": shown_text, "current": d["current"],
                                        "target": d["target"], "weekly": week, "requires": req})
            out.append(duty)
        return out

    paths = []
    for sp in save.star_paths:
        sid = sp["id"]
        title = duty_text.title(sid)
        main = shown(sp["duties"], lambda i: duty_text.duty_text(sid, i), title, None)   # before weekly: shared order
        weekly = [{"week": w, "duties": shown(duties, lambda i, w=w: duty_text.weekly_duty_text(sid, w - 1, i), title, w)}
                  for w, duties in enumerate(sp["weekly"], 1)]
        paths.append({"id": sid, "title": title, "currency": duty_text.currency_name(sid),
                      "tokens": sp["tokens"], "ends": sp["end_date"],
                      "days_left": _days_left(sp["end_date"], now),
                      "duties": main,
                      "weekly": [w for w in weekly if w["duties"]]})
    for dset in save.duty_slots:   # the rotating Dreamlight Duties (Valley) and Mist Duties (Eternity Isle): listed like a Star Path
        by_pos = {d["position"]: d for d in dset["duties"]}
        title = slot_duties.slot_title(dset["key"])
        text = lambda i, by_pos=by_pos: slot_duties.slot_duty_text(by_pos[i + 1]["duty_id"], by_pos[i + 1]["target"],
                                                                   by_pos[i + 1]["filter"])
        reward = lambda i, by_pos=by_pos, key=dset["key"]: slot_duties.slot_reward(by_pos[i + 1]["duty_id"], key)
        paths.append({"id": "DutySlots" + dset["key"], "title": title, "currency": "", "tokens": None, "ends": None,
                      "days_left": None,
                      "duties": shown(dset["duties"], text, title, None, zoned=True, reward=reward), "weekly": []})
    shared = shared_actions.do_together(open_duties)
    return paths, shared, duty_plan.duty_plan(all_open, shared), duty_mode.duty_actions(all_open, shared)


def build_report(profile, now):
    save = SaveView(profile)
    roster = Roster(save, VILLAGERS)
    villagers = roster.villagers
    event_duties, shared, plan, actions = _event_duties(save, now)
    cook = _cook_list(roster, save.inventory.owned, save.known_meals)
    return {
        "summary": {
            "total": roster.available + roster.unavailable,
            "available": {"total": roster.available, "village": roster.village, "realm": roster.realm},
            "unavailable": roster.unavailable,
            "in_owned_packs": roster.in_owned_packs,
            "max_level": roster.max_level,
            "unidentified": roster.unidentified,
            "daily_reset": save.daily_reset,
        },
        "villagers": villagers,
        "professions": _profession_cards(villagers),
        "no_profession": _no_profession(villagers),
        "gather": _gather_for_chests(save),
        "time_bending": _time_bending(save),
        "cook": cook,
        "farm": _farm_list(cook, save.inventory.owned, save.known_meals),
        "todo": _todo_list(roster, save.inventory.chests, save.inventory.backpack),
        "not_in_village": roster.not_in_village,
        "requires_dlc": roster.requires_dlc,
        "companions": _companions(save),
        "event_duties": event_duties,
        "shared": shared,
        "plan": plan,
        "actions": actions,
    }
