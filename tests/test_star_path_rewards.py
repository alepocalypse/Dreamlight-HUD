import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import gen_star_path_rewards as gen  # noqa: E402

PAGE = """==Duties==
{| class="wikitable"<!--autonumber-->
!#
!Icon
!Duty
!Amount
!Reward
|-
| align="center" | 1 || align="center" | {{inlineIcon|Night Thorns|iconOnly}} || Uproot [[Night Thorn]]s.<ref name="n">Satisfies: x</ref> || 3 || {{price|5|pumpkintoken}}
|-
| align="center" | 2 || align="center" | {{inlineIcon|Fish|iconOnly}} || Catch some [[Fishing|fish]]. || 15 || {{price|1,025|pumpkintoken}}
|-
| colspan=5 style="text-align:right;" | Total:&nbsp;{{price|30|pumpkintoken}}
|}

==Routine Duties==
{| class="wikitable"<!--autonumber-->
!Unlocks
!#
!Icon
!Duty
!Amount
!Reward
! colspan=2 | Vault Reward
|-
| rowspan="3" | Week 1<br>(2026-09-23 to 09-30)
| 1 || align="center" | {{inlineIcon|Pickaxe|iconOnly}} || Mine 20 orange gems.<ref>Satisfies: y</ref> || 20 || {{price|30|pumpkintoken}}
| rowspan=3 width=90px | [[File:Ghastly Backpack.png|90x90px|center|link=Ghastly Backpack]]
| rowspan=3 | ''[[Ghastly Backpack]]''
|-
| 2 || align="center" | {{inlineIcon|Cooking|iconOnly}} || Cook 15 servings of [[Candy]]. || 15 || {{price|35|pumpkintoken}}
|-
| rowspan="3" | Week 2<br>(2026-09-30 to 10-07)
| 3 || align="center" rowspan="3" colspan="6" | Releasing October 28<!--{{inlineIcon|Icon_TBA|iconOnly}} || TBA || Count_TBA || {{price|0|pawprinttoken}}-->
|-
| 4 <!--|| align="center" | {{inlineIcon|Icon_TBA|iconOnly}} || TBA || Count_TBA || {{price|0|pawprinttoken}}-->
|}

==In-Game Messaging==
"""
GAME = {"duties": ["Uproot Night Thorns.", "Pet your companion."], "weeks": [["Mine 20 orange gems.", "Cook 15 servings of Candy."],
                                                                   ["W2 S1", "W2 S2"]]}


class Generator(unittest.TestCase):
    def test_reads_main_and_routine_rewards_by_row_position_and_skips_releasing_weeks(self):
        table = gen.rewards("Sea2026", gen.parse_tables(PAGE), GAME, lambda msg: None)
        self.assertEqual(table, {"duties": [5, 1025], "weeks": [[30, 35]]})

    def test_warns_when_a_wiki_row_does_not_resemble_the_games_text_at_that_position(self):
        warnings = []
        gen.rewards("Sea2026", gen.parse_tables(PAGE), GAME, warnings.append)
        self.assertEqual(warnings, ["Sea2026 duty 2: wiki 'Catch some fish.' vs game 'Pet your companion.'"])

    def test_leaves_out_a_week_whose_row_count_differs_from_the_games(self):
        warnings = []
        game = {"duties": GAME["duties"], "weeks": [["a", "b", "c", "d", "e", "f"]]}
        table = gen.rewards("Sea2026", gen.parse_tables(PAGE), game, warnings.append)
        self.assertEqual((table["weeks"], warnings[-1]), ([], "Sea2026 week 1: wiki has 2 rows, game 6; left out"))
