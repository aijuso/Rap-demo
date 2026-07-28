#!/usr/bin/env python3
"""Validate and summarize human/AI-authored token-level lyric annotations."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


REQUIRED_TOKEN_FIELDS = {
    "surface", "normalized", "reading", "morae", "literal_sense",
    "contextual_sense", "plain_explanation", "speaker_attitude", "ambiguity",
    "part_of_speech", "syntax_role", "register",
    "semantic_domain", "concreteness", "sound_role", "rhyme_role",
    "humor_role", "narrative_role", "prominence", "confidence",
    "connotation", "referent", "claim_status", "evidence",
}
BAR_FUNCTIONS = {
    "setup", "development", "misdirection", "turn", "payoff",
    "callback", "bridge", "hook", "texture", "other",
}
PROMINENCE = {"background", "normal", "accented", "held", "rest-adjacent"}
CLAIM_STATUS = {"observed", "inferred", "proposed", "unknown"}


def validate_and_summarize(payload: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    tokens: list[dict] = []
    policy = payload.get("source_policy")
    if policy not in {"user_supplied_text", "original_generated_text", "commercial_work"}:
        errors.append("source_policy is missing or invalid")
    if not payload.get("bars"):
        errors.append("at least one bar or section analysis is required")
    for bar_pos, bar in enumerate(payload.get("bars", []), 1):
        if not str(bar.get("paraphrase", "")).strip() or "function" not in bar:
            errors.append(f"bar {bar_pos}: paraphrase and function are required")
        elif bar.get("function") not in BAR_FUNCTIONS:
            errors.append(f"bar {bar_pos}: invalid function")
        if policy == "commercial_work" and bar.get("surface"):
            errors.append(
                f"bar {bar_pos}: commercial_work must not store full lyric surface"
            )
        if policy == "commercial_work" and bar.get("tokens"):
            errors.append(
                f"bar {bar_pos}: commercial_work must not store reconstructable token sequences"
            )
        if policy in {"user_supplied_text", "original_generated_text"} and not bar.get("tokens"):
            errors.append(
                f"bar {bar_pos}: detailed analysis requires at least one token annotation"
            )
        for token_pos, token in enumerate(bar.get("tokens", []), 1):
            missing = sorted(REQUIRED_TOKEN_FIELDS - set(token))
            if missing:
                errors.append(
                    f"bar {bar_pos} token {token_pos}: missing {', '.join(missing)}"
                )
            nonempty_fields = [
                "surface", "normalized", "literal_sense", "contextual_sense",
                "plain_explanation", "speaker_attitude", "part_of_speech",
                "syntax_role", "register",
            ]
            for field in nonempty_fields:
                if field in token and not str(token.get(field, "")).strip():
                    errors.append(
                        f"bar {bar_pos} token {token_pos}: {field} must be nonempty"
                    )
            if not token.get("semantic_domain"):
                errors.append(
                    f"bar {bar_pos} token {token_pos}: semantic_domain must be nonempty"
                )
            if not token.get("evidence") or not all(
                str(item).strip() for item in token.get("evidence", [])
            ):
                errors.append(
                    f"bar {bar_pos} token {token_pos}: evidence must contain a nonempty item"
                )
            for field in (
                "morae", "connotation", "ambiguity", "semantic_domain",
                "sound_role", "rhyme_role", "humor_role", "narrative_role", "evidence",
            ):
                if field in token and not isinstance(token.get(field), list):
                    errors.append(
                        f"bar {bar_pos} token {token_pos}: {field} must be an array"
                    )
            if token.get("prominence") not in PROMINENCE:
                errors.append(f"bar {bar_pos} token {token_pos}: invalid prominence")
            if token.get("claim_status") not in CLAIM_STATUS:
                errors.append(f"bar {bar_pos} token {token_pos}: invalid claim_status")
            for field in ("concreteness", "confidence"):
                value = token.get(field)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not 0 <= float(value) <= 1
                ):
                    errors.append(
                        f"bar {bar_pos} token {token_pos}: {field} must be a number from 0 to 1"
                    )
            if token.get("reading") is None:
                warnings.append(f"bar {bar_pos} token {token_pos}: reading unverified")
                if token.get("claim_status") != "unknown":
                    errors.append(
                        f"bar {bar_pos} token {token_pos}: missing reading requires claim_status unknown"
                    )
            elif not token.get("morae"):
                errors.append(
                    f"bar {bar_pos} token {token_pos}: a supplied reading requires morae"
                )
            confidence = token.get("confidence")
            if isinstance(confidence, (int, float)) and confidence < 0.7:
                warnings.append(f"bar {bar_pos} token {token_pos}: low-confidence annotation")
            tokens.append(token)
    domains = Counter(
        domain
        for token in tokens
        for domain in token.get("semantic_domain", [])
    )
    parts = Counter(token.get("part_of_speech", "unknown") for token in tokens)
    rhyme_roles = Counter(
        role for token in tokens for role in token.get("rhyme_role", [])
    )
    humor_roles = Counter(
        role for token in tokens for role in token.get("humor_role", [])
    )
    concrete = [
        float(token["concreteness"])
        for token in tokens
        if isinstance(token.get("concreteness"), (int, float))
    ]
    abstract_ratio = (
        sum(value < 0.4 for value in concrete) / len(concrete) if concrete else None
    )
    if abstract_ratio is not None and abstract_ratio > 0.5:
        warnings.append("more than half of annotated tokens are abstract")
    return {
        "valid": not errors,
        "bar_count": len(payload.get("bars", [])),
        "token_count": len(tokens),
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "parts_of_speech": dict(parts),
            "semantic_domains": dict(domains),
            "rhyme_roles": dict(rhyme_roles),
            "humor_roles": dict(humor_roles),
            "mean_concreteness": (
                round(sum(concrete) / len(concrete), 3) if concrete else None
            ),
            "abstract_ratio": round(abstract_ratio, 3) if abstract_ratio is not None else None,
        },
        "limitations": [
            "Dictionary sense, contextual meaning, humor, and referents require interpretive evidence.",
            "Validation proves annotation completeness, not interpretive correctness.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(validate_and_summarize(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
