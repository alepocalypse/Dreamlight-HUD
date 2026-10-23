import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from ddvhud.duty_requirements import Requirement
from ddvhud.stock_zones import duty_zones, fish_spot, forage_zones, growth_zones, ripple_zones, stock_zones, wild_crop_zones

PERIDOT_SHINY = 2050200025     # Beach (area 0): shiny Peridot, green
TOURMALINE_SHINY = 2050200029  # SnowCliff (area 7): shiny Tourmaline, pink
CITRINE = 2050200049           # Wetlands (area 1): Citrine, orange
RED_LILY, YELLOW_DANDELION = 30800066, 30800059


def world(rocks=None, flowers=None, ripples=None, wild=None):
    return SimpleNamespace(special_rocks=rocks or {}, items_by_area=flowers or {}, ripples=ripples or {}, wild_crops=wild or {})


class Gems(unittest.TestCase):
    def test_zones_whose_special_rock_yields_a_gem_of_the_colour(self):
        w = world(rocks={0: PERIDOT_SHINY, 7: TOURMALINE_SHINY, 1: CITRINE})
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem", colour="Green"), "Green", w), ["Dazzle Beach"])
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem", colour="Orange"), "Orange", w), ["Glade of Trust"])

    def test_an_item_list_matches_its_gems_not_the_colour_word(self):
        w = world(rocks={0: PERIDOT_SHINY, 7: TOURMALINE_SHINY})
        req = Requirement("mine_gem", items=(31600050,))   # Shiny Tourmaline only
        self.assertEqual(stock_zones("mine_gem", req, "Red", w), ["Frosted Heights"])

    def test_any_gem_lists_every_zone_with_a_gem_rock_up(self):
        w = world(rocks={0: PERIDOT_SHINY, 7: TOURMALINE_SHINY, 1: 1})   # the last has unknown mining data
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem"), None, w), ["Dazzle Beach", "Frosted Heights"])
        self.assertEqual(duty_zones(Requirement("mine_gem"), {}, "Any Gem", w), ["Dazzle Beach", "Frosted Heights"])

    def test_no_matching_rock_gives_no_zones(self):
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem", colour="Blue"), "Blue", world(rocks={0: PERIDOT_SHINY})), [])

    def test_a_rock_with_unknown_mining_data_is_ignored(self):
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem", colour="Blue"), "Blue", world(rocks={0: 1})), [])

    def test_eternity_areas_use_the_wikis_zone_names(self):
        w = world(rocks={10: 2050200141, 11: 2050200145})   # Outpost 3: shiny Jade (green); Outpost 4: shiny Evergem
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem", colour="Green"), "Green", w), ["The Overlook"])
        self.assertEqual(stock_zones("mine_gem", Requirement("mine_gem", items=(31600060,)), "Green", w), ["The Ruins"])


class Flowers(unittest.TestCase):
    def test_zones_with_flowers_of_the_colour_and_how_many(self):
        w = world(flowers={2: {RED_LILY: 4, YELLOW_DANDELION: 1}, 3: {RED_LILY: 2}, 5: {YELLOW_DANDELION: 3}})
        self.assertEqual(stock_zones("pick_flower", Requirement("pick_flower", colour="Red"), "Red", w),
                         ["Peaceful Meadow (4)", "Plaza (2)"])
        self.assertEqual(stock_zones("pick_flower", Requirement("pick_flower", colour="Yellow"), "Yellow", w),
                         ["Forest of Valor (3)", "Peaceful Meadow (1)"])

    def test_the_zone_with_the_most_flowers_comes_first(self):
        w = world(flowers={2: {RED_LILY: 1}, 3: {RED_LILY: 5}})
        self.assertEqual(stock_zones("pick_flower", Requirement("pick_flower", colour="Red"), "Red", w),
                         ["Plaza (5)", "Peaceful Meadow (1)"])

    def test_two_toned_flowers_count_for_each_colour(self):
        w = world(flowers={3: {30800083: 2}})   # Hydrangea (White and Red)
        self.assertEqual(stock_zones("pick_flower", Requirement("pick_flower", colour="White"), "White", w), ["Plaza (2)"])

    def test_other_actions_have_no_zones(self):
        self.assertIsNone(stock_zones("catch_fish", Requirement("catch_fish"), "Red", world()))


MUSHROOM = 30200058


class Forage(unittest.TestCase):
    def test_zones_where_the_items_lie_with_how_many_most_first(self):
        w = world(flowers={1: {MUSHROOM: 2, RED_LILY: 9}, 2: {MUSHROOM: 5}, 3: {RED_LILY: 1}})
        self.assertEqual(forage_zones((MUSHROOM,), w), ["Peaceful Meadow (5)", "Glade of Trust (2)"])

    def test_none_lying_gives_no_zones(self):
        self.assertEqual(forage_zones((MUSHROOM,), world(flowers={1: {RED_LILY: 3}})), [])


class Ripples(unittest.TestCase):
    def test_zones_with_a_ripple_of_the_rarity(self):
        w = world(ripples={0: {"Exceptional": 1, "Normal": 7}, 3: {"Normal": 2}, 11: {"Exceptional": 2}})
        self.assertEqual(ripple_zones("Exceptional", w), ["Dazzle Beach", "The Ruins (2)"])

    def test_none_gives_no_zones(self):
        self.assertEqual(ripple_zones("Exceptional", world(ripples={0: {"Normal": 1}})), [])


class Growth(unittest.TestCase):
    def test_a_garden_crop_lists_the_wikis_zones_for_it(self):
        self.assertEqual(growth_zones(Requirement("harvest_crop", items=(30200015,))), ["Dazzle Beach", "Wild Tangle"])   # Tomato

    def test_several_crops_join_their_zones_without_repeats(self):
        zones = growth_zones(Requirement("harvest_crop", items=(30200015, 30200011)))   # Tomato, Corn
        self.assertEqual(zones, ["Dazzle Beach", "Wild Tangle", "Glittering Dunes"])

    def test_foraged_or_unlisted_items_and_other_actions_have_none(self):
        self.assertIsNone(growth_zones(Requirement("harvest_crop", items=(30200058,))))   # Mushroom is foraged
        self.assertIsNone(growth_zones(Requirement("harvest_crop")))
        self.assertIsNone(growth_zones(Requirement("catch_fish", items=(30200015,))))


class NightThorns(unittest.TestCase):
    def zones(self, text, flowers):
        return duty_zones(Requirement("unknown"), {}, None, world(flowers=flowers), text)

    def test_zones_with_thorns_and_how_many_most_first(self):
        w = {0: {31300003: 1, 31300004: 1}, 1: {31300004: 1}, 5: {31300005: 1}, 6: {RED_LILY: 4}}
        self.assertEqual(self.zones("Uproot Night Thorns.", w), ["Dazzle Beach (2)", "Glade of Trust (1)", "Forest of Valor (1)"])
        self.assertEqual(self.zones("Remove 4 Night Thorns", w)[0], "Dazzle Beach (2)")

    def test_none_lying_gives_no_zones_and_other_duties_none(self):
        self.assertEqual(self.zones("Uproot Night Thorns.", {}), [])
        self.assertIsNone(self.zones("Craft a Night Thorn plushie", {}))


class FishSpot(unittest.TestCase):
    def test_a_named_fish_gives_its_zone_and_ripple_colour(self):
        self.assertEqual(fish_spot(Requirement("catch_fish", items=(31000022,))), "Peaceful Meadow \u00b7 Blue or White")   # Bream

    def test_a_single_colour(self):
        self.assertEqual(fish_spot(Requirement("catch_fish", items=(31000002,))), "Peaceful Meadow, Forest of Valor, The Oasis \u00b7 White")   # Rainbow Trout; its Storybook zone is left out

    def test_open_water_fish(self):
        self.assertEqual(fish_spot(Requirement("catch_fish", items=(31000005,))).split(" \u00b7 ")[1], "Anywhere")   # Seaweed

    def test_several_fish_or_unknown_fish_or_other_actions_have_none(self):
        self.assertIsNone(fish_spot(Requirement("catch_fish", items=(31000022, 31000002))))
        self.assertIsNone(fish_spot(Requirement("catch_fish", items=(1,))))
        self.assertIsNone(fish_spot(Requirement("catch_fish")))
        self.assertIsNone(fish_spot(Requirement("mine_gem", items=(31000022,))))


def at(day, hour=0):
    return datetime(2026, 10, day, hour, tzinfo=timezone.utc)


class WildCrops(unittest.TestCase):
    NOW = at(22, 7)

    def test_only_ripe_patches_count_by_the_crop_they_yield(self):
        w = world(wild={1: {30400126: [at(21), at(22, 6), at(23)]}, 2: {30400126: [at(22, 8)]}, 3: {30400125: [at(21)]}})
        self.assertEqual(wild_crop_zones((MUSHROOM,), w, self.NOW), ["Glade of Trust (2)"])
        self.assertEqual(wild_crop_zones((30200091,), w, self.NOW), ["Plaza (1)"])   # Mint

    def test_most_first_and_none_ripe_gives_no_zones(self):
        w = world(wild={1: {30400126: [at(21)]}, 2: {30400126: [at(21), at(21)]}})
        self.assertEqual(wild_crop_zones((MUSHROOM,), w, self.NOW), ["Peaceful Meadow (2)", "Glade of Trust (1)"])
        self.assertEqual(wild_crop_zones((MUSHROOM,), world(wild={1: {30400126: [at(23)]}}), self.NOW), [])

    def test_a_mushroom_duty_uses_the_wild_patches(self):
        w = world(wild={1: {30400126: [at(21)]}})
        self.assertEqual(duty_zones(Requirement("harvest_crop", items=(MUSHROOM,)), {}, None, w, "Go mushroom picking.", self.NOW),
                         ["Glade of Trust (1)"])
