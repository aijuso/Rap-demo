from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from rhyme_score import score_pair  # noqa: E402


class RhymeModeTests(unittest.TestCase):
    def test_default_is_backward_compatible_balanced(self):
        old = score_pair("先輩", "限界", "センパイ", "ゲンカイ")
        self.assertEqual(old["mode"], "balanced")
        self.assertGreaterEqual(old["sound_score_after_penalty"], 0.90)

    def test_consonant_mode_rewards_pure_consonance(self):
        balanced = score_pair("カタカタ", "コトコト", "カタカタ", "コトコト")
        consonant = score_pair(
            "カタカタ", "コトコト", "カタカタ", "コトコト", mode="consonant"
        )
        self.assertGreater(
            consonant["sound_score_after_penalty"],
            balanced["sound_score_after_penalty"],
        )
        self.assertGreaterEqual(consonant["best_domain"]["onset"], 0.99)

    def test_vowel_mode_ignores_onsets(self):
        vowel = score_pair("真夜中", "歩幅", "マヨナカ", "ホハバ", mode="vowel")
        self.assertEqual(vowel["best_domain"]["vowel_or_coda"], 1.0)
        self.assertGreaterEqual(vowel["sound_score_after_penalty"], 0.85)

    def test_skeletons_are_attached(self):
        result = score_pair("カタカタ", "コトコト", "カタカタ", "コトコト")
        self.assertEqual(result["skeleton_a"]["consonant_skeleton"], "ktkt")
        self.assertEqual(result["skeleton_b"]["consonant_skeleton"], "ktkt")

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            score_pair("あ", "い", "ア", "イ", mode="loud")


if __name__ == "__main__":
    unittest.main()
