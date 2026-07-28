from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_words import validate_and_summarize  # noqa: E402
from artifact_envelope import wrap, validate_envelopes  # noqa: E402
from flow_map import compile_flow_map  # noqa: E402
from orchestrate_plan import compile_plan  # noqa: E402
from professional_audit import professional_audit  # noqa: E402
from rhyme_graph import build_graph  # noqa: E402
from validate_humor_plan import validate_humor_plan  # noqa: E402
from validate_audio_review import digest, validate_audio_review  # noqa: E402


class OrchestrationTests(unittest.TestCase):
    def test_artifact_envelope_detects_stale_brief(self):
        brief = {"mode": "create", "theme": "A"}
        artifact = wrap(
            {"ok": True},
            schema="test/v1",
            run_id="run-1",
            brief=brief,
            role="tester",
            instance_id="agent-1",
            status="ready",
            inputs=["brief.json"],
            evidence=["user request"],
            warnings=[],
        )
        self.assertTrue(validate_envelopes([artifact], brief)["valid"])
        self.assertFalse(
            validate_envelopes([artifact], {"mode": "create", "theme": "B"})["valid"]
        )

    def test_humor_schema_requires_character_and_rights_controls(self):
        schema = json.loads(
            (ROOT / "assets" / "humor-plan.schema.json").read_text(encoding="utf-8")
        )
        required = set(schema["required"])
        self.assertIn("character_knowledge", required)
        self.assertIn("voice_cast", required)
        self.assertIn("reveal_schedule", required)
        self.assertIn("rights_origin", required)

    def test_character_humor_rejects_reused_commercial_world(self):
        result = validate_humor_plan(
            {
                "mode": "character_driven",
                "purpose": "人物の認識差を見せる",
                "target_policy": {"allowed": ["narrator"], "avoided": ["protected group"]},
                "density_map": [],
                "punch_cards": [],
                "callback_map": [],
                "character_knowledge": [],
                "voice_cast": [],
                "reveal_schedule": [],
                "rights_origin": {
                    "characters_original": False,
                    "commercial_world_reused": True,
                    "evidence": ["reference request"],
                },
                "risk_flags": [],
            }
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("original characters" in item for item in result["errors"]))

    def test_audio_review_binds_findings_to_exact_files(self):
        flow_path = ROOT / "assets" / "flow-map.schema.json"
        beat_path = ROOT / "tests" / "fixtures" / "blueprint_outside_bad.tsv"
        audio_path = ROOT / "tests" / "fixtures" / "rhyme_lexicon.tsv"
        review = {
            "flow_map_sha256": digest(flow_path),
            "beat": {"id": "beat-1", "sha256": digest(beat_path)},
            "audio": {
                "id": "take-1",
                "sha256": digest(audio_path),
                "take_count": 1,
            },
            "reviewer": {"id": "reviewer-1", "independent": True},
            "reviewed_at": "2026-07-27T00:00:00+09:00",
            "host_inspection": {"audio_opened": True, "beat_opened": True},
            "bar_reviews": [
                {
                    "bar": 1,
                    "accent": "pass",
                    "pocket": "pass",
                    "breath": "pass",
                    "articulation": "pass",
                    "evidence": ["review fixture"],
                }
            ],
        }
        result = validate_audio_review(
            review,
            flow_map_path=flow_path,
            beat_path=beat_path,
            audio_path=audio_path,
        )
        self.assertTrue(result["integrity_valid"], result["errors"])
        review["audio"]["sha256"] = "0" * 64
        result = validate_audio_review(
            review,
            flow_map_path=flow_path,
            beat_path=beat_path,
            audio_path=audio_path,
        )
        self.assertFalse(result["integrity_valid"])

    def test_create_plan_has_independent_reaudit(self):
        plan = compile_plan(
            {
                "mode": "create",
                "theme": "深夜のコンビニ",
                "generation_target": "none",
                "reference_requests": ["reference-only"],
            }
        )
        tasks = {item["id"]: item for item in plan["tasks"]}
        self.assertIn("reference", tasks)
        self.assertIn("reference_sanitize", tasks)
        self.assertNotIn("reference_requests", plan["generation_brief"])
        self.assertIn("reference_requests", plan["reference_brief"])
        self.assertEqual(tasks["reference"]["input_brief"], "reference_brief")
        self.assertTrue(
            all(
                item["input_brief"] == "generation_brief"
                for item in plan["tasks"]
                if item["id"] != "reference"
            )
        )
        self.assertIn("rhyme_flow_reconcile", tasks["draft"]["depends_on"])
        self.assertIn("vocabulary_rhyme_reconcile", tasks["draft"]["depends_on"])
        self.assertIn("narrative_humor_reconcile", tasks["draft"]["depends_on"])
        self.assertEqual(tasks["audit"]["depends_on"], ["draft", "flow_remap"])
        self.assertEqual(
            tasks["reaudit"]["depends_on"], ["repair", "post_repair_flow_remap"]
        )

    def test_analyze_plan_has_semantic_and_cross_layer_analysis(self):
        plan = compile_plan(
            {
                "mode": "analyze",
                "copyright_input_class": "user_supplied_text",
            }
        )
        tasks = {item["id"]: item for item in plan["tasks"]}
        self.assertIn("source_policy", tasks)
        self.assertIn("token_semantics", tasks)
        self.assertIn("rhyme_analysis", tasks)
        self.assertIn("narrative_humor_analysis", tasks)
        self.assertIn("flow_analysis", tasks)
        self.assertIn("analysis_integration", tasks)
        self.assertIn("analysis_audit", tasks)

    def test_named_analysis_integrates_anonymous_reference_artifact(self):
        plan = compile_plan(
            {
                "mode": "analyze",
                "copyright_input_class": "user_supplied_text",
                "reference_requests": ["named reference"],
            }
        )
        tasks = {item["id"]: item for item in plan["tasks"]}
        self.assertIn("reference", tasks)
        self.assertIn("reference_sanitize", tasks["analysis_integration"]["depends_on"])
        self.assertNotIn("reference_requests", plan["generation_brief"])

    def test_commercial_analysis_uses_non_reconstructive_route(self):
        plan = compile_plan(
            {
                "mode": "analyze",
                "copyright_input_class": "commercial_work",
            }
        )
        task_ids = {item["id"] for item in plan["tasks"]}
        self.assertIn("derived_techniques", task_ids)
        self.assertIn("copyright_analysis_audit", task_ids)
        self.assertNotIn("token_semantics", task_ids)
        release_gate = next(item for item in plan["gates"] if item["id"] == "release_ready")
        self.assertTrue(
            any("non-reconstructive" in item for item in release_gate["requirements"])
        )

    def test_direct_production_requires_reaudit_and_final_flow(self):
        plan = compile_plan({"mode": "production"})
        tasks = {item["id"]: item for item in plan["tasks"]}
        self.assertIn("flow_remap", tasks)
        self.assertIn("repair", tasks)
        self.assertIn("post_repair_flow_remap", tasks)
        self.assertIn("reaudit", tasks)
        self.assertEqual(
            tasks["production"]["depends_on"],
            ["reaudit", "repair", "post_repair_flow_remap"],
        )

    def test_rhyme_graph_preserves_positions_and_sound_limits(self):
        graph = build_graph(
            [
                {
                    "id": "a",
                    "surface": "工程",
                    "reading": "コウテイ",
                    "position": "internal",
                    "bar": 1,
                },
                {
                    "id": "b",
                    "surface": "想定",
                    "reading": "ソウテイ",
                    "position": "end",
                    "bar": 3,
                },
            ],
            threshold=0.6,
        )
        self.assertEqual(len(graph["edges"]), 1)
        self.assertIn("internal_rhyme", graph["edges"][0]["rhyme_types"])
        self.assertIn("delayed_or_callback_candidate", graph["edges"][0]["rhyme_types"])
        self.assertTrue(any("not evidence" in item for item in graph["limitations"]))

    def test_commercial_analysis_rejects_stored_surface(self):
        result = validate_and_summarize(
            {
                "source_policy": "commercial_work",
                "bars": [
                    {
                        "index": 1,
                        "surface": "commercial lyric text",
                        "paraphrase": "要旨",
                        "function": "setup",
                        "tokens": [],
                    }
                ],
            }
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("must not store" in item for item in result["errors"]))

    def test_commercial_analysis_rejects_reconstructable_tokens(self):
        result = validate_and_summarize(
            {
                "source_policy": "commercial_work",
                "bars": [
                    {
                        "index": 1,
                        "surface": None,
                        "paraphrase": "場面要旨",
                        "function": "setup",
                        "tokens": [{"surface": "復元可能", "normalized": "復元可能"}],
                    }
                ],
            }
        )
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("reconstructable token sequences" in item for item in result["errors"])
        )

    def test_user_text_word_analysis_requires_and_accepts_rich_annotation(self):
        result = validate_and_summarize(
            {
                "source_policy": "user_supplied_text",
                "bars": [
                    {
                        "index": 1,
                        "surface": "レシート",
                        "paraphrase": "買い物の記録を示す",
                        "function": "setup",
                        "tokens": [
                            {
                                "surface": "レシート",
                                "normalized": "レシート",
                                "reading": "レシート",
                                "morae": ["レ", "シ", "ー", "ト"],
                                "literal_sense": "購入内容を記した紙",
                                "contextual_sense": "支出の証拠",
                                "plain_explanation": "何をいくらで買ったかが書かれた紙",
                                "speaker_attitude": "見たくないが捨てられない",
                                "ambiguity": [],
                                "connotation": ["生活感"],
                                "referent": "場面内の紙片",
                                "part_of_speech": "noun",
                                "syntax_role": "object",
                                "register": "general",
                                "semantic_domain": ["shopping", "money"],
                                "concreteness": 0.95,
                                "sound_role": ["held_vowel"],
                                "rhyme_role": [],
                                "humor_role": ["setup"],
                                "narrative_role": ["evidence"],
                                "prominence": "accented",
                                "claim_status": "inferred",
                                "confidence": 0.9,
                                "evidence": ["user text and local context"],
                            }
                        ],
                    }
                ],
            }
        )
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["token_count"], 1)

    def test_word_analysis_rejects_out_of_range_and_fake_enums(self):
        token = {
            "surface": "紙",
            "normalized": "紙",
            "reading": "カミ",
            "morae": ["カ", "ミ"],
            "literal_sense": "薄い素材",
            "contextual_sense": "記録",
            "plain_explanation": "書くための薄い物",
            "speaker_attitude": "neutral",
            "ambiguity": [],
            "connotation": [],
            "referent": "paper",
            "part_of_speech": "noun",
            "syntax_role": "object",
            "register": "general",
            "semantic_domain": ["object"],
            "concreteness": 9,
            "sound_role": [],
            "rhyme_role": [],
            "humor_role": [],
            "narrative_role": [],
            "prominence": "impossible",
            "claim_status": "invented",
            "confidence": "high",
            "evidence": ["context"],
        }
        result = validate_and_summarize(
            {
                "source_policy": "user_supplied_text",
                "bars": [
                    {
                        "index": 1,
                        "surface": "紙",
                        "paraphrase": "紙を示す",
                        "function": "setup",
                        "tokens": [token],
                    }
                ],
            }
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("concreteness" in item for item in result["errors"]))
        self.assertTrue(any("invalid prominence" in item for item in result["errors"]))

    def test_flow_map_caps_text_only_confidence(self):
        result = compile_flow_map(
            {
                "bpm": 92,
                "bars": [
                    {
                        "index": 1,
                        "reading": "レシートヲタタム",
                        "subdivision": "sixteenth",
                        "confidence": 0.95,
                    }
                ],
            }
        )
        self.assertEqual(result["status"], "proposal")
        self.assertLessEqual(result["bars"][0]["confidence"], 0.7)
        self.assertTrue(any("audio" in item for item in result["unknowns"]))

    def test_flow_map_rejects_self_declared_audio_verification(self):
        result = compile_flow_map(
            {
                "status": "audio_verified",
                "verification": "recorded_on_beat",
                "bpm": None,
                "bars": [{"index": 1, "reading": "テスト"}],
            }
        )
        self.assertEqual(result["status"], "proposal")
        self.assertEqual(result["verification"], "text_only")
        self.assertTrue(any("downgraded" in item for item in result["unknowns"]))

    def test_flow_mapper_never_self_certifies_declared_audio_ids(self):
        result = compile_flow_map(
            {
                "verification": "recorded_on_beat",
                "bpm": 92,
                "bars": [{"index": 1, "reading": "テスト"}],
                "verification_evidence": {
                    "beat_id": "declared-beat",
                    "audio_id": "declared-audio",
                    "take_count": 2,
                    "reviewer": "declared-reviewer",
                    "timestamp": "2026-07-27T00:00:00+09:00",
                },
            }
        )
        self.assertEqual(result["status"], "proposal")
        self.assertEqual(result["verification"], "text_only")
        self.assertTrue(any("cannot inspect audio" in item for item in result["unknowns"]))

    def test_professional_audit_rejects_end_only_static_draft(self):
        bars = []
        for index in range(1, 9):
            bars.append(
                {
                    "index": index,
                    "tokens": [
                        {
                            "surface": "概念",
                            "concreteness": 0.1,
                        }
                    ],
                    "rhyme_hits": [
                        {
                            "family": "A",
                            "position": "end",
                            "meaning_bearing": True,
                            "grammar_tail_only": True,
                            "reading_confidence": 0.95,
                        }
                    ],
                    "changes": [],
                    "naturalness_review": {
                        "status": "unknown",
                        "evidence": "",
                    },
                    "interesting_without_rhyme_review": {
                        "status": "fail",
                        "evidence": "韻語を外すと主張が残らない",
                    },
                    "ai_pattern_flags": ["uniform noun-ending syntax"],
                }
            )
        result = professional_audit(
            {
                "bars": bars,
                "independent_review": False,
                "audio_reviewed": False,
                "technical_rhyme_brief": True,
                "setups": [],
                "payoffs": [],
            }
        )
        self.assertEqual(result["verdict"], "reject-or-repair")
        self.assertIn(
            "rhyme architecture is concentrated at line endings",
            result["hard_gate_failures"],
        )
        self.assertIn(
            "a four-bar window lacks information, emotion, or flow change",
            result["hard_gate_failures"],
        )
        self.assertIn(
            "apparent rhyme is dominated by grammatical tails",
            result["hard_gate_failures"],
        )
        self.assertIn(
            "one or more bars have no proposition or interest without rhyme",
            result["hard_gate_failures"],
        )
        self.assertEqual(result["score_caps"]["overall_max_out_of_5"], 2)

    def test_empty_audit_is_blocked(self):
        result = professional_audit(
            {
                "bars": [],
                "independent_review": True,
                "audio_reviewed": False,
            }
        )
        self.assertEqual(result["verdict"], "reject-or-repair")
        self.assertIn("no bar-level evidence was supplied", result["hard_gate_failures"])

    def test_orphan_payoff_is_a_hard_failure(self):
        result = professional_audit(
            {
                "bars": [
                    {
                        "index": 1,
                        "tokens": [{"surface": "レシート", "concreteness": 0.9}],
                        "rhyme_hits": [],
                        "changes": ["information"],
                        "naturalness_review": {
                            "status": "pass",
                            "evidence": "音読で自然",
                        },
                        "interesting_without_rhyme_review": {
                            "status": "pass",
                            "evidence": "場面と行動が残る",
                        },
                        "ai_pattern_flags": [],
                    }
                ],
                "setups": [],
                "payoffs": [
                    {"id": "P1", "bar": 1, "setup_id": "missing", "mechanism": "reversal"}
                ],
                "independent_review": True,
                "audio_reviewed": False,
            }
        )
        self.assertEqual(result["verdict"], "reject-or-repair")
        self.assertTrue(
            any("payoffs without recorded setup" in item for item in result["hard_gate_failures"])
        )

    def test_audit_boolean_never_self_certifies_audio(self):
        result = professional_audit(
            {
                "bars": [
                    {
                        "index": 1,
                        "tokens": [{"surface": "紙", "concreteness": 0.9}],
                        "rhyme_hits": [],
                        "changes": ["information"],
                        "naturalness_review": {"status": "pass", "evidence": "音読メモ"},
                        "interesting_without_rhyme_review": {
                            "status": "pass",
                            "evidence": "場面が残る",
                        },
                        "ai_pattern_flags": [],
                    }
                ],
                "independent_review": True,
                "audio_reviewed": True,
            }
        )
        self.assertEqual(result["score_caps"]["flow"], "unverified")
        self.assertFalse(result["evidence_coverage"]["audio"])


if __name__ == "__main__":
    unittest.main()
