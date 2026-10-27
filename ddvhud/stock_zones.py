"""Where a duty can be worked right now, as zone labels (an empty list means none right now).

stock_zones(action, requirement, colour, world) for a colour duty;
forage_zones(items, world): zones where those items lie, 'Zone (count)', most first;
ripple_zones(rarity, world): zones with a fish ripple of that FishRippleRarity ('Exceptional' is the gold
ripple; the game says 'blue and gold ripples' for Enhanced and Exceptional), '(count)' only above one.

'mine_gem': the areas whose Special mining rock (World.special_rocks) yields a gem the duty accepts, the
duty's item list when it has one, else the gems tagged with its colour. 'pick_flower': the areas with
undried flowers of the colour lying in them (World.items_by_area), each as 'Zone (count)', most flowers first. Anything else: None. An empty list
means none right now. Areas come in the save's area-key order, named by the wiki's zones.
"""
import re

from .fish_pools import FISH_POOLS
from .spawns import GROUPS, SPAWNS, spawn_for
from .stock_data import FLOWER_COLOURS, GEM_COLOURS, SPECIAL_GEMS, WILD_CROPS

# Eternity Isle: the save numbers its areas 8-19 and names none, so these are worked out by matching where
# each area's Special rocks yield a gem (ActivityData names, e.g. Evergem in Outpost Area04) against the wiki's
# zones for that gem (spawns.py): Topaz in Outpost 1+2 and Jade in 2+3 pin Outpost 2 as The Courtyard,
# Garnet in Desert 1+2 and Alexandrite in 2+3 pin Desert 2, Peridot in Jungle 1+2 and Spinel in 2+3 pin
# Jungle 2; the unique Evergem, Bumblestone and Blue Zircon pin the last of each.
AREAS = {0: "Dazzle Beach", 1: "Glade of Trust", 2: "Peaceful Meadow", 3: "Plaza", 4: "Sunlit Plateau",
         5: "Forest of Valor", 6: "Forgotten Lands", 7: "Frosted Heights",
         8: "The Docks", 9: "The Courtyard", 10: "The Overlook", 11: "The Ruins",
         12: "The Plains", 13: "The Wastes", 14: "The Oasis", 15: "The Borderlands",
         16: "The Grasslands", 17: "The Promenade", 18: "The Grove", 19: "The Lagoon"}


def stock_zones(action, requirement, colour, world):
    colour = requirement.colour or colour
    if action == "mine_gem":
        def wanted(gem):
            if requirement.items:
                return gem in requirement.items
            return GEM_COLOURS.get(gem) == colour if colour else gem is not None   # no colour: any gem
        return [AREAS.get(a, f"Area {a}") for a, rock in sorted(world.special_rocks.items())
                if wanted(SPECIAL_GEMS.get(rock))]
    if action == "pick_flower":
        out = []
        for a, counts in sorted(world.items_by_area.items()):
            n = sum(c for item, c in counts.items()
                    if (item in requirement.items if requirement.items else colour in FLOWER_COLOURS.get(item, ())))
            if n:
                out.append((n, f"{AREAS.get(a, f'Area {a}')} ({n})"))
        return [label for _, label in sorted(out, key=lambda x: -x[0])]   # stable: ties keep area order
    return None


def zone_label(area, n=None):
    """A village area key as its zone name, 'Zone (n)' with a count."""
    name = AREAS.get(area, f"Area {area}")
    return f"{name} ({n})" if n else name


_label = zone_label


def forage_zones(items, world):
    found = [(sum(c for i, c in counts.items() if i in items), a) for a, counts in sorted(world.items_by_area.items())]
    return [_label(a, n) for n, a in sorted(found, key=lambda x: -x[0]) if n]


def wild_crop_zones(crops, world, now):
    """Zones with ripe wild patches (herbs, mushrooms) of those crops, 'Zone (count)', most first: a patch is
    ripe once the time the save records for its growth has passed. Wild patches are what the save stores for
    them; there are no loose mushrooms in the grids."""
    seeds = {seed for seed, crop in WILD_CROPS.items() if crop in crops}
    found = [(sum(1 for seed, times in patches.items() if seed in seeds for t in times if t <= now), a)
             for a, patches in sorted(world.wild_crops.items())]
    return [_label(a, n) for n, a in sorted(found, key=lambda x: -x[0]) if n]


def ripple_zones(rarity, world):
    return [_label(a, n if n > 1 else None) for a, counts in sorted(world.ripples.items()) if (n := counts.get(rarity))]


THORNS = (31300003, 31300004, 31300005, 31300006)   # Night Thorn Small1-3 and Big1 (the ones that give a reward)
UPROOT = re.compile(r"(?:Uproot|Remove|Clear)\b.*Night Thorns?")


def duty_zones(requirement, filter, colour, world, text="", now=None):
    """The zone labels for any duty this module can answer, else None: a gem or flower colour duty, a gold
    ripple duty (fish rarity Unique), picking foraged items (the wiki's Foraging ones, e.g. mushrooms: the ripe wild patches), or
    uprooting Night Thorns (by the duty text), listing the zones they now stand in with how many."""
    if UPROOT.match(text):
        return forage_zones(THORNS, world)
    colour = colour[:-5] if colour and colour.endswith(" Gems") else (None if colour == "Any Gem" else colour)   # a gem row is 'Blue Gems'
    if requirement.action in ("mine_gem", "pick_flower"):
        if requirement.action == "pick_flower" and not (colour or requirement.items):
            return None
        return stock_zones(requirement.action, requirement, colour, world)
    if filter.get("kind") == "Fish" and filter.get("fish_rarity") == ["Unique"]:
        return ripple_zones("Exceptional", world)
    items = requirement.items if requirement.action == "harvest_crop" else None
    if items and all((spawn_for(i) or {}).get("how") == "Foraging" for i in items):
        return wild_crop_zones(items, world, now)
    return None


def growth_zones(requirement):
    """Zone names where the duty's garden crops grow faster (the wiki's zones for them, spawns.py), else None
    for other actions or when any item is not a Gardening one."""
    rows = [SPAWNS.get(i) for i in requirement.items or ()]
    if requirement.action != "harvest_crop" or not rows or any(r is None or r[0] != "Gardening" for r in rows):
        return None
    return list(dict.fromkeys(z for _, zones in rows for z in zones))


def fish_spot(requirement):
    """Where and in what to fish for one named fish: 'Peaceful Meadow \u00b7 Blue or White', the wiki's zones
    and ripple colours for it; None for any other duty, several fish, or a fish the tables do not know."""
    if requirement.action != "catch_fish" or not requirement.items or len(requirement.items) != 1:
        return None
    found, pools = SPAWNS.get(requirement.items[0]), FISH_POOLS.get(requirement.items[0])
    if not found or found[0] != "Fishing" or not pools:
        return None
    how = " or ".join("Anywhere" if c == "None" else c for c in pools)   # 'Blue or White'; open water is 'Anywhere'
    zones = [z for z in found[1] if z in GROUPS["Valley"] + GROUPS["Eternity"]]   # the worlds a save here has
    return f"{', '.join(zones)} \u00b7 {how}" if zones else None
