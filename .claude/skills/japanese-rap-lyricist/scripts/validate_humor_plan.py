#!/usr/bin/env python3
"""Standard-library preflight for Humor Engine artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TOP_FIELDS = {
    "mode", "purpose", "target_policy", "density_map", "punch_cards",
    "callback_map", "character_knowledge", "voice_cast", "reveal_schedule",
    "rights_origin", "risk_flags",
}
PUNCH_FIELDS = {
    "id", "technique", "prediction", "violation", "reframe",
    "benignizer", "target", "timing", "meaning_without_joke",
}


def validate_humor_plan(payload: dict) -> dict:
    errors: list[str] = []
    missing = sorted(TOP_FIELDS - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("mode") not in {"general", "character_driven"}:
        errors.append("mode must be general or character_driven")
    if not str(payload.get("purpose", "")).strip():
        errors.append("purpose must be nonempty")
    for index, card in enumerate(payload.get("punch_cards", []), 1):
        card_missing = sorted(PUNCH_FIELDS - set(card))
        if card_missing:
            errors.append(f"punch {index}: missing {', '.join(card_missing)}")
        for field in PUNCH_FIELDS - {"timing"}:
            if field in card and not str(card.get(field, "")).strip():
                errors.append(f"punch {index}: {field} must be nonempty")
    rights = payload.get("rights_origin") or {}
    if not rights.get("evidence"):
        errors.append("rights_origin.evidence must be nonempty")
    if payload.get("mode") == "character_driven":
        for field in (
            "character_knowledge", "voice_cast", "reveal_schedule", "punch_cards"
        ):
            if not payload.get(field):
                errors.append(f"character_driven mode requires {field}")
        if rights.get("characters_original") is not True:
            errors.append("character_driven mode requires original characters")
        if rights.get("commercial_world_reused") is not False:
            errors.append("character_driven mode forbids reused commercial worlds")
    return {
        "valid": not errors,
        "errors": errors,
        "preflight_only": True,
        "limitations": [
            "This validator cannot determine whether a joke is funny or safe in performance.",
            "Timing and audience response require rehearsal or recorded review.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(validate_humor_plan(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
