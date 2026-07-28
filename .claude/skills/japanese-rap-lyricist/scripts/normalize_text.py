#!/usr/bin/env python3
"""Conservative normalization helpers for Japanese lyric analysis."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata


BOUNDARY_RE = re.compile(r"[\s、。,.!?！？・/／|｜「」『』（）()\[\]【】]+")
KANA_RE = re.compile(r"^[\u3040-\u30ffー\s、。,.!?！？・/／|｜「」『』（）()\[\]【】]+$")


def nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def hiragana_to_katakana(text: str) -> str:
    result: list[str] = []
    for char in text:
        code = ord(char)
        if 0x3041 <= code <= 0x3096:
            result.append(chr(code + 0x60))
        else:
            result.append(char)
    return "".join(result)


def normalize_kana(text: str, *, keep_boundaries: bool = True) -> str:
    value = hiragana_to_katakana(nfkc(text)).strip()
    if keep_boundaries:
        value = BOUNDARY_RE.sub(" ", value)
        return re.sub(r"\s+", " ", value).strip()
    return BOUNDARY_RE.sub("", value)


def is_kana_text(text: str) -> bool:
    return bool(text.strip()) and bool(KANA_RE.fullmatch(nfkc(text)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    normalized = normalize_kana(args.text, keep_boundaries=not args.compact)
    payload = {
        "surface": args.text,
        "normalized": normalized,
        "kana_only": is_kana_text(args.text),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else normalized)


if __name__ == "__main__":
    main()
