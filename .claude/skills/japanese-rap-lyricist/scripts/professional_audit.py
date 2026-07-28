#!/usr/bin/env python3
"""Evidence-based professional audit for annotated Japanese rap drafts.

This program checks measurable structure and review completeness. It refuses to
invent aesthetic scores for meaning, humor, naturalness, or delivery.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def professional_audit(payload: dict) -> dict:
    bars = payload.get("bars", [])
    hard_gates: list[str] = []
    warnings: list[str] = []
    unknowns: list[str] = []
    if not bars:
        hard_gates.append("no bar-level evidence was supplied")
    expected_bar_count = payload.get("expected_bar_count")
    if expected_bar_count is not None and len(bars) != int(expected_bar_count):
        hard_gates.append(
            f"bar count mismatch: expected {int(expected_bar_count)}, received {len(bars)}"
        )

    rhyme_hits = [hit for bar in bars for hit in bar.get("rhyme_hits", [])]
    end_hits = sum(hit.get("position") == "end" for hit in rhyme_hits)
    internal_hits = sum(
        hit.get("position") in {"initial", "internal", "caesura", "cross_bar"}
        for hit in rhyme_hits
    )
    end_bias = end_hits / len(rhyme_hits) if rhyme_hits else None
    if end_bias is not None and len(rhyme_hits) >= 4 and end_bias > 0.75:
        intentional_reason = str(payload.get("intentional_end_rhyme_reason") or "").strip()
        if payload.get("technical_rhyme_brief") and not intentional_reason:
            hard_gates.append("rhyme architecture is concentrated at line endings")
        else:
            warnings.append(
                "rhyme architecture is concentrated at line endings; verify this is intentional"
            )
    if rhyme_hits and not any(hit.get("meaning_bearing") for hit in rhyme_hits):
        hard_gates.append("no important rhyme domain is marked meaning-bearing")
    grammar_tail_ratio = (
        sum(bool(hit.get("grammar_tail_only")) for hit in rhyme_hits) / len(rhyme_hits)
        if rhyme_hits
        else None
    )
    if grammar_tail_ratio is not None and grammar_tail_ratio >= 0.75:
        hard_gates.append("apparent rhyme is dominated by grammatical tails")
    low_confidence_rhymes = [
        hit for hit in rhyme_hits if float(hit.get("reading_confidence", 1.0)) < 0.7
    ]
    if low_confidence_rhymes:
        warnings.append("one or more rhyme events depend on low-confidence readings")

    families = Counter(hit.get("family") for hit in rhyme_hits if hit.get("family"))
    dominant_family_ratio = (
        max(families.values()) / len(rhyme_hits) if rhyme_hits and families else None
    )
    if dominant_family_ratio is not None and dominant_family_ratio > 0.6:
        warnings.append("one rhyme family supplies more than 60% of rhyme hits")

    tokens = [token for bar in bars for token in bar.get("tokens", [])]
    concrete_scores = [
        float(token["concreteness"])
        for token in tokens
        if isinstance(token.get("concreteness"), (int, float))
    ]
    abstract_ratio = (
        sum(score < 0.4 for score in concrete_scores) / len(concrete_scores)
        if concrete_scores
        else None
    )
    if abstract_ratio is None:
        unknowns.append("abstract-language ratio lacks token annotations")
    elif abstract_ratio > 0.5:
        hard_gates.append("abstract terms dominate annotated vocabulary")

    failed_naturalness = []
    missing_naturalness = []
    failed_plain_test = []
    missing_plain_test = []
    ai_pattern_flags = []
    for bar in bars:
        review = bar.get("naturalness_review")
        if (
            not review
            or review.get("status") == "unknown"
            or not str(review.get("evidence", "")).strip()
        ):
            missing_naturalness.append(bar.get("index"))
        elif review.get("status") == "fail":
            failed_naturalness.append(
                {"bar": bar.get("index"), "evidence": review.get("evidence", "")}
            )
        plain_review = bar.get("interesting_without_rhyme_review")
        if (
            not plain_review
            or plain_review.get("status") == "unknown"
            or not str(plain_review.get("evidence", "")).strip()
        ):
            missing_plain_test.append(bar.get("index"))
        elif plain_review.get("status") == "fail":
            failed_plain_test.append(
                {"bar": bar.get("index"), "evidence": plain_review.get("evidence", "")}
            )
        for flag in bar.get("ai_pattern_flags", []):
            ai_pattern_flags.append({"bar": bar.get("index"), "flag": flag})
    if failed_naturalness:
        hard_gates.append("spoken Japanese naturalness review failed")
    if missing_naturalness:
        unknowns.append(f"naturalness not reviewed for bars {missing_naturalness}")
    if failed_plain_test:
        hard_gates.append("one or more bars have no proposition or interest without rhyme")
    if missing_plain_test:
        unknowns.append(f"without-rhyme plain test missing for bars {missing_plain_test}")
    if ai_pattern_flags:
        warnings.append("repeated AI-like syntax or diction patterns were flagged")

    windows = []
    for start in range(0, len(bars), 4):
        group = bars[start : start + 4]
        changes = sorted({change for bar in group for change in bar.get("changes", [])})
        windows.append(
            {
                "bars": [bar.get("index") for bar in group],
                "changes": changes,
                "passes": bool(changes),
            }
        )
    if any(not window["passes"] for window in windows):
        hard_gates.append("a four-bar window lacks information, emotion, or flow change")

    setups = {item["id"]: item for item in payload.get("setups", [])}
    payoffs = {item["id"]: item for item in payload.get("payoffs", [])}
    unresolved_setups = [
        setup_id
        for setup_id, setup in setups.items()
        if setup.get("expected_payoff_id") not in payoffs
    ]
    orphan_payoffs = [
        payoff_id
        for payoff_id, payoff in payoffs.items()
        if payoff.get("setup_id") not in setups
    ]
    if unresolved_setups:
        hard_gates.append(f"setups without payoff: {unresolved_setups}")
    if orphan_payoffs:
        hard_gates.append(f"payoffs without recorded setup: {orphan_payoffs}")

    empty_entities = [
        item for item in payload.get("named_entities", []) if not item.get("function", "").strip()
    ]
    if empty_entities:
        hard_gates.append("proper nouns are present without a semantic or comic function")

    unknowns.extend(
        [
            "accent naturalness requires a separate host audio-review artifact",
            "pocket, breath, microtiming, and delivery require a separate host audio-review artifact",
        ]
    )
    if payload.get("audio_reviewed"):
        warnings.append(
            "audio_reviewed boolean is not accepted as verification by deterministic preflight"
        )
    if not payload.get("independent_review"):
        warnings.append("audit is not independent; overall score must remain capped")

    evidence_coverage = {
        "token_semantics": bool(tokens),
        "rhyme_placement": bool(rhyme_hits),
        "naturalness": not missing_naturalness,
        "without_rhyme_plain_test": not missing_plain_test,
        "four_bar_change": bool(windows),
        "setup_payoff": bool(setups or payoffs),
        "audio": False,
        "independent": bool(payload.get("independent_review")),
    }
    evidence_blocked = bool(missing_naturalness or missing_plain_test or not bars)
    cap = 2 if hard_gates else (3 if evidence_blocked else (4 if payload.get("independent_review") else 3))
    if hard_gates:
        verdict = "reject-or-repair"
    elif evidence_blocked:
        verdict = "blocked-insufficient-evidence"
    else:
        verdict = "eligible-for-human-release-review"
    return {
        "verdict": verdict,
        "preflight_only": True,
        "hard_gate_failures": hard_gates,
        "warnings": warnings,
        "unknowns": sorted(set(unknowns)),
        "metrics": {
            "bar_count": len(bars),
            "rhyme_hit_count": len(rhyme_hits),
            "end_rhyme_bias": round(end_bias, 3) if end_bias is not None else None,
            "internal_or_cross_rhyme_hits": internal_hits,
            "dominant_family_ratio": (
                round(dominant_family_ratio, 3)
                if dominant_family_ratio is not None
                else None
            ),
            "grammar_tail_ratio": (
                round(grammar_tail_ratio, 3) if grammar_tail_ratio is not None else None
            ),
            "low_confidence_rhyme_count": len(low_confidence_rhymes),
            "abstract_token_ratio": (
                round(abstract_ratio, 3) if abstract_ratio is not None else None
            ),
            "four_bar_windows": windows,
            "unresolved_setups": unresolved_setups,
            "orphan_payoffs": orphan_payoffs,
            "ai_pattern_flags": ai_pattern_flags,
        },
        "evidence_coverage": evidence_coverage,
        "score_caps": {
            "overall_max_out_of_5": cap,
            "flow": "unverified",
            "delivery": "unverified",
        },
        "limitations": [
            "Humor quality and whether a line is interesting without rhyme remain human judgments.",
            "A passed structural audit is not a claim of professional artistic quality.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(professional_audit(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
