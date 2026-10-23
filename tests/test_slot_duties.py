import unittest

from ddvhud.slot_duties import slot_duty_text, slot_title


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
