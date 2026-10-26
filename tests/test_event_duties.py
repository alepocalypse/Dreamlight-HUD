import unittest
from datetime import datetime, timezone

from ddvhud.report import build_report

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)


def task(state, cur=0, target=1, data=None):
    objective = {"CurAmount": cur, "TargetAmount": target}
    if data is not None:
        objective["ItemFilter"] = {"Data": data}
    return {"Objective": objective, "TaskState": "BattlePassTaskState_" + state}


def full_report(progress):
    return build_report({"Player": {"BattlePassStates": {"Progress": progress}}}, NOW)


def report_plan(progress):
    return full_report(progress)["plan"]


def report(progress):
    return full_report(progress)["event_duties"]


SCROOGE_BOTH = {"Seafaring2026": {"TasksProgress": [task("NotStarted")] * 5 + [task("OnGoing", 1, 3)]},
                "HauntingElegance2026": {"TasksProgress": [task("NotStarted")] * 13 + [task("OnGoing", 2, 4)]}}


def event_report(achievements, now=datetime(2026, 10, 26, 22, 0, tzinfo=timezone.utc)):
    return build_report({"Player": {"AchievementsData": [
        {"AchievementID": i, "CurAmount": c, "ClaimedRewardMilestone": m, "State": "AchievementState_OnGoing"}
        for i, c, m in achievements]}}, now)


class SeasonalEvent(unittest.TestCase):
    def test_a_running_event_is_a_duty_list_after_the_star_paths_with_hints_and_days_left(self):
        r = event_report([(2110100132, 1, 0), (2110100133, 0, 0), (2110100136, 100, 100)])
        [ev] = r["event_duties"]
        self.assertEqual((ev["id"], ev["title"], ev["tokens"], ev["days_left"]), ("EventHalloween", "Trick-or-Treat Event", None, 5))
        self.assertEqual(ev["duties"], [
            {"text": "Sugar Rush", "current": 1, "target": 15, "done": False, "hint": "Eat a lot of Candies!"},
            {"text": "Trick or Treat", "current": 0, "target": 10, "done": False, "hint": "Distribute Candies to Villagers!"}])

    def test_event_duties_are_singles_in_duty_mode_with_their_item_reward_at_no_dreamlight_value(self):
        r = event_report([(2110100133, 0, 0)])
        [a] = r["actions"]
        self.assertEqual((a["size"], a["label"], a["value"]), ("Single", "Trick or Treat", 0))
        self.assertEqual(a["duties"][0]["reward"], {"amount": 1, "currency": "Mickey Mouse Pumpkin"})
        self.assertEqual(a["duties"][0]["hint"], "Distribute Candies to Villagers!")

    def test_no_list_once_the_event_is_over(self):
        self.assertEqual(event_report([(2110100132, 1, 0)], datetime(2026, 11, 2, tzinfo=timezone.utc))["event_duties"], [])


class EventDuties(unittest.TestCase):
    def test_duty_text_is_looked_up_from_zero_based_position(self):
        tasks = [task("OnGoing", 1, 10)] + [task("NotStarted")] * 6 + [task("OnGoing", 2, 5)]
        [sp] = report({"Seafaring2026": {"TasksProgress": tasks}})
        self.assertEqual(sp["duties"], [{"text": "Catch any fish.", "current": 1, "target": 10, "done": False},
                                        {"text": "Mine for blue gems.", "current": 2, "target": 5, "done": False}])

    def test_only_ongoing_and_unclaimed_completed_duties_are_listed(self):
        tasks = [task("NotStarted"), task("CurrencyClaimed", 1, 1), task("Completed", 3, 3),
                 task("OnGoing", 4, 4), task("OnGoing", 1, 4)]
        [sp] = report({"Seafaring2026": {"TasksProgress": tasks}})
        self.assertEqual(sp["duties"], [
            {"text": "Go fishing for seaweed (on purpose!).", "current": 3, "target": 3, "done": True},
            {"text": "Go mining for gems.", "current": 4, "target": 4, "done": True},
            {"text": "Feed Sea Turtles their favorite food.", "current": 1, "target": 4, "done": False,
             "requires": {"label": "Feed sea turtles their favorite food", "action": "feed", "place": None,
                          "colour": None, "items": None, "target": "sea turtles"}}])

    def test_weekly_sets_with_work_are_listed_by_week_number(self):
        weeks = [{"TasksProgress": [task("CurrencyClaimed", 1, 1)]},
                 {"TasksProgress": [task("OnGoing", 3, 20), task("Completed", 5, 5)]},
                 {"TasksProgress": [task("NotStarted", 0, 9)]}]
        [sp] = report({"Seafaring2026": {"WeeklyTasksProgress": weeks}})
        self.assertEqual(sp["weekly"], [{"week": 2, "duties": [
            {"text": "Hang out with a mermaid princess.", "current": 3, "target": 20, "done": False},
            {"text": "Mine for blue gems.", "current": 5, "target": 5, "done": True}]}])

    def test_first_weekly_slot_is_zero_based_text(self):
        [sp] = report({"Seafaring2026": {"WeeklyTasksProgress": [{"TasksProgress": [task("OnGoing", 1, 20)]}]}})
        self.assertEqual(sp["weekly"][0]["duties"][0]["text"], "Catch 20 fish.")

    def test_classified_duties_carry_their_requirement(self):
        beach = {"ActivityItemType": "ActivityItemType_Fish", "FishLocation": {"UseField": True, "Value": ["Location_Beach"]}}
        tasks = [task("OnGoing", 1, 10, {"ActivityItemType": "ActivityItemType_Fish"})] + [task("NotStarted")] * 3 + \
            [task("OnGoing", 0, 3, beach)]
        [sp] = report({"Seafaring2026": {"TasksProgress": tasks}})
        self.assertEqual(sp["duties"][0]["requires"], {"label": "Catch any fish", "action": "catch_fish", "place": None,
                                                       "colour": None, "items": None, "target": None})
        self.assertEqual(sp["duties"][1]["requires"]["place"], "Dazzle Beach")

    def test_the_same_ask_in_two_star_paths_has_equal_requirements(self):
        a, b = report({"Seafaring2026": {"TasksProgress": [task("NotStarted")] * 5 + [task("OnGoing")]},
                       "HauntingElegance2026": {"TasksProgress": [task("NotStarted")] * 13 + [task("OnGoing")]}})
        self.assertEqual(a["duties"][0]["requires"], b["duties"][0]["requires"])
        self.assertEqual(a["duties"][0]["requires"]["target"], "Scrooge McDuck's Store")

    def test_weekly_duties_carry_requirements_too(self):
        fish = {"ActivityItemType": "ActivityItemType_Fish"}
        [sp] = report({"Seafaring2026": {"WeeklyTasksProgress": [{"TasksProgress": [task("OnGoing", 3, 20, fish)]}]}})
        self.assertEqual(sp["weekly"][0]["duties"][0]["requires"]["label"], "Catch any fish")

    def test_unclassified_duties_have_no_requirement_field(self):
        [sp] = report({"Seafaring2026": {"TasksProgress": [task("OnGoing"), task("NotStarted"), task("OnGoing")]}})
        self.assertNotIn("requires", sp["duties"][1])

    def test_shared_section_groups_the_same_purchase_across_both_star_paths(self):
        [g] = full_report(SCROOGE_BOTH)["shared"]
        self.assertEqual(g["label"], "Buy from Scrooge McDuck's Store")
        self.assertEqual(g["spans"], 2)
        self.assertEqual([(d["path"], d["current"], d["target"], d["weekly"]) for d in g["duties"]],
                         [("Seafaring Star Path", 1, 3, None), ("Haunting Elegance", 2, 4, None)])

    def test_shared_section_includes_weekly_duties_and_skips_finished_ones(self):
        fish = {"ActivityItemType": "ActivityItemType_Fish"}
        progress = {"Seafaring2026": {"TasksProgress": [task("OnGoing", 1, 10, fish)] + [task("NotStarted")] * 5 +
                                      [task("Completed", 3, 3, fish)],
                                      "WeeklyTasksProgress": [{"TasksProgress": [task("OnGoing", 3, 20, fish)]}]}}
        [g] = full_report(progress)["shared"]
        self.assertEqual((g["label"], g["spans"], [(d["text"], d["weekly"]) for d in g["duties"]]),
                         ("Catch any fish", 1, [("Catch any fish.", None), ("Catch 20 fish.", 1)]))

    def test_shared_is_empty_without_overlap(self):
        self.assertEqual(full_report({})["shared"], [])

    def test_plan_lists_the_cross_star_path_group_first_then_every_other_open_duty_once(self):
        progress = {k: dict(v) for k, v in SCROOGE_BOTH.items()}
        progress["Seafaring2026"]["TasksProgress"] = [task("OnGoing", 0, 5)] + progress["Seafaring2026"]["TasksProgress"][1:]
        plan = full_report(progress)["plan"]
        self.assertEqual([(e["tier"], e["label"], e["spans"]) for e in plan],
                         [("cross", "Buy from Scrooge McDuck's Store", 2), ("single", "Catch any fish.", 1)])
        self.assertEqual(plan[0]["duties"][0], {"path": "Seafaring Star Path", "text": plan[0]["duties"][0]["text"],
                                                "current": 1, "target": 3, "weekly": None,
                                                "reward": {"amount": 10, "currency": "Doubloon Tokens"}, "value": 100})

    def test_a_colour_duty_lists_the_zones_that_can_serve_it_right_now(self):
        blue = {"ActivityItemType": "ActivityItemType_Mineral", "Tags": [2000700000]}   # Mine for blue gems.
        tasks = [task("NotStarted")] * 7 + [task("OnGoing", 2, 5, blue)]
        rock = {"Special": {"MiningDataItemID": 2050200023, "NumberOfHits": 0, "NumberOfHitsNeeded": 5}}   # shiny Aquamarine
        profile = {"Player": {"BattlePassStates": {"Progress": {"Seafaring2026": {"TasksProgress": tasks}}}},
                   "World": {"Villages": [{"Areas": {"0": {"MiningRocks": [rock]}, "7": {"MiningRocks": [{}]}}}]}}
        [entry] = build_report(profile, NOW)["plan"]
        self.assertEqual(entry["duties"][0]["zones"], ["Dazzle Beach"])
        self.assertEqual((entry["duties"][0]["family"], entry["duties"][0]["row"]), ("Mine", "Blue Gems"))

    def test_gold_ripple_and_mushroom_duties_list_their_zones(self):
        tasks = [task("NotStarted")] * 9 + [task("OnGoing", 0, 5, {"ActivityItemType": "ActivityItemType_Fish",
                                                                      "FishRarity": {"UseField": True, "Value": ["FishRarity_Unique"]}})]
        ripple = {"Rarity": "FishRippleRarity_Exceptional", "Location": {"VillageArea": "VillageAreaType_Beach"}}
        profile = {"Player": {"BattlePassStates": {"Progress": {"Seafaring2026": {"TasksProgress": tasks}}}},
                   "World": {"PendingFishes": {"1": ripple, "2": dict(ripple, Rarity="FishRippleRarity_Normal")}}}
        [entry] = build_report(profile, NOW)["plan"]
        self.assertEqual(entry["duties"][0]["zones"], ["Dazzle Beach"])

    def test_a_mushroom_duty_lists_the_zones_with_ripe_wild_patches_and_how_many(self):
        tasks = [task("NotStarted")] * 9 + [task("OnGoing", 0, 15, {"ActivityItemType": "ActivityItemType_Crop",
                                                                      "ItemList": [30200058, 30200186, 30200213]})]

        def patch(ends, item=20200007):
            return {"ItemID": item, "State": {"GardenData": {"Slots": [
                {"PlantedSeedItemID": 30400126, "Harvest": {"EndOfGrowth": ends, "NumberOfProductionLeft": 1}}]}}}
        patches = [patch("2026-10-18T00:00:00Z"), patch("2026-10-19T11:00:00Z"), patch("2026-10-20T00:00:00Z"),
                   patch("2026-10-01T00:00:00Z", item=20200006)]   # the third is not ripe yet, the fourth is a player plot
        profile = {"Player": {"BattlePassStates": {"Progress": {"HauntingElegance2026": {"TasksProgress": tasks}}}},
                   "World": {"Villages": [{"Areas": {"1": {"GridIDs": [8]}}}],
                             "GridCollection": {"Grids": {"8": {"ID": 8, "Objects": patches}}}}}
        [entry] = build_report(profile, NOW)["plan"]
        self.assertEqual(entry["duties"][0]["zones"], ["Glade of Trust (2)"])

    def test_a_garden_crop_duty_lists_where_it_grows_faster(self):
        tasks = [task("NotStarted")] * 10 + [task("OnGoing", 0, 20, {"ActivityItemType": "ActivityItemType_Crop", "Item": 30200015})]
        [entry] = report_plan({"HauntingElegance2026": {"TasksProgress": tasks}})
        self.assertEqual(entry["duties"][0]["grows"], ["Dazzle Beach", "Wild Tangle"])

    def test_rotating_duty_sets_are_listed_like_star_paths(self):
        def duty_slot(i, duty, state="OnGoing", cur=0, target=5):
            return {"SlotId": i, "DutyId": duty, "State": "DutySlotState_" + state,
                    "StepData": {"ItemFilter": {"Data": None}, "TargetAmount": target, "curAmount": cur}}
        profile = {"Player": {"DutySlots": {
            "1540000000": {"Slots": [duty_slot(0, 2110000034, cur=2), duty_slot(1, 2110000051, "Completed", 1, 1)]},
            "1540000101": {"Slots": [duty_slot(0, 2110000051, target=1)]}}}}
        r = build_report(profile, NOW)
        valley, mist = r["event_duties"]
        self.assertEqual((valley["title"], mist["title"]), ("Dreamlight Duties", "Mist Duties"))
        self.assertEqual([(d["text"], d["current"], d["target"], d["done"]) for d in valley["duties"]],
                         [("Plant 5 Vegetables", 2, 5, False), ("Change Outfit", 1, 1, True)])
        self.assertEqual(valley["weekly"], [])
        self.assertEqual([(e["label"], e["duties"][0]["path"]) for e in r["plan"]],
                         [("Plant 5 Vegetables", "Dreamlight Duties"), ("Change Outfit", "Mist Duties")])

    def test_a_rotating_duty_that_names_a_zone_in_its_text_is_not_classified(self):
        slot = {"SlotId": 0, "DutyId": 2110000135, "State": "DutySlotState_OnGoing",
                "StepData": {"ItemFilter": {"Data": {"ActivityItemType": "ActivityItemType_Mineral"}}, "TargetAmount": 4, "curAmount": 0}}
        [valley] = build_report({"Player": {"DutySlots": {"1540000000": {"Slots": [slot]}}}}, NOW)["event_duties"]
        self.assertEqual(valley["duties"][0]["text"], "Mine 4 Rock Spots in the Forest of Valor")
        self.assertNotIn("requires", valley["duties"][0])

    def test_rock_spots_join_the_mine_family_with_their_zone(self):
        def spot(i, duty):
            return {"SlotId": i, "DutyId": duty, "State": "DutySlotState_OnGoing",
                    "StepData": {"ItemFilter": {"Data": {"ActivityItemType": "ActivityItemType_Mineral"}}, "TargetAmount": 4, "curAmount": 1}}
        profile = {"Player": {"DutySlots": {"1540000000": {"Slots": [spot(0, 2110000135), spot(1, 2110000111)]}}}}
        [entry] = build_report(profile, NOW)["plan"]
        a, b = entry["duties"]
        self.assertEqual((entry["tier"], entry["label"]), ("rows", "Mine"))
        self.assertEqual((a["row"], a["place"]), ("Nodes", "Forest of Valor"))
        self.assertNotIn("place", b)

    def test_a_named_fish_duty_says_where_and_in_what_to_fish(self):
        slot = {"SlotId": 0, "DutyId": 2110000128, "State": "DutySlotState_OnGoing",
                "StepData": {"ItemFilter": {"Data": {"Item": 31000022, "ActivityItemType": "ActivityItemType_Fish"}},
                             "TargetAmount": 3, "curAmount": 0}}
        [entry] = build_report({"Player": {"DutySlots": {"1540000000": {"Slots": [slot]}}}}, NOW)["plan"]
        self.assertEqual(entry["duties"][0]["spot"], "Peaceful Meadow \u00b7 Blue or White")

    def test_a_feeding_duty_says_what_the_animal_likes(self):
        slot = {"SlotId": 0, "DutyId": 2110000149, "State": "DutySlotState_OnGoing", "StepData": {"ItemFilter": {"Data": None}, "TargetAmount": 1, "curAmount": 0}}
        [entry] = build_report({"Player": {"DutySlots": {"1540000000": {"Slots": [slot]}}}}, NOW)["plan"]
        self.assertEqual(entry["duties"][0]["food"], "White Sturgeon")   # Feed a Fox

    def test_duties_without_a_colour_have_no_zones_field(self):
        [entry] = full_report({"Seafaring2026": {"TasksProgress": [task("OnGoing", 0, 5)]}})["plan"]
        self.assertNotIn("zones", entry["duties"][0])

    def test_plan_is_empty_without_star_paths(self):
        self.assertEqual(full_report({})["plan"], [])

    def test_title_currency_tokens_and_end_date(self):
        [sp] = report({"Seafaring2026": {"CurrencyAmount": 42, "EndDate": "2026-12-01T00:00:00Z"}})
        self.assertEqual(sp, {"id": "Seafaring2026", "title": "Seafaring Star Path", "currency": "Doubloon Tokens",
                              "tokens": 42, "ends": "2026-12-01T00:00:00Z", "days_left": 43,
                              "duties": [], "weekly": []})

    def test_days_left_rounds_a_part_day_up_and_stops_at_zero(self):
        def days(ends):
            return report({"Seafaring2026": {"EndDate": ends}})[0]["days_left"]
        self.assertEqual(days("2026-10-20T12:00:00Z"), 1)    # exactly one day
        self.assertEqual(days("2026-10-20T12:00:01Z"), 2)    # one second over
        self.assertEqual(days("2026-10-19T13:00:00Z"), 1)    # an hour left still counts as a day
        self.assertEqual(days("2026-10-01T00:00:00Z"), 0)    # already ended

    def test_no_or_unreadable_end_date_has_no_days_left(self):
        self.assertIsNone(report({"Seafaring2026": {}})[0]["days_left"])
        self.assertIsNone(report({"Seafaring2026": {"EndDate": "soon"}})[0]["days_left"])

    def test_rotating_duty_sets_have_no_days_left(self):
        slot = {"SlotId": 0, "DutyId": 2110000149, "State": "DutySlotState_OnGoing",
                "StepData": {"ItemFilter": {"Data": None}, "TargetAmount": 1, "curAmount": 0}}
        [sp] = build_report({"Player": {"DutySlots": {"1540000000": {"Slots": [slot]}}}}, NOW)["event_duties"]
        self.assertIsNone(sp["days_left"])

    def test_unknown_star_path_gets_placeholders(self):
        [sp] = report({"Mystery2030": {"TasksProgress": [task("OnGoing", 0, 2)]}})
        self.assertEqual((sp["title"], sp["currency"], sp["duties"][0]["text"]), ("Mystery2030", "Tokens", "Duty #1"))

    def test_duty_at_target_is_done_even_when_still_ongoing(self):
        [sp] = report({"Seafaring2026": {"TasksProgress": [task("OnGoing", 10, 10)]}})
        self.assertTrue(sp["duties"][0]["done"])

    def test_no_star_paths_gives_an_empty_list(self):
        self.assertEqual(build_report({}, NOW)["event_duties"], [])
        self.assertEqual(report({}), [])


if __name__ == "__main__":
    unittest.main()
