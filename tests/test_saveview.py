import unittest
from datetime import datetime, timezone

from ddvhud.saveview import SaveView


def slot(item, amount):
    return {"ItemID": item, "Amount": amount}


def cont(cid, slots, parent=None, mine=True):
    c = {"ID": cid, "BelongsToPlayer": mine, "Inventory": slots}
    if parent:
        c["ParentItemID"] = parent
    return c


def view(containers):
    return SaveView({"Player": {"ContainerInventories": containers}}).inventory


class Backpack(unittest.TestCase):
    def test_backpack_is_container_zero_only(self):
        inv = view({"a": cont(0, [slot(5, 2), slot(5, 3)]), "b": cont(1, [slot(5, 100)])})
        self.assertEqual(inv.backpack, {5: 5})


class Chests(unittest.TestCase):
    def test_chest_needs_parent_item_and_belonging_to_player(self):
        inv = view({"a": cont(0, [slot(5, 1)]), "b": cont(1, [slot(5, 2)]),
                    "c": cont(7, [slot(5, 4)], parent=900), "d": cont(8, [slot(5, 8)], parent=901),
                    "e": cont(9, [slot(5, 16)], parent=902, mine=False), "f": cont(10, [slot(5, 32)], mine=False)})
        self.assertEqual(inv.chests, {5: 12})


class Owned(unittest.TestCase):
    def test_owned_is_every_container_of_the_player(self):
        inv = view({"a": cont(0, [slot(5, 1)]), "b": cont(1, [slot(5, 2)]),
                    "c": cont(7, [slot(6, 4)], parent=900), "e": cont(9, [slot(5, 16)], parent=902, mine=False)})
        self.assertEqual(inv.owned, {5: 3, 6: 4})


class OddData(unittest.TestCase):
    def test_empty_and_odd_slots_are_skipped(self):
        inv = view({"a": cont(0, [slot(0, 3), {"Amount": 3}, slot(5, 0), slot(5, -1), slot(5, "2"),
                                  {"ItemID": 5}, None, "x", slot(6, 2)])})
        self.assertEqual(inv.backpack, {6: 2})

    def test_containers_may_be_a_list_and_odd_entries_are_skipped(self):
        inv = view([cont(0, [slot(5, 2)]), None, "x", {"ID": 0}, {"ID": 0, "Inventory": None}])
        self.assertEqual(inv.backpack, {5: 2})

    def test_missing_data_gives_empty_totals(self):
        for profile in ({}, {"Player": None}, {"Player": {}}, {"Player": {"ContainerInventories": None}}):
            inv = SaveView(profile).inventory
            self.assertEqual((inv.backpack, inv.chests, inv.owned), ({}, {}, {}))


class Characters(unittest.TestCase):
    def test_a_character_is_plain_facts(self):
        profile = {"World": {"Characters": [{
            "Base": {"id": 10000003}, "Status": "CharacterStatus_InVillage", "FriendshipLevel": 4,
            "ProfessionID": 1500000001, "DiscussedWithTheAvatarToday": True,
            "LastGiftDate": "2026-10-19T06:00:00Z",
            "PreferredItemSlots": [{"PreferredItemId": 30300001, "Gifted": True},
                                   {"PreferredItemId": 30300002}]}]}}
        self.assertEqual(SaveView(profile).characters, [{
            "id": 10000003, "status": "InVillage", "level": 4, "profession": 1500000001,
            "talked_today": True, "last_gift": "2026-10-19T06:00:00Z",
            "gift_slots": [(30300001, True), (30300002, False)]}])

    def test_missing_world_or_characters_gives_no_characters(self):
        for profile in ({}, {"World": None}, {"World": {}}, {"World": {"Characters": None}}):
            self.assertEqual(SaveView(profile).characters, [])

    def test_non_dict_entries_and_entries_without_an_id_are_skipped(self):
        entries = [None, "x", {}, {"Base": None}, {"Base": {}}, {"Base": {"id": 0}}, {"Base": {"id": 10000003}}]
        self.assertEqual([c["id"] for c in SaveView({"World": {"Characters": entries}}).characters], [10000003])

    def test_a_bare_character_has_default_facts(self):
        self.assertEqual(SaveView({"World": {"Characters": [{"Base": {"id": 10000003}}]}}).characters, [{
            "id": 10000003, "status": "", "level": 0, "profession": 0,
            "talked_today": False, "last_gift": None, "gift_slots": []}])

    def test_odd_gift_slots_are_skipped(self):
        c = {"Base": {"id": 10000003}, "PreferredItemSlots": [None, "x", {"PreferredItemId": 5, "Gifted": True}]}
        self.assertEqual(SaveView({"World": {"Characters": [c]}}).characters[0]["gift_slots"], [(5, True)])


class DailyReset(unittest.TestCase):
    def test_daily_reset_is_the_saved_text_or_none(self):
        self.assertEqual(SaveView({"LastDailyReset": "2026-10-19T05:00:00Z"}).daily_reset, "2026-10-19T05:00:00Z")
        self.assertIsNone(SaveView({}).daily_reset)


if __name__ == "__main__":
    unittest.main()


def world(w):
    return SaveView({"World": w}).world


def grids(g):
    return {"GridCollection": {"Grids": g}}


class Loose(unittest.TestCase):
    def test_counts_objects_with_the_item_across_dict_grids(self):
        w = world(grids({"a": {"Objects": {"x": {"ItemID": 7}, "y": {"ItemID": 7}, "z": {"ItemID": 8}}},
                         "b": {"Objects": {"x": {"ItemID": 7}}}}))
        self.assertEqual(w.loose(7), 3)
        self.assertEqual(w.loose(8), 1)

    def test_grids_and_objects_may_be_lists(self):
        w = world(grids([{"Objects": [{"ItemID": 7}, {"ItemID": 8}]}, {"Objects": {"x": {"ItemID": 7}}}]))
        self.assertEqual(w.loose(7), 2)

    def test_missing_world_or_grids_is_zero(self):
        self.assertEqual(SaveView({}).world.loose(7), 0)
        self.assertEqual(world({}).loose(7), 0)
        self.assertEqual(world({"GridCollection": {}}).loose(7), 0)
        self.assertEqual(world(grids({"a": {}, "b": {"Objects": None}})).loose(7), 0)

    def test_malformed_grids_and_objects_are_skipped(self):
        w = world(grids({"a": "junk", "b": {"Objects": [None, 5, {"Name": "x"}, {"ItemID": 7}]}}))
        self.assertEqual(w.loose(7), 1)


def treasure(area):
    return {"Location": {"VillageArea": area}}


class TimeNodes(unittest.TestCase):
    def test_counts_per_area_with_prefix_removed(self):
        w = world({"TimeLostTreasures": {"a": treasure("VillageAreaType_Beach"), "b": treasure("VillageAreaType_Beach"),
                                         "c": treasure("VillageAreaType_Jungle")}})
        self.assertEqual(w.time_nodes, {"Beach": 2, "Jungle": 1})

    def test_list_treasures_and_entries_without_an_area_are_skipped(self):
        w = world({"TimeLostTreasures": [treasure("VillageAreaType_Cliff"), {}, None, {"Location": None},
                                         {"Location": {}}, {"Location": {"VillageArea": ""}}, "junk"]})
        self.assertEqual(w.time_nodes, {"Cliff": 1})

    def test_missing_treasures_is_empty(self):
        self.assertEqual(world({}).time_nodes, {})
        self.assertEqual(SaveView({}).world.time_nodes, {})


def special(item, hits=0, needed=5):
    return {"Special": {"MiningDataItemID": item, "NumberOfHits": hits, "NumberOfHitsNeeded": needed}}


def areas(**by_key):
    return {"Villages": [{"Areas": {k[1:]: v for k, v in by_key.items()}}]}


def boat(level=10, collect="2026-10-19T10:00:00Z"):
    return {"ItemID": 20100002, "State": {"FishingStallData": {"UpgradeState": {"Level": level}, "LastCollect": collect,
                                                               "PendingFishes": []}}}


class Boats(unittest.TestCase):
    def test_a_boat_is_its_area_level_and_last_collect(self):
        w = world({**grids({"a": {"ID": 9, "Objects": {"451": boat(11, "2026-10-23T20:03:15.088970900Z")}}}),
                   "Villages": [{"Areas": {"0": {"GridIDs": [9]}}}]})
        self.assertEqual(w.boats, [{"area": 0, "level": 11,
                                    "last_collect": datetime(2026, 10, 23, 20, 3, 15, 88970, tzinfo=timezone.utc)}])

    def test_a_boat_in_no_listed_area_and_missing_data_give_defaults(self):
        w = world(grids({"a": {"ID": 9, "Objects": {"1": {"ItemID": 20100002, "State": {"FishingStallData": {}}},
                                                   "2": boat(collect=None), "3": boat(level="x")}}}))
        self.assertEqual(w.boats, [{"area": None, "level": 0, "last_collect": None},
                                   {"area": None, "level": 10, "last_collect": None},
                                   {"area": None, "level": 0,
                                    "last_collect": datetime(2026, 10, 19, 10, tzinfo=timezone.utc)}])

    def test_objects_without_fishing_stall_data_are_not_boats(self):
        w = world(grids({"a": {"ID": 9, "Objects": {"1": {"ItemID": 20100002, "State": {"FishingStallData": "junk"}},
                                                   "2": {"ItemID": 20100002, "State": {"StallData": {}}},
                                                   "3": {"ItemID": 7}}}}))
        self.assertEqual(w.boats, [])
        self.assertEqual(SaveView({}).world.boats, [])


class SpecialRocks(unittest.TestCase):
    def test_an_area_with_an_unmined_special_rock_maps_to_its_mining_data(self):
        w = world(areas(a7={"MiningRocks": [{"LastHit": "t"}, special(2050200029)]}, a2={"MiningRocks": [{}]}))
        self.assertEqual(w.special_rocks, {7: 2050200029})

    def test_a_fully_hit_special_is_gone(self):
        w = world(areas(a7={"MiningRocks": [special(5, hits=5)]}))
        self.assertEqual(w.special_rocks, {})

    def test_villages_are_merged_and_odd_data_is_skipped(self):
        w = world({"Villages": [{"Areas": {"0": {"MiningRocks": [special(1)]}}},
                                {"Areas": {"8": {"MiningRocks": [special(2)]}, "x": {"MiningRocks": [special(3)]},
                                           "9": "junk", "10": {"MiningRocks": None}}}, "junk", None]})
        self.assertEqual(w.special_rocks, {0: 1, 8: 2})
        self.assertEqual(SaveView({}).world.special_rocks, {})


def flower(item, dry=False):
    return {"ItemID": item, "State": {"FlowerData": {"Dry": dry}}}


class ItemsByArea(unittest.TestCase):
    def test_items_are_counted_per_area_through_its_grids(self):
        w = world({**areas(a7={"GridIDs": [3, 4]}, a2={"GridIDs": [5]}),
                   **grids({"3": {"ID": 3, "Objects": {"a": flower(30800066), "b": flower(30800066), "c": {"ItemID": 30200058}}},
                            "4": {"ID": 4, "Objects": [flower(30800059)]},
                            "5": {"ID": 5, "Objects": [flower(30800066)]},
                            "6": {"ID": 6, "Objects": [flower(30800066)]}})})
        self.assertEqual(w.items_by_area, {7: {30800066: 2, 30200058: 1, 30800059: 1}, 2: {30800066: 1}})

    def test_dry_flowers_are_not_available(self):
        w = world({**areas(a7={"GridIDs": [3]}),
                   **grids({"3": {"ID": 3, "Objects": [flower(30800066, dry=True), flower(30800059)]}})})
        self.assertEqual(w.items_by_area, {7: {30800059: 1}})

    def test_missing_data_is_empty(self):
        self.assertEqual(SaveView({}).world.items_by_area, {})
        self.assertEqual(world(areas(a7={"GridIDs": [3]})).items_by_area, {})


def wild_plot(seed, ends, left=1, item=20200007):
    return {"ItemID": item, "State": {"GardenData": {"Slots": [
        {"PlantedSeedItemID": seed, "Harvest": {"EndOfGrowth": ends, "NumberOfProductionLeft": left}}]}}}


class WildCrops(unittest.TestCase):
    def test_wild_plots_give_their_seed_and_when_it_is_ready_per_area(self):
        w = world({**areas(a1={"GridIDs": [8]}, a2={"GridIDs": [9]}),
                   **grids({"8": {"ID": 8, "Objects": [wild_plot(30400126, "2026-10-22T06:39:44.475919200Z"),
                                                       wild_plot(30400126, "2026-10-23T01:00:00Z")]},
                            "9": {"ID": 9, "Objects": [wild_plot(30400125, "2026-10-21T00:00:00Z")]}})})
        self.assertEqual(sorted(w.wild_crops[1][30400126]),
                         [datetime(2026, 10, 22, 6, 39, 44, 475919, tzinfo=timezone.utc), datetime(2026, 10, 23, 1, tzinfo=timezone.utc)])
        self.assertEqual(w.wild_crops[2], {30400125: [datetime(2026, 10, 21, tzinfo=timezone.utc)]})

    def test_player_gardens_and_spent_or_odd_plots_are_not_wild_crops(self):
        w = world({**areas(a1={"GridIDs": [8]}),
                   **grids({"8": {"ID": 8, "Objects": [wild_plot(30400126, "2026-10-21T00:00:00Z", item=20200006),
                                                       wild_plot(30400126, "2026-10-21T00:00:00Z", left=0),
                                                       wild_plot(0, "2026-10-21T00:00:00Z"),
                                                       wild_plot(30400126, "not a time")]}})})
        self.assertEqual(w.wild_crops, {})
        self.assertEqual(SaveView({}).world.wild_crops, {})


class FruitTrees(unittest.TestCase):
    def test_fruit_trees_give_their_seed_and_when_the_fruit_is_ready_per_area(self):
        w = world({**areas(a2={"GridIDs": [8]}, a8={"GridIDs": [9]}),
                   **grids({"8": {"ID": 8, "Objects": [wild_plot(30400029, "2022-11-28T01:40:07.123456700Z", left=-1, item=20200002),
                                                       wild_plot(30400029, "2026-10-23T21:41:04Z", left=-1, item=20200002)]},
                            "9": {"ID": 9, "Objects": [wild_plot(30400074, "2026-10-20T01:05:10Z", left=-1, item=20200002)]}})})
        self.assertEqual(sorted(w.fruit_trees[2][30400029]),
                         [datetime(2022, 11, 28, 1, 40, 7, 123456, tzinfo=timezone.utc), datetime(2026, 10, 23, 21, 41, 4, tzinfo=timezone.utc)])
        self.assertEqual(w.fruit_trees[8], {30400074: [datetime(2026, 10, 20, 1, 5, 10, tzinfo=timezone.utc)]})
        self.assertEqual(w.wild_crops, {})

    def test_other_gardens_and_odd_trees_are_not_fruit_trees(self):
        w = world({**areas(a2={"GridIDs": [8]}),
                   **grids({"8": {"ID": 8, "Objects": [wild_plot(30400029, "2026-10-21T00:00:00Z", left=-1),   # a wild patch
                                                       wild_plot(30400029, "2026-10-21T00:00:00Z", left=0, item=20200002),
                                                       wild_plot(0, "2026-10-21T00:00:00Z", left=-1, item=20200002),
                                                       wild_plot(30400029, None, left=-1, item=20200002)]}})})
        self.assertEqual(w.fruit_trees, {})
        self.assertEqual(SaveView({}).world.fruit_trees, {})


def ripple(rarity, area):
    return {"Rarity": "FishRippleRarity_" + rarity, "Location": {"VillageArea": "VillageAreaType_" + area}}


class Ripples(unittest.TestCase):
    def test_pending_ripples_are_counted_per_area_key_and_rarity(self):
        w = world({"PendingFishes": {"1": ripple("Exceptional", "Beach"), "2": ripple("Exceptional", "Beach"),
                                     "3": ripple("Normal", "Beach"), "4": ripple("Exceptional", "Cliff"),
                                     "5": ripple("Exceptional", "Jungle02"), "6": ripple("Enhanced", "AtlanteanOutpost03"),
                                     "7": ripple("Exceptional", "Desert04")}})
        self.assertEqual(w.ripples, {0: {"Exceptional": 2, "Normal": 1}, 7: {"Exceptional": 1}, 17: {"Exceptional": 1},
                                     10: {"Enhanced": 1}, 15: {"Exceptional": 1}})

    def test_odd_or_unknown_ripples_are_skipped(self):
        w = world({"PendingFishes": {"1": ripple("Normal", "Moon"), "2": "junk", "3": {"Rarity": "FishRippleRarity_Normal"},
                                     "4": {"Location": {"VillageArea": "VillageAreaType_Beach"}}}})
        self.assertEqual(w.ripples, {})
        self.assertEqual(SaveView({}).world.ripples, {})


def duty_slot(i, duty, state="OnGoing", cur=0, target=5, data=None):
    return {"SlotId": i, "DutyId": duty, "State": "DutySlotState_" + state,
            "StepData": {"ItemFilter": {"Data": data}, "TargetAmount": target, "curAmount": cur}}


class DutySlots(unittest.TestCase):
    def test_each_village_set_is_plain_duties_in_slot_order(self):
        profile = {"Player": {"DutySlots": {
            "1540000000": {"Slots": [duty_slot(0, 2110000034, cur=2, target=5, data={"ActivityItemType": "ActivityItemType_Crop"}),
                                     duty_slot(1, 2110000050, state="Completed", cur=500, target=500)]},
            "1540000101": {"Slots": [duty_slot(0, 2110000051, target=1)]}}}}
        a, b = SaveView(profile).duty_slots
        self.assertEqual(a["key"], "1540000000")
        self.assertEqual(a["duties"][0], {"position": 1, "duty_id": 2110000034, "state": "OnGoing", "current": 2,
                                          "target": 5, "filter": {"kind": "Crop"}})
        self.assertEqual((a["duties"][1]["position"], a["duties"][1]["state"]), (2, "Completed"))
        self.assertEqual((b["key"], len(b["duties"])), ("1540000101", 1))

    def test_missing_or_odd_slot_data_gives_no_duties(self):
        for profile in ({}, {"Player": {}}, {"Player": {"DutySlots": None}}, {"Player": {"DutySlots": {"1": "x"}}}):
            self.assertEqual(SaveView(profile).duty_slots, [], profile)
        odd = SaveView({"Player": {"DutySlots": {"1": {"Slots": ["junk", None, {"DutyId": 5}]}}}}).duty_slots
        self.assertEqual([d["duty_id"] for d in odd[0]["duties"]], [5])


def companions(player=None, world=None):
    profile = {}
    if player is not None:
        profile["Player"] = player
    if world is not None:
        profile["World"] = world
    return SaveView(profile).companions


class Achievements(unittest.TestCase):
    def test_achievements_map_id_to_count_claimed_milestone_and_state(self):
        v = SaveView({"Player": {"AchievementsData": [
            {"AchievementID": 2110100132, "CurAmount": 1, "ClaimedRewardMilestone": 0, "State": "AchievementState_OnGoing"},
            {"AchievementID": 2110100136, "CurAmount": 100, "ClaimedRewardMilestone": 100, "State": "AchievementState_Completed"}]}})
        self.assertEqual(v.achievements, {2110100132: {"current": 1, "claimed": 0, "state": "OnGoing"},
                                          2110100136: {"current": 100, "claimed": 100, "state": "Completed"}})

    def test_missing_fields_default_and_odd_entries_are_skipped(self):
        v = SaveView({"Player": {"AchievementsData": [{"AchievementID": 7}, {"CurAmount": 3}, None, "x"]}})
        self.assertEqual(v.achievements, {7: {"current": 0, "claimed": 0, "state": ""}})
        self.assertEqual(SaveView({}).achievements, {})
        self.assertEqual(SaveView({"Player": {"AchievementsData": {"7": 1}}}).achievements, {})


class Unlocked(unittest.TestCase):
    def test_unlocked_maps_companion_id_to_companion_level(self):
        c = companions(player={"Pets": [{"PetItemID": 7, "FriendshipLevel": 5},
                                        {"PetItemID": 8, "FriendshipLevel": 2}]})
        self.assertEqual(c.unlocked, {7: 5, 8: 2})

    def test_missing_companion_level_defaults_to_one(self):
        self.assertEqual(companions(player={"Pets": [{"PetItemID": 7}]}).unlocked, {7: 1})

    def test_odd_entries_are_skipped(self):
        c = companions(player={"Pets": [None, 3, {"FriendshipLevel": 4}, {"PetItemID": 9, "FriendshipLevel": 3}]})
        self.assertEqual(c.unlocked, {9: 3})


class Equipped(unittest.TestCase):
    def test_equipped_is_the_assigned_companion_ids(self):
        c = companions(player={"Pets": [{"PetItemID": 7}, {"PetItemID": 8}], "AssignedPets": [8, 99]})
        self.assertEqual(c.equipped, {8, 99})


class FedCritters(unittest.TestCase):
    def test_critters_map_id_to_feedings_done(self):
        c = companions(world={"Critters": [{"CritterItemID": 4, "NumberOfFeedingDone": 2},
                                           {"CritterItemID": 5, "NumberOfFeedingDone": 0}]})
        self.assertEqual(c.critters, {4: 2, 5: 0})

    def test_missing_feedings_default_to_zero(self):
        self.assertEqual(companions(world={"Critters": [{"CritterItemID": 4}]}).critters, {4: 0})

    def test_odd_critter_entries_are_skipped(self):
        c = companions(world={"Critters": ["x", None, {"NumberOfFeedingDone": 3}, {"CritterItemID": 6}]})
        self.assertEqual(c.critters, {6: 0})


class MissingCompanionData(unittest.TestCase):
    def test_no_player_or_world_gives_empty_answers(self):
        c = companions()
        self.assertEqual((c.unlocked, c.equipped, c.critters), ({}, set(), {}))

    def test_null_lists_give_empty_answers(self):
        c = companions(player={"Pets": None, "AssignedPets": None}, world={"Critters": None})
        self.assertEqual((c.unlocked, c.equipped, c.critters), ({}, set(), {}))


def star_paths(progress):
    return SaveView({"Player": {"BattlePassStates": {"Progress": progress}}}).star_paths


def task(state="OnGoing", cur=0, target=1, data=None):
    return {"Objective": {"ItemFilter": {"Data": data}, "TargetAmount": target, "CurAmount": cur},
            "TaskState": "BattlePassTaskState_" + state}


class StarPaths(unittest.TestCase):
    def test_a_star_path_is_plain_facts_with_duties_in_order(self):
        paths = star_paths({"Seafaring2026": {
            "CurrencyAmount": 10, "EndDate": "2026-12-01T00:00:00Z",
            "TasksProgress": [task("Completed", 3, 3), task("NotStarted", 0, 5)]}})
        self.assertEqual(paths, [{
            "id": "Seafaring2026", "tokens": 10, "end_date": "2026-12-01T00:00:00Z",
            "duties": [{"position": 1, "state": "Completed", "current": 3, "target": 3, "filter": {}},
                       {"position": 2, "state": "NotStarted", "current": 0, "target": 5, "filter": {}}],
            "weekly": []}])

    def test_weekly_sets_are_lists_of_duties_in_week_order(self):
        paths = star_paths({"Seafaring2026": {"WeeklyTasksProgress": [
            {"TasksProgress": [task("CurrencyClaimed", 1, 1), task("OnGoing", 2, 4)]},
            {"TasksProgress": [task("NotStarted", 0, 9)]}]}})
        self.assertEqual(paths[0]["weekly"], [
            [{"position": 1, "state": "CurrencyClaimed", "current": 1, "target": 1, "filter": {}},
             {"position": 2, "state": "OnGoing", "current": 2, "target": 4, "filter": {}}],
            [{"position": 1, "state": "NotStarted", "current": 0, "target": 9, "filter": {}}]])

    def test_missing_or_odd_star_path_data_gives_no_star_paths(self):
        for profile in ({}, {"Player": None}, {"Player": {}}, {"Player": {"BattlePassStates": None}},
                        {"Player": {"BattlePassStates": {}}}, {"Player": {"BattlePassStates": {"Progress": None}}},
                        {"Player": {"BattlePassStates": {"Progress": []}}}):
            self.assertEqual(SaveView(profile).star_paths, [])
        self.assertEqual(star_paths({"A": None, "B": "x"}), [])

    def test_wrongly_typed_star_path_data_gives_empty_results_not_errors(self):
        for states in ({"Progress": [1]}, "x", 5, [1], {"Progress": 5}):
            self.assertEqual(SaveView({"Player": {"BattlePassStates": states}}).star_paths, [])
        self.assertEqual(star_paths({"A": {"WeeklyTasksProgress": 5}})[0]["weekly"], [])
        self.assertEqual(star_paths({"A": {"WeeklyTasksProgress": "x", "TasksProgress": 5}})[0]["duties"], [])

    def test_wrongly_typed_filter_values_are_ignored(self):
        data = {"Type": 5, "ActivityItemType": 7, "MineralRoughness": 3, "Item": 9}
        paths = star_paths({"A": {"TasksProgress": [{"TaskState": 4, "Objective": {"ItemFilter": {"Data": data}}}]}})
        self.assertEqual(paths[0]["duties"][0]["filter"], {"item": 9})
        self.assertEqual(paths[0]["duties"][0]["state"], "")

    def test_a_bare_star_path_has_default_facts(self):
        self.assertEqual(star_paths({"A": {}}), [
            {"id": "A", "tokens": 0, "end_date": None, "duties": [], "weekly": []}])
        self.assertEqual(star_paths({"A": {"TasksProgress": None, "WeeklyTasksProgress": None}})[0]["weekly"], [])

    def test_odd_duties_and_weeks_are_skipped_but_keep_their_position(self):
        paths = star_paths({"A": {"TasksProgress": [None, "x", task("OnGoing", 1, 2), {"TaskState": None}],
                                  "WeeklyTasksProgress": [None, {"TasksProgress": None},
                                                          {"TasksProgress": [task("NotStarted", 0, 1), 5]}]}})
        self.assertEqual(paths[0]["duties"], [
            {"position": 3, "state": "OnGoing", "current": 1, "target": 2, "filter": {}},
            {"position": 4, "state": "", "current": 0, "target": 0, "filter": {}}])
        self.assertEqual(paths[0]["weekly"], [[], [], [{"position": 1, "state": "NotStarted", "current": 0, "target": 1,
                                                        "filter": {}}]])


def required(**data):
    """The filter of a duty whose requirement data is the game's defaults plus `data`."""
    base = {"Item": 0, "ItemList": [], "Type": "ItemType_ActivityItem", "ActivityItemType": "ActivityItemType_Default",
            "AnyActivityItem": False, "Tags": [], "MinMealStarRating": 0, "TagCondition": "TagFilterCondition_AllTags",
            "MineralRoughness": "MineralRoughness_Any", "IngredientsType": [],
            "Complexity": {"UseField": False, "Random": False, "Complexity": "Complexity_Lavish"}}
    base.update(data)
    return star_paths({"A": {"TasksProgress": [task(data=base)]}})[0]["duties"][0]["filter"]


class DutyFilters(unittest.TestCase):
    def test_default_fields_are_left_out(self):
        self.assertEqual(required(), {"type": "ActivityItem"})

    def test_item_item_list_kind_type_and_tags_are_exposed(self):
        self.assertEqual(required(Item=31000005, ActivityItemType="ActivityItemType_Fish"),
                         {"item": 31000005, "kind": "Fish", "type": "ActivityItem"})
        self.assertEqual(required(ItemList=[1, 2], Type="ItemType_ActivityData", Tags=[2001500003]),
                         {"item_list": [1, 2], "type": "ActivityData", "tags": [2001500003]})

    def test_used_nested_filters_are_exposed_as_their_values(self):
        meta = {"UseField": True, "Random": False, "ShowRandomCheckbox": True}
        self.assertEqual(required(
            FishLocation=dict(meta, VillageAreas={"AreaList": ["VillageAreaType_Beach", "VillageAreaType_Forest"]}),
            FishRarity=dict(meta, FishRarities={"FishRarities": ["FishRarity_Unique"]}),
            Complexity=dict(meta, Complexity="Complexity_Lavish")),
            {"type": "ActivityItem", "fish_location": ["Beach", "Forest"], "fish_rarity": ["Unique"],
             "complexity": "Lavish"})

    def test_unused_nested_filters_are_left_out(self):
        unused = {"UseField": False, "VillageAreas": {"AreaList": ["VillageAreaType_Beach"]}}
        self.assertEqual(required(FishLocation=unused), {"type": "ActivityItem"})

    def test_other_non_default_requirements_are_exposed(self):
        self.assertEqual(required(AnyActivityItem=True, MinMealStarRating=4, IngredientsType=[2001400001],
                                  TagCondition="TagFilterCondition_AtLeastOneTag", Tags=[1, 2],
                                  MineralRoughness="MineralRoughness_Shiny"),
                         {"type": "ActivityItem", "any": True, "min_meal_stars": 4, "ingredient_tags": [2001400001],
                          "tags": [1, 2], "tags_any": True, "roughness": "Shiny"})

    def test_odd_filter_data_is_tolerated(self):
        for data in (None, [], "x", {}, {"Tags": None, "Type": None, "ActivityItemType": None, "Complexity": None}):
            paths = star_paths({"A": {"TasksProgress": [{"Objective": {"ItemFilter": {"Data": data}}}]}})
            self.assertEqual(paths[0]["duties"][0]["filter"], {})
        paths = star_paths({"A": {"TasksProgress": [{"Objective": {"ItemFilter": None}}]}})
        self.assertEqual(paths[0]["duties"][0]["filter"], {})
