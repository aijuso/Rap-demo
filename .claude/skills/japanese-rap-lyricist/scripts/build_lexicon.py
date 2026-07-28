#!/usr/bin/env python3
"""Build a compact JSONL rhyme lexicon from user-supplied TSV.

Expected columns: surface, reading, optional pos, optional comma-separated tags.
No commercial lyric corpus is bundled or scraped.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from kana_to_mora import parse_morae
from normalize_text import normalize_kana


def build(source: Path, output: Path) -> dict:
    written = skipped = 0
    with source.open(encoding="utf-8", newline="") as handle, output.open(
        "w", encoding="utf-8"
    ) as target:
        reader = csv.reader(handle, delimiter="\t")
        for row_index, row in enumerate(reader, 1):
            if not row or row[0].startswith("#"):
                continue
            if len(row) < 2:
                skipped += 1
                continue
            surface, reading = row[0].strip(), normalize_kana(row[1].strip())
            pos = row[2].strip() if len(row) > 2 else ""
            tags = [item.strip() for item in row[3].split(",") if item.strip()] if len(row) > 3 else []
            moras, warnings = parse_morae(reading)
            if not moras or warnings:
                skipped += 1
                continue
            signature = [m.signature for m in moras]
            item = {
                "surface": surface,
                "reading": reading,
                "pos": pos,
                "tags": tags,
                "mora_count": len(moras),
                "signature": signature,
                "reversed_signature": list(reversed(signature)),
                "source_row": row_index,
            }
            target.write(json.dumps(item, ensure_ascii=False) + "\n")
            written += 1
    return {"written": written, "skipped": skipped, "output": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
