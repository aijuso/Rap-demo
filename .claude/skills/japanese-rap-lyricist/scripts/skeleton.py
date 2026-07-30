#!/usr/bin/env python3
"""Extract vowel and consonant skeletons from a kana reading.

The vowel skeleton is the ordered nucleus sequence ("a-a-a-a" for カタカタ).
The consonant skeleton is the ordered onset sequence in two spellings:

- compact: one token per mora joined directly when every onset is a single
  letter or marker (カタカタ -> "ktkt", ポケット -> "pkQt");
- dotted:  always dot-separated, unambiguous for multi-letter onsets
  (キャク -> "ky.k").

Markers: "-" onsetless vowel mora, "N" moraic nasal, "Q" geminate stop,
":" long-vowel continuation.
"""

from __future__ import annotations

import argparse
import json

from kana_to_mora import Mora, parse_morae


def consonant_token(mora: Mora) -> str:
    if mora.special == "N":
        return "N"
    if mora.special == "Q":
        return "Q"
    if mora.special == "R":
        return ":"
    return mora.onset or "-"


def vowel_token(mora: Mora) -> str:
    if mora.special in {"N", "Q"}:
        return mora.special
    return mora.nucleus or "?"


def skeletons(reading: str) -> dict:
    moras, warnings = parse_morae(reading)
    consonant_tokens = [consonant_token(m) for m in moras]
    vowel_tokens = [vowel_token(m) for m in moras]
    return {
        "reading": reading,
        "mora_count": len(moras),
        "moras": [m.surface for m in moras],
        "vowel_skeleton": "-".join(vowel_tokens),
        "consonant_skeleton": "".join(consonant_tokens),
        "consonant_skeleton_dotted": ".".join(consonant_tokens),
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("reading")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = skeletons(args.reading)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload["vowel_skeleton"])
        print(payload["consonant_skeleton"])
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
