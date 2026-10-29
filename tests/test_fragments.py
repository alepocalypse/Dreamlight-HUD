import unittest

from ddvhud.fragments import FRAGMENTS


class FragmentTableTests(unittest.TestCase):
    def test_holds_the_sixteen_timebending_fragments_with_their_names(self):
        self.assertEqual(FRAGMENTS, {
            31700067: "Cracked Palace Tower",
            31700068: "Lute Head",
            31700069: "Piano Leg",
            31700070: "Jokester-of-the-Month Frame",
            31700071: "Broken Sword",
            31700072: "V8 Decoration",
            31700073: "Wagon Wheel",
            31700074: "Tapestry Piece",
            31700075: "Pedestal Chunk",
            31700076: "Mythic Vase Handle",
            31700093: "Broken Metal Sign",
            31700094: "Green Stone Carving",
            31700095: "Pink Floral Pillow",
            31700096: "Toonish Canister",
            31700097: "Broken Lollipop",
            31700098: "Stained Glass Fragment",
        })


if __name__ == "__main__":
    unittest.main()
