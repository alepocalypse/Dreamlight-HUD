# Villager content packs

Researched 2026-10-23 for GitHub issue #16. Sources read via the wiki's MediaWiki API (`api.php?action=parse&prop=wikitext`) fetched through WebFetch, which summarises pages with a small model; wording quoted below is from those summaries. Direct `curl` and the wiki's `Version_History` HTML page were blocked (Cloudflare 403), so nothing was read byte-for-byte.

## 1. Villager to pack

Pack assignments come from the wiki's Characters page (villagers grouped by area, 74 total) and the area pages. All 74 Villagers in `ddvhud/villagers.py` were matched. Counts: base 57 listed on the wiki, of which the roster has all matching names; Eternity Isle 5, Storybook Vale 5, Wishblossom 4, Honeyglow Woods 3.

| id | name | pack | source |
|---|---|---|---|
| 10000002 | Belle | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000003 | Mickey Mouse | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000004 | Goofy | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000007 | The Beast | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000009 | Pumbaa | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000010 | Timon | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000011 | Donald Duck | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000013 | Buzz Lightyear | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000014 | WALL·E | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000016 | Moana | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000018 | Remy | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000019 | Maui | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000020 | Lumiere | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000025 | Cogsworth | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000027 | Rapunzel | Expansion 1: A Rift in Time (paid) | https://dreamlightvalleywiki.com/Eternity_Isle |
| 10000029 | Olaf | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000030 | Simba | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000031 | Vanellope | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000032 | Woody | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000033 | Nala | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000034 | Anna | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000035 | Merlin | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000038 | EVE | Expansion 1: A Rift in Time (paid) | https://dreamlightvalleywiki.com/Eternity_Isle |
| 10000040 | Cinderella | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000043 | Gaston | Expansion 1: A Rift in Time (paid) | https://dreamlightvalleywiki.com/Eternity_Isle |
| 10000044 | Elsa | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000046 | Minnie Mouse | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000052 | Prince Eric | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000053 | Ariel | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000055 | Scrooge McDuck | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000059 | Flynn | Expansion 2: The Storybook Vale (paid) | https://dreamlightvalleywiki.com/Storybook_Vale |
| 10000060 | Ursula | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000061 | Scar | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000062 | Mother Gothel | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000063 | The Fairy Godmother | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000070 | Kristoff | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000073 | Stitch | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000098 | The Forgotten | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000099 | Mirabel | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000103 | Jafar | Expansion 1: A Rift in Time (paid) | https://dreamlightvalleywiki.com/Eternity_Isle |
| 10000105 | Jack Skellington | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000109 | Sulley | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000110 | Mike Wazowski | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000113 | Daisy | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000114 | Oswald | Expansion 1: A Rift in Time (paid) | https://dreamlightvalleywiki.com/Eternity_Isle |
| 10000115 | Mulan | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000116 | Mushu | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000117 | Merida | Expansion 2: The Storybook Vale (paid) | https://dreamlightvalleywiki.com/Storybook_Vale |
| 10000119 | Hades | Expansion 2: The Storybook Vale (paid) | https://dreamlightvalleywiki.com/Storybook_Vale |
| 10000125 | Tiana | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000127 | Maleficent | Expansion 2: The Storybook Vale (paid) | https://dreamlightvalleywiki.com/Storybook_Vale |
| 10000129 | Sally | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000130 | Aladdin | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000131 | Jasmine | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000179 | Lady | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000180 | Tramp | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000182 | Pocahontas | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000012 | Ralph | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000132 | Alice | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000133 | Cheshire Cat | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000135 | Aurora | Expansion 2: The Storybook Vale (paid) | https://dreamlightvalleywiki.com/Storybook_Vale |
| 10000137 | Peter Pan | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000156 | Joy | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000157 | Sadness | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000158 | Snow White | Expansion 3: Wishblossom Ranch (paid) | https://dreamlightvalleywiki.com/Wishblossom_Mountains |
| 10000160 | Tinker Bell | Expansion 3: Wishblossom Ranch (paid) | https://dreamlightvalleywiki.com/Wishblossom_Mountains |
| 10000162 | Cruella | Expansion 3: Wishblossom Ranch (paid) | https://dreamlightvalleywiki.com/Wishblossom_Mountains |
| 10000166 | Tigger | Expansion 3: Wishblossom Ranch (paid) | https://dreamlightvalleywiki.com/Wishblossom_Mountains |
| 10000183 | Winnie the Pooh | Adventure Pack 1: Honeyglow Woods (paid) | https://dreamlightvalleywiki.com/Honeyglow_Woods |
| 10000184 | Piglet | Adventure Pack 1: Honeyglow Woods (paid) | https://dreamlightvalleywiki.com/Honeyglow_Woods |
| 10000185 | Eeyore | Adventure Pack 1: Honeyglow Woods (paid) | https://dreamlightvalleywiki.com/Honeyglow_Woods |
| 10000186 | Phil | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000187 | Hercules | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |
| 10000212 | Oogie Boogie | Base game (incl. free updates; see caveat) | https://dreamlightvalleywiki.com/Characters |

Per-villager pages confirm the paid assignments for Tigger ("requires purchasing the paid expansion Expansion 3: Wishblossom Ranch") and Winnie the Pooh ("requires purchasing the paid adventure pack expansion 'Honeyglow Woods'"): https://dreamlightvalleywiki.com/Tigger, https://dreamlightvalleywiki.com/Winnie_the_Pooh.

Caveat: the "Dreamlight Valley" area on Characters is described as base game needing no expansion. I did not check each base villager's page, so which free update added which (for example Ralph, Vanellope, Lady, Tramp, Hercules) is not recorded here. Not needed for paid/free split.

## 2. Packs

| wiki name | wiki URL | save ID | status |
|---|---|---|---|
| Base game | https://dreamlightvalleywiki.com/Characters | `BaseGame` | confirmed present in real save (`LastKnownBoughtExpansionsAnyPlatform`) |
| Expansion 1: A Rift in Time (released 5 Dec 2023) | https://dreamlightvalleywiki.com/Version_History/Expansion_1 , https://dreamlightvalleywiki.com/Eternity_Isle | `Expansion01` | ID confirmed in save; mapping to A Rift in Time is inferred (see below), strongly supported |
| Expansion 2: The Storybook Vale (20 Nov 2024) | https://dreamlightvalleywiki.com/Version_History/Expansion_2 , https://dreamlightvalleywiki.com/Storybook_Vale | unknown | unconfirmed (guess would be `Expansion02`, not verified) |
| Expansion 3: Wishblossom Ranch (19 Nov 2025 per a search summary of the wiki version history) | https://dreamlightvalleywiki.com/Wishblossom_Mountains | unknown | unconfirmed |
| Adventure Pack 1: Honeyglow Woods (8 Jul 2026, same caveat) | https://dreamlightvalleywiki.com/Honeyglow_Woods | unknown | unconfirmed |

Why `Expansion01` = A Rift in Time: (a) the wiki numbers it "Expansion 1" and A Rift in Time is the first expansion; (b) the local save `samples/profile.decoded.json` has `Expansion01` asset paths such as `SceneLayouts/OffGridBuildings/Expansion01/JafarPalaceSecretEntrance/...`, and Jafar belongs to Eternity Isle; (c) the Steam ownership entry is named `Expansion1PackExpansionPass_Steam_OnlineKey`. No primary source states the mapping in words.

## 3. Unconfirmed / conflicting

- Save IDs for Storybook Vale, Wishblossom Ranch, Honeyglow Woods: not found. Tried web searches for `Expansion02`/`Expansion03`/`LastKnownBoughtExpansions`; only GBAtemp forum posts naming the three key names turned up (page itself 403). No official source states them. Do not assume a naming pattern.
- Wiki area page for Wishblossom is titled `Wishblossom_Mountains` but the pack is named "Wishblossom Ranch" (a name I first tried, "Wishblossom_Ridge", does not exist). The Characters summary calls the area "Wishblossom Mountains". Treat as a naming quirk.
- Oswald: the wiki's `Version_History/Expansion_1` character list names EVE, Gaston, Jafar, Rapunzel only (and says its lists are unofficial); the Eternity Isle page and Characters list Oswald there too. I followed Eternity Isle.
- Release dates for Wishblossom and Honeyglow come from a search-engine summary of the wiki's Version History page, which I could not open directly.
- No official Disney/Gameloft page was consulted for pack membership; store listings appeared in search results but were not read.
- Honeyglow Woods is a paid "adventure pack", not numbered an expansion; whether the game's save treats it as an "Expansion" key is unknown.
- Base-game villagers added by free updates were not individually verified.
