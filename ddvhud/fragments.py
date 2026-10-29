"""Item ID -> English name for the 16 Timebending Fragments.

Copied from the game's item data, which the tool never reads at runtime (ADR 0001):
  <game>/ddv_Data/StreamingAssets/itemlist/ActivityItem.json  (items whose internal name
  starts with "TimeBending!Expansion01!Shards!")
  <game>/ddv_Data/StreamingAssets/Localization/LocDB_en-US.zip  (English names)
To refresh after a game update: python3 tools/gen_fragments.py (read-only; id, internal
name, English name) and copy the result in.
"""

FRAGMENTS = {
    31700067: 'Cracked Palace Tower',
    31700068: 'Lute Head',
    31700069: 'Piano Leg',
    31700070: 'Jokester-of-the-Month Frame',
    31700071: 'Broken Sword',
    31700072: 'V8 Decoration',
    31700073: 'Wagon Wheel',
    31700074: 'Tapestry Piece',
    31700075: 'Pedestal Chunk',
    31700076: 'Mythic Vase Handle',
    31700093: 'Broken Metal Sign',
    31700094: 'Green Stone Carving',
    31700095: 'Pink Floral Pillow',
    31700096: 'Toonish Canister',
    31700097: 'Broken Lollipop',
    31700098: 'Stained Glass Fragment',
}
