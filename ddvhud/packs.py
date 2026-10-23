"""Content packs and which Villagers they add. Hand-maintained from docs/research/villager-packs.md
(dreamlightvalleywiki.com Characters and area pages); every Villager not listed here is base game.

save_id is the pack's key in the save's LastKnownBoughtExpansionsAnyPlatform, None when not yet
confirmed from a real save (only BaseGame and Expansion01 are)."""
WIKI = "https://dreamlightvalleywiki.com/"

PACKS = {
    "expansion1": {"name": "Expansion 1: A Rift in Time", "wiki_url": WIKI + "Eternity_Isle", "save_id": "Expansion01"},
    "expansion2": {"name": "Expansion 2: The Storybook Vale", "wiki_url": WIKI + "Storybook_Vale", "save_id": None},
    "expansion3": {"name": "Expansion 3: Wishblossom Ranch", "wiki_url": WIKI + "Wishblossom_Mountains", "save_id": None},
    "adventure1": {"name": "Adventure Pack 1: Honeyglow Woods", "wiki_url": WIKI + "Honeyglow_Woods", "save_id": None},
}

VILLAGER_PACK = {
    10000027: "expansion1", 10000038: "expansion1", 10000043: "expansion1", 10000103: "expansion1",  # Rapunzel, EVE, Gaston, Jafar
    10000114: "expansion1",                                                                          # Oswald
    10000059: "expansion2", 10000117: "expansion2", 10000119: "expansion2", 10000127: "expansion2",  # Flynn, Merida, Hades, Maleficent
    10000135: "expansion2",                                                                          # Aurora
    10000160: "expansion3", 10000158: "expansion3", 10000162: "expansion3", 10000166: "expansion3",  # Tinker Bell, Snow White, Cruella, Tigger
    10000183: "adventure1", 10000184: "adventure1", 10000185: "adventure1",                          # Pooh, Piglet, Eeyore
}


def owned_packs(owned_ids, moved_in_ids):
    """Keys of PACKS the player has, or may have: when in doubt a pack counts as owned, so no Villager is
    hidden by mistake. `owned_ids`: the save's owned pack ids, None when unreadable (then all are owned).
    `moved_in_ids`: Villager ids in the village or a realm.

    A pack with a known save id is owned exactly when that id is listed. A pack whose id is not known is
    owned when the list holds an id we do not recognise, or when one of its Villagers has moved in."""
    if not owned_ids:
        return set(PACKS)
    known = {"BaseGame"} | {p["save_id"] for p in PACKS.values() if p["save_id"]}
    unrecognised = any(i not in known for i in owned_ids)
    moved_in_packs = {VILLAGER_PACK[i] for i in moved_in_ids if i in VILLAGER_PACK}
    return {key for key, p in PACKS.items()
            if (p["save_id"] in owned_ids if p["save_id"] else unrecognised or key in moved_in_packs)}
