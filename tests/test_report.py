import unittest
from datetime import datetime, timezone

from ddvhud.report import SHOW_MIN_WOOD, build_report

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
MICKEY, MINNIE, GOOFY, DONALD = 10000003, 10000046, 10000004, 10000011
UNNAMED_VILLAGER = 10000132  # placeholder: must be handled via a roster id with no name


def char(cid, status, level=0, prof=0):
    return {"Base": {"id": cid}, "Status": "CharacterStatus_" + status,
            "FriendshipLevel": level, "ProfessionID": prof}


def profile(*chars):
    return {"World": {"Characters": list(chars)}}


class SummaryBuckets(unittest.TestCase):
    def test_each_bucket(self):
        r = build_report(profile(
            char(MICKEY, "InVillage", 10),
            char(MINNIE, "InVillage", 3),
            char(GOOFY, "InRealm", 10),
            char(DONALD, "Secret"),
        ), NOW)
        s = r["summary"]
        self.assertEqual(s["total"], 4)
        self.assertEqual(s["available"], {"total": 3, "village": 2, "realm": 1})
        self.assertEqual(s["unavailable"], 1)
        self.assertEqual(s["max_level"], 2)
        self.assertEqual(s["unidentified"], 0)

    def test_secret_not_on_roster_is_unidentified_only(self):
        r = build_report(profile(
            char(MICKEY, "InVillage", 1),
            char(10000101, "Secret"),   # Dark Portal: not a Villager
            char(10000118, "Secret"),   # The Lorekeeper
            char(99999999, "Secret"),
        ), NOW)
        s = r["summary"]
        self.assertEqual(s["total"], 1)
        self.assertEqual(s["unavailable"], 0)
        self.assertEqual(s["unidentified"], 3)

    def test_non_villagers_are_not_on_roster(self):
        ids = [10000100, 10000101, 10000102, 10000118, 10000124, 10000126]
        r = build_report(profile(*[char(i, "Secret") for i in ids]), NOW)
        self.assertEqual(r["summary"]["total"], 0)
        self.assertEqual(r["summary"]["unidentified"], 6)

    def test_the_forgotten_and_extra_ids_are_villagers(self):
        ids = [10000098, 10000130, 10000131, 10000020, 10000025,
               10000040, 10000179, 10000180, 10000182]
        r = build_report(profile(*[char(i, "Secret") for i in ids]), NOW)
        self.assertEqual(r["summary"]["unavailable"], 9)


class Names(unittest.TestCase):
    def test_named_and_unnamed_villagers(self):
        from ddvhud import villagers
        r = build_report(profile(char(MICKEY, "InVillage", 2)), NOW)
        self.assertEqual(r["villagers"][0]["name"], "Mickey Mouse")
        # an Available entry that is not in the name table shows as Villager #id
        r = build_report(profile(char(12345678, "InVillage", 2)), NOW)
        self.assertEqual(r["villagers"][0]["name"], "Villager #12345678")
        self.assertEqual(r["summary"]["total"], 1)  # Available always counts

GARDENING, FISHING, MINING = 1500000001, 1500000002, 1500000003


def cards(r):
    return {c["name"]: c for c in r["professions"]}


class ProfessionCards(unittest.TestCase):
    def test_six_cards_in_order_even_when_empty(self):
        r = build_report(profile(), NOW)
        self.assertEqual([c["name"] for c in r["professions"]],
                         ["Digging", "Fishing", "Foraging", "Gardening", "Mining", "Time-bending"])
        for c in r["professions"]:
            self.assertEqual((c["count"], c["not_max"], c["villagers"], c["done"]), (0, 0, [], []))

    def test_counts_and_villagers_below_max_sorted_lowest_level_first(self):
        r = build_report(profile(
            char(MICKEY, "InVillage", 10, GARDENING),
            char(MINNIE, "InVillage", 2, GARDENING),
            char(GOOFY, "InVillage", 5, GARDENING),
            char(DONALD, "InVillage", 7, FISHING),
        ), NOW)
        g = cards(r)["Gardening"]
        self.assertEqual(g["count"], 3)
        self.assertEqual(g["not_max"], 2)
        # only the Villagers below Max level are listed with their level ...
        self.assertEqual(g["villagers"], [
            {"name": "Minnie Mouse", "level": 2},
            {"name": "Goofy", "level": 5},
        ])
        # ... the ones at Max level are just names, for one short "done" line
        self.assertEqual(g["done"], ["Mickey Mouse"])
        self.assertEqual(cards(r)["Fishing"]["count"], 1)

    def test_max_level_names_sorted_by_name_and_same_level_by_name(self):
        r = build_report(profile(
            char(MINNIE, "InVillage", 10, MINING),
            char(GOOFY, "InVillage", 10, MINING),
            char(MICKEY, "InVillage", 10, MINING),
            char(DONALD, "InVillage", 4, MINING),
            char(10000053, "InVillage", 4, MINING),   # Ariel: same level as Donald, sorts first by name
        ), NOW)
        m = cards(r)["Mining"]
        self.assertEqual((m["count"], m["not_max"]), (5, 2))
        self.assertEqual(m["villagers"], [{"name": "Ariel", "level": 4}, {"name": "Donald Duck", "level": 4}])
        self.assertEqual(m["done"], ["Goofy", "Mickey Mouse", "Minnie Mouse"])

    def test_card_with_everyone_at_max_lists_no_villagers(self):
        r = build_report(profile(char(MICKEY, "InVillage", 10, FISHING), char(MINNIE, "InVillage", 10, FISHING)), NOW)
        f = cards(r)["Fishing"]
        self.assertEqual((f["count"], f["not_max"], f["villagers"]), (2, 0, []))
        self.assertEqual(f["done"], ["Mickey Mouse", "Minnie Mouse"])

    def test_villagers_with_no_profession_are_listed_lowest_level_first_with_max_level_last(self):
        r = build_report(profile(char(MICKEY, "InVillage", 10, 0), char(DONALD, "InVillage", 4, 0),
                                 char(GOOFY, "InVillage", 4, 0), char(MINNIE, "InVillage", 6, MINING),
                                 char(10000053, "InRealm", 2, 0)), NOW)   # a realm Villager is not in the village
        self.assertEqual(r["no_profession"], [{"name": "Donald Duck", "level": 4}, {"name": "Goofy", "level": 4},
                                              {"name": "Mickey Mouse", "level": 10}])

    def test_everyone_with_a_profession_leaves_the_no_profession_list_empty(self):
        self.assertEqual(build_report(profile(char(MICKEY, "InVillage", 4, FISHING)), NOW)["no_profession"], [])

    def test_unknown_profession_gets_its_own_card(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4, 1599999999)), NOW)
        self.assertEqual(r["professions"][-1]["name"], "Unknown profession")
        self.assertEqual(r["professions"][-1]["count"], 1)
        self.assertEqual(sum(c["count"] for c in r["professions"][:6]), 0)

    def test_several_unknown_ids_share_one_card(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4, 1599999999),
                                 char(MINNIE, "InVillage", 4, 1500000042)), NOW)
        self.assertEqual(len(r["professions"]), 7)
        self.assertEqual(r["professions"][-1]["count"], 2)

    def test_no_unknown_card_without_unknown_ids(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4, MINING)), NOW)
        self.assertEqual(len(r["professions"]), 6)

    def test_villagers_without_profession_are_not_counted_on_profession_cards(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4)), NOW)
        self.assertEqual(sum(c["count"] for c in r["professions"]), 0)


TIMEB = 1500000006
V = [10000003, 10000046, 10000004, 10000011, 10000053, 10000100, 10000101, 10000102]  # Mickey, Minnie, Goofy, Donald, Ariel, ...


def bonus(prof, name, *levels):
    r = build_report(profile(*[char(V[i], "InVillage", lv, prof) for i, lv in enumerate(levels)]), NOW)
    return cards(r)[name]["bonus"]


class BonusChance(unittest.TestCase):
    """Wiki Roles and Bonuses: chance = base + 3.5 * active level + 1 * each other level."""

    def test_gardening_base_is_20_and_mining_base_is_25(self):
        g, m = bonus(GARDENING, "Gardening", 0), bonus(MINING, "Mining", 0)
        self.assertEqual((g["base"], g["chance"]), (20, 20.0))
        self.assertEqual((m["base"], m["chance"]), (25, 25.0))

    def test_single_villager_is_active_with_no_inactive_part(self):
        b = bonus(FISHING, "Fishing", 6)
        self.assertEqual((b["chance"], b["active_level"]), (46.0, 6))

    def test_two_villagers_best_is_active(self):
        b = bonus(MINING, "Mining", 2, 8)
        self.assertEqual((b["chance"], b["active_level"]), (25 + 28 + 2, 8))

    def test_mix_of_levels_with_half_percent(self):
        # Time-bending 6, 5, 4: 25 + 21 + 5 + 4 = 55; Gardening 5 alone: 20 + 17.5
        self.assertEqual(bonus(TIMEB, "Time-bending", 4, 6, 5)["chance"], 55.0)
        self.assertEqual(bonus(GARDENING, "Gardening", 5)["chance"], 37.5)

    def test_all_level_10_chance(self):
        b = bonus(MINING, "Mining", 10, 10, 10)
        self.assertEqual(b["chance"], 80.0)
        self.assertNotIn("potential", b)

    def test_no_villagers_no_bonus(self):
        r = build_report(profile(), NOW)
        for c in r["professions"]:
            self.assertIsNone(c["bonus"])

    def test_above_100_not_capped_with_tier_note(self):
        b = bonus(GARDENING, "Gardening", 10, 10, 10, 10, 10, 10, 4, 3)
        self.assertEqual(b["chance"], 20 + 35 + 50 + 4 + 3)
        self.assertEqual(b["chance"], 112.0)
        self.assertIn("guaranteed 1 bonus item", b["tier"])

    def test_exactly_100_is_one_bonus_item_and_below_has_no_tier(self):
        self.assertEqual(bonus(MINING, "Mining", 10, 10, 10, 10, 10)["chance"], 100.0)
        self.assertIn("1 bonus item", bonus(MINING, "Mining", 10, 10, 10, 10, 10)["tier"])
        self.assertIsNone(bonus(MINING, "Mining", 10, 10, 10, 10)["tier"])

    def test_levels_of_max_villagers_count_although_split_off_the_list(self):
        # one Villager at 10 is only in "done", yet is the active one
        self.assertEqual(bonus(FISHING, "Fishing", 10, 3)["chance"], 25 + 35 + 3)


def todo(r):
    return r["todo"]


class TodoList(unittest.TestCase):
    def test_max_level_and_unavailable_never_appear(self):
        r = build_report(profile(
            char(MICKEY, "InVillage", 10),
            char(MINNIE, "Secret", 0),
            char(GOOFY, "InVillage", 9),
        ), NOW)
        self.assertEqual([t["name"] for t in todo(r)], ["Goofy"])

    def test_ordered_highest_level_then_name(self):
        r = build_report(profile(
            char(GOOFY, "InVillage", 1),
            char(DONALD, "InVillage", 6),
            char(MINNIE, "InVillage", 2),
            char(MICKEY, "InVillage", 2),
        ), NOW)
        self.assertEqual([t["name"] for t in todo(r)],
                         ["Donald Duck", "Mickey Mouse", "Minnie Mouse", "Goofy"])
        self.assertEqual([t["location"] for t in todo(r)], ["valley"] * 4)

    def test_single_card(self):
        r = build_report(profile(char(GOOFY, "InVillage", 7)), NOW)
        self.assertEqual([t["name"] for t in todo(r)], ["Goofy"])

    def test_row_has_profession_level_and_none(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4, MINING),
                                 char(MINNIE, "InVillage", 5)), NOW)
        self.assertEqual((todo(r)[1]["name"], todo(r)[1]["profession"], todo(r)[1]["level"]),
                         ("Mickey Mouse", "Mining", 4))
        self.assertIsNone(todo(r)[0]["profession"])

    def test_row_carries_the_villager_id(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4), char(12345678, "InVillage", 3)), NOW)
        self.assertEqual([t["id"] for t in todo(r)], [MICKEY, 12345678])

    def test_unnamed_villager_is_listed(self):
        r = build_report(profile(char(12345678, "InVillage", 3)), NOW)
        self.assertEqual(todo(r)[0]["name"], "Villager #12345678")


RESET = "2026-10-19T05:00:00Z"   # NOW (12:00 on the 19th) is inside this game day
BEFORE_RESET = "2026-10-18T12:00:00Z"
AFTER_RESET = "2026-10-19T09:30:00Z"


def todo_char(talked=False, gifted=(), gift_date=AFTER_RESET, level=3):
    c = char(MICKEY, "InVillage", level)
    c["DiscussedWithTheAvatarToday"] = talked
    c["LastGiftDate"] = gift_date
    c["PreferredItemSlots"] = [{"PreferredItemId": i, "Gifted": g} for i, g in enumerate(gifted)]
    return c


def row(c, now=NOW, reset=RESET):
    p = profile(c)
    if reset:
        p["LastDailyReset"] = reset
    return build_report(p, now)["todo"][0]


def row_of(p, now=NOW):
    p.setdefault("LastDailyReset", RESET)
    return build_report(p, now)["todo"][0]


class DailyTalk(unittest.TestCase):
    def test_not_done_is_flagged(self):
        self.assertTrue(row(todo_char(talked=False))["daily_talk_needed"])

    def test_done_today_is_not_flagged(self):
        self.assertFalse(row(todo_char(talked=True, gifted=(False,)))["daily_talk_needed"])

    def test_done_flag_is_trusted_even_when_now_is_well_past_the_recorded_reset(self):
        # real case (Buzz Lightyear): saved after a daily talk on the 20th, yet the game
        # left LastDailyReset at the 19th; the saved flag is the truth
        later = datetime(2026, 10, 20, 5, 31, tzinfo=timezone.utc)
        self.assertFalse(row(todo_char(talked=True, gifted=(False,)), now=later)["daily_talk_needed"])
        self.assertTrue(row(todo_char(talked=False), now=later)["daily_talk_needed"])

    def test_missing_reset_trusts_the_flag(self):
        self.assertFalse(row(todo_char(talked=True, gifted=(False,)), reset=None)["daily_talk_needed"])


def slots(*pairs):
    return [{"PreferredItemId": i, "Gifted": g} for i, g in pairs]


class WantedGifts(unittest.TestCase):
    A, B, C = 31600021, 30800073, 30300180   # Shiny Amethyst, White Bell Flower, Sweet Herring

    def wanted(self, gifted, **kw):
        c = todo_char(**kw)
        c["PreferredItemSlots"] = slots(*zip((self.A, self.B, self.C), gifted))
        return [g["name"] for g in row(c)["gifts"]]

    def test_three_wanted_gifts_in_slot_order(self):
        self.assertEqual(self.wanted([False] * 3),
                         ["Shiny Amethyst", "White Bell Flower", "Sweet Herring"])

    def test_a_given_gift_is_omitted(self):
        self.assertEqual(self.wanted([False, True, False]), ["Shiny Amethyst", "Sweet Herring"])

    def test_all_three_given_leaves_no_gifts(self):
        self.assertEqual(self.wanted([True] * 3), [])

    def test_gift_recorded_before_the_reset_is_wanted_again(self):
        self.assertEqual(self.wanted([True, True, False], gift_date=BEFORE_RESET),
                         ["Shiny Amethyst", "White Bell Flower", "Sweet Herring"])

    def test_gifts_after_the_reset_stay_given_when_now_is_past_the_next_one(self):
        c = todo_char()
        c["PreferredItemSlots"] = slots((self.A, True), (self.B, False))
        later = datetime(2026, 10, 20, 6, 0, tzinfo=timezone.utc)
        self.assertEqual([g["name"] for g in row(c, now=later)["gifts"]], ["White Bell Flower"])

    def test_two_wanted_gifts_with_one_name_get_their_id_appended(self):
        from unittest import mock
        c = todo_char()
        c["PreferredItemSlots"] = slots((self.A, False), (self.B, False), (self.C, False))
        with mock.patch.dict("ddvhud.items.ITEMS", {self.A: "Twin", self.B: "Twin", self.C: "Solo"}, clear=True):
            self.assertEqual([g["name"] for g in row(c)["gifts"]], [f"Twin (#{self.A})", f"Twin (#{self.B})", "Solo"])

    def test_unknown_item_id_shows_as_item_number(self):
        c = todo_char()
        c["PreferredItemSlots"] = slots((99999999, False))
        self.assertEqual([g["name"] for g in row(c)["gifts"]], ["Item #99999999"])

    def test_missing_slots_means_no_gifts(self):
        self.assertEqual(row(char(MICKEY, "InVillage", 3))["gifts"], [])

    def test_old_count_fields_are_gone(self):
        r = row(todo_char())
        self.assertNotIn("gifts_given", r)
        self.assertNotIn("gifts_total", r)


def chest(cid, items, parent=40001190, mine=True):
    c = {"ID": cid, "Size": 48, "BelongsToPlayer": mine, "Inventory": [
        {"ItemID": i, "Amount": a, "State": {}} for i, a in items]}
    if parent is not None:
        c["ParentItemID"] = parent
    return c


class InChest(unittest.TestCase):
    A, B, C = 31600021, 30800073, 30300180   # Shiny Amethyst, White Bell Flower, Sweet Herring

    def gifts(self, *containers, drop_key=False):
        c = todo_char()
        c["PreferredItemSlots"] = slots((self.A, False), (self.B, False), (self.C, False))
        p = profile(c)
        if not drop_key:
            p["Player"] = {"ContainerInventories": {str(c["ID"]): c for c in containers}}
        return {g["name"]: g for g in row_of(p)["gifts"]}

    def test_item_in_one_chest(self):
        g = self.gifts(chest(100, [(self.A, 7)]))
        self.assertEqual((g["Shiny Amethyst"]["in_chest"], g["Shiny Amethyst"]["chest_count"]), (True, 7))
        self.assertEqual((g["White Bell Flower"]["in_chest"], g["White Bell Flower"]["chest_count"]), (False, 0))

    def test_split_across_two_chests_is_summed(self):
        g = self.gifts(chest(100, [(self.A, 7)]), chest(101, [(self.B, 1), (self.A, 5)], parent=40000229))
        self.assertEqual(g["Shiny Amethyst"]["chest_count"], 12)

    def test_only_in_backpack_and_storage_is_not_in_chest(self):
        g = self.gifts(chest(0, [(self.A, 9)], parent=None), chest(1, [(self.A, 4)], parent=None))
        self.assertEqual((g["Shiny Amethyst"]["in_chest"], g["Shiny Amethyst"]["chest_count"]), (False, 0))

    def test_only_in_non_chest_furniture_is_not_in_chest(self):
        g = self.gifts(chest(200, [(self.A, 3)], mine=False))
        self.assertFalse(g["Shiny Amethyst"]["in_chest"])

    def test_empty_slots_do_not_count(self):
        g = self.gifts(chest(100, [(0, 50), (self.A, 0)]) | {"Inventory": [
            {"ItemID": 0, "Amount": 50}, {"ItemID": self.A, "Amount": 0}, {}, {"Amount": 5}]})
        self.assertEqual((g["Shiny Amethyst"]["in_chest"], g["Shiny Amethyst"]["chest_count"]), (False, 0))

    def test_cooked_dish_with_meal_state_in_chest(self):
        c = chest(100, [])
        c["Inventory"] = [{"ItemID": self.C, "Amount": 2, "State": {"MealData": {"Quality": 3}}}]
        g = self.gifts(c)
        self.assertEqual((g["Sweet Herring"]["in_chest"], g["Sweet Herring"]["chest_count"]), (True, 2))

    def test_no_containers_at_all(self):
        for g in (self.gifts(), self.gifts(drop_key=True)):
            self.assertEqual([(x["in_chest"], x["chest_count"]) for x in g.values()], [(False, 0)] * 3)

    def test_same_name_gifts_each_get_their_own_count(self):
        from unittest import mock
        c = todo_char()
        c["PreferredItemSlots"] = slots((self.A, False), (self.B, False))
        p = profile(c)
        p["Player"] = {"ContainerInventories": {"100": chest(100, [(self.B, 4)])}}
        with mock.patch.dict("ddvhud.items.ITEMS", {self.A: "Twin", self.B: "Twin"}, clear=True):
            gifts = row_of(p)["gifts"]
        self.assertEqual([(g["name"], g["chest_count"]) for g in gifts],
                         [(f"Twin (#{self.A})", 0), (f"Twin (#{self.B})", 4)])


class InBackpack(unittest.TestCase):
    A, B, C = 31600021, 30800073, 30300180

    def gifts(self, *containers, drop_key=False):
        c = todo_char()
        c["PreferredItemSlots"] = slots((self.A, False), (self.B, False), (self.C, False))
        p = profile(c)
        if not drop_key:
            p["Player"] = {"ContainerInventories": {str(c["ID"]): c for c in containers}}
        return {g["name"]: g for g in row_of(p)["gifts"]}

    def counts(self, g):
        return {n: (x["backpack_count"], x["chest_count"]) for n, x in g.items()}

    def test_backpack_only(self):
        g = self.gifts(chest(0, [(self.A, 3)], parent=None))
        self.assertEqual(g["Shiny Amethyst"]["backpack_count"], 3)
        self.assertEqual(g["Shiny Amethyst"]["chest_count"], 0)
        self.assertEqual(g["White Bell Flower"]["backpack_count"], 0)

    def test_chest_only(self):
        g = self.gifts(chest(100, [(self.A, 7)]))
        self.assertEqual(self.counts(g)["Shiny Amethyst"], (0, 7))

    def test_both(self):
        g = self.gifts(chest(0, [(self.A, 2)], parent=None), chest(100, [(self.A, 7)]))
        self.assertEqual(self.counts(g)["Shiny Amethyst"], (2, 7))

    def test_neither(self):
        g = self.gifts(chest(0, [(self.B, 2)], parent=None))
        self.assertEqual(self.counts(g)["Shiny Amethyst"], (0, 0))

    def test_stack_split_over_two_slots(self):
        g = self.gifts(chest(0, [(self.A, 3), (self.B, 1), (self.A, 4)], parent=None))
        self.assertEqual(g["Shiny Amethyst"]["backpack_count"], 7)

    def test_storage_only_is_not_backpack(self):
        g = self.gifts(chest(0, [], parent=None), chest(1, [(self.A, 4)], parent=None))
        self.assertEqual(g["Shiny Amethyst"]["backpack_count"], 0)

    def test_empty_slots_ignored(self):
        bp = chest(0, [], parent=None)
        bp["Inventory"] = [{"ItemID": 0, "Amount": 50}, {"ItemID": self.A, "Amount": 0}, {}, {"Amount": 5}]
        self.assertEqual(self.gifts(bp)["Shiny Amethyst"]["backpack_count"], 0)

    def test_no_containers(self):
        for g in (self.gifts(), self.gifts(drop_key=True)):
            self.assertEqual([x["backpack_count"] for x in g.values()], [0, 0, 0])

    def test_backpack_identified_by_id_field(self):
        bp = chest(0, [(self.A, 5)], parent=None)
        p = profile(todo_char())
        c = p["World"]["Characters"][0]
        c["PreferredItemSlots"] = slots((self.A, False))
        p["Player"] = {"ContainerInventories": {"weird": bp}}
        self.assertEqual(row_of(p)["gifts"][0]["backpack_count"], 5)


class ItemNames(unittest.TestCase):
    def test_known_ids(self):
        from ddvhud.items import item_name
        self.assertEqual(item_name(31600021), "Shiny Amethyst")
        self.assertEqual(item_name(30800073), "White Bell Flower")
        self.assertEqual(item_name(30200015), "Tomato")
        self.assertEqual(item_name(30800088), "Orange & Red Marsh Milkweed")
        self.assertEqual(item_name(30300602), "Halloween Gingerbread Cookies")

    def test_unknown_id(self):
        from ddvhud.items import item_name
        self.assertEqual(item_name(1), "Item #1")


class DailyResetSummary(unittest.TestCase):
    def test_summary_exposes_the_saved_reset(self):
        p = profile(todo_char())
        p["LastDailyReset"] = RESET
        self.assertEqual(build_report(p, NOW)["summary"]["daily_reset"], RESET)

    def test_summary_reset_is_none_when_absent(self):
        self.assertIsNone(build_report(profile(todo_char()), NOW)["summary"]["daily_reset"])


if __name__ == "__main__":
    unittest.main()


class NotInTheVillage(unittest.TestCase):
    WALLE = 10000014

    def listed(self, *chars):
        return build_report(profile(*chars), NOW)["not_in_village"]

    def test_realm_and_unavailable_carry_only_name_where_and_link(self):
        rows = self.listed(char(GOOFY, "InRealm", 4, MINING), char(DONALD, "Secret"),
                           char(MICKEY, "InVillage", 4))
        self.assertEqual(sorted(rows, key=lambda x: x["name"]), [
            {"name": "Donald Duck", "where": "unavailable",
             "wiki_url": "https://dreamlightvalleywiki.com/Donald_Duck"},
            {"name": "Goofy", "where": "realm",
             "wiki_url": "https://dreamlightvalleywiki.com/Goofy"},
        ])

    def test_hidden_fields_not_anywhere_for_non_village(self):
        r = build_report(profile(char(GOOFY, "InRealm", 4, MINING), char(MICKEY, "InVillage", 4, MINING)), NOW)
        self.assertEqual([t["name"] for t in r["todo"]], ["Mickey Mouse"])
        self.assertEqual([v["name"] for v in r["villagers"]], ["Mickey Mouse"])
        self.assertEqual([c["name"] for c in cards(r)["Mining"]["villagers"]], ["Mickey Mouse"])
        self.assertEqual(cards(r)["Mining"]["count"], 1)

    def test_in_village_keeps_hidden_fields(self):
        r = build_report(profile(char(MICKEY, "InVillage", 4, MINING)), NOW)
        self.assertEqual((r["todo"][0]["profession"], r["todo"][0]["level"]), ("Mining", 4))
        self.assertEqual(r["not_in_village"], [])

    def test_unnamed_villager_has_no_link(self):
        rows = self.listed(char(12345678, "InRealm", 2))
        self.assertEqual(rows, [{"name": "Villager #12345678", "where": "realm", "wiki_url": None}])

    def test_punctuation_is_quoted_safely(self):
        rows = self.listed(char(self.WALLE, "Secret"))
        self.assertEqual(rows[0]["wiki_url"], "https://dreamlightvalleywiki.com/WALL%C2%B7E")

    def test_apostrophes_and_dots_are_safe(self):
        from unittest import mock
        from ddvhud import report
        names = {1: "Mother Gothel's Dr. X/Y?#", 2: "Mickey Mouse"}
        with mock.patch.object(report, "VILLAGERS", names):
            rows = self.listed(char(1, "InRealm"))
        self.assertEqual(rows[0]["wiki_url"],
                         "https://dreamlightvalleywiki.com/Mother_Gothel%27s_Dr._X%2FY%3F%23")

    def test_unidentified_secret_excluded_and_counts_unchanged(self):
        r = build_report(profile(char(99999999, "Secret"), char(GOOFY, "InRealm", 10),
                                 char(MICKEY, "InVillage", 3)), NOW)
        self.assertEqual([x["name"] for x in r["not_in_village"]], ["Goofy"])
        self.assertEqual(r["summary"]["available"], {"total": 2, "village": 1, "realm": 1})
        self.assertEqual((r["summary"]["unidentified"], r["summary"]["max_level"]), (1, 1))


class GiftWikiLinks(unittest.TestCase):
    WIKI = "https://dreamlightvalleywiki.com/"

    def urls(self, *ids, names=None):
        from unittest import mock
        c = todo_char()
        c["PreferredItemSlots"] = slots(*[(i, False) for i in ids])
        if names is None:
            return {g["name"]: g["wiki_url"] for g in row(c)["gifts"]}
        with mock.patch.dict("ddvhud.items.ITEMS", names, clear=True):
            return {g["name"]: g["wiki_url"] for g in row(c)["gifts"]}

    def test_item_with_a_known_page_links_to_its_display_name(self):
        self.assertEqual(self.urls(30200015), {"Tomato": self.WIKI + "Tomato"})
        self.assertEqual(self.urls(30800073), {"White Bell Flower": self.WIKI + "White_Bell_Flower"})

    def test_override_title_for_shiny_onyx(self):
        self.assertEqual(self.urls(31600040), {"Shiny Onyx": self.WIKI + "Onyx"})

    def test_item_without_a_page_links_to_the_wiki_search(self):
        self.assertEqual(self.urls(30300112),
                         {"Grilled Eel": self.WIKI + "index.php?search=Grilled%20Eel"})
        self.assertEqual(self.urls(30200018), {"Lime": self.WIKI + "index.php?search=Lime"})

    def test_unknown_item_id_has_no_link(self):
        self.assertEqual(self.urls(99999999), {"Item #99999999": None})

    def test_ampersand_and_accent_give_valid_urls(self):
        self.assertEqual(self.urls(30800088),
                         {"Orange & Red Marsh Milkweed": self.WIKI + "Orange_%26_Red_Marsh_Milkweed"})
        self.assertEqual(self.urls(30300031), {"Soufflé": self.WIKI + "Souffl%C3%A9"})

    def test_apostrophe_is_percent_encoded(self):
        self.assertEqual(self.urls(1, names={1: "Baker's Pie"}), {"Baker's Pie": self.WIKI + "Baker%27s_Pie"})

    def test_disambiguation_suffix_is_not_in_the_url(self):
        urls = self.urls(1, 2, names={1: "Twin", 2: "Twin"})
        self.assertEqual(urls, {"Twin (#1)": self.WIKI + "Twin", "Twin (#2)": self.WIKI + "Twin"})

    def test_every_override_is_a_title_or_a_search_with_text(self):
        from ddvhud.items import ITEMS, WIKI_OVERRIDES
        for item_id, title in WIKI_OVERRIDES.items():
            self.assertIn(item_id, ITEMS)
            self.assertTrue(title is None or title.strip(), item_id)


class FinishedCardsLeave(unittest.TestCase):
    def names(self, c):
        p = profile(c)
        p["LastDailyReset"] = RESET
        return [t["name"] for t in build_report(p, NOW)["todo"]]

    def test_talk_and_all_gifts_done_hides_the_card(self):
        self.assertEqual(self.names(todo_char(talked=True, gifted=(True, True, True))), [])

    def test_talk_done_but_a_gift_left_keeps_the_card(self):
        self.assertEqual(self.names(todo_char(talked=True, gifted=(True, True, False))), ["Mickey Mouse"])

    def test_gifts_done_but_talk_left_keeps_the_card(self):
        self.assertEqual(self.names(todo_char(talked=False, gifted=(True, True, True))), ["Mickey Mouse"])

    def test_gifts_recorded_before_the_reset_count_as_outstanding(self):
        self.assertEqual(self.names(todo_char(talked=True, gifted=(True, True, True), gift_date=BEFORE_RESET)),
                         ["Mickey Mouse"])


def container(items, cid=2, parent=40001190, mine=True):
    return {"ID": cid, "BelongsToPlayer": mine, "ParentItemID": parent,
            "Inventory": [{"ItemID": i, "Amount": n} for i, n in items.items()]}


DARK_WOOD, INGOT, NUGGET, COAL = 31700002, 31700007, 31700018, 31700017


def gather(held=None, spawned=SHOW_MIN_WOOD):
    p = {"World": {"Characters": [], "GridCollection": {"Grids": {"1": {"Objects": {
        str(n): {"ID": n, "ItemID": DARK_WOOD} for n in range(spawned)}}}}},
        "Player": {"ContainerInventories": {"2": container(held or {})}}}
    return build_report(p, NOW)["gather"]


def lines(g):
    return {l["name"]: l for l in g["lines"]}


class GatherForChests(unittest.TestCase):
    def test_absent_once_five_chests_can_be_crafted(self):
        self.assertIsNone(gather({DARK_WOOD: 125, INGOT: 25}))

    def test_ingots_may_be_crafted_from_nuggets_and_coal(self):
        self.assertIsNone(gather({DARK_WOOD: 125, NUGGET: 125, COAL: 25}))

    def test_present_when_wood_is_short_or_ingots_are_short(self):
        self.assertEqual(gather({DARK_WOOD: 124, INGOT: 25})["craftable"], 4)
        self.assertIsNotNone(gather({DARK_WOOD: 125, INGOT: 24}))

    def test_empty_profile_wants_all_materials_for_five(self):
        l = lines(gather())
        self.assertEqual([(x["have"], x["need"], x["short"]) for x in
                          (l["Dark Wood"], l["Gold Nugget"], l["Coal Ore"])],
                         [(0, 125, 125), (0, 125, 125), (0, 25, 25)])

    def test_held_ingots_reduce_nugget_and_coal_needs(self):
        l = lines(gather({INGOT: 10}))
        self.assertEqual((l["Gold Nugget"]["need"], l["Coal Ore"]["need"]), (75, 15))

    def test_counts_backpack_storage_and_chests_together(self):
        p = {"World": {"Characters": [], "GridCollection": {"Grids": {"1": {"Objects": {
            str(n): {"ID": n, "ItemID": DARK_WOOD} for n in range(SHOW_MIN_WOOD)}}}}}, "Player": {"ContainerInventories": {
            "0": container({DARK_WOOD: 10}, cid=0, parent=None),
            "1": container({DARK_WOOD: 20}, cid=1, parent=None),
            "2": container({DARK_WOOD: 30}),
            "3": container({DARK_WOOD: 99}, cid=3, mine=False)}}}
        self.assertEqual(lines(build_report(p, NOW)["gather"])["Dark Wood"]["have"], 60)

    def test_dark_wood_ok_when_world_covers_the_shortfall(self):
        w = lines(gather({DARK_WOOD: 100}, spawned=25))["Dark Wood"]
        self.assertEqual((w["short"], w["spawned"], w["ok"]), (25, 25, True))

    def test_dark_wood_ok_from_seven_spawned_even_when_more_is_short(self):
        self.assertIs(lines(gather(spawned=7))["Dark Wood"]["ok"], True)

    def test_dark_wood_not_ok_below_seven_spawned(self):
        self.assertIs(lines(gather(spawned=6))["Dark Wood"]["ok"], False)

    def test_untrackable_materials_have_no_verdict(self):
        l = lines(gather())
        self.assertIsNone(l["Gold Nugget"]["spawned"])
        self.assertIsNone(l["Gold Nugget"]["ok"])

    def test_a_covered_material_has_no_line(self):
        g = gather({DARK_WOOD: 125, INGOT: 5})
        self.assertNotIn("Dark Wood", lines(g))
        self.assertEqual(set(lines(gather({NUGGET: 125, COAL: 25}))), {"Dark Wood"})

    def test_spawnable_shortfall_sorts_before_untrackable(self):
        self.assertEqual(gather(spawned=125)["lines"][0]["name"], "Dark Wood")

    def test_absent_unless_six_dark_wood_lie_in_the_world(self):
        self.assertIsNone(gather(spawned=SHOW_MIN_WOOD - 1))
        self.assertIsNotNone(gather(spawned=SHOW_MIN_WOOD))
        self.assertIsNone(build_report(profile(), NOW)["gather"])

    def test_covered_wood_does_not_exempt_the_card_from_the_world_rule(self):
        self.assertIsNone(gather({DARK_WOOD: 125}, spawned=0))


class TimeBending(unittest.TestCase):
    def zones(self, per_area):
        areas = {"Valley": ["Beach", "Wetland", "Meadow", "Urban", "Savannah", "Forest", "DarkMountains", "Cliff"],
                 "Eternity": [f"{k}{i:02d}" for k in ("AtlanteanOutpost", "Desert", "Jungle") for i in range(1, 5)]}
        t, n = {}, 0
        for zone, names in areas.items():
            for a in names:
                for _ in range(per_area[zone]):
                    n += 1
                    t[str(n)] = {"Location": {"VillageArea": "VillageAreaType_" + a}}
        return build_report({"World": {"Characters": [], "TimeLostTreasures": t}}, NOW)["time_bending"]

    def test_a_card_per_zone_full_or_not(self):
        z = self.zones({"Valley": 3, "Eternity": 1})
        self.assertEqual([(c["zone"], c["nodes"], c["total"], c["full"]) for c in z],
                         [("Valley", 24, 24, True), ("Eternity Isle", 12, 24, False)])

    def test_both_zones_full(self):
        self.assertEqual([c["full"] for c in self.zones({"Valley": 3, "Eternity": 2})], [True, True])

    def test_a_zone_with_no_nodes_has_no_card(self):
        self.assertEqual([c["zone"] for c in self.zones({"Valley": 0, "Eternity": 1})], ["Eternity Isle"])
        self.assertEqual(build_report({"World": {"Characters": []}}, NOW)["time_bending"], [])


class GiftWanted(unittest.TestCase):
    def test_wanted_counts_the_villagers_asking_for_the_same_gift(self):
        emerald, ruby = 31600001, 31600002
        a, b = todo_char(gifted=(False, False)), todo_char(gifted=(False,))
        a["CharacterID"], b["CharacterID"] = MICKEY, MINNIE
        a["PreferredItemSlots"] = slots((emerald, False), (ruby, False))
        b["PreferredItemSlots"] = slots((emerald, False))
        r = build_report(profile(a, b), NOW)
        self.assertEqual(sorted(g["wanted"] for t in r["todo"] for g in t["gifts"]), [1, 2, 2])


class CookIngredients(unittest.TestCase):
    TOMATO, WHEAT, CARROT = 30200015, 30200004, 30200000

    def cook(self, meal, held, cookbook=None, **kw):
        from ddvhud.items import ITEMS
        meal_id = next(i for i, n in ITEMS.items() if n == meal)
        c = todo_char(gifted=(False,))
        c["PreferredItemSlots"] = slots((meal_id, False))
        p = profile(c)
        p["Player"] = {"ContainerInventories": {"2": container(held, **kw)}}
        if cookbook is not None:
            p["Player"]["Cookbook"] = cookbook
        p["LastDailyReset"] = RESET
        (m,) = build_report(p, NOW)["cook"]
        return m

    def test_a_meal_held_in_storage_or_a_chest_is_not_cooked_again(self):
        from ddvhud.items import ITEMS
        meal_id = next(i for i, n in ITEMS.items() if n == "Veggie Pasta")
        c = todo_char(gifted=(False,))
        c["PreferredItemSlots"] = slots((meal_id, False))
        p = profile(c)
        p["Player"] = {"ContainerInventories": {"1": container({meal_id: 1}, cid=1, parent=None)}}
        p["LastDailyReset"] = RESET
        self.assertEqual(build_report(p, NOW)["cook"], [])

    def test_known_follows_the_cookbook(self):
        from ddvhud.cookbook_data import RECIPE_MEALS
        recipe = next(r for r, m in RECIPE_MEALS.items() if m == 30300170)   # Roasted Asparagus
        for cookbook, known in (({"Recipes": [recipe]}, True), ({"Recipes": []}, False), (None, None)):
            m = self.cook("Roasted Asparagus", {}, cookbook=cookbook)
            self.assertIs(m["known"], known)

    def seen(self, m):
        return [(x["name"], x["have"], x["where"]) for x in m["ingredients"]]

    def test_everything_in_stock_is_ready(self):
        m = self.cook("Veggie Pasta", {self.TOMATO: 1, self.WHEAT: 1, self.CARROT: 1})
        self.assertTrue(m["ready"])
        self.assertEqual([x["have"] for x in m["ingredients"]], [True, True, True])
        self.assertEqual([x["where"] for x in m["ingredients"]], ["", "", ""])

    def test_missing_ingredient_gets_its_where_tag_and_the_meal_is_not_ready(self):
        m = self.cook("Veggie Pasta", {self.WHEAT: 1, self.CARROT: 1})
        self.assertFalse(m["ready"])
        self.assertEqual(self.seen(m)[0], ("Tomato", False, "Farm, Dazzle/Tangle"))

    def test_a_category_slot_takes_any_item_of_the_category(self):
        m = self.cook("Veggie Pasta", {self.TOMATO: 1, self.WHEAT: 1, self.CARROT: 1})
        self.assertEqual(self.seen(m)[2], ("Vegetables", True, ""))

    def test_a_category_slot_cannot_take_the_unit_a_named_ingredient_needs(self):
        m = self.cook("Veggie Pasta", {self.TOMATO: 1, self.WHEAT: 1})
        self.assertEqual(self.seen(m), [("Tomato", True, ""), ("Wheat", True, ""), ("Vegetables", False, "any")])
        self.assertFalse(m["ready"])

    def test_two_category_slots_need_two_units(self):
        self.assertEqual([x["have"] for x in self.cook("Vegetable Soup", {self.CARROT: 1})["ingredients"]], [True, False])
        self.assertTrue(self.cook("Vegetable Soup", {self.CARROT: 2})["ready"])

    def test_stock_is_summed_over_everything_the_player_owns(self):
        # the 48-slot storage (ID 1) has no ParentItemID; a container that is not the player's does not count
        self.assertTrue(self.cook("Veggie Pasta", {self.TOMATO: 1, self.WHEAT: 1, self.CARROT: 1}, cid=1, parent=None)["ready"])
        self.assertFalse(self.cook("Veggie Pasta", {self.TOMATO: 1, self.WHEAT: 1, self.CARROT: 1}, mine=False)["ready"])

    def test_every_recipe_ingredient_is_in_the_ingredient_table_or_a_category(self):
        from ddvhud.ingredients import CATEGORIES, INGREDIENTS
        from ddvhud.recipes import RECIPES
        names = {n.strip() for r in RECIPES.values() for n in r.split(",")}
        self.assertEqual(sorted(n for n in names if n not in INGREDIENTS and n not in CATEGORIES), [])


class SpawnLine(unittest.TestCase):
    AMETHYST, TOMATO = 31600021, 30200015   # Shiny Amethyst (Mining), Tomato (Gardening)

    def gift(self, item, held=0):
        c = todo_char(gifted=(False,))
        c["PreferredItemSlots"] = slots((item, False))
        p = profile(c)
        p["Player"] = {"ContainerInventories": {"0": container({item: held}, cid=0, parent=None)} if held else {}}
        return row_of(p)["gifts"][0]["spawn"]

    def test_not_in_the_backpack_shows_how_and_where_with_short_zone_names(self):
        self.assertEqual(self.gift(self.AMETHYST), {"how": "Mining", "where": "Frosted, Forgotten"})
        self.assertEqual(self.gift(self.TOMATO), {"how": "Gardening", "where": "Dazzle, Tangle"})

    def test_in_the_backpack_has_no_spawn_line(self):
        self.assertIsNone(self.gift(self.AMETHYST, held=1))

    def test_a_meal_is_cooking_with_no_zone(self):
        self.assertEqual(self.gift(30300180), {"how": "Cooking", "where": ""})   # Sweet Herring
        self.assertIsNone(self.gift(30300180, held=1))

    def test_unknown_item_has_no_spawn_line(self):
        self.assertIsNone(self.gift(99999999))


class SpawnWhere(unittest.TestCase):
    def test_one_or_two_zones_are_named(self):
        from ddvhud.spawns import where
        self.assertEqual(where(["Dazzle Beach"]), "Dazzle")
        self.assertEqual(where(["Forest of Valor", "Glade of Trust"]), "Valor, Glade")

    def test_three_zones_name_the_first_two(self):
        from ddvhud.spawns import where
        self.assertEqual(where(["Dazzle Beach", "Wild Tangle", "Everafter"]), "Dazzle, Tangle")

    def test_four_or_more_zones_name_the_area_at_most_two(self):
        from ddvhud.spawns import where
        valley = ["Plaza", "Peaceful Meadow", "Forest of Valor", "Glade of Trust"]
        self.assertEqual(where(valley), "Valley")
        self.assertEqual(where(valley + ["Wild Tangle", "Everafter"]), "Valley, Eternity")
        self.assertEqual(where(["The Docks", "The Overlook", "Wild Tangle", "Glittering Dunes"]), "Eternity")

    def test_a_zone_outside_every_area_keeps_its_own_name(self):
        from ddvhud.spawns import where
        self.assertEqual(where(["Pixie Acres", "Wishing Alps", "Glamour Gulch", "Honeyglow Woods"]), "Pixie, Alps")

    def test_anywhere(self):
        from ddvhud.spawns import where
        self.assertEqual(where(["Plaza", "All Biomes"]), "Anywhere")


class FarmCard(unittest.TestCase):
    ONION = 30200010

    def farm(self, held):
        c = todo_char(gifted=(False,))
        c["PreferredItemSlots"] = slots((next(i for i, n in __import__("ddvhud.items", fromlist=["ITEMS"]).ITEMS.items()
                                              if n == "Veggie Pasta"), False))
        p = profile(c)
        p["Player"] = {"ContainerInventories": {"2": container(held)}, "Cookbook": {"Recipes": []}}   # no known recipes: only the Cook card's
        p["LastDailyReset"] = RESET
        return build_report(p, NOW)["farm"]

    def test_lists_ingredients_under_25_with_how_and_zone(self):
        rows = {r["name"]: r for r in self.farm({30200015: 3})}
        self.assertEqual((rows["Tomato"]["have"], rows["Tomato"]["need"]), (3, 25))
        self.assertEqual((rows["Tomato"]["how"], rows["Tomato"]["where"]), ("Farm", "Dazzle/Tangle"))

    def test_emptiest_first_and_stocked_ones_dropped(self):
        names = [r["name"] for r in self.farm({30200015: 25, 30200004: 5})]
        self.assertEqual(names, ["Wheat"])
        names = [r["name"] for r in self.farm({30200015: 2, 30200004: 5})]
        self.assertEqual(names, ["Tomato", "Wheat"])   # fewest held first

    def test_category_slots_are_not_listed(self):
        self.assertNotIn("Vegetables", [r["name"] for r in self.farm({})])

    def test_grown_ingredients_of_known_recipes_are_listed_without_a_wanted_meal(self):
        from ddvhud.cookbook_data import RECIPE_MEALS
        recipe = next(r for r, m in RECIPE_MEALS.items() if m == 30300170)   # Roasted Asparagus
        p = profile()
        p["Player"] = {"Cookbook": {"Recipes": [recipe]}}
        rows = {r["name"]: r for r in build_report(p, NOW)["farm"]}
        self.assertEqual((rows["Asparagus"]["how"], rows["Asparagus"]["where"]), ("Farm", "Frosted"))
        self.assertNotIn("Tuna", rows)   # fish only count for a meal on the Cook card
