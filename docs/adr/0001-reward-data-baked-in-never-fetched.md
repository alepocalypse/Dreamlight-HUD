---
status: accepted
---
# Reward data is baked into the code, never fetched at runtime

Duty mode ranks Actions by Reward, but the save file holds no reward amounts. Dreamlight and Mist Duty
rewards exist in the game's own data files; Star Path token rewards exist only on the community wiki
(dreamlightvalleywiki.com), which lags the game by days for new Star Paths and unreleased weeks. We
read both through generator tools (`tools/gen_*.py`) and commit the resulting tables, exactly as the
recipe and critter data already are, and the app never goes online. Fetching the wiki at runtime would
be fresher, but the README promises that the app makes no network requests of its own, and that promise
is worth more than a day of stale rewards. Consequence: a new Star Path, or a week the wiki has not
listed yet, ranks at the Star Path's median known reward until someone reruns the generator.

The cross-currency ratio is baked in as well (1 Star Path token = 10 Dreamlight; Dreamlight, Mist and
Storybook Magic at par) rather than user-configurable: the game pays the same nominal amounts across
its own currencies, and a settings panel was judged not worth its weight for a first version.
