import unittest

from ddvhud.duty_requirements import classify, colour_family, cook_family, fish_family, clean_family, craft_family, generic_rank, currency_family, feed_family, food_for, gift_family, hang_out_family, sell_family, node_family, node_place


class Fish(unittest.TestCase):
    def test_any_fish_comes_from_the_filter_kind(self):
        r = classify("Catch any fish.", {"kind": "Fish", "type": "ActivityItem"})
        self.assertEqual((r.action, r.label), ("catch_fish", "Catch any fish"))

    def test_fish_at_a_place_is_narrower_than_any_fish(self):
        r = classify("Catch Fish from Dazzle Beach.", {"kind": "Fish", "fish_location": ["Beach"]})
        self.assertEqual((r.action, r.place, r.label), ("catch_fish", "Dazzle Beach", "Catch fish at Dazzle Beach"))
        self.assertNotEqual(r, classify("Catch any fish.", {"kind": "Fish"}))

    def test_same_requirement_from_different_text_is_equal(self):
        self.assertEqual(classify("Catch 20 fish.", {"kind": "Fish"}), classify("Catch 30 Fish.", {"kind": "Fish"}))

    def test_a_specific_fish_is_narrower_still(self):
        r = classify("Go fishing for seaweed (on purpose!).", {"kind": "Fish", "item": 31000005})
        self.assertEqual((r.action, r.items, r.label), ("catch_fish", (31000005,), "Catch Seaweed"))
        self.assertNotEqual(r, classify("Catch any fish.", {"kind": "Fish"}))


class Gems(unittest.TestCase):
    def test_gem_colour_comes_from_the_colour_tag(self):
        r = classify("Mine for blue gems.", {"kind": "Mineral", "tags": [2000700000]})
        self.assertEqual((r.action, r.colour, r.items, r.label), ("mine_gem", "Blue", None, "Mine blue gems"))
        self.assertEqual(classify("Mine 20 orange gems.", {"kind": "Mineral", "tags": [2000700007]}).colour, "Orange")
        self.assertNotEqual(r, classify("x", {"kind": "Mineral", "tags": [2000700002]}))

    def test_gem_item_list_is_the_listed_gems(self):
        r = classify("Mine for red gems.", {"kind": "Mineral", "item_list": [31600010, 31600036, 31600013, 31600044]})
        self.assertEqual((r.action, r.colour, r.items), ("mine_gem", None, (31600010, 31600013, 31600036, 31600044)))
        self.assertEqual(r.label, "Mine Garnet, Ruby, Shiny Garnet and 1 more")

    def test_gems_without_a_kind_in_the_filter_still_use_the_item_list(self):
        r = classify("Mine 20 square gems.", {"item_list": [31600020, 31600021]})
        self.assertEqual((r.action, r.items), ("mine_gem", (31600020, 31600021)))

    def test_any_gem_has_no_narrowing(self):
        r = classify("Go mining for gems.", {"kind": "Mineral"})
        self.assertEqual((r.action, r.colour, r.items, r.label), ("mine_gem", None, None, "Mine any gem"))

    def test_unknown_colour_tag_is_not_guessed(self):
        self.assertEqual(classify("x", {"kind": "Mineral", "tags": [123]}).action, "unknown")


class Plants(unittest.TestCase):
    def test_a_specific_crop(self):
        r = classify("Harvest some tomatoes.", {"kind": "Crop", "item": 30200015})
        self.assertEqual((r.action, r.items, r.label), ("harvest_crop", (30200015,), "Harvest Tomato"))

    def test_a_crop_list_is_those_crops_in_any_order(self):
        a = classify("Go mushroom picking.", {"kind": "Crop", "item_list": [30200213, 30200058, 30200186]})
        self.assertEqual((a.action, a.items), ("harvest_crop", (30200058, 30200186, 30200213)))
        self.assertEqual(a, classify("x", {"kind": "Crop", "item_list": [30200186, 30200213, 30200058]}))

    def test_flower_colour(self):
        r = classify("Pick some yellow flowers", {"kind": "Flower", "tags": [2000700006]})
        self.assertEqual((r.action, r.colour, r.label), ("pick_flower", "Yellow", "Pick yellow flowers"))

    def test_tagged_crops_that_are_not_a_colour_are_not_guessed(self):
        self.assertEqual(classify("x", {"kind": "Crop", "tags": [2001200010], "any": True}).action, "unknown")


class FromText(unittest.TestCase):
    def test_buy_from_a_named_shop_is_the_same_in_every_star_path(self):
        r = classify("Buy something from Scrooge McDuck's Store.", {})
        self.assertEqual((r.action, r.target, r.label), ("buy", "Scrooge McDuck's Store", "Buy from Scrooge McDuck's Store"))
        self.assertEqual(r, classify("Buy something from Scrooge McDuck's Store.", {}))
        self.assertNotEqual(r, classify("Buy something from Goofy's Stall.", {}))

    def test_hang_out_and_selfie_name_the_villager_from_the_text(self):
        h = classify("Hang out with Goofy.", {"item": 10000004, "type": "Character"})
        self.assertEqual((h.action, h.target, h.label), ("hang_out", "Goofy", "Hang out with Goofy"))
        s = classify("Take a selfie with Mickey Mouse.", {"item": 10000003, "type": "Character"})
        self.assertEqual((s.action, s.target, s.label), ("selfie", "Mickey Mouse", "Take a selfie with Mickey Mouse"))
        self.assertEqual(classify("Hang out with the Pumpkin King.", {}).target, "the Pumpkin King")
        self.assertNotEqual(h, classify("Hang out with Mickey Mouse.", {}))

    def test_hang_out_with_a_kind_of_villager_is_not_guessed(self):
        self.assertEqual(classify("Hang out with a mermaid princess.", {}).action, "unknown")

    def test_feed_names_the_animal_whatever_the_capitalisation(self):
        a = classify("Feed Sea Turtles their favorite food.", {})
        self.assertEqual((a.action, a.target, a.label), ("feed", "sea turtles", "Feed sea turtles their favorite food"))
        self.assertEqual(a, classify("Feed sea turtles their favorite food.", {}))

    def test_cook_a_dish_from_the_filter_meal(self):
        r = classify("Cook 10 Tuna Burgers.", {"item": 30300186, "kind": "Meal"})
        self.assertEqual((r.action, r.items, r.label), ("cook", (30300186,), "Cook " + "Tuna Burger"))

    def test_sell_only_when_the_filter_narrows_nothing(self):
        r = classify("Sell 100 items.", {})
        self.assertEqual((r.action, r.label), ("sell", "Sell items"))
        self.assertEqual(classify("Sell 50 seafood.", {"kind": "Crop", "tags": [2001200010], "any": True}).action, "unknown")

    def test_sell_text_wins_over_a_crop_filter(self):
        self.assertEqual(classify("Sell 50 tomatoes.", {"kind": "Crop", "item": 30200015}).action, "unknown")

    def test_filter_wins_over_text(self):
        self.assertEqual(classify("Buy something from Goofy's Stall.", {"kind": "Fish"}).action, "catch_fish")


class Covers(unittest.TestCase):
    any_fish = classify("a", {"kind": "Fish"})
    beach = classify("a", {"kind": "Fish", "fish_location": ["Beach"]})
    seaweed = classify("a", {"kind": "Fish", "item": 31000005})
    any_gem = classify("a", {"kind": "Mineral"})
    blue = classify("a", {"kind": "Mineral", "tags": [2000700000]})
    two_gems = classify("a", {"kind": "Mineral", "item_list": [31600010, 31600013]})
    one_gem = classify("a", {"kind": "Mineral", "item": 31600010})

    def test_a_wider_requirement_covers_a_narrower_one_of_the_same_action(self):
        for narrow in (self.beach, self.seaweed, self.any_fish):
            self.assertTrue(self.any_fish.covers(narrow))
        self.assertTrue(self.any_gem.covers(self.blue))
        self.assertTrue(self.two_gems.covers(self.one_gem))

    def test_narrower_or_unrelated_requirements_do_not_cover(self):
        self.assertFalse(self.beach.covers(self.any_fish))
        self.assertFalse(self.beach.covers(self.seaweed))   # whether seaweed grows at the beach is not known
        self.assertFalse(self.blue.covers(self.two_gems))   # nor which colour a listed gem counts as
        self.assertFalse(self.one_gem.covers(self.two_gems))
        self.assertFalse(self.any_fish.covers(self.any_gem))

    def test_unknown_covers_and_is_covered_by_nothing(self):
        u = classify("Vote", {})
        self.assertFalse(u.covers(u))
        self.assertFalse(self.any_fish.covers(u))


class Unknown(unittest.TestCase):
    def test_unrecognised_duty_is_standalone_and_equals_nothing(self):
        a, b = classify("Vote 10 times in DreamSnaps contests.", {}), classify("Vote 10 times in DreamSnaps contests.", {})
        self.assertEqual(a.action, "unknown")
        self.assertNotEqual(a, b)
        self.assertEqual(a, a)
        self.assertEqual(a.label, "")

    def test_a_filter_field_the_model_does_not_know_makes_it_standalone(self):
        for extra in ({"roughness": "Rough"}, {"min_meal_stars": 3}, {"ingredient_tags": [1]}, {"mystery": 1}):
            self.assertEqual(classify("x", {"kind": "Mineral", **extra}).action, "unknown")

    def test_unrecognised_place_is_not_guessed(self):
        self.assertEqual(classify("Catch fish somewhere.", {"kind": "Fish", "fish_location": ["Moon"]}).action, "unknown")


class ColourFamily(unittest.TestCase):
    def test_a_colour_tag_names_the_colour(self):
        r = classify("Mine 20 orange gems.", {"kind": "Mineral", "tags": [2000700007]})
        self.assertEqual(colour_family("Mine 20 orange gems.", r), ("Mine", "Orange Gems"))

    def test_a_listed_gem_set_takes_its_colour_from_the_text(self):
        r = classify("Mine for red gems.", {"kind": "Mineral", "item_list": [31600001, 31600002]})
        self.assertEqual(colour_family("Mine for red gems.", r), ("Mine", "Red Gems"))

    def test_flowers(self):
        r = classify("Pick some yellow flowers", {"kind": "Flower", "tags": [2000700006]})
        self.assertEqual(colour_family("Pick some yellow flowers", r), ("Pick flowers", "Yellow"))

    def test_no_colour_or_other_actions_have_no_family(self):
        self.assertIsNone(colour_family("Catch any fish.", classify("Catch any fish.", {"kind": "Fish"})))
        self.assertIsNone(colour_family("Cook 10 red things", classify("Cook 10 red things", {"kind": "Meal"})))




class AnyGem(unittest.TestCase):
    def fam(self, text, filter):
        return colour_family(text, classify(text, filter))

    def test_a_gem_duty_with_no_colour_is_the_any_gem_row(self):
        for text in ("Mine for gems.", "Mine 30 gems.", "Go mining for gems."):
            self.assertEqual(self.fam(text, {"kind": "Mineral"}), ("Mine", "Any Gem"), text)

    def test_a_named_set_of_gems_keeps_its_word(self):
        self.assertEqual(self.fam("Mine for square gems.", {"item_list": [31600020, 31600009]}), ("Mine", "Square Gems"))

    def test_shiny_gems_are_not_classified_so_have_no_row(self):
        self.assertIsNone(self.fam("Mine for shiny gems.", {"kind": "Mineral", "roughness": "Shiny"}))


class HangOut(unittest.TestCase):
    def test_a_named_character_filter_gives_the_villager_name(self):
        self.assertEqual(hang_out_family("Hang out with a hot-tempered duck.", {"item": 10000011, "type": "Character"}),
                         ("Hang outs", "Donald Duck"))

    def test_a_plain_name_in_the_text_is_kept(self):
        self.assertEqual(hang_out_family("Hang out with the Pumpkin King.", {"item": 99999999, "type": "Character"}),
                         ("Hang outs", "Pumpkin King"))

    def test_a_set_of_characters_uses_the_text(self):
        f = {"item_list": [10000113, 10000011], "type": "Character"}
        self.assertEqual(hang_out_family("Hang out with Mickey & Friends.", f), ("Hang outs", "Mickey & Friends"))

    def test_clue_text_without_a_known_id_loses_its_article(self):
        self.assertEqual(hang_out_family("Hang out with a long-bearded wizard.", {"type": "Character"}),
                         ("Hang outs", "long-bearded wizard"))

    def test_other_duties_have_none(self):
        self.assertIsNone(hang_out_family("Make small talk.", {}))


class OtherVerbs(unittest.TestCase):
    def test_watering_crops_is_not_harvesting_them(self):
        r = classify("Water dried-up crops.", {"kind": "Crop", "type": "ActivityItem"})
        self.assertEqual(r.action, "unknown")
        self.assertNotEqual(r, classify("Harvest 20 crops.", {"kind": "Crop", "type": "ActivityItem"}))

    def test_giving_or_planting_a_kind_is_not_the_kind_action(self):
        for text, kind in (("Give a Villager their favorite flowers.", "Flower"), ("Plant 10 crops.", "Crop")):
            self.assertEqual(classify(text, {"kind": kind}).action, "unknown", text)


class IsMineralTag(unittest.TestCase):
    def test_the_is_mineral_tag_next_to_a_colour_changes_nothing(self):
        both = classify("Mine for purple gems.", {"kind": "Mineral", "tags": [2000700009, 2001200027]})
        self.assertEqual((both.action, both.colour), ("mine_gem", "Purple"))
        self.assertEqual(both, classify("Mine for purple gems.", {"kind": "Mineral", "tags": [2000700009]}))


class Cook(unittest.TestCase):
    def test_a_named_dish_uses_its_item_name(self):
        self.assertEqual(cook_family("Cook 10 Tuna Burgers.", {"item": 30300186, "kind": "Meal"}), ("Cook", "Tuna Burger"))

    def test_a_dish_name_with_a_different_verb(self):
        self.assertEqual(cook_family("Prepare Tekka Maki.", {"item": 30300023, "kind": "Meal"})[0], "Cook")

    def test_a_kind_of_meal_uses_the_text_without_its_verb(self):
        self.assertEqual(cook_family("Cook any 2-star meal.", {"kind": "Meal", "min_meal_stars": 2}), ("Cook", "any 2-star meal"))
        self.assertEqual(cook_family("Whip up some 3-star meals.", {"kind": "Meal"}), ("Cook", "3-star meals"))
        self.assertEqual(cook_family("Cook 10 seafood meals.", {"kind": "Meal"}), ("Cook", "seafood meals"))
        self.assertEqual(cook_family("Cook some pumpkin-based meals.", {"kind": "Ingredient", "item": 30200062}),
                         ("Cook", "pumpkin-based meals"))

    def test_other_duties_have_none(self):
        self.assertIsNone(cook_family("Serve meals in Remy's Restaurant.", {}))
        self.assertIsNone(cook_family("Catch any fish.", {"kind": "Fish"}))


class OriginTags(unittest.TestCase):
    def test_a_named_item_ignores_the_origin_tag_beside_it(self):
        r = classify("Catch 3 Bream", {"item": 31000022, "kind": "Fish", "tags": [2001200028]})   # IsDreamlightValley
        self.assertEqual((r.action, r.items), ("catch_fish", (31000022,)))

    def test_a_tag_that_is_not_a_colour_still_narrows_a_kind_without_an_item(self):
        self.assertEqual(classify("Plant 5 Vegetables", {"kind": "Mineral", "tags": [2001200014]}).action, "unknown")


class Nodes(unittest.TestCase):
    def test_rock_spots_are_nodes_of_the_mine_family(self):
        self.assertEqual(node_family("Mine 4 Rock Spots in the Forest of Valor"), ("Mine", "Nodes"))
        self.assertEqual(node_family("Mine 3 Rock Spots"), ("Mine", "Nodes"))
        self.assertIsNone(node_family("Mine for gems."))
        self.assertIsNone(node_family("Sell 3 Minerals"))

    def test_the_zone_is_what_follows_in_on_or_at(self):
        self.assertEqual(node_place("Mine 4 Rock Spots in the Forest of Valor"), "Forest of Valor")
        self.assertEqual(node_place("Mine 4 Rock Spots on Dazzle Beach"), "Dazzle Beach")
        self.assertEqual(node_place("Mine 4 Rock Spots on the Sunlit Plateau"), "Sunlit Plateau")
        self.assertEqual(node_place("Mine 4 Rock Spots in Mythopia"), "Mythopia")
        self.assertIsNone(node_place("Mine 3 Rock Spots"))


class FishRows(unittest.TestCase):
    def fam(self, text, filter):
        return fish_family(text, classify(text, filter), filter)

    def test_any_fish_a_place_and_named_fish_are_rows_of_the_fish_family(self):
        self.assertEqual(self.fam("Catch any fish.", {"kind": "Fish"}), ("Fish", "Any fish"))
        self.assertEqual(self.fam("Catch 20 fish.", {"kind": "Fish"}), ("Fish", "Any fish"))
        self.assertEqual(self.fam("Catch Fish from Dazzle Beach.", {"kind": "Fish", "fish_location": ["Beach"]}),
                         ("Fish", "Dazzle Beach"))
        self.assertEqual(self.fam("Catch 3 Bream", {"kind": "Fish", "item": 31000022}), ("Fish", "Bream"))
        self.assertEqual(self.fam("Go fishing for seaweed (on purpose!).", {"kind": "Fish", "item": 31000005}), ("Fish", "Seaweed"))

    def test_a_zone_named_in_the_text_is_the_row(self):
        for text, row in (("Catch 3 Fish from the Frosted Heights", "Frosted Heights"), ("Catch 5 Fish from Dazzle Beach", "Dazzle Beach"),
                          ("Catch 4 Fish in the Bind", "Bind"), ("Catch 4 Fish in Everafter", "Everafter")):
            self.assertEqual(fish_family(text, classify(text, {}), {"kind": "Fish"}), ("Fish", row), text)

    def test_seafood_is_a_row(self):
        self.assertEqual(fish_family("Catch 4 Seafood", classify("Catch 4 Seafood", {}), {"kind": "Fish"}), ("Fish", "Seafood"))

    def test_gold_ripples_are_a_row(self):
        self.assertEqual(self.fam("Catch fish in gold ripples.", {"kind": "Fish", "fish_rarity": ["Unique"]}),
                         ("Fish", "Gold ripples"))

    def test_other_fish_conditions_and_other_duties_have_none(self):
        self.assertIsNone(self.fam("Catch fish in the rain.", {"kind": "Fish", "fish_weather": ["Rain"]}))
        self.assertIsNone(self.fam("Sell any fish.", {"kind": "Fish"}))
        self.assertIsNone(self.fam("Mine for gems.", {"kind": "Mineral"}))


class Sell(unittest.TestCase):
    def test_what_is_sold_is_the_row_whatever_the_catchy_prefix(self):
        for text, row in (("Don't be shellfish! Sell 100 seafood.", "Seafood"), ("Sell 50 seafood.", "Seafood"),
                          ("Sell any fish.", "Fish"), ("Sell 1 Minerals", "Minerals"), ("Sell items.", "Items"),
                          ("Sell some crops.", "Crops")):
            self.assertEqual(sell_family(text), ("Sell", row), text)

    def test_other_duties_have_none(self):
        self.assertIsNone(sell_family("Catch any fish."))
        self.assertIsNone(sell_family("Resell nothing"))


class Gifts(unittest.TestCase):
    def test_who_gets_the_gift_is_the_row(self):
        for text, row in (("Give Goofy his favorite gift.", "Goofy"), ("Give the Pumpkin King his favorite gifts.", "Pumpkin King"),
                          ("Give Mickey & Friends their favorite gifts.", "Mickey & Friends"),
                          ("Give a boy who never grows up his favorite gift.", "Boy who never grows up"),
                          ("Bring a Friend their favorite Gift", "Any Friend"),
                          ("Give a Villager their favorite gifts.", "Any Villager")):
            self.assertEqual(gift_family(text), ("Gifts", row), text)

    def test_other_duties_have_none(self):
        self.assertIsNone(gift_family("Bring 5 Gifts"))
        self.assertIsNone(gift_family("Hang out with Goofy."))


class Currency(unittest.TestCase):
    def test_each_currency_is_a_row(self):
        star = {"item": 80000000, "type": "Currency"}
        self.assertEqual(currency_family("Earn 8,000 Star Coins.", star), ("Earn Currency", "Star Coins"))
        self.assertEqual(currency_family("Gain 500 Star Coins", star), ("Earn Currency", "Star Coins"))
        self.assertEqual(currency_family("Earn 1,500 Dreamlight.", {"item": 80300000, "type": "Currency"}),
                         ("Earn Currency", "Dreamlight"))

    def test_other_duties_have_none(self):
        self.assertIsNone(currency_family("Earn 5 trophies.", {}))
        self.assertIsNone(currency_family("Catch any fish.", {"kind": "Fish"}))


class Feed(unittest.TestCase):
    def test_the_animal_fed_is_the_row(self):
        for text, row in (("Feed a Squirrel", "Squirrel"), ("Feed a Fox", "Fox"),
                          ("Feed sea turtles their favorite food.", "Sea turtles"),
                          ("Feed Sea Turtles their favorite food.", "Sea turtles"),
                          ("Feed the Sunbirds their favorite food.", "Sunbirds")):
            self.assertEqual(feed_family(text), ("Feed", row), text)

    def test_the_animals_favorite_food_comes_from_its_kind(self):
        self.assertEqual(food_for("Squirrel"), "Peanut")
        self.assertEqual(food_for("Sea turtles"), "Seaweed")
        self.assertEqual(food_for("Sunbirds"), "Blue and Red Flowers")
        self.assertEqual(food_for("Fox"), "White Sturgeon")
        self.assertIsNone(food_for("Dragonfly"))

    def test_other_duties_have_none(self):
        self.assertIsNone(feed_family("Serve a Meal in the Restaurant"))
        self.assertIsNone(feed_family("Feed 5 critters in the Wild Tangle"))


class Craft(unittest.TestCase):
    def test_what_is_crafted_is_the_row(self):
        for text, row in (("Craft Natural Rock Paths.", "Natural Rock Paths"), ("Craft some fabric.", "fabric"),
                          ("Craft 5 Large Chests", "Large Chests"), ("Craft any Training Manual.", "Training Manual")):
            self.assertEqual(craft_family(text), ("Craft", row[:1].upper() + row[1:]), text)

    def test_other_duties_have_none(self):
        self.assertIsNone(craft_family("Get crafty!"))
        self.assertIsNone(craft_family("Cook some Whimsical Pies."))


class Clean(unittest.TestCase):
    def test_getting_rid_of_a_pest_is_the_clean_family(self):
        for text, row in (("Uproot Night Thorns.", "Night Thorns"), ("Remove 4 Night Thorns", "Night Thorns"),
                          ("Clear the evil mushrooms.", "Evil mushrooms"), ("Get rid of the evil plants.", "Evil plants"),
                          ("Uproot 3 weeds", "Weeds")):
            self.assertEqual(clean_family(text), ("Clean", row), text)

    def test_other_duties_have_none(self):
        self.assertIsNone(clean_family("Remove your hat"))
        self.assertIsNone(clean_family("Go mushroom picking."))
        self.assertIsNone(clean_family("Water dried-up plants."))


class GenericRank(unittest.TestCase):
    def test_nodes_then_any_then_a_place_then_the_specific(self):
        r = generic_rank
        self.assertEqual(r("Mine", "Nodes", "Mine 4 Rock Spots", {}), -1)
        self.assertEqual(r("Mine", "Any Gem", "Mine 30 gems.", {"kind": "Mineral"}), 0)
        self.assertEqual(r("Fish", "Any fish", "Catch any fish.", {"kind": "Fish"}), 0)
        self.assertEqual(r("Fish", "Frosted Heights", "Catch 3 Fish from the Frosted Heights", {"kind": "Fish"}), 1)
        self.assertEqual(r("Fish", "Dazzle Beach", "Catch Fish from Dazzle Beach.", {"kind": "Fish", "fish_location": ["Beach"]}), 1)
        self.assertEqual(r("Fish", "Bream", "Catch 3 Bream", {"kind": "Fish", "item": 31000022}), 2)
        self.assertEqual(r("Mine", "Purple Gems", "Mine for purple gems.", {"kind": "Mineral"}), 2)
        self.assertEqual(r("Gifts", "Any Friend", "Bring a Friend their favorite Gift", {}), 0)

    def test_a_meal_kind_is_between_any_meal_and_a_named_dish(self):
        r = generic_rank
        self.assertEqual(r("Cook", "any 2-star meal", "Cook any 2-star meal.", {"kind": "Meal"}), 0)
        self.assertEqual(r("Cook", "seafood meals", "Cook 10 seafood meals.", {"kind": "Meal"}), 1)
        self.assertEqual(r("Cook", "Tuna Burger", "Cook 10 Tuna Burgers.", {"kind": "Meal", "item": 30300186}), 2)


if __name__ == "__main__":
    unittest.main()
