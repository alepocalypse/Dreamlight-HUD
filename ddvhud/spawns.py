"""Where a gift item spawns, for the To-do cards: item id -> (how you get it, zones in the wiki's order).

Copied from dreamlightvalleywiki.com item pages (MediaWiki API, read 2026-10-21); regenerate the rows
with: python3 tools/gen_spawns.py. Zones are the wiki's names, most likely first as the wiki lists them.
Meals are absent (spawn_for answers 'Cooking' for them); items with no listed zone are absent. The how is the Profession the
icon shows (a cooking pot for meals): Mining, Digging, Fishing, Gardening, Foraging.
"""
SPAWNS = {
    30200000: ('Gardening', ('Peaceful Meadow',)),  # Carrot
    30200001: ('Foraging', ('Dazzle Beach', 'Forest of Valor')),  # Blueberry
    30200002: ('Foraging', ('Plaza', 'Forgotten Lands')),  # Apple
    30200003: ('Gardening', ('Glade of Trust',)),  # Rice
    30200004: ('Gardening', ('Peaceful Meadow', "Ancient's Landing")),  # Wheat
    30200005: ('Gardening', ('Forgotten Lands', 'Wild Tangle')),  # Potato
    30200009: ('Gardening', ('Peaceful Meadow',)),  # Lettuce
    30200010: ('Gardening', ('Forest of Valor',)),  # Onion
    30200011: ('Gardening', ('Dazzle Beach', 'Glittering Dunes')),  # Corn
    30200012: ('Gardening', ('Forest of Valor',)),  # Bell Pepper
    30200013: ('Gardening', ('Sunlit Plateau', 'Glittering Dunes')),  # Chili Pepper
    30200014: ('Gardening', ('Frosted Heights',)),  # Cucumber
    30200015: ('Gardening', ('Dazzle Beach', 'Wild Tangle')),  # Tomato
    30200016: ('Foraging', ('Sunlit Plateau', 'Frosted Heights')),  # Cherry
    30200017: ('Foraging', ('Forest of Valor', 'Glade of Trust')),  # Lemon
    30200019: ('Foraging', ("Ancient's Landing",)),  # Strawberry
    30200020: ('Foraging', ('Glade of Trust', 'Sunlit Plateau')),  # Cocoa Bean
    30200022: ('Foraging', ('Peaceful Meadow', 'Dazzle Beach')),  # Banana
    30200045: ('Gardening', ('Dazzle Beach',)),  # Sugarcane
    30200046: ('Foraging', ('Frosted Heights', 'Forgotten Lands')),  # Gooseberry
    30200047: ('Gardening', ('Frosted Heights',)),  # Eggplant
    30200048: ('Foraging', ('Plaza', 'Peaceful Meadow')),  # Raspberry
    30200049: ('Gardening', ('Glade of Trust',)),  # Spinach
    30200051: ('Gardening', ('Sunlit Plateau',)),  # Zucchini
    30200058: ('Foraging', ('Glade of Trust',)),  # Mushroom
    30200062: ('Gardening', ('Forgotten Lands',)),  # Pumpkin
    30200081: ('Gardening', ('Frosted Heights',)),  # Asparagus
    30200082: ('Gardening', ('Forest of Valor', "Ancient's Landing")),  # Canola
    30200083: ('Gardening', ('Forgotten Lands',)),  # Leek
    30200084: ('Gardening', ('Glade of Trust',)),  # Okra
    30200085: ('Gardening', ('Sunlit Plateau',)),  # Soya
    30200086: ('Foraging', ('Plaza',)),  # Oregano
    30200087: ('Foraging', ('Peaceful Meadow',)),  # Basil
    30200088: ('Foraging', ('Forest of Valor', 'Drowsybloom Acre', 'Gloommeadow')),  # Garlic
    30200089: ('Foraging', ('Forgotten Lands',)),  # Ginger
    30200090: ('Foraging', ('Sunlit Plateau', 'Mythopia')),  # Vanilla
    30200091: ('Foraging', ('Frosted Heights',)),  # Mint
    30200096: ('Foraging', ('Dazzle Beach',)),  # Coconut
    30200111: ('Foraging', ('Glade of Trust',)),  # Coffee Bean
    30200115: ('Foraging', ('Sunlit Plateau', 'Glade of Trust', 'Frosted Heights', 'Forgotten Lands')),  # Dreamlight Fruit
    30200124: ('Gardening', ("Ancient's Landing",)),  # Grapes
    30200125: ('Foraging', ('Wild Tangle',)),  # Almonds
    30200126: ('Foraging', ('Glittering Dunes',)),  # Dates
    30200127: ('Gardening', ('Glittering Dunes',)),  # Melon
    30200129: ('Gardening', ('Wild Tangle',)),  # Pineapple
    30200131: ('Foraging', ("Ancient's Landing",)),  # Nestling Pear
    30200132: ('Foraging', ('Glittering Dunes',)),  # Cactoberries
    30200133: ('Foraging', ('Wild Tangle',)),  # Dreamango
    30200134: ('Gardening', ("Ancient's Landing",)),  # Cosmic Figs
    30200135: ('Gardening', ('Glittering Dunes',)),  # Flute Root
    30200136: ('Gardening', ("Ancient's Landing",)),  # Celery
    30200137: ('Gardening', ("Ancient's Landing",)),  # Yam
    30200138: ('Gardening', ('Glittering Dunes',)),  # Beans
    30200139: ('Gardening', ('Glittering Dunes',)),  # Broccoli
    30200140: ('Gardening', ('Wild Tangle',)),  # Cabbage
    30200141: ('Gardening', ('Wild Tangle',)),  # Ruby Lentils
    30200142: ('Gardening', ('Wild Tangle',)),  # Turnip
    30200143: ('Foraging', ("Ancient's Landing",)),  # Cumin
    30200144: ('Foraging', ('Glittering Dunes',)),  # Agave
    30200145: ('Foraging', ('Glittering Dunes',)),  # Paprika
    30200146: ('Foraging', ("Ancient's Landing",)),  # Majestea
    30200147: ('Foraging', ('Wild Tangle', 'The Bind')),  # Cinnamon
    30200148: ('Foraging', ('Wild Tangle',)),  # Bamboo
    30200162: ('Gardening', ('The Bind',)),  # Chia Seeds
    30200163: ('Gardening', ('The Bind',)),  # Cauliflower
    30200165: ('Gardening', ('The Bind',)),  # Ring Squash
    30200167: ('Gardening', ('The Bind',)),  # Barley
    30200168: ('Foraging', ('The Bind',)),  # Sour Berries
    30200169: ('Foraging', ('The Bind',)),  # Persimmon
    30200170: ('Foraging', ('The Bind',)),  # Cape Gooseberry
    30200171: ('Gardening', ('Mythopia',)),  # Honeydew Melon
    30200172: ('Gardening', ('Mythopia',)),  # Radicchio
    30200173: ('Gardening', ('Mythopia',)),  # Black Pepper
    30200174: ('Foraging', ('Mythopia',)),  # Olives
    30200175: ('Foraging', ('Mythopia',)),  # Nutmeg
    30200176: ('Fishing', ('The Bind',)),  # Sea Grapes
    30200177: ('Gardening', ('Everafter',)),  # Faerie Rye
    30200178: ('Foraging', ('Mythopia',)),  # Lightning Spice
    30200179: ('Gardening', ('Everafter',)),  # Radish
    30200180: ('Gardening', ('Everafter',)),  # Oats
    30200181: ('Gardening', ('Everafter',)),  # Rhubarb
    30200182: ('Gardening', ('Everafter',)),  # Green Beans
    30200183: ('Foraging', ('Everafter',)),  # Brussels Sprout
    30200184: ('Foraging', ('Everafter',)),  # Spiral Strawberries
    30200186: ('Foraging', ('Everafter',)),  # Porcini Mushrooms
    30200187: ('Fishing', ('Everafter',)),  # Salt Crystal
    30200191: ('Foraging', ('Plaza', 'Peaceful Meadow')),  # Pink Marshmallow
    30200200: ('Foraging', ('The Bind',)),  # Trumpet Snail
    30200207: ('Gardening', ('Wishblossom Mountains',)),  # Beetroot
    30200208: ('Gardening', ('Wishblossom Mountains',)),  # Scarlet Kale
    30200209: ('Foraging', ('Wishing Alps',)),  # Dill
    30200210: ('Foraging', ('Wishing Alps',)),  # Red Currants
    30200213: ('Foraging', ('Glamour Gulch',)),  # Button Mushroom
    30200214: ('Foraging', ('Glamour Gulch',)),  # Pincushion Peach
    30200215: ('Gardening', ('Wishblossom Mountains',)),  # Pearly Barley
    30200216: ('Gardening', ('Wishblossom Mountains',)),  # Dark Chocolate Coffee Beans
    30200217: ('Foraging', ('Pixie Acres',)),  # Fairy Sprinkles
    30200218: ('Foraging', ('Pixie Acres',)),  # Bonsai Star Fruit
    30200219: ('Gardening', ('Wishblossom Mountains',)),  # Lollipop Fruit
    30200220: ('Gardening', ('Wishblossom Mountains',)),  # Fairy Kamut
    30200226: ('Foraging', ('Honeyglow Woods',)),  # Truffle
    30200227: ('Foraging', ('Gloommeadow', 'Braveheart Grove')),  # Juniper Berry
    30200228: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Sweet Chestnut
    30200229: ('Gardening', ('Honeyglow Woods',)),  # Parsnip
    30200230: ('Gardening', ('Honeyglow Woods',)),  # Pufflebud Pods
    30200231: ('Gardening', ('Honeyglow Woods',)),  # Golden Pattypan
    30800054: ('Foraging', ('Forest of Valor',)),  # Purple Bell Flower
    30800055: ('Foraging', ('Sunlit Plateau',)),  # Pink Bromeliad
    30800058: ('Foraging', ('Peaceful Meadow',)),  # White Daisy
    30800059: ('Foraging', ('Plaza',)),  # Dandelion
    30800060: ('Foraging', ('Plaza',)),  # Purple Falling Penstemon
    30800061: ('Foraging', ('Sunlit Plateau',)),  # Pink Houseleek
    30800062: ('Foraging', ('Dazzle Beach',)),  # Blue Hydrangea
    30800063: ('Foraging', ('Forgotten Lands',)),  # Purple Impatiens
    30800064: ('Foraging', ('Glade of Trust',)),  # White Marsh Milkweed
    30800065: ('Foraging', ('Forgotten Lands',)),  # Red Nasturtium
    30800066: ('Foraging', ('Frosted Heights',)),  # Red Passion Lily
    30800067: ('Foraging', ('Peaceful Meadow',)),  # Purple Rising Penstemon
    30800068: ('Foraging', ('Forest of Valor',)),  # Blue Star Lily
    30800069: ('Foraging', ('Dazzle Beach',)),  # Sunflower
    30800071: ('Foraging', ('Forest of Valor',)),  # Red Bell Flower
    30800072: ('Foraging', ('Sunlit Plateau',)),  # Red Bromeliad
    30800073: ('Foraging', ('Forest of Valor',)),  # White Bell Flower
    30800074: ('Foraging', ('Sunlit Plateau',)),  # Yellow Bromeliad
    30800075: ('Foraging', ('Peaceful Meadow',)),  # Yellow Daisy
    30800076: ('Foraging', ('Peaceful Meadow',)),  # Red Daisy
    30800077: ('Foraging', ('Plaza',)),  # Red Falling Penstemon
    30800078: ('Foraging', ('Plaza',)),  # Blue Falling Penstemon
    30800079: ('Foraging', ('Plaza',)),  # White & Pink Falling Penstemon
    30800080: ('Foraging', ('Sunlit Plateau',)),  # Orange Houseleek
    30800081: ('Foraging', ('Dazzle Beach',)),  # Pink Hydrangea
    30800082: ('Foraging', ('Dazzle Beach',)),  # Purple Hydrangea
    30800083: ('Foraging', ('Dazzle Beach',)),  # White & Red Hydrangea
    30800084: ('Foraging', ('Forgotten Lands',)),  # White Impatiens
    30800085: ('Foraging', ('Glade of Trust',)),  # Orange Marsh Milkweed
    30800086: ('Foraging', ('Glade of Trust',)),  # Purple Marsh Milkweed
    30800087: ('Foraging', ('Glade of Trust',)),  # Blue Marsh Milkweed
    30800088: ('Foraging', ('Glade of Trust',)),  # Orange & Red Marsh Milkweed
    30800089: ('Foraging', ('Forgotten Lands',)),  # Orange Nasturtium
    30800090: ('Foraging', ('Forgotten Lands',)),  # Yellow Nasturtium
    30800091: ('Foraging', ('Frosted Heights',)),  # White Passion Lily
    30800092: ('Foraging', ('Frosted Heights',)),  # Green Passion Lily
    30800093: ('Foraging', ('Frosted Heights',)),  # Blue Passion Lily
    30800094: ('Foraging', ('Frosted Heights',)),  # Black Passion Lily
    30800095: ('Foraging', ('Peaceful Meadow',)),  # Green Rising Penstemon
    30800096: ('Foraging', ('Forest of Valor',)),  # Orange Star Lily
    30800108: ('Foraging', ('The Docks', 'The Courtyard')),  # Orange Bird of Paradise
    30800109: ('Foraging', ('The Docks', 'The Courtyard')),  # Yellow Bird of Paradise
    30800110: ('Foraging', ('The Docks', 'The Courtyard')),  # White Bird of Paradise
    30800111: ('Foraging', ('The Overlook', 'The Ruins')),  # Blue Luminescent Flower
    30800112: ('Foraging', ('The Overlook', 'The Ruins')),  # Green Luminescent Flower
    30800113: ('Foraging', ('The Overlook', 'The Ruins')),  # Pink Luminescent Flower
    30800114: ('Foraging', ('The Overlook', 'The Ruins')),  # Red Luminescent Flower
    30800115: ('Foraging', ('The Plains', 'The Wastes')),  # Blue Glass-Like Flowers
    30800116: ('Foraging', ('The Plains', 'The Wastes')),  # Green Glass-Like Flowers
    30800117: ('Foraging', ('The Plains', 'The Wastes')),  # Black Glass-Like Flowers
    30800118: ('Foraging', ('The Plains', 'The Wastes')),  # Orange Glass-Like Flowers
    30800119: ('Foraging', ('The Oasis', 'The Borderlands')),  # Pink Cactus Flower
    30800120: ('Foraging', ('The Oasis', 'The Borderlands')),  # Yellow Cactus Flower
    30800121: ('Foraging', ('The Oasis', 'The Borderlands')),  # White Cactus Flower
    30800122: ('Foraging', ('The Oasis', 'The Borderlands')),  # Purple Cactus Flower
    30800123: ('Foraging', ('The Grasslands', 'The Promenade')),  # Green Fly Trap
    30800124: ('Foraging', ('The Grasslands', 'The Promenade')),  # Purple Fly Trap
    30800125: ('Foraging', ('The Grove', 'The Lagoon')),  # Red Pitcher Plant
    30800126: ('Foraging', ('The Grove', 'The Lagoon')),  # Yellow Pitcher Plant
    30800127: ('Foraging', ('The Grove', 'The Lagoon')),  # Orange Pitcher Plant
    30800128: ('Foraging', ("Beast's Greenhouse",)),  # Red Rose
    30800139: ('Foraging', ('The Elysian Fields', 'Mount Olympus')),  # Crimson Eternal Poppies
    30800140: ('Foraging', ('The Fiery Plains', "The Statue's Shadow")),  # Goldenrod Eternal Poppies
    30800141: ('Foraging', ('The Elysian Fields', "The Statue's Shadow")),  # Teal Eternal Poppies
    30800142: ('Foraging', ('The Fiery Plains', 'Mount Olympus')),  # Fuchsia Eternal Poppies
    30800143: ('Foraging', ('The Bind',)),  # Yellow Tale Cone Flowers
    30800144: ('Foraging', ('The Bind',)),  # Blue Tale Cone Flower
    30800145: ('Foraging', ('The Bind',)),  # Olive Green Tale Cone Flower
    30800146: ('Foraging', ('The Bind',)),  # Beige Tale Cone Flower
    30800147: ('Foraging', ('The Wild Woods', 'The Beanstalk Marshes')),  # Dusty Violet Rose
    30800148: ('Foraging', ('Teapot Falls', 'The Fallen Fortress')),  # Slate Gray Rose
    30800149: ('Foraging', ('The Wild Woods', 'The Fallen Fortress')),  # White Rose
    30800150: ('Foraging', ('Teapot Falls', 'The Beanstalk Marshes')),  # Pink Rose
    30800164: ('Foraging', ('Wishing Alps',)),  # White Crocus
    30800165: ('Foraging', ('Wishing Alps',)),  # Yellow Crocus
    30800166: ('Foraging', ('Wishing Alps',)),  # Purple Crocus
    30800167: ('Foraging', ('Wishing Alps',)),  # Pink Crocus
    30800173: ('Foraging', ('Glamour Gulch',)),  # Black Silk Flower
    30800174: ('Foraging', ('Glamour Gulch',)),  # Green Silk Flower
    30800175: ('Foraging', ('Glamour Gulch',)),  # Red Silk Flower
    30800176: ('Foraging', ('Glamour Gulch',)),  # Silver Silk Flower
    30800177: ('Foraging', ('Pixie Acres',)),  # Pink Lily of the Valley
    30800178: ('Foraging', ('Pixie Acres',)),  # Blue Lily of the Valley
    30800179: ('Foraging', ('Pixie Acres',)),  # Yellow Lily of the Valley
    30800180: ('Foraging', ('Pixie Acres',)),  # Purple Lily of the Valley
    30800181: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # White Thistle
    30800182: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Yellow & Orange Foxglove
    30800183: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # White & Pink Foxglove
    30800184: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Rose & Cream Foxglove
    30800185: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Purple & White Foxglove
    30800186: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Red Thistle
    30800187: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Purple Thistle
    30800188: ('Foraging', ('Drowsybloom Acre', 'Gloommeadow', 'Braveheart Grove', 'Nectar Apiary')),  # Yellow Thistle
    31000000: ('Fishing', ('Sunlit Plateau', 'Frosted Heights', 'The Grasslands', 'The Promenade')),  # Salmon
    31000001: ('Fishing', ('Dazzle Beach', 'Glade of Trust', 'Forgotten Lands', 'The Docks', 'The Overlook', 'Everafter', 'Glamour Gulch')),  # Cod
    31000002: ('Fishing', ('Peaceful Meadow', 'Forest of Valor', 'The Oasis', 'Everafter')),  # Rainbow Trout
    31000003: ('Fishing', ('Sunlit Plateau', 'Frosted Heights', 'Pixie Acres')),  # Tilapia
    31000004: ('Fishing', ('Glade of Trust', 'Forgotten Lands', 'The Bind', 'Wishing Alps')),  # Tuna
    31000005: ('Fishing', ('Dream Castle', 'Wild Tangle')),  # Seaweed
    31000007: ('Fishing', ('Dazzle Beach',)),  # Shrimp
    31000008: ('Fishing', ('Dazzle Beach',)),  # Kingfish
    31000009: ('Fishing', ('Glade of Trust', 'Forgotten Lands', 'Mythopia')),  # Squid
    31000010: ('Fishing', ('Dazzle Beach',)),  # Swordfish
    31000011: ('Fishing', ('Forgotten Lands', 'The Docks', 'The Overlook')),  # Sole
    31000012: ('Fishing', ('Frosted Heights', 'Wishing Alps')),  # Crab
    31000013: ('Fishing', ('Dazzle Beach', 'Glade of Trust')),  # Herring
    31000014: ('Fishing', ('Glade of Trust',)),  # Lobster
    31000016: ('Fishing', ('Peaceful Meadow', 'Forest of Valor', 'Sunlit Plateau', 'Frosted Heights', 'Glittering Dunes', 'Wild Tangle', 'Honeyglow Woods')),  # Bass
    31000017: ('Fishing', ('Sunlit Plateau',)),  # Walleye
    31000018: ('Fishing', ('Forest of Valor', 'Sunlit Plateau', 'The Grove', 'The Lagoon')),  # Perch
    31000019: ('Fishing', ('Frosted Heights',)),  # White Sturgeon
    31000020: ('Fishing', ('Forest of Valor', 'Sunlit Plateau')),  # Carp
    31000021: ('Fishing', ('Forest of Valor',)),  # Pike
    31000022: ('Fishing', ('Peaceful Meadow',)),  # Bream
    31000023: ('Fishing', ('Peaceful Meadow',)),  # Catfish
    31000028: ('Fishing', ('Dazzle Beach',)),  # Fugu
    31000029: ('Fishing', ('Forgotten Lands',)),  # Anglerfish
    31000030: ('Fishing', ('Forgotten Lands',)),  # Lancetfish
    31000052: ('Fishing', ('Glade of Trust',)),  # Festive Squid
    31000053: ('Fishing', ('Dazzle Beach',)),  # Festive Fugu
    31000054: ('Fishing', ('Peaceful Meadow',)),  # Festive Bass
    31000055: ('Fishing', ('Sunlit Plateau',)),  # Festive Salmon
    31000056: ('Fishing', ('Forgotten Lands',)),  # Festive Anglerfish
    31000057: ('Fishing', ('[[Dreamlight Valley]] biomes', '(6am-10am or 6pm-10pm)', 'After')),  # Here and There Fish
    31000059: ('Fishing', ('Glittering Dunes',)),  # Sand Fish
    31000060: ('Fishing', ('The Docks', 'The Overlook')),  # Shad
    31000061: ('Fishing', ('Glittering Dunes',)),  # Skeleton Fish
    31000062: ('Fishing', ('Wild Tangle',)),  # Pirarucu
    31000063: ('Fishing', ('The Docks', 'The Overlook')),  # Robot Fish
    31000064: ('Fishing', ('The Grasslands', 'The Promenade')),  # Electric Eel
    31000065: ('Fishing', ('The Lagoon',)),  # Piranha
    31000066: ('Fishing', ('The Oasis',)),  # Dunebopper
    31000067: ('Fishing', ("Ancient's Landing",)),  # Sea Snail
    31000068: ('Fishing', ("Ancient's Landing",)),  # Octopus
    31000069: ('Fishing', ('The Oasis',)),  # Brilliant Blue Starfish
    31000070: ('Fishing', ('Wild Tangle',)),  # Prisma Shrimp
    31000071: ('Fishing', ('Glittering Dunes',)),  # Scorpion
    31000072: ('Fishing', ('Glittering Dunes',)),  # Sand Worm
    31000074: ('Fishing', ('The Oasis',)),  # Pretty Pink Starfish
    31000083: ('Fishing', ('The Bind',)),  # Sorcerer Hat Hermit Crab
    31000084: ('Foraging', ('Mythopia',)),  # Mussel
    31000085: ('Fishing', ('Mythopia',)),  # Flying Fish
    31000086: ('Fishing', ('The Bind',)),  # Koi
    31000087: ('Fishing', ('The Bind',)),  # Sea Wolf
    31000088: ('Fishing', ('Mythopia',)),  # Hippocampus
    31000089: ('Fishing', ('Mythopia',)),  # Stygian Mudskipper
    31000090: ('Fishing', ('Everafter',)),  # Lamprey
    31000102: ('Fishing', ('Wishing Alps',)),  # Mountain Whitefish
    31000103: ('Fishing', ('Wishing Alps',)),  # Red Alpine Bass
    31000104: ('Fishing', ('Glamour Gulch',)),  # Jellied Fish
    31000105: ('Fishing', ('Glamour Gulch',)),  # Measuring-Tape Snail
    31000108: ('Fishing', ('Pixie Acres',)),  # Tigger Fish
    31000109: ('Fishing', ('Pixie Acres',)),  # Honey Coral
    31000113: ('Fishing', ('Honeyglow Woods',)),  # Plush Fish
    31000114: ('Fishing', ('Honeyglow Woods',)),  # Sweet Jelly
    31000115: ('Fishing', ('Honeyglow Woods',)),  # Acorn Snail
    31100030: ('Foraging', ('Dazzle Beach',)),  # Clam
    31100031: ('Foraging', ('Dazzle Beach',)),  # Oyster
    31100032: ('Foraging', ('Dazzle Beach',)),  # Scallop
    31100155: ('Foraging', ('Plaza', 'Peaceful Meadow')),  # Blue Marshmallow
    31100250: ('Digging', ('Honeyglow Woods',)),  # Tree Resin
    31600002: ('Mining', ('Forgotten Lands',)),  # Diamond
    31600008: ('Mining', ('Glade of Trust', 'Sunlit Plateau')),  # Shiny Citrine
    31600009: ('Mining', ('Forest of Valor', 'Glade of Trust')),  # Emerald
    31600010: ('Mining', ('Plaza', 'Peaceful Meadow', 'The Plains', 'The Wastes')),  # Garnet
    31600011: ('Mining', ('Anywhere',)),  # Onyx
    31600012: ('Mining', ('Peaceful Meadow', 'Dazzle Beach', 'The Grasslands', 'The Promenade')),  # Peridot
    31600013: ('Mining', ('Vitalys Mine', 'Mythopia')),  # Ruby
    31600014: ('Mining', ('Vitalys Mine',)),  # Sapphire
    31600015: ('Mining', ('Plaza', 'The Docks', 'The Courtyard', 'The Bind')),  # Topaz
    31600016: ('Mining', ('Sunlit Plateau', 'Frosted Heights')),  # Tourmaline
    31600017: ('Mining', ('The Wastes', 'The Oasis')),  # Alexandrite
    31600019: ('Mining', ('The Wastes', 'The Oasis')),  # Shiny Alexandrite
    31600020: ('Mining', ('Frosted Heights', 'Forgotten Lands')),  # Amethyst
    31600021: ('Mining', ('Frosted Heights', 'Forgotten Lands')),  # Shiny Amethyst
    31600022: ('Mining', ('Dazzle Beach', 'Forest of Valor')),  # Aquamarine
    31600024: ('Mining', ('Dazzle Beach', 'Forest of Valor')),  # Shiny Aquamarine
    31600025: ('Mining', ('The Lagoon',)),  # Blue Zircon
    31600026: ('Mining', ('The Lagoon',)),  # Shiny Blue Zircon
    31600027: ('Mining', ('Glade of Trust', 'Sunlit Plateau')),  # Citrine
    31600032: ('Mining', ('Forgotten Lands',)),  # Shiny Diamond
    31600034: ('Mining', ('Forest of Valor', 'Glade of Trust')),  # Shiny Emerald
    31600036: ('Mining', ('Plaza', 'Peaceful Meadow', 'The Plains', 'The Wastes')),  # Shiny Garnet
    31600042: ('Mining', ('Peaceful Meadow', 'Dazzle Beach', 'The Grasslands', 'The Promenade')),  # Shiny Peridot
    31600044: ('Mining', ('Vitalys Mine', 'Mythopia')),  # Shiny Ruby
    31600046: ('Mining', ('Vitalys Mine',)),  # Shiny Sapphire
    31600048: ('Mining', ('Plaza', 'The Docks', 'The Courtyard', 'The Bind')),  # Shiny Topaz
    31600050: ('Mining', ('Sunlit Plateau', 'Frosted Heights')),  # Shiny Tourmaline
    31600052: ('Mining', ('Vitalys Mine',)),  # Vitalys Crystal
    31600053: ('Mining', ('The Courtyard', 'The Overlook')),  # Jade
    31600054: ('Mining', ('The Courtyard', 'The Overlook')),  # Shiny Jade
    31600057: ('Mining', ('The Promenade', 'The Grove')),  # Spinel
    31600058: ('Mining', ('The Promenade', 'The Grove')),  # Shiny Spinel
    31600059: ('Mining', ('The Ruins',)),  # Evergem
    31600060: ('Mining', ('The Ruins',)),  # Shiny Evergem
    31600061: ('Mining', ('The Borderlands',)),  # Bumblestone
    31600062: ('Mining', ('The Borderlands',)),  # Shiny Bumblestone
    31600066: ('Mining', ('The Bind',)),  # Opal
    31600067: ('Mining', ('Everafter',)),  # Star Sapphire
    31600068: ('Mining', ('Everafter',)),  # Pure Ice
    31600069: ('Mining', ('Mythopia',)),  # Magma
    31600070: ('Mining', ('Mythopia',)),  # Shiny Magma
    31600071: ('Mining', ('The Bind',)),  # Shiny Opal
    31600072: ('Mining', ('Everafter',)),  # Shiny Pure Ice
    31600073: ('Mining', ('Everafter',)),  # Shiny Star Sapphire
    31600075: ('Mining', ('Wishing Alps',)),  # Pyrite
    31600076: ('Mining', ('Wishing Alps',)),  # Shiny Pyrite
    31600077: ('Mining', ('Glamour Gulch',)),  # Jasper
    31600078: ('Mining', ('Glamour Gulch',)),  # Shiny Jasper
    31600079: ('Mining', ('Pixie Acres',)),  # Honeycomb Stone
    31600080: ('Mining', ('Pixie Acres',)),  # Shiny Honeycomb Stone
    31600081: ('Mining', ('Honeyglow Woods',)),  # Shiny Honey Agate
    31600082: ('Mining', ('Honeyglow Woods',)),  # Honey Agate
    31700001: ('Digging', ('Glade of Trust', 'Sunlit Plateau', 'Forgotten Lands', 'Pixie Acres')),  # Clay
    31700002: ('Foraging', ('Forgotten Lands',)),  # Dark Wood
    31700003: ('Foraging', ('Sunlit Plateau', 'Frosted Heights', 'Forgotten Lands', 'Wishing Alps')),  # Dry Wood
    31700008: ('Digging', ('Forest of Valor', 'Glade of Trust', 'Sunlit Plateau', 'Frosted Heights', 'Pixie Acres')),  # Hardwood
    31700010: ('Mining', ('Forest of Valor', 'Glade of Trust', 'Sunlit Plateau', 'Frosted Heights', 'Forgotten Lands', 'Vitalys Mine', 'The Bind', 'Everafter')),  # Iron Ore
    31700011: ('Digging', ('Dazzle Beach', 'Forest of Valor', 'Sunlit Plateau', 'Forgotten Lands', 'Wishing Alps')),  # Pebbles
    31700012: ('Digging', ('Dazzle Beach', 'Glittering Dunes', 'Glamour Gulch')),  # Sand
    31700013: ('Digging', ('Frosted Heights', 'Wishing Alps')),  # Snowball
    31700014: ('Digging', ('Plaza', 'Peaceful Meadow', 'Forest of Valor', 'Glade of Trust', "Ancient's Landing")),  # Softwood
    31700015: ('Digging', ('All Biomes',)),  # Soil
    31700016: ('Mining', ('All Biomes',)),  # Stone
    31700017: ('Mining', ('All Biomes',)),  # Coal Ore
    31700018: ('Mining', ('Sunlit Plateau', 'Frosted Heights', 'Forgotten Lands', 'Mythopia', 'Vitalys Mine')),  # Gold Nugget
    31700019: ('Mining', ('Forgotten Lands',)),  # Crystal
    31700020: ('Gardening', ('Sunlit Plateau',)),  # Cotton
    31700021: ('Digging', ('All biomes',)),  # Night Shard
    31700033: ('Fishing', ('All Biomes',)),  # Red Algae
    31700035: ('Digging', ('Glittering Dunes',)),  # Oasis Glass
    31700037: ('Mining', ("Ancient's Landing", 'Glittering Dunes', 'Wild Tangle')),  # Copper
    31700038: ('Foraging', ('Wild Tangle',)),  # Tropical Wood
    31700039: ('Fishing', ("Ancient's Landing",)),  # Plastic Scrap
    31700060: ('Mining', ("Ancient's Landing",)),  # Quartz
    31700061: ('Mining', ('Glittering Dunes',)),  # Tin
    31700062: ('Mining', ('Wild Tangle',)),  # Zinc
    31700063: ('Foraging', ('[[Multiplayer]]',)),  # Pixel Shard
    31700064: ('Digging', ('Wild Tangle',)),  # Amber
    31700065: ('Digging', ("Ancient's Landing",)),  # Pearl
    31700077: ('Digging', ('Glittering Dunes',)),  # Bones
    31700078: ('Fishing', ('Glittering Dunes',)),  # Scales
    31700121: ('Foraging', ('The Bind', 'Everafter')),  # Moss
    31700123: ('Mining', ('The Bind', 'Everafter')),  # Petrified Wood
    31700126: ('Digging', ('The Bind', 'Everafter')),  # Mud
    31700128: ('Fishing', ('Mythopia',)),  # Posidonia
    31700129: ('Digging', ('Mythopia',)),  # Gravel
    31700130: ('Digging', ('Mythopia',)),  # Broken Weapon
    31700131: ('Foraging', ('The Bind',)),  # Pine Cone
    31700132: ('Digging', ('Everafter',)),  # Fairy Bubbles
    31700133: ('Digging', ('Everafter', 'Mythopia')),  # Volcanic Rock
    31700134: ('Fishing', ('Everafter',)),  # Sea Monster Tooth
    31700135: ('Mining', ('Mythopia',)),  # Marble
    31700148: ('Foraging', ('Everafter',)),  # Common Club Rush
    31700156: ('Foraging', ('Wishing Alps',)),  # Reclaimed Barn Wood
    31700157: ('Fishing', ('Wishing Alps',)),  # Old Braided Rope
    31700158: ('Digging', ('Wishing Alps',)),  # Rusty Hinge
    31700160: ('Mining', ('Wishing Alps',)),  # Silver Ore
    31700161: ('Mining', ('Wishblossom Mountains',)),  # Pixie Dust
    31700163: ('Mining', ('Glamour Gulch',)),  # Antique Clothes Iron
    31700164: ('Foraging', ('Glamour Gulch',)),  # Sequin Strands
    31700165: ('Fishing', ('Glamour Gulch',)),  # Wire Coat Hanger
    31700167: ('Digging', ('Glamour Gulch',)),  # Beady Soil
    31700169: ('Foraging', ("Beast's Greenhouse",)),  # Rainbow Rose Bouquet
    31700170: ('Mining', ('Pixie Acres',)),  # Grassy Ore
    31700171: ('Foraging', ('Pixie Acres',)),  # Copter Seeds
    31700172: ('Fishing', ('Pixie Acres',)),  # Goose Feathers
    31700173: ('Digging', ('Pixie Acres',)),  # Giant Acorns
    31700174: ('Fishing', ('Pixie Acres',)),  # Balloon Fish
    31700176: ('Foraging', ('Honeyglow Woods',)),  # Oak Leaves
    31700177: ('Mining', ('Honeyglow Woods',)),  # Soft Limestone
    31700178: ('Fishing', ('Honeyglow Woods',)),  # Driftwood
}

# Expansion areas, for the group label (the sub-biomes are listed with their biome). A zone in no group
# (Pixie Acres, Wishing Alps, ...) is always listed by its own short name.
GROUPS = {
    "Valley": ("Plaza", "Peaceful Meadow", "Forest of Valor", "Glade of Trust", "Sunlit Plateau", "Dazzle Beach",
               "Forgotten Lands", "Frosted Heights", "Dream Castle"),
    "Eternity": ("Ancient's Landing", "The Docks", "The Overlook", "The Courtyard", "The Ruins", "Glittering Dunes",
                 "The Oasis", "The Borderlands", "The Wastes", "Wild Tangle", "The Grasslands", "The Promenade",
                 "The Grove", "The Lagoon", "The Plains"),
    "Storybook": ("The Bind", "Mythopia", "Everafter", "The Wild Woods", "The Fiery Plains", "The Fallen Fortress",
                  "The Elysian Fields", "The Beanstalk Marshes", "Teapot Falls", "Mount Olympus"),
}
SHORT = {"Dazzle Beach": "Dazzle", "Forest of Valor": "Valor", "Peaceful Meadow": "Meadow", "Sunlit Plateau": "Plateau",
         "Glade of Trust": "Glade", "Forgotten Lands": "Forgotten", "Frosted Heights": "Frosted",
         "Glittering Dunes": "Dunes", "Wild Tangle": "Tangle", "Ancient's Landing": "Landing",
         "Wishblossom Mountains": "Wishblossom", "Wishing Alps": "Alps", "Pixie Acres": "Pixie",
         "Glamour Gulch": "Gulch", "Honeyglow Woods": "Honeyglow", "Drowsybloom Acre": "Drowsybloom",
         "Braveheart Grove": "Braveheart", "Nectar Apiary": "Apiary"}
ANYWHERE = ("All Biomes", "Anywhere")
MANY = 4   # this many zones or more: name the area (Valley, Eternity, Storybook) instead of the zones
MAX_SHOWN = 2


def _short(zone):
    return SHORT.get(zone) or zone.removeprefix("The ")


def _group(zone):
    return next((g for g, zones in GROUPS.items() if zone in zones), None)


def where(zones):
    """Short text for a list of zones: 'Anywhere'; the area names ('Valley') when there are MANY zones;
    else the first MAX_SHOWN zones by short name ('Dazzle, Valor')."""
    if any(z in ANYWHERE for z in zones):
        return "Anywhere"
    if len(zones) >= MANY:
        labels = list(dict.fromkeys(_group(z) or _short(z) for z in zones))
    else:
        labels = [_short(z) for z in zones]
    return ", ".join(labels[:MAX_SHOWN])


def spawn_for(item_id):
    """{'how': 'Mining', 'where': 'Plateau, Glade'} for an item, None when the wiki lists no zone.
    A meal (ID block 303) is cooked, not found: {'how': 'Cooking', 'where': ''}."""
    if 30300000 <= item_id < 30400000:
        return {"how": "Cooking", "where": ""}
    found = SPAWNS.get(item_id)
    return {"how": found[0], "where": where(found[1])} if found else None
