#!/usr/bin/env python3
"""Standard-library preflight for research-bank, rhyme-bank, and scout-research artifacts.

Checks required structure, id cross-references, evidence coverage, and (for
rhyme banks) per-keyword type minimums. It does not judge whether a keyword is
interesting or a rhyme candidate is natural — those remain human checkpoints.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

EVIDENCE_KINDS = {
    "user_input", "performed_reading", "dictionary",
    "interview", "paper", "inference", "web",
}
KEYWORD_KINDS = {"vocabulary", "episode", "association"}
DOMAINS = {
    "object", "action", "place", "time_or_number", "sound",
    "body", "institution_or_money", "relationship", "other",
}
# Per selected keyword, the rhyme bank must reach these counts per bucket.
DEFAULT_TYPE_MINIMUMS = {
    "assonance": 5,
    "consonance": 3,
    "multimora": 3,
    "phrase_or_mosaic": 3,
    "placement_proposal": 2,
}
TYPE_BUCKETS = {
    "assonance": {"assonance", "near_assonance", "exact_rhyme"},
    "consonance": {"consonance", "alliteration"},
    "multimora": {"multimora_rhyme", "multisyllabic_rhyme", "multi_mora"},
    "phrase_or_mosaic": {"phrase_rhyme", "mosaic_rhyme", "split_rhyme"},
    "placement_proposal": {
        "internal_rhyme", "initial_rhyme", "cross_bar_rhyme",
        "delayed_rhyme", "medial_rhyme",
    },
}
MIN_CANDIDATES_PER_KEYWORD = 20


def check_evidence(items: list, owner: str, errors: list[str]) -> None:
    if not items:
        errors.append(f"{owner}: evidence is empty")
        return
    for index, item in enumerate(items):
        kind = item.get("kind")
        if kind not in EVIDENCE_KINDS:
            errors.append(f"{owner}: evidence[{index}] has unknown kind {kind!r}")
        if not str(item.get("pointer", "")).strip():
            errors.append(f"{owner}: evidence[{index}] has no pointer")
        if kind == "web" and not str(item.get("pointer", "")).startswith("http"):
            errors.append(f"{owner}: evidence[{index}] is web without a URL pointer")


def validate_research(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "research-bank/v1":
        errors.append("schema must be research-bank/v1")
    if not str(payload.get("theme", "")).strip():
        errors.append("theme is empty")
    keywords = payload.get("keywords", [])
    if not keywords:
        errors.append("keywords is empty")
    seen_ids: set[str] = set()
    for keyword in keywords:
        kid = str(keyword.get("id", ""))
        owner = f"keyword {kid or '<missing id>'}"
        if not kid:
            errors.append("a keyword has no id")
        elif kid in seen_ids:
            errors.append(f"duplicate keyword id {kid}")
        seen_ids.add(kid)
        for field in ("surface", "reading", "vowel_skeleton", "consonant_skeleton", "plain_meaning"):
            if not str(keyword.get(field, "")).strip():
                errors.append(f"{owner}: {field} is empty")
        if keyword.get("kind") not in KEYWORD_KINDS:
            errors.append(f"{owner}: kind must be one of {sorted(KEYWORD_KINDS)}")
        if keyword.get("domain") not in DOMAINS:
            errors.append(f"{owner}: domain must be one of {sorted(DOMAINS)}")
        if keyword.get("confidence") not in {"high", "medium", "low"}:
            errors.append(f"{owner}: confidence must be high/medium/low")
        check_evidence(keyword.get("evidence", []), owner, errors)
    return errors


def validate_rhyme(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "rhyme-bank/v1":
        errors.append("schema must be rhyme-bank/v1")
    keywords = {str(k.get("id", "")): k for k in payload.get("keywords", [])}
    if not keywords:
        errors.append("keywords is empty")
    candidates = payload.get("candidates", [])
    if not candidates:
        errors.append("candidates is empty")
    minimums = {**DEFAULT_TYPE_MINIMUMS, **payload.get("type_minimums", {})}
    per_keyword: Counter[str] = Counter()
    per_bucket: dict[str, Counter] = {bucket: Counter() for bucket in TYPE_BUCKETS}
    for index, candidate in enumerate(candidates):
        kid = str(candidate.get("keyword_id", ""))
        owner = f"candidate[{index}] {candidate.get('surface', '')!r}"
        if kid not in keywords:
            errors.append(f"{owner}: keyword_id {kid!r} is not in keywords")
            continue
        per_keyword[kid] += 1
        for field in ("surface", "reading", "vowel_skeleton", "consonant_skeleton", "example_phrase"):
            if not str(candidate.get(field, "")).strip():
                errors.append(f"{owner}: {field} is empty")
        types = candidate.get("rhyme_types", [])
        if not types:
            errors.append(f"{owner}: rhyme_types is empty")
        for bucket, members in TYPE_BUCKETS.items():
            if members & set(types):
                per_bucket[bucket][kid] += 1
        for field in ("score_vowel", "score_consonant", "score_balanced"):
            value = candidate.get(field)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                errors.append(f"{owner}: {field} must be a number in [0,1]")
    for kid in keywords:
        if per_keyword[kid] < MIN_CANDIDATES_PER_KEYWORD:
            errors.append(
                f"keyword {kid}: only {per_keyword[kid]} candidates; "
                f"minimum is {MIN_CANDIDATES_PER_KEYWORD}"
            )
        for bucket, minimum in minimums.items():
            have = per_bucket.get(bucket, Counter())[kid]
            if have < minimum:
                errors.append(
                    f"keyword {kid}: bucket {bucket} has {have} candidates; "
                    f"minimum is {minimum}"
                )
    return errors


def validate_scout(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "scout-research/v1":
        errors.append("schema must be scout-research/v1")
    if not isinstance(payload.get("round"), int) or payload.get("round", 0) < 1:
        errors.append("round must be a positive integer")
    if not str(payload.get("focus", "")).strip():
        errors.append("focus is empty")
    angles = payload.get("angles", [])
    if not 2 <= len(angles) <= 6:
        errors.append("angles must contain 2-6 entries")
    for index, angle in enumerate(angles):
        owner = f"angle[{index}]"
        if not str(angle.get("premise", "")).strip():
            errors.append(f"{owner}: premise is empty")
        if not angle.get("motifs"):
            errors.append(f"{owner}: motifs is empty")
        check_evidence(angle.get("evidence", []), owner, errors)
    return errors


VALIDATORS = {
    "research-bank/v1": validate_research,
    "rhyme-bank/v1": validate_rhyme,
    "scout-research/v1": validate_scout,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.path.read_text(encoding="utf-8"))
    validator = VALIDATORS.get(payload.get("schema"))
    if validator is None:
        result = {"valid": False, "errors": [f"unknown schema {payload.get('schema')!r}"]}
    else:
        errors = validator(payload)
        result = {"valid": not errors, "schema": payload.get("schema"), "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
