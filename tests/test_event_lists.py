import unittest
from datetime import datetime, timezone

from ddvhud.event_duties import EVENTS, event_lists
from ddvhud.event_duty_data import EVENT_DUTIES

DURING = datetime(2026, 10, 26, 22, 0, tzinfo=timezone.utc)
SUGAR_RUSH, TRICK_OR_TREAT, PUMPKINS, KNOCK = 2110100132, 2110100133, 2110100136, 2110100411


def ach(current, claimed=0, state="OnGoing"):
    return {"current": current, "claimed": claimed, "state": state}


class EventDutyData(unittest.TestCase):
    def test_the_trick_or_treat_duties_are_the_games(self):
        key, title, hint, milestones = EVENT_DUTIES[SUGAR_RUSH]
        self.assertEqual((key, title, hint), ("Halloween", "Sugar Rush", "Eat a lot of Candies!"))
        self.assertEqual([count for count, _ in milestones], [15, 30, 45])
        self.assertEqual(EVENT_DUTIES[KNOCK][1], "Sweet 'n' Scary")

    def test_every_event_in_the_table_has_duties(self):
        keys = {row[0] for row in EVENT_DUTIES.values()}
        self.assertLessEqual(set(EVENTS), keys)


class EventLists(unittest.TestCase):
    def test_an_event_that_is_on_lists_its_open_duties_with_the_next_milestone(self):
        [ev] = event_lists({SUGAR_RUSH: ach(1), KNOCK: ach(1, claimed=1)}, DURING)
        self.assertEqual((ev["key"], ev["title"], ev["ends"]), ("Halloween", "Trick-or-Treat Event", "2026-10-31T14:00:00Z"))
        self.assertEqual([(d["text"], d["current"], d["target"], d["done"]) for d in ev["duties"]],
                         [("Sugar Rush", 1, 15, False), ("Sweet 'n' Scary", 1, 2, False)])
        self.assertEqual(ev["duties"][1]["hint"], "Perform 2 Trick or Treat actions on lit lanterns.")
        self.assertEqual(ev["duties"][1]["reward"], {"amount": 1, "currency": "Halloween Town Small Fence Recipe"})

    def test_a_duty_at_its_milestone_is_done_until_claimed_then_moves_on_or_leaves(self):
        [ev] = event_lists({SUGAR_RUSH: ach(15), PUMPKINS: ach(100, claimed=100, state="Completed")}, DURING)
        self.assertEqual([(d["text"], d["done"]) for d in ev["duties"]], [("Sugar Rush", True)])
        [ev] = event_lists({SUGAR_RUSH: ach(15, claimed=15)}, DURING)
        self.assertEqual((ev["duties"][0]["target"], ev["duties"][0]["done"]), (30, False))

    def test_nothing_outside_the_window_or_without_the_events_duties(self):
        self.assertEqual(event_lists({SUGAR_RUSH: ach(1)}, datetime(2026, 11, 1, tzinfo=timezone.utc)), [])
        self.assertEqual(event_lists({SUGAR_RUSH: ach(1)}, datetime(2026, 10, 14, 13, tzinfo=timezone.utc)), [])
        self.assertEqual(event_lists({2110100137: ach(1), 5: ach(1)}, DURING), [])   # a Christmas duty, an unknown id
        self.assertEqual(event_lists({}, DURING), [])


if __name__ == "__main__":
    unittest.main()
