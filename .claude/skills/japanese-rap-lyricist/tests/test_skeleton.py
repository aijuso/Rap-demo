from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from skeleton import skeletons  # noqa: E402


class SkeletonTests(unittest.TestCase):
    def test_katakata(self):
        result = skeletons("カタカタ")
        self.assertEqual(result["consonant_skeleton"], "ktkt")
        self.assertEqual(result["vowel_skeleton"], "a-a-a-a")
        self.assertFalse(result["warnings"])

    def test_pocket_keeps_geminate(self):
        result = skeletons("ポケット")
        self.assertEqual(result["consonant_skeleton"], "pkQt")
        self.assertEqual(result["vowel_skeleton"], "o-e-Q-o")

    def test_moraic_nasal_and_long_vowel(self):
        result = skeletons("カンジョー")
        self.assertEqual(result["consonant_skeleton_dotted"], "k.N.jy.:")
        self.assertEqual(result["vowel_skeleton"], "a-N-o-o")

    def test_yoon_uses_dotted_form(self):
        result = skeletons("キャク")
        self.assertEqual(result["consonant_skeleton_dotted"], "ky.k")
        self.assertEqual(result["vowel_skeleton"], "a-u")

    def test_onsetless_vowel(self):
        result = skeletons("アオイ")
        self.assertEqual(result["consonant_skeleton"], "---")
        self.assertEqual(result["vowel_skeleton"], "a-o-i")

    def test_extended_kana(self):
        result = skeletons("ティファニー")
        self.assertEqual(result["consonant_skeleton_dotted"], "t.f.n.:")
        self.assertFalse(result["warnings"])


if __name__ == "__main__":
    unittest.main()
