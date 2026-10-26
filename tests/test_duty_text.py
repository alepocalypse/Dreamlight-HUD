import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import gen_duties  # noqa: E402

from ddvhud import duty_text  # noqa: E402


def varint(n):
    out = bytearray()
    while n > 127:
        out.append(n & 0x7F | 0x80)
        n >>= 7
    return bytes(out + bytes([n]))


def pair(key, value):
    """One record as the .locbin stores it: 0x0a, length, then field 1 (key) and field 2 (text)."""
    k, v = key.encode(), value.encode()
    body = b"\x0a" + varint(len(k)) + k + b"\x12" + varint(len(v)) + v
    return b"\x0a" + varint(len(body)) + body


class ParseLocbin(unittest.TestCase):
    def test_reads_key_value_pairs_with_one_and_two_byte_lengths(self):
        long_text = "x" * 200
        data = pair("Sea_Title", "Seafaring Star Path") + pair("Sea_Task02_Description", long_text)
        self.assertEqual(gen_duties.parse_locbin(data),
                         {"Sea_Title": "Seafaring Star Path", "Sea_Task02_Description": long_text})


class StarPathTable(unittest.TestCase):
    TEXT = {
        "Sea2026_Title": "Sea Star Path", "Sea2026_CurrencyName": "Doubloon Tokens",
        "Sea2026_Task10_Description": "Second\u00a0duty.", "Sea2026_Task02_Description": "First duty.",
        "Sea2026_Week02Task01_Description": "W2 S1", "Sea2026_Week01Task03_Description": "W1 S3",
        "Sea2026_Week01Task01_Description": "W1 S1", "Sea2026_Week01Task02_Description": "W1 S2",
        "Sea2026Start_Title": "News", "Plain_Title": "No duties", "Bundle_Foo_Title": "Bundle",
    }

    def test_groups_by_star_path_ordering_tasks_numerically_and_fixing_spaces(self):
        self.assertEqual(gen_duties.star_paths(self.TEXT), {"Sea2026": {
            "title": "Sea Star Path", "currency": "Doubloon Tokens",
            "duties": ["First duty.", "Second duty."],
            "weeks": [["W1 S1", "W1 S2", "W1 S3"], ["W2 S1"]]}})


class Lookup(unittest.TestCase):
    def test_seafaring_positions_0_to_7_match_the_duties_page(self):
        self.assertEqual(duty_text.duty_text("Seafaring2026", 0), "Catch any fish.")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 1), "Pet your companion.")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 2), "Go fishing for seaweed (on purpose!).")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 3), "Go mining for gems.")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 4), "Feed Sea Turtles their favorite food.")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 5), "Buy something from Scrooge McDuck's Store.")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 6), "Catch Fish from Dazzle Beach.")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 7), "Mine for blue gems.")

    def test_unknown_star_path_or_position_gives_a_numbered_placeholder(self):
        self.assertEqual(duty_text.duty_text("Nope2030", 0), "Duty #1")
        self.assertEqual(duty_text.duty_text("Seafaring2026", 25), "Duty #26")

    def test_weekly_duty_text_by_week_and_slot(self):
        self.assertEqual(duty_text.weekly_duty_text("Seafaring2026", 0, 0), "Catch 20 fish.")

    def test_unknown_weekly_duty_gives_a_placeholder(self):
        self.assertEqual(duty_text.weekly_duty_text("Seafaring2026", 6, 0), "Weekly duty #7-1")
        self.assertEqual(duty_text.weekly_duty_text("Seafaring2026", 0, 3), "Weekly duty #1-4")
        self.assertEqual(duty_text.weekly_duty_text("Nope2030", 1, 2), "Weekly duty #2-3")

    def test_title_and_currency_name(self):
        self.assertEqual(duty_text.title("Seafaring2026"), "Seafaring Star Path")
        self.assertEqual(duty_text.currency_name("Seafaring2026"), "Doubloon Tokens")
        self.assertEqual(duty_text.title("Nope2030"), "Nope2030")
        self.assertEqual(duty_text.currency_name("Nope2030"), "Tokens")


if __name__ == "__main__":
    unittest.main()


class Rewards(unittest.TestCase):
    """Amounts from the wiki's Haunting Elegance Star Path page (2026-10-25): Duties row 1 pays 5, row 6 pays 25;
    Routine Duties week 1 pays 30, 30, 40; weeks 6 and 7 were still 'Releasing ...'."""

    def test_a_main_duty_pays_the_amount_of_its_row_in_the_star_paths_currency(self):
        self.assertEqual(duty_text.duty_reward("HauntingElegance2026", 0), {"amount": 5, "currency": "Pumpkin Tokens"})
        self.assertEqual(duty_text.duty_reward("HauntingElegance2026", 5), {"amount": 25, "currency": "Pumpkin Tokens"})

    def test_a_routine_duty_pays_the_amount_of_its_week_and_slot(self):
        self.assertEqual(duty_text.weekly_duty_reward("HauntingElegance2026", 0, 2),
                         {"amount": 40, "currency": "Pumpkin Tokens"})
        self.assertEqual(duty_text.weekly_duty_reward("HauntingElegance2026", 0, 0),
                         {"amount": 30, "currency": "Pumpkin Tokens"})

    def test_duties_missing_from_the_table_have_no_reward(self):
        self.assertIsNone(duty_text.duty_reward("HauntingElegance2026", 500))
        self.assertIsNone(duty_text.weekly_duty_reward("HauntingElegance2026", 5, 0))   # 'Releasing October 28'
        self.assertIsNone(duty_text.weekly_duty_reward("HauntingElegance2026", 0, 3))
        self.assertIsNone(duty_text.duty_reward("NoSuchPath2099", 0))
