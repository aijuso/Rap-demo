import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_research_html import render as render_research  # noqa: E402
from render_rhyme_html import render as render_rhyme  # noqa: E402
from validate_bank import validate_research, validate_rhyme, validate_scout  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ValidatorTests(unittest.TestCase):
    def test_research_fixture_is_valid(self):
        self.assertEqual(validate_research(load("research_bank.json")), [])

    def test_research_web_evidence_requires_url(self):
        payload = load("research_bank.json")
        payload["keywords"][0]["evidence"] = [{"kind": "web", "pointer": "somewhere"}]
        errors = validate_research(payload)
        self.assertTrue(any("without a URL" in e for e in errors))

    def test_rhyme_fixture_is_valid(self):
        self.assertEqual(validate_rhyme(load("rhyme_bank.json")), [])

    def test_rhyme_type_minimums_are_enforced(self):
        payload = load("rhyme_bank.json")
        payload["candidates"] = [
            c for c in payload["candidates"] if "consonance" not in c["rhyme_types"]
        ]
        errors = validate_rhyme(payload)
        self.assertTrue(any("bucket consonance" in e for e in errors))

    def test_rhyme_minimum_candidate_count(self):
        payload = load("rhyme_bank.json")
        payload["candidates"] = payload["candidates"][:10]
        errors = validate_rhyme(payload)
        self.assertTrue(any("minimum is 20" in e for e in errors))

    def test_scout_shape(self):
        good = {
            "schema": "scout-research/v1", "round": 1, "focus": "テーマ×方向性",
            "angles": [
                {"premise": "案A", "motifs": ["m1"],
                 "evidence": [{"kind": "web", "pointer": "https://example.com"}]},
                {"premise": "案B", "motifs": ["m2"], "evidence": [{"kind": "inference", "pointer": "既知の事実から"}]},
            ],
        }
        self.assertEqual(validate_scout(good), [])
        bad = dict(good, angles=good["angles"][:1])
        self.assertTrue(validate_scout(bad))


class RenderTests(unittest.TestCase):
    def test_research_html_is_self_contained(self):
        html = render_research(load("research_bank.json"))
        self.assertIn("<table", html)
        self.assertIn("K01", html)
        self.assertIn("ktkt" if "ktkt" in html else "改札", html)
        for marker in ("http-equiv", "src=\"http", "href=\"http://cdn", "@import"):
            self.assertNotIn(marker, html)
        # external links in evidence are allowed; scripts/styles must be inline
        self.assertNotIn("<script src", html)
        self.assertNotIn("<link", html)

    def test_rhyme_html_groups_by_keyword(self):
        html = render_rhyme(load("rhyme_bank.json"))
        self.assertIn("韻バンク", html)
        self.assertIn("K01-01", html)
        self.assertIn("badge-ok", html)
        self.assertNotIn("<script src", html)
        self.assertNotIn("<link", html)


if __name__ == "__main__":
    unittest.main()
