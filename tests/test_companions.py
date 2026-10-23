import unittest
from datetime import datetime, timezone

from ddvhud.companions import COMPANIONS, CRITTERS, JOBS
from ddvhud.report import build_report

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
SQUIRREL_01, SQUIRREL_02, SQUIRREL_03 = 120000001, 120000005, 120000006   # Foraging
RABBIT_03, CELESTIAL_TURTLE, ROYAL_FOX = 120000014, 120000043, 120000044  # Gardening, Fishing, Fishing
FESTIVE_FOX, PUA, HEIHEI = 120000048, 120000000, 120000259                # Fishing, Foraging (per the player), no Job known (Baby Lynx)
SCARY_SQUIRREL = 120000051                                                # a Squirrel that mines, per its wiki page
CRITTER_RABBIT_03, CRITTER_SQUIRREL_01, CRITTER_RAVEN_01 = 120100013, 120100001, 120100004
CRITTER_RABBIT_01 = 120100000
RABBIT_03_NAME = COMPANIONS[RABBIT_03][0]
CRITTER_RABBIT_03_NAME = CRITTERS[CRITTER_RABBIT_03][0]
EVENT_CRITTER = 120100082   # event Critter, unlocks no Companion


def pet(pid, level=1):
    return {"PetItemID": pid, "FriendshipLevel": level, "FriendshipXp": 0}


def fed(cid, n):
    return {"CritterItemID": cid, "NumberOfFeedingDone": n, "LastFeedingTime": "2026-10-01T00:00:00Z"}


def report(pets=(), equipped=(), critters=()):
    return build_report({"Player": {"Pets": list(pets), "AssignedPets": list(equipped)},
                         "World": {"Critters": list(critters)}}, NOW)["companions"]


def job(r, name):
    return next(j for j in r["jobs"] if j["job"] == name)


class UnlockedPerJob(unittest.TestCase):
    def test_nine_jobs_in_order_even_when_empty(self):
        r = report()
        self.assertEqual([j["job"] for j in r["jobs"]], [
            "Digging", "Fishing", "Foraging", "Gardening", "Mining", "Time-bending",
            "Flower pick-up", "Wood pick-up", "Snippet catching"])
        self.assertTrue(all(j["goal"] == 2 and j["unlocked"] == [] and j["unlocked_count"] == 0
                            and j["at_max_count"] == 0 and not j["complete"] for j in r["jobs"]))
        self.assertEqual(r["no_job"], [])

    def test_unlocked_sorted_highest_level_first_with_game_names(self):
        f = job(report([pet(FESTIVE_FOX, 1), pet(CELESTIAL_TURTLE, 5), pet(ROYAL_FOX, 3), pet(SQUIRREL_02, 3)]), "Fishing")
        self.assertEqual([(c["name"], c["level"]) for c in f["unlocked"]],
                         [("Celestial Sea Turtle", 5), ("Regal Fox", 3), ("Festive Fox", 1)])
        self.assertEqual(f["unlocked_count"], 3)

    def test_each_companion_lands_under_its_own_job(self):
        r = report([pet(SQUIRREL_02, 3), pet(RABBIT_03, 4)])
        self.assertEqual([c["name"] for c in job(r, "Foraging")["unlocked"]], ["Red Squirrel"])
        self.assertEqual([c["name"] for c in job(r, "Gardening")["unlocked"]], [RABBIT_03_NAME])
        self.assertEqual(job(r, "Fishing")["unlocked"], [])


class Goal(unittest.TestCase):
    def test_a_variant_can_have_another_job_than_its_species(self):
        r = report([pet(SCARY_SQUIRREL, 5), pet(SQUIRREL_01, 5)])
        self.assertEqual([c["name"] for c in job(r, "Mining")["unlocked"]], ["Scary Squirrel"])
        self.assertEqual([c["name"] for c in job(r, "Foraging")["unlocked"]], ["Classic Squirrel"])

    def test_two_at_level_5_is_complete(self):
        j = job(report([pet(SQUIRREL_01, 5), pet(SQUIRREL_02, 5)]), "Foraging")
        self.assertEqual((j["unlocked_count"], j["at_max_count"], j["complete"]), (2, 2, True))

    def test_two_unlocked_but_one_below_5_is_not_complete(self):
        j = job(report([pet(SQUIRREL_01, 5), pet(SQUIRREL_02, 4)]), "Foraging")
        self.assertEqual((j["unlocked_count"], j["at_max_count"], j["complete"]), (2, 1, False))

    def test_three_unlocked_counts_all_but_level_5_counted_as_found(self):
        j = job(report([pet(SQUIRREL_01, 5), pet(SQUIRREL_02, 5), pet(SQUIRREL_03, 5)]), "Foraging")
        self.assertEqual((j["unlocked_count"], j["at_max_count"], j["complete"]), (3, 3, True))


class Equipped(unittest.TestCase):
    def test_equipped_flag(self):
        j = job(report([pet(SQUIRREL_01, 1), pet(SQUIRREL_02, 3)], equipped=[SQUIRREL_02]), "Foraging")
        self.assertEqual([(c["name"], c["equipped"]) for c in j["unlocked"]],
                         [("Red Squirrel", True), ("Classic Squirrel", False)])


class CritterProgress(unittest.TestCase):
    def test_fed_critter_in_progress(self):
        j = job(report(critters=[fed(CRITTER_RABBIT_03, 1)]), "Gardening")
        self.assertEqual(j["critters"], [{"name": CRITTER_RABBIT_03_NAME, "companion": RABBIT_03_NAME,
                                          "fed": 1, "needed": 2}])

    def test_fully_fed_critter_is_omitted(self):
        j = job(report(critters=[fed(CRITTER_SQUIRREL_01, 2)]), "Foraging")
        self.assertEqual(j["critters"], [])

    def test_in_progress_kept_while_finished_one_dropped(self):
        j = job(report(critters=[fed(CRITTER_SQUIRREL_01, 2), fed(CRITTER_RABBIT_03, 1)]), "Foraging")
        self.assertEqual(j["critters"], [])
        j = job(report(critters=[fed(CRITTER_SQUIRREL_01, 2), fed(CRITTER_RABBIT_03, 1)]), "Gardening")
        self.assertEqual([c["companion"] for c in j["critters"]], [RABBIT_03_NAME])

    def test_critter_whose_companion_is_unlocked_is_omitted_even_if_underfed(self):
        j = job(report([pet(RABBIT_03)], critters=[fed(CRITTER_RABBIT_03, 1)]), "Gardening")
        self.assertEqual(j["critters"], [])

    def test_critters_never_fed_are_not_listed(self):
        self.assertEqual(job(report(), "Gardening")["critters"], [])


class UnknownAndNoJob(unittest.TestCase):
    def test_unknown_companion_id(self):
        r = report([pet(129999999, 2)])
        self.assertEqual(r["no_job"], [{"name": "Companion #129999999", "level": 2, "equipped": False}])

    def test_companion_with_no_known_job(self):
        r = report([pet(HEIHEI, 2), pet(SQUIRREL_01, 1)], equipped=[HEIHEI])
        self.assertEqual(r["no_job"], [{"name": "Baby Lynx", "level": 2, "equipped": True}])
        self.assertEqual(sum(j["unlocked_count"] for j in r["jobs"]), 1)

    def test_pua_forages(self):
        j = job(report([pet(PUA, 2)]), "Foraging")
        self.assertEqual([u["name"] for u in j["unlocked"]], ["Pua"])

    def test_unknown_critter_id(self):
        r = report(critters=[fed(129999998, 1)])
        self.assertEqual(r["no_job_critters"], [{"name": "Critter #129999998", "companion": None,
                                                 "fed": 1, "needed": None}])

    def test_event_critter_with_no_companion_goes_under_no_job(self):
        r = report(critters=[fed(EVENT_CRITTER, 1)])
        self.assertEqual(len(r["no_job_critters"]), 1)
        self.assertTrue(all(j["critters"] == [] for j in r["jobs"]))

    def test_missing_pets_and_critters_keys(self):
        r = build_report({}, NOW)["companions"]
        self.assertEqual(len(r["jobs"]), 9)


class Tables(unittest.TestCase):
    def test_every_critter_companion_is_known_or_null(self):
        for cid, (_, comp, _) in CRITTERS.items():
            self.assertTrue(comp is None or comp in COMPANIONS, cid)

    def test_every_job_is_one_of_the_nine_or_unknown(self):
        self.assertEqual(len(JOBS), 9)
        for cid, (_, _, jb) in COMPANIONS.items():
            self.assertIn(jb, JOBS + ["unknown"], cid)

    def test_names_are_the_games_display_names(self):
        self.assertEqual(COMPANIONS[SQUIRREL_01][0], "Classic Squirrel")
        self.assertEqual(COMPANIONS[SQUIRREL_02][0], "Red Squirrel")
        self.assertEqual(COMPANIONS[120000007][0], "Black Squirrel")
        self.assertEqual(COMPANIONS[PUA][0], "Pua")
        self.assertEqual(CRITTERS[CRITTER_SQUIRREL_01][0], "Classic Squirrel")


class FallbackName(unittest.TestCase):
    def test_missing_game_text_key_falls_back_to_the_tidied_name(self):
        import importlib.util, pathlib
        path = pathlib.Path(__file__).resolve().parent.parent / "tools" / "gen_names.py"
        spec = importlib.util.spec_from_file_location("gen_names", path)
        gen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen)
        text = {"Squirrel!Squirrel02_DisplayName": "Red Squirrel"}
        self.assertEqual(gen.display_name(text, "Squirrel!Squirrel02", "Squirrel 02"), "Red Squirrel")
        self.assertEqual(gen.display_name(text, "Made!Up99", "Made Up 99"), "Made Up 99")


class SameNameStaysDistinguishable(unittest.TestCase):
    def test_critter_name_equals_companion_name_in_report(self):
        j = job(report(critters=[fed(CRITTER_SQUIRREL_01, 1)]), "Foraging")
        self.assertEqual((j["critters"][0]["name"], j["critters"][0]["companion"]),
                         ("Classic Squirrel", "Classic Squirrel"))

    def test_two_unlocked_companions_with_one_name_get_their_variant_appended(self):
        from unittest import mock
        fake = {1: ("Twin", "X", "Foraging"), 2: ("Twin", "X", "Foraging"), 3: ("Solo", "X", "Foraging")}
        with mock.patch.dict("ddvhud.report.COMPANIONS", fake, clear=True):
            j = job(report([pet(1, 3), pet(2, 2), pet(3, 1)]), "Foraging")
        names = [c["name"] for c in j["unlocked"]]
        self.assertEqual(names, ["Twin (#1)", "Twin (#2)", "Solo"])


if __name__ == "__main__":
    unittest.main()
