#!/usr/bin/env python3
"""Validate file identity and coverage for a host-authored audio review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REVIEW_VALUES = {"pass", "fail", "unknown"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_audio_review(
    review: dict,
    *,
    flow_map_path: Path,
    beat_path: Path,
    audio_path: Path,
) -> dict:
    errors: list[str] = []
    expected = {
        "flow_map_sha256": digest(flow_map_path),
        "beat_sha256": digest(beat_path),
        "audio_sha256": digest(audio_path),
    }
    if review.get("flow_map_sha256") != expected["flow_map_sha256"]:
        errors.append("flow map hash mismatch")
    if (review.get("beat") or {}).get("sha256") != expected["beat_sha256"]:
        errors.append("beat hash mismatch")
    if (review.get("audio") or {}).get("sha256") != expected["audio_sha256"]:
        errors.append("audio hash mismatch")
    if not (review.get("host_inspection") or {}).get("audio_opened"):
        errors.append("host did not attest that audio was opened")
    if not (review.get("host_inspection") or {}).get("beat_opened"):
        errors.append("host did not attest that beat was opened")
    if int((review.get("audio") or {}).get("take_count", 0) or 0) < 1:
        errors.append("take_count must be at least one")
    if not str((review.get("reviewer") or {}).get("id", "")).strip():
        errors.append("reviewer id is required")
    bars = review.get("bar_reviews", [])
    if not bars:
        errors.append("bar_reviews must be nonempty")
    for index, item in enumerate(bars, 1):
        for field in ("accent", "pocket", "breath", "articulation"):
            if item.get(field) not in REVIEW_VALUES:
                errors.append(f"bar review {index}: invalid {field}")
        if not item.get("evidence") or not all(
            str(entry).strip() for entry in item.get("evidence", [])
        ):
            errors.append(f"bar review {index}: evidence is required")
    unresolved = [
        item.get("bar")
        for item in bars
        if "unknown" in {
            item.get("accent"), item.get("pocket"),
            item.get("breath"), item.get("articulation"),
        }
    ]
    return {
        "integrity_valid": not errors,
        "eligible_for_audio_informed_audit": not errors and not unresolved,
        "errors": errors,
        "unresolved_bars": unresolved,
        "verified_hashes": expected,
        "limitations": [
            "Hash validation proves which files were reviewed, not that the artistic judgment is correct.",
            "A host must actually open/listen to both files before setting host_inspection.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("review", type=Path)
    parser.add_argument("--flow-map", type=Path, required=True)
    parser.add_argument("--beat", type=Path, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    args = parser.parse_args()
    review = json.loads(args.review.read_text(encoding="utf-8"))
    result = validate_audio_review(
        review,
        flow_map_path=args.flow_map,
        beat_path=args.beat,
        audio_path=args.audio,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
