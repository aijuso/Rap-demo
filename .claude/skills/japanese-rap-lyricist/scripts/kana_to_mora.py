#!/usr/bin/env python3
"""Parse a Japanese reading into morae without silently discarding N/Q/R."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from normalize_text import normalize_kana


SMALL = set("ャュョァィゥェォヮ")
VOWEL = {
    **{c: "a" for c in "アカサタナハマヤラワガザダバパヷ"},
    **{c: "i" for c in "イキシチニヒミリヰギジヂビピヸ"},
    **{c: "u" for c in "ウクスツヌフムユルグズヅブプヴ"},
    **{c: "e" for c in "エケセテネヘメレヱゲゼデベペヹ"},
    **{c: "o" for c in "オコソトノホモヨロヲゴゾドボポヺ"},
    "ァ": "a",
    "ィ": "i",
    "ゥ": "u",
    "ェ": "e",
    "ォ": "o",
    "ヮ": "a",
    "ャ": "a",
    "ュ": "u",
    "ョ": "o",
}

ONSETS = {
    "ア": "", "イ": "", "ウ": "", "エ": "", "オ": "",
    "カ": "k", "キ": "k", "ク": "k", "ケ": "k", "コ": "k",
    "サ": "s", "シ": "sh", "ス": "s", "セ": "s", "ソ": "s",
    "タ": "t", "チ": "ch", "ツ": "ts", "テ": "t", "ト": "t",
    "ナ": "n", "ニ": "n", "ヌ": "n", "ネ": "n", "ノ": "n",
    "ハ": "h", "ヒ": "h", "フ": "f", "ヘ": "h", "ホ": "h",
    "マ": "m", "ミ": "m", "ム": "m", "メ": "m", "モ": "m",
    "ヤ": "y", "ユ": "y", "ヨ": "y",
    "ラ": "r", "リ": "r", "ル": "r", "レ": "r", "ロ": "r",
    "ワ": "w", "ヰ": "w", "ヱ": "w", "ヲ": "w",
    "ガ": "g", "ギ": "g", "グ": "g", "ゲ": "g", "ゴ": "g",
    "ザ": "z", "ジ": "j", "ズ": "z", "ゼ": "z", "ゾ": "z",
    "ダ": "d", "ヂ": "j", "ヅ": "z", "デ": "d", "ド": "d",
    "バ": "b", "ビ": "b", "ブ": "b", "ベ": "b", "ボ": "b",
    "パ": "p", "ピ": "p", "プ": "p", "ペ": "p", "ポ": "p",
    "ヴ": "v",
}


@dataclass(frozen=True)
class Mora:
    surface: str
    onset: str
    nucleus: str
    special: str | None = None
    source_start: int = 0
    source_end: int = 0

    @property
    def signature(self) -> str:
        if self.special == "N":
            return "N"
        if self.special == "Q":
            return "Q"
        return self.nucleus


def onset_for(surface: str) -> str:
    base = ONSETS.get(surface[0], "")
    if len(surface) == 1:
        return base
    small = surface[1]
    if small in "ャュョ":
        return base.rstrip("iy") + "y"
    if surface[0] in {"フ", "ヴ"}:
        return ONSETS[surface[0]]
    if surface[0] in {"テ", "デ"} and small == "ィ":
        return ONSETS[surface[0]]
    if surface[0] == "ト" and small == "ゥ":
        return "t"
    if surface[0] == "ド" and small == "ゥ":
        return "d"
    return base


def parse_morae(reading: str) -> tuple[list[Mora], list[str]]:
    text = normalize_kana(reading, keep_boundaries=True)
    moras: list[Mora] = []
    warnings: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == " ":
            i += 1
            continue
        if char == "ン":
            moras.append(Mora(char, "", "", "N", i, i + 1))
            i += 1
            continue
        if char == "ッ":
            moras.append(Mora(char, "", "", "Q", i, i + 1))
            i += 1
            continue
        if char == "ー":
            if not moras or not moras[-1].nucleus:
                warnings.append(f"orphan long mark at {i}")
                i += 1
                continue
            moras.append(Mora(char, "", moras[-1].nucleus, "R", i, i + 1))
            i += 1
            continue
        if char in SMALL:
            warnings.append(f"orphan small kana {char!r} at {i}")
            i += 1
            continue
        if char not in VOWEL:
            warnings.append(f"unknown reading symbol {char!r} at {i}")
            i += 1
            continue
        surface = char
        end = i + 1
        if end < len(text) and text[end] in SMALL:
            surface += text[end]
            end += 1
        nucleus = VOWEL[surface[-1]]
        moras.append(Mora(surface, onset_for(surface), nucleus, None, i, end))
        i = end
    return moras, warnings


def analysis(reading: str) -> dict:
    moras, warnings = parse_morae(reading)
    return {
        "reading": reading,
        "normalized_reading": normalize_kana(reading, keep_boundaries=True),
        "moras": [asdict(m) | {"signature": m.signature} for m in moras],
        "mora_count": len(moras),
        "signature": [m.signature for m in moras],
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reading")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analysis(args.reading)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(" ".join(m["surface"] for m in payload["moras"]))
        print(" ".join(payload["signature"]))
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
