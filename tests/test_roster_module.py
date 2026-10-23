import unittest

from ddvhud.roster import Roster as _Roster
from ddvhud.saveview import SaveView

RESET = "2026-10-19T05:00:00Z"
BEFORE_RESET = "2026-10-19T04:00:00Z"
AFTER_RESET = "2026-10-19T06:00:00Z"
MEAL = 30300001


def Roster(characters, reset):
    return _Roster(SaveView({"World": {"Characters": characters}, "LastDailyReset": reset}))


def char(cid, status="InVillage", level=0, talked=False, slots=(), gifted_at=None, profession=0):
    c = {"Base": {"id": cid}, "Status": "CharacterStatus_" + status, "FriendshipLevel": level,
         "DiscussedWithTheAvatarToday": talked, "ProfessionID": profession,
         "PreferredItemSlots": [{"PreferredItemId": i, "Gifted": g} for i, g in slots]}
    if gifted_at:
        c["LastGiftDate"] = gifted_at
    return c


class Summary(unittest.TestCase):
    def test_counts_by_status_and_max_level(self):
        r = Roster([char(10000003, "InVillage", 10), char(10000004, "InRealm", 3),
                    char(10000007, "Secret"), char(10000100, "Secret"), char(10000006, "Gone")], RESET)
        self.assertEqual((r.village, r.realm, r.unavailable, r.unidentified, r.max_level), (1, 1, 1, 1, 1))

    def test_only_in_village_characters_are_villager_rows(self):
        r = Roster([char(10000003, level=4, talked=True), char(10000004, "InRealm")], RESET)
        self.assertEqual([(v["name"], v["level"], v["talk_needed"]) for v in r.villagers], [("Mickey Mouse", 4, False)])
        self.assertEqual([(n["name"], n["where"]) for n in r.not_in_village], [("Goofy", "realm")])


class Todo(unittest.TestCase):
    def names(self, chars):
        return [v["name"] for v in Roster(chars, RESET).todo]

    def test_talk_alone_makes_todo(self):
        self.assertEqual(self.names([char(10000003, level=2)]), ["Mickey Mouse"])

    def test_gift_alone_makes_todo(self):
        self.assertEqual(self.names([char(10000003, talked=True, slots=[(MEAL, False)])]), ["Mickey Mouse"])

    def test_done_villager_is_not_todo(self):
        self.assertEqual(self.names([char(10000003, talked=True, slots=[(MEAL, True)], gifted_at=AFTER_RESET)]), [])

    def test_max_level_is_never_todo(self):
        self.assertEqual(self.names([char(10000003, level=10)]), [])

    def test_gift_before_reset_does_not_count_as_given(self):
        r = Roster([char(10000003, talked=True, slots=[(MEAL, True)], gifted_at=BEFORE_RESET)], RESET)
        self.assertEqual(len(r.villagers[0]["gifts"]), 1)
        self.assertEqual(len(r.todo), 1)

    def test_without_saved_reset_flagged_gifts_count_as_given(self):
        r = Roster([char(10000003, talked=True, slots=[(MEAL, True)])], None)
        self.assertEqual(r.todo, [])

    def test_by_priority_orders_highest_level_then_name(self):
        r = Roster([char(10000004, level=3), char(10000003, level=3), char(10000007, level=7)], RESET)
        self.assertEqual([v["name"] for v in r.todo_by_priority()], ["The Beast", "Goofy", "Mickey Mouse"])
