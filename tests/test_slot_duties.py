import unittest

from ddvhud.slot_duties import slot_duty_text, slot_reward, slot_title


class SlotDutyText(unittest.TestCase):
    def test_the_target_fills_the_template(self):
        self.assertEqual(slot_duty_text(2110000034, 5, {}), "Plant 5 Vegetables")
        self.assertEqual(slot_duty_text(2110000201, 3, {}), "Add 3 Decorations to the Glittering Dunes")

    def test_an_item_name_comes_from_the_filters_item(self):
        self.assertEqual(slot_duty_text(2110000128, 3, {"item": 31000022}), "Catch 3 Bream")
        self.assertEqual(slot_duty_text(2110000186, 5, {"item": 10000043}), "Hang out with Gaston for 5 minutes")

    def test_a_duty_whose_text_key_is_not_its_name_is_found(self):
        self.assertEqual(slot_duty_text(2110000045, 1, {"item": 30300186}), "Prepare a Meal: Tuna Burger")

    def test_a_template_without_placeholders_is_unchanged(self):
        self.assertEqual(slot_duty_text(2110000051, 1, {}), "Change Outfit")

    def test_an_unknown_duty_or_item_has_a_visible_placeholder(self):
        self.assertEqual(slot_duty_text(1, 1, {}), "Duty #1")
        self.assertIn("Item #", slot_duty_text(2110000128, 3, {"item": 1}))

    def test_the_two_sets_have_the_games_names(self):
        self.assertEqual(slot_title("1540000000"), "Dreamlight Duties")
        self.assertEqual(slot_title("1540000101"), "Mist Duties")
        self.assertEqual(slot_title("5"), "Duties")


class SlotReward(unittest.TestCase):
    # amounts as the game's DutyAch.json lists them for 2110000111 (Mine Rock Spots): 200 Dreamlight, 250 Mist,
    # 150 Storybook Magic; 2110000201 (Decorate the Glittering Dunes) pays Mist only
    def test_the_reward_is_in_the_currency_its_set_pays(self):
        self.assertEqual(slot_reward(2110000111, "1540000000"), {"amount": 200, "currency": "Dreamlight"})
        self.assertEqual(slot_reward(2110000111, "1540000101"), {"amount": 250, "currency": "Mist"})
        self.assertEqual(slot_reward(2110000111, "1540000119"), {"amount": 150, "currency": "Storybook Magic"})

    def test_a_duty_missing_from_the_table_has_no_reward(self):
        self.assertIsNone(slot_reward(1, "1540000000"))

    def test_a_duty_with_no_amount_in_its_sets_currency_or_an_unknown_set_has_no_reward(self):
        self.assertIsNone(slot_reward(2110000201, "1540000000"))
        self.assertIsNone(slot_reward(2110000111, "5"))
