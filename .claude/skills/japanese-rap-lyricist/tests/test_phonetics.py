from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from kana_to_mora import parse_morae  # noqa: E402
from rhyme_score import score_pair  # noqa: E402


class MoraTests(unittest.TestCase):
    def test_yoon_is_one_mora(self):
        kya, warnings = parse_morae("キャ")
        kiya, _ = parse_morae("キヤ")
        self.assertFalse(warnings)
        self.assertEqual(len(kya), 1)
        self.assertEqual(len(kiya), 2)
        self.assertEqual(kya[0].surface, "キャ")

    def test_special_morae_are_preserved(self):
        moras, warnings = parse_morae("ガッコー")
        self.assertFalse(warnings)
        self.assertEqual([m.signature for m in moras], ["a", "Q", "o", "o"])
        self.assertEqual(moras[-1].special, "R")

    def test_moraic_nasal(self):
        moras, _ = parse_morae("シンブン")
        self.assertEqual([m.signature for m in moras], ["i", "N", "u", "N"])

    def test_extended_kana(self):
        moras, warnings = parse_morae("ティファニー")
        self.assertFalse(warnings)
        self.assertEqual([m.surface for m in moras], ["ティ", "ファ", "ニ", "ー"])


class RhymeTests(unittest.TestCase):
    def test_common_end_rhyme_is_sound_match_not_quality(self):
        result = score_pair("工程", "想定", "コウテイ", "ソウテイ")
        self.assertGreaterEqual(result["sound_score_after_penalty"], 0.70)
        self.assertIn(
            "Meaning, naturalness, placement, beat salience, and performance are not scored.",
            result["limitations"],
        )

    def test_same_word_is_penalized(self):
        result = score_pair("未来", "未来", "ミライ", "ミライ")
        self.assertEqual(result["trivial_repetition_penalty"], 0.55)
        self.assertLess(result["sound_score_after_penalty"], result["best_domain"]["raw_sound_score"])

    def test_non_rhyme_is_not_strong(self):
        result = score_pair("猫", "空港", "ネコ", "クウコウ")
        self.assertNotEqual(result["label"], "strong")


if __name__ == "__main__":
    unittest.main()
