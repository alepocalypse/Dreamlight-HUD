import unittest
from datetime import datetime, timezone

from ddvhud.report import build_report
from ddvhud.villagers import VILLAGERS

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)

# Wiki roster, 2026-10-19: 73 Villagers plus The Forgotten
WIKI_ROSTER = {
    "Aladdin", "Jasmine", "Alice", "Cheshire Cat", "Belle", "Cogsworth", "The Beast", "Lumiere",
    "Cinderella", "The Fairy Godmother", "The Forgotten", "Mirabel", "Anna", "Elsa", "Kristoff",
    "Olaf", "Hercules", "Phil", "Joy", "Sadness", "Lady", "Tramp", "Stitch", "Daisy", "Donald Duck",
    "Goofy", "Mickey Mouse", "Minnie Mouse", "Scrooge McDuck", "Maui", "Moana", "Mike Wazowski",
    "Sulley", "Mulan", "Mushu", "Peter Pan", "Pocahontas", "Remy", "Mother Gothel", "Nala", "Pumbaa",
    "Scar", "Simba", "Timon", "Ariel", "Prince Eric", "Ursula", "Tiana", "Merlin", "Jack Skellington",
    "Oogie Boogie", "Sally", "Buzz Lightyear", "Woody", "WALL·E", "Ralph", "Vanellope", "Jafar",
    "Gaston", "Oswald", "Rapunzel", "EVE", "Merida", "Hades", "Aurora", "Maleficent", "Flynn",
    "Cruella", "Tinker Bell", "Snow White", "Tigger", "Eeyore", "Piglet", "Winnie the Pooh",
}
NON_VILLAGERS = [10000100, 10000101, 10000102, 10000118, 10000124, 10000126, 10000211, 10000218, 10000219,
                 10000134, 10000136, 10000138, 10000139, 10000146, 10000147]


def secret(cid):
    return {"Base": {"id": cid}, "Status": "CharacterStatus_Secret", "FriendshipLevel": 0}


def report(*ids):
    return build_report({"World": {"Characters": [secret(i) for i in ids]}}, NOW)


class Roster(unittest.TestCase):
    def test_roster_villager_counts_as_unavailable(self):
        s = report(10000003)["summary"]
        self.assertEqual((s["unavailable"], s["unidentified"]), (1, 0))

    def test_newly_added_villager_is_named(self):
        r = report(10000012, 10000212)
        self.assertEqual({n["name"] for n in r["not_in_village"]}, {"Ralph", "Oogie Boogie"})

    def test_non_villagers_are_unidentified(self):
        s = report(*NON_VILLAGERS)["summary"]
        self.assertEqual((s["total"], s["unavailable"], s["unidentified"]), (0, 0, len(NON_VILLAGERS)))

    def test_unknown_id_is_unidentified(self):
        s = report(99999999)["summary"]
        self.assertEqual((s["unavailable"], s["unidentified"]), (0, 1))

    def test_roster_is_the_wiki_roster(self):
        self.assertEqual(sorted(VILLAGERS.values()), sorted(WIKI_ROSTER))

    def test_no_non_villager_on_roster(self):
        self.assertEqual(set(NON_VILLAGERS) & set(VILLAGERS), set())


if __name__ == "__main__":
    unittest.main()
