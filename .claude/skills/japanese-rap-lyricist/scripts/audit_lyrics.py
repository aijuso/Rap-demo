#!/usr/bin/env python3
"""Conservative structural audit for original Japanese rap drafts.

Input format: one bar per line. Add a tab and performed reading when available:
    surface<TAB>reading
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from kana_to_mora import parse_morae
from rhyme_score import score_pair


GENERIC_TERMS = {
    "夢", "未来", "光", "闇", "希望", "運命", "境界線", "人生", "世界",
    "自分らしく", "諦めない", "信じる", "羽ばたく", "輝く", "一歩ずつ",
}
FORCED_PATTERNS = {
    "変えてく生成": "noun chosen to preserve an end sound",
    "隣にいる生命": "dehumanizing or unnatural abstraction for a person",
    "胸の警報": "stock metaphor unless grounded by a concrete event",
    "夢までは囲えない": "generic motivational abstraction",
}


def load_bars(path: Path) -> list[dict]:
    bars = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            surface, reading = line.split("\t", 1)
        else:
            surface, reading = line, None
        bars.append({"surface": surface.strip(), "reading": reading.strip() if reading else None})
    return bars


def signature_windows(reading: str, minimum: int = 2, maximum: int = 6) -> set[tuple[str, ...]]:
    moras, _ = parse_morae(reading)
    sig = [m.signature for m in moras]
    windows: set[tuple[str, ...]] = set()
    for size in range(minimum, min(maximum, len(sig)) + 1):
        for start in range(0, len(sig) - size + 1):
            windows.add(tuple(sig[start : start + size]))
    return windows


def audit(bars: list[dict]) -> dict:
    warnings: list[dict] = []
    hard_gates: list[str] = []
    suffixes = Counter(bar["surface"][-2:] for bar in bars if len(bar["surface"]) >= 2)
    repeated_suffixes = {key: count for key, count in suffixes.items() if count >= 3}
    if repeated_suffixes:
        warnings.append({"code": "repeated_surface_suffix", "details": repeated_suffixes})
    generic_hits = []
    forced_hits = []
    for index, bar in enumerate(bars, 1):
        for term in GENERIC_TERMS:
            if term in bar["surface"]:
                generic_hits.append({"bar": index, "term": term})
        for pattern, reason in FORCED_PATTERNS.items():
            if pattern in bar["surface"]:
                forced_hits.append({"bar": index, "pattern": pattern, "reason": reason})
    if generic_hits:
        warnings.append({"code": "generic_abstraction", "details": generic_hits})
    if forced_hits:
        warnings.append({"code": "forced_or_stock_language", "details": forced_hits})
        hard_gates.append("central Japanese may be unnatural or rhyme-driven")
    readings_available = all(bar["reading"] for bar in bars) and bool(bars)
    rhyme_pairs = []
    internal_evidence = []
    if readings_available:
        for left in range(len(bars)):
            for right in range(left + 1, min(len(bars), left + 4)):
                pair = score_pair(
                    bars[left]["surface"],
                    bars[right]["surface"],
                    bars[left]["reading"],
                    bars[right]["reading"],
                )
                if pair["sound_score_after_penalty"] >= 0.65:
                    rhyme_pairs.append(
                        {
                            "bars": [left + 1, right + 1],
                            "score": pair["sound_score_after_penalty"],
                            "domain": pair["best_domain"]["domain_length"],
                            "span": [
                                pair["best_domain"]["span_a"],
                                pair["best_domain"]["span_b"],
                            ],
                        }
                    )
        seen: dict[tuple[str, ...], list[tuple[int, int]]] = {}
        for bar_index, bar in enumerate(bars, 1):
            moras, _ = parse_morae(bar["reading"])
            sig = [m.signature for m in moras]
            for size in range(3, min(6, len(sig)) + 1):
                for start in range(0, max(0, len(sig) - size)):
                    window = tuple(sig[start : start + size])
                    seen.setdefault(window, []).append((bar_index, start))
        for window, positions in seen.items():
            if len({p[0] for p in positions}) >= 2:
                internal_evidence.append({"signature": list(window), "positions": positions[:6]})
    else:
        warnings.append(
            {
                "code": "reading_missing",
                "details": "Sound analysis is provisional; provide surface<TAB>reading.",
            }
        )
    if len(bars) >= 8 and not internal_evidence:
        warnings.append(
            {
                "code": "no_internal_rhyme_evidence",
                "details": "No repeated 3+ mora internal window was established.",
            }
        )
    if len(generic_hits) >= max(3, len(bars) // 3):
        hard_gates.append("generic abstraction dominates the draft")
    if len(rhyme_pairs) and not internal_evidence and len(bars) >= 8:
        hard_gates.append("apparent technique is concentrated at line endings")
    maximum_overall = 2.0 if hard_gates else 3.0
    return {
        "bar_count": len(bars),
        "readings_complete": readings_available,
        "rhyme_pairs": rhyme_pairs,
        "internal_rhyme_evidence": internal_evidence[:20],
        "warnings": warnings,
        "hard_gate_failures": hard_gates,
        "score_caps": {
            "overall_max_without_independent_evaluation": maximum_overall,
            "flow": "unverified",
            "delivery": "unverified",
        },
        "verdict": "reject-or-rebuild" if hard_gates else "requires-human-and-performance-review",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lyrics", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(load_bars(args.lyrics))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
