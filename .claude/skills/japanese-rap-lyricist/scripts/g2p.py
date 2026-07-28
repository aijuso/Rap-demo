#!/usr/bin/env python3
"""Return pronunciation candidates with provenance and confidence.

The script deliberately refuses to guess kanji readings when no backend is available.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict

from kana_to_mora import analysis as mora_analysis
from normalize_text import is_kana_text, normalize_kana


@dataclass
class Candidate:
    reading: str
    source: str
    confidence: float
    notes: list[str]


def candidates(text: str, manual_reading: str | None = None) -> tuple[list[Candidate], list[str]]:
    results: list[Candidate] = []
    warnings: list[str] = []
    if manual_reading:
        results.append(Candidate(normalize_kana(manual_reading), "manual", 1.0, []))
    if is_kana_text(text):
        direct = normalize_kana(text)
        if all(item.reading != direct for item in results):
            results.append(Candidate(direct, "surface-kana", 0.98, []))
    try:
        import pyopenjtalk  # type: ignore

        reading = pyopenjtalk.g2p(text, kana=True)
        if isinstance(reading, list):
            reading = "".join(reading)
        reading = normalize_kana(str(reading))
        if reading and all(item.reading != reading for item in results):
            results.append(
                Candidate(
                    reading,
                    "pyopenjtalk",
                    0.82,
                    ["Verify names, slang, numbers, and performed contractions."],
                )
            )
    except Exception as exc:
        warnings.append(f"pyopenjtalk unavailable or failed: {type(exc).__name__}")
    try:
        from fugashi import Tagger  # type: ignore

        tagger = Tagger()
        parts: list[str] = []
        for token in tagger(text):
            feature = token.feature
            pron = getattr(feature, "pron", None) or getattr(feature, "pronBase", None)
            parts.append(pron or token.surface)
        reading = normalize_kana("".join(parts))
        if reading and all(item.reading != reading for item in results):
            results.append(
                Candidate(
                    reading,
                    "fugashi-unidic",
                    0.86,
                    ["Verify OOV tokens and the intended spoken form."],
                )
            )
    except Exception as exc:
        warnings.append(f"fugashi/UniDic unavailable or failed: {type(exc).__name__}")
    if not results:
        warnings.append("No reliable reading produced; supply --reading.")
    return sorted(results, key=lambda item: item.confidence, reverse=True), warnings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--reading")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    items, warnings = candidates(args.text, args.reading)
    payload = {
        "surface": args.text,
        "candidates": [
            asdict(item) | {"mora_analysis": mora_analysis(item.reading)} for item in items
        ],
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in payload["candidates"]:
            print(f"{item['reading']}\t{item['source']}\t{item['confidence']:.2f}")
        for warning in warnings:
            print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
