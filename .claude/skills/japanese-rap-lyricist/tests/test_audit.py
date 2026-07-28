from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_lyrics import audit, load_bars  # noqa: E402
from flow_grid import propose_grid  # noqa: E402
from similarity_guard import compare  # noqa: E402


class AuditTests(unittest.TestCase):
    def test_failed_blueprint_example_is_rejected(self):
        bars = load_bars(ROOT / "tests" / "fixtures" / "blueprint_outside_bad.tsv")
        result = audit(bars)
        self.assertEqual(result["verdict"], "reject-or-rebuild")
        self.assertLessEqual(result["score_caps"]["overall_max_without_independent_evaluation"], 2.0)
        codes = {item["code"] for item in result["warnings"]}
        self.assertIn("forced_or_stock_language", codes)

    def test_flow_grid_never_claims_verification(self):
        result = propose_grid("コトバヲオク", 16, 2)
        self.assertEqual(result["status"], "proposal-only")
        self.assertTrue(any("Pocket" in item for item in result["limitations"]))

    def test_similarity_guard_flags_long_exact_span(self):
        result = compare(
            "この長い一致表現はそのまま残っている候補です",
            "前半が違ってもこの長い一致表現はそのまま残っている候補です",
        )
        self.assertTrue(result["review_required"])


if __name__ == "__main__":
    unittest.main()
