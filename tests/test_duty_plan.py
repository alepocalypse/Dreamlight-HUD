import unittest

from ddvhud.duty_plan import duty_plan


def duty(text, path="Seafaring", weekly=None, current=0, target=5):
    return {"path": path, "text": text, "current": current, "target": target, "weekly": weekly}


def group(label, *duties):
    return {"label": label, "spans": len({d["path"] for d in duties}), "duties": list(duties)}


def shown(entries):   # tier, label, duty texts
    return [(e["tier"], e["label"], [d["text"] for d in e["duties"]]) for e in entries]


class DutyPlan(unittest.TestCase):
    def test_cross_star_path_groups_come_before_groups_within_one_star_path(self):
        a, b = duty("fish a"), duty("fish b")
        c, d = duty("scrooge", "Seafaring"), duty("scrooge", "Haunting")
        plan = duty_plan([a, b, c, d], [group("Fish", a, b), group("Scrooge", c, d)])
        self.assertEqual(shown(plan), [("cross", "Scrooge", ["scrooge", "scrooge"]),
                                       ("together", "Fish", ["fish a", "fish b"])])
        self.assertEqual(plan[0]["spans"], 2)

    def test_within_a_tier_the_group_advancing_most_duties_comes_first(self):
        a, b, c, d, e = (duty(t) for t in "abcde")
        plan = duty_plan([a, b, c, d, e], [group("Pair", a, b), group("Triple", c, d, e)])
        self.assertEqual([e["label"] for e in plan], ["Triple", "Pair"])

    def test_equal_groups_follow_the_star_path_save_order(self):
        a, b = duty("a", "Seafaring"), duty("b", "Seafaring")
        c, d = duty("c", "Haunting"), duty("d", "Haunting")
        duties = [a, b, c, d]
        self.assertEqual([e["label"] for e in duty_plan(duties, [group("Late", c, d), group("Early", a, b)])],
                         ["Early", "Late"])

    def test_duties_in_no_group_follow_as_singles_in_input_order(self):
        a, b = duty("fish a"), duty("fish b")
        x, y = duty("lone x", "Haunting"), duty("lone y", "Haunting", weekly=2)
        plan = duty_plan([x, a, b, y], [group("Fish", a, b)])
        self.assertEqual(shown(plan), [("together", "Fish", ["fish a", "fish b"]),
                                       ("single", "lone x", ["lone x"]), ("single", "lone y", ["lone y"])])
        self.assertEqual(plan[1]["spans"], 1)

    def test_a_duty_in_several_groups_is_listed_under_each_action_that_advances_it(self):
        any_fish, beach, seaweed = duty("any"), duty("beach"), duty("seaweed")
        plan = duty_plan([any_fish, beach, seaweed],
                         [group("Beach", any_fish, beach), group("Seaweed", any_fish, seaweed)])
        self.assertEqual(shown(plan), [("together", "Beach", ["any", "beach"]), ("together", "Seaweed", ["any", "seaweed"])])

    def test_a_duty_in_two_groups_is_not_also_listed_as_a_single(self):
        a, b, c = duty("a"), duty("b"), duty("c")
        plan = duty_plan([a, b, c], [group("First", a, b), group("Second", a, c)])
        self.assertEqual([e["tier"] for e in plan], ["together", "together"])

    def test_done_duties_are_absent(self):
        a, b, done = duty("a"), duty("b"), duty("done", current=5)
        lone_done = duty("lone done", target=3, current=3)
        plan = duty_plan([a, b, done, lone_done], [group("Pair", a, b, done)])
        self.assertEqual(shown(plan), [("together", "Pair", ["a", "b"])])

    def test_group_input_order_does_not_change_the_plan(self):
        a, b, c, d, e = (duty(t) for t in "abcde")
        groups = [group("One", a, b), group("Two", c, d), group("Three", c, e)]
        duties = [a, b, c, d, e]
        want = duty_plan(duties, groups)
        self.assertEqual(duty_plan(duties, list(reversed(groups))), want)
        self.assertEqual(duty_plan(duties, groups), want)

    def test_every_open_duty_appears_at_least_once(self):
        a, b, c, d, e = duty("a", "Seafaring"), duty("b", "Haunting"), duty("c", "Haunting"), duty("d", "Seafaring"), duty("e")
        plan = duty_plan([a, b, c, d, e], [group("X", a, b, c), group("Y", b, d), group("Z", c, d)])
        texts = {x["text"] for en in plan for x in en["duties"]}
        self.assertEqual(texts, {"a", "b", "c", "d", "e"})

    def test_a_group_with_only_one_open_duty_gives_it_up_as_a_single(self):
        a, b = duty("a"), duty("b", current=5)
        self.assertEqual(shown(duty_plan([a, b], [group("Pair", a, b)])), [("single", "a", ["a"])])

    def test_a_group_whose_second_star_path_is_done_is_no_longer_cross(self):
        s1, s2, h1 = duty("s1"), duty("s2"), duty("h1", "Haunting", current=5)
        plan = duty_plan([s1, s2, h1], [group("G", s1, s2, h1)])
        self.assertEqual([(e["tier"], e["spans"]) for e in plan], [("together", 1)])

    def test_ungrouped_row_duties_of_one_family_merge_into_one_entry_at_the_first_one(self):
        a = duty("lone a")
        r = dict(duty("Mine for red gems."), family="Mine gems", row="Red")
        b = duty("lone b")
        o = dict(duty("Mine 20 orange gems.", weekly=1), family="Mine gems", row="Orange")
        f = dict(duty("Pick some yellow flowers"), family="Pick flowers", row="Yellow")
        plan = duty_plan([a, r, b, o, f], [])
        self.assertEqual(shown(plan), [("single", "lone a", ["lone a"]),
                                       ("rows", "Mine gems", ["Mine for red gems.", "Mine 20 orange gems."]),
                                       ("single", "lone b", ["lone b"]),
                                       ("rows", "Pick flowers", ["Pick some yellow flowers"])])   # a lone family duty is still its family's entry

    def test_a_colour_duty_already_in_a_group_is_not_merged(self):
        r = dict(duty("red"), family="Mine gems", row="Red")
        o = dict(duty("orange"), family="Mine gems", row="Orange")
        b = dict(duty("blue"), family="Mine gems", row="Blue")
        x = duty("x")
        plan = duty_plan([r, o, b, x], [group("Orange pair", o, x)])
        self.assertEqual([e["tier"] for e in plan], ["together", "rows"])
        self.assertEqual([d["text"] for d in plan[1]["duties"]], ["red", "blue"])

    def test_a_group_wholly_inside_one_family_dissolves_into_that_familys_entry(self):
        a = dict(duty("any fish"), family="Fish", row="Any fish")
        b = dict(duty("seaweed"), family="Fish", row="Seaweed")
        c = dict(duty("bream", "Dreamlight"), family="Fish", row="Bream")
        plan = duty_plan([a, b, c], [group("Seaweed", a, b), group("Bream", a, c)])
        self.assertEqual(shown(plan), [("rows", "Fish", ["any fish", "seaweed", "bream"])])

    def test_a_group_with_a_duty_outside_the_family_stays_a_group(self):
        a = dict(duty("any fish"), family="Fish", row="Any fish")
        x = duty("something else")
        plan = duty_plan([a, x], [group("Both", a, x)])
        self.assertEqual([e["tier"] for e in plan], ["together"])

    def test_rows_in_an_entry_go_from_the_most_generic_to_the_least(self):
        gem = dict(duty("purple"), family="Mine", row="Purple Gems", rank=2)
        any_gem = dict(duty("any gem"), family="Mine", row="Any Gem", rank=0)
        nodes = dict(duty("nodes"), family="Mine", row="Nodes", rank=-1)
        blue = dict(duty("blue"), family="Mine", row="Blue Gems", rank=2)
        unranked = dict(duty("odd"), family="Mine", row="Odd")
        plan = duty_plan([gem, any_gem, nodes, blue, unranked], [])
        self.assertEqual(shown(plan), [("rows", "Mine", ["nodes", "any gem", "purple", "blue", "odd"])])   # ties keep the list order


if __name__ == "__main__":
    unittest.main()
