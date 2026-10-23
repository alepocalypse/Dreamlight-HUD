"""Named lookups over the generated game tables, with the unknown-id fallbacks and wiki-link rules.
Callers use these instead of indexing a table entry by position."""
from collections import namedtuple
from urllib.parse import quote

from .companions import COMPANIONS, CRITTERS
from .ingredients import INGREDIENTS
from .items import ITEMS, item_name, item_wiki_title
from .villagers import PROFESSIONS, VILLAGERS

_WIKI = "https://dreamlightvalleywiki.com/"

Companion = namedtuple("Companion", "name job")
Critter = namedtuple("Critter", "name companion needed")


def companion(pid):
    """The Companion's name and Job; "Companion #id" and Job "unknown" for an id not in the table."""
    entry = COMPANIONS.get(pid)
    return Companion(entry[0], entry[2]) if entry else Companion(f"Companion #{pid}", "unknown")


def critter(cid):
    """The Critter's name, the id of the Companion it unlocks and the feedings needed;
    "Critter #id" with no Companion and no feedings for an id not in the table."""
    return Critter(*CRITTERS[cid]) if cid in CRITTERS else Critter(f"Critter #{cid}", None, None)

_ITEM_IDS = {name: i for i, name in ITEMS.items()}


def _page_url(title):
    return _WIKI + quote(title.replace(" ", "_"), safe="")


def villager_name(cid, names=VILLAGERS):
    """The Villager's name, "Villager #id" for an id not in `names`."""
    return names.get(cid) or f"Villager #{cid}"


def villager_wiki_url(cid, names=VILLAGERS):
    """Wiki page of a Villager, None for an id not in `names`."""
    name = names.get(cid)
    return _page_url(name) if name else None


def item_wiki_url(item_id):
    """Wiki page of an item, the wiki search for it when it has no page, None for an unknown id."""
    found = item_wiki_title(item_id)
    if found is None:
        return None
    title, has_page = found
    return _page_url(title) if has_page else _WIKI + "index.php?search=" + quote(title, safe="")


def profession_name(pid):
    """The Profession's name, "Unknown profession" for an id not in the table."""
    return PROFESSIONS.get(pid, "Unknown profession")


def item_id(name):
    """The item id for an item name, None when the name is not an item."""
    return _ITEM_IDS.get(name)


def ingredient_where(name):
    """The wiki's tag for getting an ingredient; empty for a name not on its ingredient list."""
    return INGREDIENTS.get(name, ("", ""))[1]


def category_item_ids(category):
    """Item ids of the ingredients in a category ("Vegetables"), those that have an item id here."""
    return [_ITEM_IDS[n] for n, (cat, _) in INGREDIENTS.items() if cat == category and n in _ITEM_IDS]
