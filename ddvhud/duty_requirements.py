"""What a Star Path duty asks for: classify(text, filter) -> Requirement.

A Requirement is the action ('catch_fish', 'mine_gem', ...) plus how narrow it is: a place, a colour,
or specific items (item ids, sorted); none of them set means any. Anything not recognised is a
standalone Requirement (action 'unknown') that equals nothing, not even a rebuilt copy of itself,
so it is never grouped with another duty. The filter is read first; the duty text is only a fallback.
"""
import re

from .fav_foods import FAV_FOODS
from .items import item_name
from .villagers import VILLAGERS

# The filter's activity kind -> (action, verb, singular noun, plural noun).
KINDS = {
    "Fish": ("catch_fish", "Catch", "fish", "fish"),
    "Mineral": ("mine_gem", "Mine", "gem", "gems"),
    "Crop": ("harvest_crop", "Harvest", "crop", "crops"),
    "Flower": ("pick_flower", "Pick", "flower", "flowers"),
    "Meal": ("cook", "Cook", "meal", "meals"),
}
GEM_BLOCK = 316   # item ids // 100000

# Colour tag ids as the game's Tag.json numbers them (ids 2000700000-2000700010, in this order).
# To refresh after a game update: read the Tag.json records named Tag.Blue ... Tag.Gray (0x08 id-varint
# 0x12 len name); the ids were consecutive, Blue first.
COLOUR_TAGS = {2000700000 + n: c for n, c in enumerate(
    ("Blue", "Green", "Red", "Pink", "White", "Black", "Yellow", "Orange", "Brown", "Purple", "Gray"))}

IGNORED_TAGS = {2001200027}   # IsMineral: on every gem duty that names a colour, so it narrows nothing
PLACES = {"Beach": "Dazzle Beach"}   # the filter's fish_location names -> the zone names the page uses
KNOWN_FIELDS = {"item", "item_list", "kind", "type", "tags", "fish_location"}   # filter fields the model reads
UNKNOWN = "unknown"

# Duties whose filter carries nothing (or only a Character): the text pattern -> (action, label template).
# The captured name is the target; it is compared as written (feed targets lower-cased), so a Villager
# or shop spelled differently in two Star Paths would not group (safe, never a wrong match).
TEXT_PATTERNS = [
    (re.compile(r"Buy something from (.+?)\.?$"), "buy", "Buy from {}"),
    (re.compile(r"Hang out with ((?!an? |any ).+?)\.?$"), "hang_out", "Hang out with {}"),
    (re.compile(r"Take a selfie with ((?!an? |any ).+?)\.?$"), "selfie", "Take a selfie with {}"),
    (re.compile(r"Feed (.+?) their favou?rite food\.?$", re.I), "feed", "Feed {} their favorite food"),
]
SELL = re.compile(r"Sell\b")
OTHER_VERB = re.compile(r"(Water|Give|Plant|Place|Craft|Gift)\b")   # the filter names a kind, but the duty does something else with it


class Requirement:
    def __init__(self, action, label="", place=None, colour=None, items=None, target=None):
        self.action = action
        self.label = label
        self.place = place
        self.colour = colour
        self.items = items
        self.target = target

    def _key(self):
        return (self.action, self.place, self.colour, self.items, self.target)

    def __eq__(self, other):
        if self.action == UNKNOWN:
            return self is other
        return isinstance(other, Requirement) and self._key() == other._key()

    def to_json(self):
        return {"label": self.label, "action": self.action, "place": self.place, "colour": self.colour,
                "items": list(self.items) if self.items else None, "target": self.target}

    def covers(self, other):
        """True when every action that satisfies `other` also satisfies this one (same action, this one
        no narrower). Only what the data proves: a place or colour never covers an item list or the
        reverse, since the item-to-place and listed-gem-to-colour links are not known."""
        if self.action == UNKNOWN or other.action != self.action:
            return False
        return (self.place in (None, other.place) and self.colour in (None, other.colour)
                and self.target in (None, other.target)
                and (self.items is None or (other.items is not None and set(other.items) <= set(self.items))))

    def __hash__(self):
        return id(self) if self.action == UNKNOWN else hash(self._key())


def _names(verb, items):
    names = [item_name(i) for i in items]
    more = f" and {len(names) - 3} more" if len(names) > 3 else ""
    return f"{verb} {', '.join(names[:3])}{more}"


def classify(text, filter):
    if SELL.match(text):   # the verb is not in the filter (selling seafood carries a Crop filter)
        return Requirement("sell", "Sell items") if not filter else Requirement(UNKNOWN)
    if set(filter) - KNOWN_FIELDS:   # e.g. a roughness or meal-star condition: narrower than we model
        return Requirement(UNKNOWN)
    kind = filter.get("kind")
    items = filter.get("item_list") or ([filter["item"]] if "item" in filter else [])
    if kind is None and items and all(i // 100000 == GEM_BLOCK for i in items):
        kind = "Mineral"
    if kind not in KINDS:
        for pattern, action, label in TEXT_PATTERNS:
            m = pattern.match(text)
            if m:
                target = m.group(1).lower() if action == "feed" else m.group(1)
                return Requirement(action, label.format(target), target=target)
        return Requirement(UNKNOWN)
    if OTHER_VERB.match(text):
        return Requirement(UNKNOWN)
    action, verb, noun, plural = KINDS[kind]
    places = [PLACES.get(p) for p in filter.get("fish_location", [])]
    # a named item already says what is wanted, so a tag beside it (IsDreamlightValley, the origin) adds nothing
    colours = [COLOUR_TAGS.get(t) for t in filter.get("tags", []) if t not in IGNORED_TAGS and (t in COLOUR_TAGS or not items)]
    if None in places or None in colours or len(places) + len(colours) + bool(items) > 1:
        return Requirement(UNKNOWN)
    if places:
        return Requirement(action, f"{verb} {noun} at {places[0]}", place=places[0])
    if colours:
        return Requirement(action, f"{verb} {colours[0].lower()} {plural}", colour=colours[0])
    if items:
        return Requirement(action, _names(verb, sorted(items)), items=tuple(sorted(items)))
    return Requirement(action, f"{verb} any {noun}")


def colour_family(text, req):
    """(family, row) for a gem or flower duty, else None: the family ('Mine', 'Pick flowers') is what the
    duties of different colours share, the row 'Purple Gems' or 'Yellow'. The colour is the filter's tag, or
    for a listed gem set the colour word in the duty text. A gem duty with no colour is the 'Any Gem' row, a
    named set of gems ('square gems') its own word; a flower duty with no colour has none."""
    if req.action not in ("mine_gem", "pick_flower"):
        return None
    colour = req.colour
    if colour is None:
        found = [c for c in COLOUR_TAGS.values() if re.search(rf"\b{c}\b", text, re.I)]
        colour = found[0] if len(found) == 1 else None
    if req.action == "pick_flower":
        return ("Pick flowers", colour) if colour else None
    if colour:
        return "Mine", f"{colour} Gems"
    word = re.search(r"\b(?:for|\d+) (\w+) gems", text)
    return "Mine", (f"{word[1].capitalize()} Gems" if word else "Any Gem")


def hang_out_family(text, filter):
    """('Hang outs', who) for a 'Hang out with ...' duty on a Character, else None. who is the Villager's name
    when the filter names one, else the text's own wording without its article ('long-bearded wizard')."""
    m = re.match(r"Hang out with (.+?)\.?$", text)
    if not m or filter.get("type") != "Character":
        return None
    who = VILLAGERS.get(filter["item"]) if "item" in filter else None
    return "Hang outs", who or re.sub(r"^(a|an|the|your pal|someone with a|one who) ", "", m.group(1), flags=re.I)


COOK_VERB = re.compile(r"(?:Cook|Whip up|Prepare) (?:\d+ |some )?(?:servings of )?", re.I)


def cook_family(text, filter):
    """('Cook', what) for a duty that cooks something, else None. what is the dish's name when the filter
    names a Meal, else the text without its verb and count ('3-star meals', 'seafood meals')."""
    m = COOK_VERB.match(text)
    if not m or filter.get("kind") not in ("Meal", "Ingredient"):
        return None
    if filter["kind"] == "Meal" and "item" in filter:
        return "Cook", item_name(filter["item"])
    return "Cook", text[m.end():].rstrip(".")


ROCK_SPOTS = re.compile(r"Mine \d+ Rock Spots(?: (?:in|on|at)(?: the)? (.+?))?\.?$")


def node_family(text):
    """('Mine', 'Nodes') for a 'Mine N Rock Spots ...' duty, else None."""
    return ("Mine", "Nodes") if ROCK_SPOTS.match(text) else None


def node_place(text):
    """The zone a Rock Spots duty names ('Forest of Valor'), None when it names none."""
    m = ROCK_SPOTS.match(text)
    return m.group(1) if m else None

FISH_ZONE = re.compile(r"Catch \d+ Fish (?:in|from|on)(?: the)? (.+?)\.?$")


def fish_family(text, req, filter):
    """('Fish', row) for a duty about catching fish, else None: 'Any fish', the place, the named fish, or
    'Gold ripples' (fish rarity Unique); other conditions (weather, ...) are left alone."""
    if filter.get("kind") == "Fish" and filter.get("fish_rarity") == ["Unique"] and set(filter) <= KNOWN_FIELDS | {"fish_rarity"}:
        return "Fish", "Gold ripples"
    if filter.get("kind") == "Fish":
        m = FISH_ZONE.match(text)
        if m:   # slot duties name the zone in their text only
            return "Fish", m.group(1)
        if re.fullmatch(r"Catch \d+ Seafood\.?", text):
            return "Fish", "Seafood"
    if req.action != "catch_fish":
        return None
    if req.place:
        return "Fish", req.place
    if req.items:
        return "Fish", ", ".join(item_name(i) for i in req.items[:3])
    return "Fish", "Any fish"


SELL_WHAT = re.compile(r"\bSell (?:(?:\d+|any|some) )*(.+?)[.!]?$")


def sell_family(text):
    """('Sell', what) for a duty that sells something, whatever catchy line comes before ('Don't be shellfish! Sell
    100 seafood.' -> 'Seafood'), else None."""
    m = SELL_WHAT.search(text)
    return ("Sell", m.group(1)[:1].upper() + m.group(1)[1:]) if m else None


GIVE_GIFT = re.compile(r"(?:Give|Bring) (.+?) (?:their|his|her) favou?rite gifts?\.?$", re.I)


def gift_family(text):
    """('Gifts', who) for a 'give X their favorite gift' duty, else None. The filter says nothing here, so who
    is the text's own wording without its article ('Goofy', 'Boy who never grows up'); 'a Friend' or 'a
    Villager' is 'Any Friend' / 'Any Villager'."""
    m = GIVE_GIFT.match(text)
    if not m:
        return None
    who = re.sub(r"^(?:a|an|the) ", "", m.group(1), flags=re.I)
    if who.lower() in ("friend", "villager"):
        who = "Any " + who.capitalize()
    return "Gifts", who[:1].upper() + who[1:]


EARN = re.compile(r"(?:Earn|Gain) [\d,]+ (.+?)\.?$")


def currency_family(text, filter):
    """('Earn Currency', currency) for a duty that earns a currency (the filter's type is Currency), else None;
    the currency is the text's own name for it ('Star Coins', 'Dreamlight')."""
    m = EARN.match(text)
    return ("Earn Currency", m.group(1)) if m and filter.get("type") == "Currency" else None


FEED_WHO = re.compile(r"Feed (?:an? |the )?([A-Za-z' -]+?)(?: their favou?rite food)?\.?$")


def feed_family(text):
    """('Feed', animal) for a duty that feeds a kind of animal ('Feed a Fox', 'Feed Sea Turtles their favorite
    food.'), else None; the animal is capitalised the same way whatever the text's case."""
    m = FEED_WHO.match(text)
    if not m:
        return None
    who = m.group(1)
    return "Feed", who[:1].upper() + who[1:].lower()


def food_for(animal):
    """The favorite food of the kind of animal a Feed row names ('Sea turtles' -> 'Seaweed'), None if unknown.
    The kind is the row's last word, singular."""
    kind = animal.split()[-1].rstrip("s").capitalize() if animal else ""
    return FAV_FOODS.get(kind)


CRAFT_WHAT = re.compile(r"Craft (?:\d+ |some |any |an? )?(.+?)\.?$")


def craft_family(text):
    """('Craft', what) for a 'Craft ...' duty, else None; what is the text without the verb and the count
    or 'some' ('Natural Rock Paths', 'Fabric')."""
    m = CRAFT_WHAT.match(text)
    return ("Craft", m.group(1)[:1].upper() + m.group(1)[1:]) if m else None


CLEAN_WHAT = re.compile(r"(?:Uproot|Remove|Clear|Get rid of|Banish) (?:\d+ |some |the |all )*(.+?)\.?$", re.I)
PESTS = re.compile(r"Night Thorns?|evil|thorn|weeds?|mushrooms?|plants?", re.I)


def clean_family(text):
    """('Clean', pest) for a duty that gets rid of a pest (Night Thorns, evil mushrooms or plants, weeds), else
    None; the pest is the text's own wording without the verb, count and article."""
    m = CLEAN_WHAT.match(text)
    if not m or not PESTS.search(m.group(1)):
        return None
    return "Clean", m.group(1)[:1].upper() + m.group(1)[1:]


def generic_rank(family, row, text, filter):
    """Where a row goes in its card, most generic first: -1 rock nodes (any gem or ore), 0 'any' of the kind,
    1 a place or a kind of dish, 2 a specific item, colour or condition."""
    if family == "Mine" and row == "Nodes":
        return -1
    if row.lower().startswith("any "):
        return 0
    if family == "Fish" and (filter.get("fish_location") or FISH_ZONE.match(text)):
        return 1
    if family == "Cook" and "item" not in filter:
        return 1
    return 2
