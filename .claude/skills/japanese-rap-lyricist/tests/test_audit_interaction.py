from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from professional_audit import professional_audit  # noqa: E402


def minimal_bar(index: int) -> dict:
    return {
        "index": index,
        "tokens": [{"surface": "駅", "concreteness": 1.0}],
        "rhyme_hits": [{"family": "a-i", "position": "internal", "meaning_bearing": True}],
        "changes": ["information"],
        "naturalness_review": {"status": "pass", "evidence": "自然な語順"},
        "interesting_without_rhyme_review": {"status": "pass", "evidence": "命題が残る"},
        "ai_pattern_flags": [],
    }


def base_payload() -> dict:
    return {
        "bars": [minimal_bar(i) for i in range(1, 5)],
        "independent_review": True,
        "audio_reviewed": False,
    }


def full_evidence() -> list[dict]:
    return [
        {"checkpoint": cp, "user_reply_quote": f"{cp}への返答"}
        for cp in ("CP1", "CP2", "CP3", "CP4")
    ]


class InteractionGateTests(unittest.TestCase):
    def g8_failures(self, result: dict) -> list[str]:
        return [g for g in result["hard_gate_failures"] if g.startswith("G8")]

    def test_collaborative_with_all_evidence_passes(self):
        payload = base_payload()
        payload["interaction"] = {
            "interaction_mode": "collaborative",
            "checkpoint_evidence": full_evidence(),
        }
        self.assertEqual(self.g8_failures(professional_audit(payload)), [])

    def test_collaborative_missing_cp3_fails(self):
        payload = base_payload()
        evidence = [e for e in full_evidence() if e["checkpoint"] != "CP3"]
        payload["interaction"] = {
            "interaction_mode": "collaborative",
            "checkpoint_evidence": evidence,
        }
        failures = self.g8_failures(professional_audit(payload))
        self.assertTrue(any("CP3" in f for f in failures))

    def test_empty_quote_counts_as_missing(self):
        payload = base_payload()
        evidence = full_evidence()
        evidence[0]["user_reply_quote"] = "   "
        payload["interaction"] = {
            "interaction_mode": "collaborative",
            "checkpoint_evidence": evidence,
        }
        failures = self.g8_failures(professional_audit(payload))
        self.assertTrue(any("CP1" in f for f in failures))

    def test_autonomous_with_delegation_quote_passes(self):
        payload = base_payload()
        payload["interaction"] = {
            "interaction_mode": "autonomous",
            "checkpoint_evidence": [],
            "delegation_quote": "全部お任せするので最後まで進めて",
        }
        self.assertEqual(self.g8_failures(professional_audit(payload)), [])

    def test_autonomous_without_quote_fails(self):
        payload = base_payload()
        payload["interaction"] = {
            "interaction_mode": "autonomous",
            "checkpoint_evidence": [],
            "delegation_quote": None,
        }
        failures = self.g8_failures(professional_audit(payload))
        self.assertTrue(any("delegation" in f for f in failures))

    def test_missing_block_warns_but_does_not_gate(self):
        payload = base_payload()
        result = professional_audit(payload)
        self.assertEqual(self.g8_failures(result), [])
        self.assertTrue(any("interaction block missing" in u for u in result["unknowns"]))
        self.assertTrue(any("interaction block" in w for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
