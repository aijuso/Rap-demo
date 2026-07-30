#!/usr/bin/env python3
"""Explainable, conservative Japanese rhyme-pair scoring."""

from __future__ import annotations

import argparse
import json
import math
from difflib import SequenceMatcher

from kana_to_mora import Mora, parse_morae
from normalize_text import normalize_kana


VOWEL_COST = {
    "a": {"a": 0, "i": 3, "u": 5, "e": 2, "o": 4},
    "i": {"a": 3, "i": 0, "u": 2, "e": 1, "o": 3},
    "u": {"a": 5, "i": 2, "u": 0, "e": 3, "o": 1},
    "e": {"a": 2, "i": 1, "u": 3, "e": 0, "o": 2},
    "o": {"a": 4, "i": 3, "u": 1, "e": 2, "o": 0},
}

# Weight presets over (vowel, special, onset, length_bonus). "balanced" is the
# historical default; "consonant" exists for 子音韻/頭韻 hunting, where カタカタ
# and コトコト should rank as a pair even though every nucleus differs.
MODE_WEIGHTS = {
    "balanced": (0.65, 0.10, 0.10, 0.15),
    "vowel": (0.75, 0.10, 0.00, 0.15),
    "consonant": (0.15, 0.10, 0.60, 0.15),
}

ONSET_FEATURES = {
    "": ("none", "none", "none"),
    "k": ("velar", "stop", "voiceless"), "g": ("velar", "stop", "voiced"),
    "s": ("alveolar", "fricative", "voiceless"), "z": ("alveolar", "fricative", "voiced"),
    "sh": ("postalveolar", "fricative", "voiceless"),
    "j": ("postalveolar", "affricate", "voiced"),
    "t": ("alveolar", "stop", "voiceless"), "d": ("alveolar", "stop", "voiced"),
    "ch": ("postalveolar", "affricate", "voiceless"),
    "ts": ("alveolar", "affricate", "voiceless"),
    "n": ("alveolar", "nasal", "voiced"), "m": ("bilabial", "nasal", "voiced"),
    "h": ("glottal", "fricative", "voiceless"), "f": ("bilabial", "fricative", "voiceless"),
    "b": ("bilabial", "stop", "voiced"), "p": ("bilabial", "stop", "voiceless"),
    "r": ("alveolar", "tap", "voiced"), "y": ("palatal", "approximant", "voiced"),
    "w": ("bilabial", "approximant", "voiced"), "v": ("bilabial", "fricative", "voiced"),
}


def unit_similarity(a: Mora, b: Mora) -> tuple[float, float, float]:
    if a.special in {"N", "Q"} or b.special in {"N", "Q"}:
        special = 1.0 if a.special == b.special and a.special in {"N", "Q"} else 0.0
        return special, special, 0.5
    if not a.nucleus or not b.nucleus:
        return 0.0, 0.0, 0.0
    cost = VOWEL_COST[a.nucleus][b.nucleus]
    vowel = max(0.0, 1.0 - cost / 5.0)
    features_a = ONSET_FEATURES.get(a.onset, ("other", "other", "other"))
    features_b = ONSET_FEATURES.get(b.onset, ("other", "other", "other"))
    onset = sum(x == y for x, y in zip(features_a, features_b)) / 3.0
    special = 1.0 if a.special == b.special else 0.7 if {a.special, b.special} <= {None, "R"} else 0.0
    return vowel, special, onset


def score_pair(
    surface_a: str,
    surface_b: str,
    reading_a: str,
    reading_b: str,
    *,
    max_domain: int = 8,
    mode: str = "balanced",
) -> dict:
    if mode not in MODE_WEIGHTS:
        raise ValueError(f"unknown mode {mode!r}; choose from {sorted(MODE_WEIGHTS)}")
    w_vowel, w_special, w_onset, w_length = MODE_WEIGHTS[mode]
    moras_a, warnings_a = parse_morae(reading_a)
    moras_b, warnings_b = parse_morae(reading_b)
    max_len = min(len(moras_a), len(moras_b), max_domain)
    best: dict | None = None
    for length in range(2, max_len + 1):
        span_a = moras_a[-length:]
        span_b = moras_b[-length:]
        weights = [((index + 1) / length) ** 2 for index in range(length)]
        denom = sum(weights)
        vowel = special = onset = 0.0
        alignment: list[dict] = []
        for ma, mb, weight in zip(span_a, span_b, weights):
            v, s, o = unit_similarity(ma, mb)
            vowel += v * weight
            special += s * weight
            onset += o * weight
            alignment.append(
                {
                    "a": ma.surface,
                    "b": mb.surface,
                    "vowel_or_coda_similarity": round(v, 3),
                    "onset_similarity": round(o, 3),
                }
            )
        vowel /= denom
        special /= denom
        onset /= denom
        length_bonus = min(1.0, math.log2(length + 1) / math.log2(max_domain + 1))
        sound = w_vowel * vowel + w_special * special + w_onset * onset + w_length * length_bonus
        candidate = {
            "domain_length": length,
            "vowel_or_coda": vowel,
            "special_mora": special,
            "onset": onset,
            "length_bonus": length_bonus,
            "raw_sound_score": sound,
            "alignment": alignment,
            "span_a": "".join(m.surface for m in span_a),
            "span_b": "".join(m.surface for m in span_b),
        }
        if best is None or candidate["raw_sound_score"] > best["raw_sound_score"]:
            best = candidate
    if best is None:
        best = {
            "domain_length": max_len,
            "vowel_or_coda": 0.0,
            "special_mora": 0.0,
            "onset": 0.0,
            "length_bonus": 0.0,
            "raw_sound_score": 0.0,
            "alignment": [],
            "span_a": "",
            "span_b": "",
        }
    norm_a = normalize_kana(reading_a, keep_boundaries=False)
    norm_b = normalize_kana(reading_b, keep_boundaries=False)
    surface_ratio = SequenceMatcher(None, surface_a, surface_b).ratio()
    reading_ratio = SequenceMatcher(None, norm_a, norm_b).ratio()
    trivial_penalty = 0.0
    if surface_a == surface_b:
        trivial_penalty = 0.55
    elif surface_ratio >= 0.8:
        trivial_penalty = 0.30
    elif reading_ratio >= 0.9:
        trivial_penalty = 0.12
    score = max(0.0, best["raw_sound_score"] - trivial_penalty)
    if score >= 0.82 and best["domain_length"] >= 3:
        label = "strong"
    elif score >= 0.65 and best["domain_length"] >= 2:
        label = "usable"
    elif score >= 0.48:
        label = "weak-or-contextual"
    else:
        label = "not-established"
    from skeleton import skeletons

    return {
        "surface_a": surface_a,
        "surface_b": surface_b,
        "reading_a": normalize_kana(reading_a),
        "reading_b": normalize_kana(reading_b),
        "mode": mode,
        "skeleton_a": {
            key: value
            for key, value in skeletons(reading_a).items()
            if key in {"vowel_skeleton", "consonant_skeleton", "consonant_skeleton_dotted"}
        },
        "skeleton_b": {
            key: value
            for key, value in skeletons(reading_b).items()
            if key in {"vowel_skeleton", "consonant_skeleton", "consonant_skeleton_dotted"}
        },
        "best_domain": {
            **best,
            "vowel_or_coda": round(best["vowel_or_coda"], 3),
            "special_mora": round(best["special_mora"], 3),
            "onset": round(best["onset"], 3),
            "length_bonus": round(best["length_bonus"], 3),
            "raw_sound_score": round(best["raw_sound_score"], 3),
        },
        "trivial_repetition_penalty": round(trivial_penalty, 3),
        "sound_score_after_penalty": round(score, 3),
        "label": label,
        "limitations": [
            "Meaning, naturalness, placement, beat salience, and performance are not scored.",
            "A high sound score is not a high lyric-quality score.",
        ],
        "warnings": warnings_a + warnings_b,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("surface_a")
    parser.add_argument("surface_b")
    parser.add_argument("--reading-a", required=True)
    parser.add_argument("--reading-b", required=True)
    parser.add_argument("--max-domain", type=int, default=8)
    parser.add_argument("--mode", choices=sorted(MODE_WEIGHTS), default="balanced")
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()
    result = score_pair(
        args.surface_a,
        args.surface_b,
        args.reading_a,
        args.reading_b,
        max_domain=args.max_domain,
        mode=args.mode,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
