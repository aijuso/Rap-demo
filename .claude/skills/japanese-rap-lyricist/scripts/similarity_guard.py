#!/usr/bin/env python3
"""Compare a candidate with user-provided references; flags are not legal conclusions."""

from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path

from normalize_text import nfkc


def ngrams(text: str, n: int) -> set[str]:
    compact = "".join(nfkc(text).split())
    if len(compact) < n:
        return {compact} if compact else set()
    return {compact[i : i + n] for i in range(len(compact) - n + 1)}


def compare(candidate: str, reference: str, n: int = 5) -> dict:
    a = ngrams(candidate, n)
    b = ngrams(reference, n)
    union = a | b
    jaccard = len(a & b) / len(union) if union else 0.0
    matcher = SequenceMatcher(None, candidate, reference)
    match = matcher.find_longest_match()
    longest = candidate[match.a : match.a + match.size]
    flag = jaccard >= 0.18 or match.size >= 16
    return {
        "ngram_size": n,
        "jaccard": round(jaccard, 4),
        "longest_exact_span": longest,
        "longest_exact_length": match.size,
        "review_required": flag,
        "limitations": [
            "This detects surface overlap only.",
            "It cannot decide copyright infringement or stylistic imitation.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--ngram", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = compare(
        args.candidate.read_text(encoding="utf-8"),
        args.reference.read_text(encoding="utf-8"),
        args.ngram,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
