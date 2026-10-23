import unittest
from datetime import datetime, timezone

from ddvhud.report import build_report
from ddvhud.saveview import SaveView

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
RALPH, JAFAR = 10000012, 10000103                       # base game, Expansion 1
MERIDA, AURORA, FLYNN = 10000117, 10000135, 10000059     # Storybook Vale
CRUELLA, POOH = 10000162, 10000183                       # Wishblossom, Honeyglow Woods
UNLISTED = 10009999                                      # not in the pack table


def character(cid, status="Secret"):
    return {"Base": {"id": cid}, "Status": "CharacterStatus_" + status, "FriendshipLevel": 0}


def report(characters, owned="missing"):
    profile = {"World": {"Characters": [character(*c) if isinstance(c, tuple) else character(c) for c in characters]}}
    if owned != "missing":
        profile["LastKnownBoughtExpansionsAnyPlatform"] = owned
    return build_report(profile, NOW)


def names(rows):
    return {r["name"] for r in rows}


class OwnedPacks(unittest.TestCase):
    def test_owned_pack_ids_come_from_the_save(self):
        self.assertEqual(SaveView({"LastKnownBoughtExpansionsAnyPlatform": ["BaseGame", "Expansion01"]}).owned_pack_ids,
                         ["BaseGame", "Expansion01"])

    def test_missing_or_odd_owned_list_is_none(self):
        for profile in ({}, {"LastKnownBoughtExpansionsAnyPlatform": None}, {"LastKnownBoughtExpansionsAnyPlatform": "x"},
                        {"LastKnownBoughtExpansionsAnyPlatform": []}):
            self.assertIsNone(SaveView(profile).owned_pack_ids)

    def test_non_string_entries_are_ignored(self):
        self.assertEqual(SaveView({"LastKnownBoughtExpansionsAnyPlatform": ["BaseGame", 5, None]}).owned_pack_ids, ["BaseGame"])


class NotInVillageByPack(unittest.TestCase):
    OWNED = ["BaseGame", "Expansion01"]

    def test_villagers_of_packs_you_do_not_own_require_additional_dlc(self):
        r = report([RALPH, JAFAR, MERIDA, CRUELLA, POOH], self.OWNED)
        self.assertEqual(names(r["not_in_village"]), {"Ralph", "Jafar"})
        self.assertEqual({(g["pack"], tuple(sorted(names(g["villagers"])))) for g in r["requires_dlc"]},
                         {("Expansion 2: The Storybook Vale", ("Merida",)),
                          ("Expansion 3: Wishblossom Ranch", ("Cruella",)),
                          ("Adventure Pack 1: Honeyglow Woods", ("Winnie the Pooh",))})

    def test_each_pack_group_links_to_its_wiki_page(self):
        [g] = report([MERIDA], self.OWNED)["requires_dlc"]
        self.assertEqual(g["wiki_url"], "https://dreamlightvalleywiki.com/Storybook_Vale")

    def test_denominator_counts_only_owned_pack_villagers(self):
        s = report([(RALPH, "InVillage"), JAFAR, MERIDA, FLYNN, CRUELLA], self.OWNED)["summary"]
        self.assertEqual(s["in_owned_packs"], 2)    # Ralph and Jafar; Storybook and Wishblossom are not owned

    def test_no_pack_means_nothing_requires_dlc(self):
        r = report([RALPH, JAFAR], self.OWNED)
        self.assertEqual(r["requires_dlc"], [])

    def test_villager_missing_from_the_table_counts_as_owned(self):
        r = report([UNLISTED], self.OWNED)   # unlisted ids are also "unidentified" and skipped, like before
        self.assertEqual((names(r["not_in_village"]), r["requires_dlc"]), (set(), []))

    def test_unreadable_owned_list_hides_nothing(self):
        for owned in ("missing", None, []):
            r = report([MERIDA, CRUELLA], owned)
            self.assertEqual((names(r["not_in_village"]), r["requires_dlc"]), ({"Merida", "Cruella"}, []))

    def test_an_owned_id_we_do_not_recognise_means_unconfirmed_packs_may_be_owned(self):
        r = report([MERIDA, CRUELLA, JAFAR], self.OWNED + ["Expansion02"])
        self.assertEqual(names(r["not_in_village"]), {"Merida", "Cruella", "Jafar"})
        self.assertEqual(r["requires_dlc"], [])

    def test_a_moved_in_villager_proves_their_pack_is_owned(self):
        r = report([(MERIDA, "InRealm"), AURORA, FLYNN, CRUELLA], self.OWNED)
        self.assertEqual(names(r["not_in_village"]), {"Merida", "Aurora", "Flynn"})   # whole Storybook Vale pack
        self.assertEqual([g["pack"] for g in r["requires_dlc"]], ["Expansion 3: Wishblossom Ranch"])

    def test_a_known_pack_id_is_decided_by_the_list_not_by_villagers(self):
        r = report([(JAFAR, "InVillage"), CRUELLA], ["BaseGame"])   # Expansion01 absent: a leftover Villager does not own it
        self.assertEqual([g["pack"] for g in r["requires_dlc"]], ["Expansion 3: Wishblossom Ranch"])


if __name__ == "__main__":
    unittest.main()
