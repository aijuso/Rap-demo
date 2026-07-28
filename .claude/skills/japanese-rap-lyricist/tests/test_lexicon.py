import json
import tempfile
import unittest
from pathlib import Path

from build_lexicon import build
from search_rhymes import search


FIXTURE = Path(__file__).parent / "fixtures" / "rhyme_lexicon.tsv"


class LexiconTests(unittest.TestCase):
    def test_build_and_search_user_supplied_lexicon(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "lexicon.jsonl"
            report = build(FIXTURE, output)
            self.assertEqual(report["written"], 5)
            rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all("signature" in row for row in rows))

            results = search(
                output,
                "工程",
                "コウテイ",
                tags={"計画"},
                pos="名詞",
                top_k=3,
            )
            self.assertEqual(results[0]["surface"], "想定")
            self.assertGreater(results[0]["sound_score"], 0.8)
            self.assertIn("contextual review", results[0]["warning"])


if __name__ == "__main__":
    unittest.main()
