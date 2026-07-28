#!/usr/bin/env python3
"""Create a provisional mora grid; never verifies pocket or delivery."""

from __future__ import annotations

import argparse
import json

from kana_to_mora import parse_morae


def propose_grid(reading: str, subdivisions: int = 16, pickup: int = 0) -> dict:
    moras, warnings = parse_morae(reading)
    if subdivisions < 4:
        raise ValueError("subdivisions must be at least 4")
    events = []
    for index, mora in enumerate(moras):
        grid = pickup + index
        events.append(
            {
                "mora": mora.surface,
                "grid": grid % subdivisions,
                "bar_offset": grid // subdivisions,
                "strong_grid": (grid % subdivisions) in {0, subdivisions // 2},
            }
        )
    bars_needed = max(1, ((pickup + len(moras) - 1) // subdivisions) + 1) if moras else 1
    return {
        "status": "proposal-only",
        "reading": reading,
        "subdivisions_per_bar": subdivisions,
        "pickup_slots": pickup,
        "events": events,
        "bars_needed_if_one_mora_per_slot": bars_needed,
        "warnings": warnings,
        "limitations": [
            "This grid does not infer swing, microtiming, stress, rests, or actual breath.",
            "Pocket and performability require a beat and a human or recorded performance.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reading")
    parser.add_argument("--subdivisions", type=int, default=16)
    parser.add_argument("--pickup", type=int, default=0)
    args = parser.parse_args()
    print(
        json.dumps(
            propose_grid(args.reading, args.subdivisions, args.pickup),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
