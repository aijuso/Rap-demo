#!/usr/bin/env python3
"""Compile an explicit, provisional bar-by-bar flow map from JSON input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kana_to_mora import parse_morae


def density_label(mora_count: int | None, subdivision: str) -> str:
    if mora_count is None:
        return "medium"
    capacity = {"eighth": 8, "sixteenth": 16, "triplet": 12, "mixed": 16}[subdivision]
    ratio = mora_count / capacity
    if ratio <= 0.45:
        return "sparse"
    if ratio <= 0.85:
        return "medium"
    if ratio <= 1.15:
        return "dense"
    return "burst"


def compile_flow_map(payload: dict) -> dict:
    output: list[dict] = []
    unknowns = list(payload.get("unknowns", []))
    if not payload.get("bars"):
        raise ValueError("at least one bar is required for a flow map")
    evidence = payload.get("verification_evidence") or {}
    evidence_complete = (
        bool(str(evidence.get("beat_id", "")).strip())
        and bool(str(evidence.get("audio_id", "")).strip())
        and int(evidence.get("take_count", 0) or 0) >= 1
        and bool(str(evidence.get("reviewer", "")).strip())
        and bool(str(evidence.get("timestamp", "")).strip())
    )
    external_audio_claim_complete = (
        payload.get("verification") == "recorded_on_beat"
        and payload.get("bpm") is not None
        and evidence_complete
    )
    if payload.get("verification") == "recorded_on_beat" and not external_audio_claim_complete:
        unknowns.append(
            "recorded_on_beat claim was downgraded: BPM, bars, beat/audio ids, take count, reviewer, and timestamp are required"
        )
    if external_audio_claim_complete:
        unknowns.append(
            "audio evidence was declared, but this deterministic mapper cannot inspect audio; a host audio-review artifact must verify it"
        )
    audio_verified = False
    for position, bar in enumerate(payload.get("bars", []), 1):
        reading = bar.get("reading")
        mora_count = None
        if reading:
            moras, warnings = parse_morae(reading)
            if warnings:
                unknowns.extend(f"bar {position}: {warning}" for warning in warnings)
            else:
                mora_count = len(moras)
        else:
            unknowns.append(f"bar {position}: performed reading missing")
        subdivision = bar.get("subdivision", "sixteenth")
        output.append(
            {
                "index": int(bar.get("index", position)),
                "subdivision": subdivision,
                "mora_count": mora_count,
                "density": bar.get("density", density_label(mora_count, subdivision)),
                "rests": bar.get("rests", []),
                "accents": bar.get("accents", []),
                "held_vowels": bar.get("held_vowels", []),
                "breath": bar.get("breath", "none"),
                "voice": bar.get("voice", "main"),
                "function": bar.get("function", "development"),
                "entry": bar.get("entry", "beat_1"),
                "fast_zone": bar.get("fast_zone"),
                "repeat_count": int(bar.get("repeat_count", 0)),
                "character_voice": bar.get("character_voice", bar.get("voice", "main")),
                "narrative_reason": bar.get(
                    "narrative_reason", "requires human specification"
                ),
                "repeat_pattern": bar.get("repeat_pattern"),
                "switch": bar.get("switch"),
                "pre_punch_silence": bar.get("pre_punch_silence"),
                "confidence": min(
                    float(bar.get("confidence", 0.6)),
                    1.0 if audio_verified else 0.7,
                ),
            }
        )
    if not audio_verified:
        unknowns.append("pocket, microtiming, breath, and live feasibility require audio")
    return {
        "status": "audio_verified" if audio_verified else "proposal",
        "verification": "text_only",
        "bpm": payload.get("bpm"),
        "meter": payload.get("meter", "4/4"),
        "bars": output,
        "verification_evidence": None,
        "unknowns": sorted(set(unknowns)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(compile_flow_map(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
