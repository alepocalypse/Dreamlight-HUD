import unittest

from ddvhud import catalog


class CompanionLookup(unittest.TestCase):
    def test_unknown_companion_has_numbered_name_and_unknown_job(self):
        c = catalog.companion(99999999)
        self.assertEqual((c.name, c.job), ("Companion #99999999", "unknown"))

    def test_known_companion_has_its_name_and_job(self):
        c = catalog.companion(120000000)
        self.assertEqual((c.name, c.job), ("Pua", "Foraging"))


class CritterLookup(unittest.TestCase):
    def test_known_critter_has_name_companion_and_feedings(self):
        c = catalog.critter(120100001)
        self.assertEqual((c.name, c.companion, c.needed), ("Classic Squirrel", 120000001, 2))

    def test_unknown_critter_is_numbered_with_no_companion_or_feedings(self):
        c = catalog.critter(99999999)
        self.assertEqual((c.name, c.companion, c.needed), ("Critter #99999999", None, None))


class VillagerLookup(unittest.TestCase):
    def test_known_and_unknown_villager_names(self):
        self.assertEqual(catalog.villager_name(10000003), "Mickey Mouse")
        self.assertEqual(catalog.villager_name(99999999), "Villager #99999999")

    def test_wiki_url_uses_underscores_and_quoting(self):
        self.assertEqual(catalog.villager_wiki_url(10000003), "https://dreamlightvalleywiki.com/Mickey_Mouse")
        names = {1: "Mother Gothel's Dr. X/Y?#"}
        self.assertEqual(catalog.villager_wiki_url(1, names),
                         "https://dreamlightvalleywiki.com/Mother_Gothel%27s_Dr._X%2FY%3F%23")

    def test_unknown_villager_has_no_wiki_url(self):
        self.assertIsNone(catalog.villager_wiki_url(99999999))


class ItemLookup(unittest.TestCase):
    WIKI = "https://dreamlightvalleywiki.com/"

    def test_known_and_unknown_item_names(self):
        self.assertEqual(catalog.item_name(30200015), "Tomato")
        self.assertEqual(catalog.item_name(1), "Item #1")

    def test_item_wiki_url_quotes_the_name(self):
        self.assertEqual(catalog.item_wiki_url(30200015), self.WIKI + "Tomato")
        self.assertEqual(catalog.item_wiki_url(30800088), self.WIKI + "Orange_%26_Red_Marsh_Milkweed")

    def test_item_wiki_url_follows_overrides(self):
        self.assertEqual(catalog.item_wiki_url(31600040), self.WIKI + "Onyx")   # Shiny Onyx has no page of its own
        self.assertEqual(catalog.item_wiki_url(30300112), self.WIKI + "index.php?search=Grilled%20Eel")
        self.assertEqual(catalog.item_wiki_url(30200018), self.WIKI + "index.php?search=Lime")

    def test_unknown_item_has_no_wiki_url(self):
        self.assertIsNone(catalog.item_wiki_url(1))


class ProfessionLookup(unittest.TestCase):
    def test_known_and_unknown_profession_names(self):
        self.assertEqual(catalog.profession_name(1500000003), "Mining")
        self.assertEqual(catalog.profession_name(1), "Unknown profession")


class IngredientLookup(unittest.TestCase):
    def test_where_to_get_an_ingredient(self):
        self.assertEqual(catalog.ingredient_where("Agave"), "Forage, Dunes")

    def test_ingredient_not_on_the_wiki_list_has_no_where(self):
        self.assertEqual(catalog.ingredient_where("Not A Food"), "")

    def test_category_members_are_item_ids_of_its_ingredients(self):
        members = catalog.category_item_ids("Sweets")
        self.assertIn(30200144, members)                      # Agave
        self.assertNotIn(30200015, members)                   # Tomato is a Vegetable

    def test_item_id_by_name(self):
        self.assertEqual(catalog.item_id("Agave"), 30200144)
        self.assertIsNone(catalog.item_id("Not A Food"))


if __name__ == "__main__":
    unittest.main()
