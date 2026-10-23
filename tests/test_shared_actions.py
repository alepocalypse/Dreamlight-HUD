import unittest

from ddvhud.duty_requirements import Requirement
from ddvhud.shared_actions import do_together

ANY_FISH = Requirement("catch_fish", "Catch any fish")
BEACH_FISH = Requirement("catch_fish", "Catch fish at Dazzle Beach", place="Dazzle Beach")
SEAWEED = Requirement("catch_fish", "Catch Seaweed", items=(1,))
SCROOGE = Requirement("buy", "Buy from Scrooge McDuck", target="Scrooge McDuck")
ANY_GEM = Requirement("mine_gem", "Mine any gem")
RED_GEM = Requirement("mine_gem", "Mine red gems", colour="Red")
BLUE_GEM = Requirement("mine_gem", "Mine blue gems", colour="Blue")


def duty(text, requires, path="Seafaring", weekly=None):
    return {"path": path, "text": text, "current": 0, "target": 5, "weekly": weekly, "requires": requires}


def shown(group):   # the group's label, its Star Path count and its duty texts
    return group["label"], group["spans"], [d["text"] for d in group["duties"]]


class DoTogether(unittest.TestCase):
    def test_equal_requirements_in_two_star_paths_form_one_group(self):
        groups = do_together([duty("Buy something from Scrooge.", SCROOGE, "Seafaring"),
                              duty("Buy something from Scrooge.", Requirement("buy", "Buy from Scrooge McDuck",
                                                                              target="Scrooge McDuck"), "Haunting")])
        self.assertEqual([shown(g) for g in groups],
                         [("Buy from Scrooge McDuck", 2, ["Buy something from Scrooge.", "Buy something from Scrooge."])])
        self.assertEqual([d["path"] for d in groups[0]["duties"]], ["Seafaring", "Haunting"])

    def test_the_group_duties_do_not_carry_the_requirement_object(self):
        [g] = do_together([duty("a", SCROOGE), duty("b", SCROOGE)])
        self.assertEqual(g["duties"][0], {"path": "Seafaring", "text": "a", "current": 0, "target": 5, "weekly": None})

    def test_wider_duties_join_the_group_of_the_narrowest_action(self):
        groups = do_together([duty("any", ANY_FISH), duty("beach", BEACH_FISH), duty("weekly", ANY_FISH, weekly=1)])
        self.assertEqual([shown(g) for g in groups],
                         [("Catch fish at Dazzle Beach", 1, ["any", "beach", "weekly"])])

    def test_incomparable_narrow_requirements_each_get_a_group_sharing_the_wide_duty(self):
        groups = do_together([duty("any", ANY_FISH), duty("beach", BEACH_FISH), duty("weed", SEAWEED)])
        self.assertEqual([shown(g) for g in groups],
                         [("Catch fish at Dazzle Beach", 1, ["any", "beach"]), ("Catch Seaweed", 1, ["any", "weed"])])

    def test_any_gem_groups_with_a_coloured_gem_but_colours_stay_apart(self):
        groups = do_together([duty("any", ANY_GEM), duty("red", RED_GEM), duty("blue", BLUE_GEM)])
        self.assertEqual([shown(g) for g in groups],
                         [("Mine red gems", 1, ["any", "red"]), ("Mine blue gems", 1, ["any", "blue"])])

    def test_duties_with_nothing_in_common_make_no_groups(self):
        self.assertEqual(do_together([duty("fish", ANY_FISH), duty("gem", SCROOGE), duty("blue", BLUE_GEM, "Haunting"), duty("red", RED_GEM)]),
                         [])
        self.assertEqual(do_together([]), [])

    def test_unknown_requirements_are_never_grouped(self):
        self.assertEqual(do_together([duty("a", Requirement("unknown")), duty("b", Requirement("unknown"))]), [])

    def test_a_group_across_both_star_paths_says_so_and_lists_weekly_duties(self):
        [g] = do_together([duty("any", ANY_FISH, "Seafaring"), duty("beach", BEACH_FISH, "Haunting", weekly=2)])
        self.assertEqual((g["spans"], [(d["path"], d["weekly"]) for d in g["duties"]]),
                         (2, [("Seafaring", None), ("Haunting", 2)]))


if __name__ == "__main__":
    unittest.main()
